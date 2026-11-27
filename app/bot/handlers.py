from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (CallbackQuery, ChatMemberUpdated, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PreCheckoutQuery, WebAppInfo)

from .. import content, db
from ..config import settings
from .texts import add_channel_link, add_group_link, t

log = logging.getLogger(__name__)
router = Router()
_awaiting_suggestion: set[int] = set()
_awaiting_payment_msg: set[int] = set()
_awaiting_paysupport: set[int] = set()


def lang_of(code: str | None) -> str:
    return "en" if code and not code.startswith("ar") else "ar"


def app_button(lang: str, path: str = "") -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t(lang, "open_app"), web_app=WebAppInfo(url=f"{settings.public_url}/{path}"))


def main_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [[app_button(lang)],
            [InlineKeyboardButton(text=t(lang, "follow_main", ig=settings.instagram_main),
                                  url=f"https://instagram.com/{settings.instagram_main}")]]
    if settings.instagram_partner:
        rows[-1].append(InlineKeyboardButton(
            text=t(lang, "follow_partner", label=settings.instagram_partner_label),
            url=f"https://instagram.com/{settings.instagram_partner}"))
    rows.append([InlineKeyboardButton(text=t(lang, "add_channel"), url=add_channel_link()),
                 InlineKeyboardButton(text=t(lang, "add_group"), url=add_group_link())])
    rows.append([InlineKeyboardButton(text=t(lang, "suggest_btn"), callback_data="suggest")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def channel_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "add_channel"), url=add_channel_link())],
        [InlineKeyboardButton(text=t(lang, "add_group"), url=add_group_link())],
        [app_button(lang, "#channels")]])


def is_admin(uid: int) -> bool:
    return uid in settings.admin_ids


# ───────────── user commands ─────────────

@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start(m: Message, command: CommandObject):
    u = m.from_user
    row = await db.upsert_user(u.id, u.first_name, u.username, u.language_code, command.args)
    lang = row["lang"]
    from .. import referral
    if referral.inviter_from(command.args) and await referral.attach(u.id, command.args):
        await m.answer(t(lang, "welcome", name=escape(u.first_name or "")), reply_markup=main_keyboard(lang),
                       disable_web_page_preview=True)
        await m.answer(t(lang, "ref_gift"), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[app_button(lang)]]))
        return
    if command.args == "pay":
        await send_pay_methods(m, lang)
        return
    if command.args == "invite":
        await send_invite(m, lang)
        return
    if command.args == "channel":
        await m.answer(t(lang, "channel_info"), reply_markup=channel_keyboard(lang))
        return
    if command.args in ("inline_daily", "inline_weekly", "inline_place"):
        page = {"inline_daily": "#daily", "inline_weekly": "#weekly", "inline_place": ""}[command.args]
        await m.answer(t(lang, command.args, name=escape(u.first_name or "")),
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[app_button(lang, page)]]))
        return
    if command.args in ("daily", "weekly"):
        await m.answer(t(lang, f"start_{command.args}"),
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[app_button(lang, f"#{command.args}")]]))
        return
    await m.answer(t(lang, "welcome", name=escape(u.first_name or "")), reply_markup=main_keyboard(lang),
                   disable_web_page_preview=True)


async def send_invite(m: Message, lang: str) -> None:
    from urllib.parse import quote

    from .. import referral
    st = await referral.stats(m.from_user.id)
    share = f"https://t.me/share/url?url={quote(st['link'])}&text={quote(t(lang, 'invite_share_text'))}"
    await m.answer(t(lang, "invite_info", link=st["link"], invited=st["invited"], active=st["active"], days=st["days"]),
                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                       [InlineKeyboardButton(text=t(lang, "invite_share"), url=share)], [app_button(lang, "#invite")]]),
                   disable_web_page_preview=True)


@router.message(Command("invite"), F.chat.type == ChatType.PRIVATE)
async def cmd_invite(m: Message):
    row = await db.upsert_user(m.from_user.id, m.from_user.first_name, m.from_user.username, m.from_user.language_code)
    await send_invite(m, row["lang"])


@router.message(Command("app"), F.chat.type == ChatType.PRIVATE)
async def cmd_app(m: Message):
    lang = lang_of(m.from_user.language_code)
    await m.answer("🔭", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[app_button(lang)]]))


@router.message(Command("channel"), F.chat.type == ChatType.PRIVATE)
async def cmd_channel(m: Message):
    lang = lang_of(m.from_user.language_code)
    await m.answer(t(lang, "channel_info"), reply_markup=channel_keyboard(lang))


@router.message(Command("help"), F.chat.type == ChatType.PRIVATE)
async def cmd_help(m: Message):
    lang = lang_of(m.from_user.language_code)
    await m.answer(t(lang, "help"), reply_markup=main_keyboard(lang))


@router.message(Command("about"), F.chat.type == ChatType.PRIVATE)
async def cmd_about(m: Message):
    lang = lang_of(m.from_user.language_code)
    await m.answer(t(lang, "about", source=settings.source_url), disable_web_page_preview=True)


@router.message(Command("suggest"), F.chat.type == ChatType.PRIVATE)
async def cmd_suggest(m: Message, command: CommandObject, bot: Bot):
    lang = lang_of(m.from_user.language_code)
    if command.args:
        await save_feedback(bot, m.from_user.id, m.from_user.first_name, m.from_user.username, command.args)
        await m.answer(t(lang, "suggest_thanks"))
        return
    _awaiting_suggestion.add(m.from_user.id)
    await m.answer(t(lang, "suggest_prompt"))


@router.callback_query(F.data == "suggest")
async def cb_suggest(c: CallbackQuery):
    _awaiting_suggestion.add(c.from_user.id)
    await c.message.answer(t(lang_of(c.from_user.language_code), "suggest_prompt"))
    await c.answer()


@router.message(Command("cancel"), F.chat.type == ChatType.PRIVATE)
async def cmd_cancel(m: Message):
    _awaiting_suggestion.discard(m.from_user.id)
    _awaiting_payment_msg.discard(m.from_user.id)
    _awaiting_paysupport.discard(m.from_user.id)
    await m.answer(t(lang_of(m.from_user.language_code), "cancelled"))


async def save_feedback(bot: Bot, uid: int, first_name: str | None, username: str | None, text: str,
                        kind: str = "suggestion") -> None:
    text = text.strip()[:3500]
    stored = f"💳 [طلب دفع] {text}" if kind == "payment" else text
    await db.pool().execute("INSERT INTO feedback(user_id,text) VALUES($1,$2)", uid, stored)
    who = f"@{username}" if username else escape(first_name or "")
    head = "💳 <b>طلب طريقة دفع تانية</b>" if kind == "payment" else "💡 <b>اقتراح جديد</b>"
    msg = (f"{head}\nمن: {who} (<code>{uid}</code>)\n\n{escape(text)}\n\n"
           f"للرد: <code>/reply {uid} </code>نص الرد")
    for admin in settings.admin_ids:
        try:
            await bot.send_message(admin, msg)
        except Exception as e:  # admin hasn't started the bot, etc.
            log.warning("feedback notify failed: %s", e)


# ───────────── admin commands ─────────────

@router.message(Command("stats"), F.chat.type == ChatType.PRIVATE)
async def cmd_stats(m: Message):
    if not is_admin(m.from_user.id):
        return
    p = db.pool()
    users = await p.fetchval("SELECT count(*) FROM users")
    active7 = await p.fetchval("SELECT count(*) FROM users WHERE last_seen > now() - interval '7 days'")
    new1 = await p.fetchval("SELECT count(*) FROM users WHERE created_at > now() - interval '1 day'")
    daily = await p.fetchval("SELECT count(*) FROM daily_prefs WHERE subscribed")
    chats = await p.fetchval("SELECT count(*) FROM broadcast_chats WHERE active")
    charts = await p.fetchval("SELECT count(*) FROM events WHERE name='chart'")
    profiles = await p.fetchval("SELECT count(*) FROM profiles")
    fb = await p.fetchval("SELECT count(*) FROM feedback")
    prem = await p.fetchval("SELECT count(DISTINCT user_id) FROM subscriptions WHERE ends_at > now()")
    stars = await p.fetchval("SELECT coalesce(sum(stars),0) FROM payments WHERE NOT refunded")
    ads = await p.fetch("""SELECT provider, count(*) n FROM ad_events WHERE status='completed'
                           GROUP BY provider ORDER BY n DESC""")
    syn = await p.fetchval("SELECT count(*) FROM events WHERE name='synastry'")
    nofill = await p.fetchval("SELECT count(*) FROM ad_events WHERE status='nofill'")
    langs = await p.fetch("SELECT lang, count(*) n FROM users GROUP BY lang ORDER BY n DESC")
    countries = await p.fetch("""SELECT country, count(DISTINCT user_id) n FROM profiles WHERE is_main
                                 GROUP BY country ORDER BY n DESC LIMIT 8""")
    sources = await p.fetch("""SELECT coalesce(start_param,'-') s, count(*) n FROM users
                               GROUP BY s ORDER BY n DESC LIMIT 6""")
    txt = (f"📊 <b>الإحصائيات</b>\n👥 المستخدمين: {users} (جدد اليوم {new1}، نشطين 7 أيام {active7})\n"
           f"🌅 مشتركين بالأبراج: {daily}\n📢 قنوات/مجموعات: {chats}\n🔭 خرائط محسوبة: {charts} · ملفات محفوظة: {profiles}\n"
           f"💡 اقتراحات: {fb}\n💞 توافقات: {syn}\n⭐ مميزين الآن: {prem} · مجموع النجوم: {stars}\n"
           f"📺 إعلانات مكتملة: " + (", ".join(f"{r['provider']} {r['n']}" for r in ads) or "0")
           + f" · بدون إعلان متاح: {nofill}\n\n🌐 اللغات: " + ", ".join(f"{r['lang']} {r['n']}" for r in langs)
           + "\n📍 دول الولادة: " + (", ".join(f"{r['country']} {r['n']}" for r in countries) or "-")
           + "\n🔗 المصادر: " + ", ".join(f"{r['s']} {r['n']}" for r in sources))
    await m.answer(txt)


@router.message(Command("reply"), F.chat.type == ChatType.PRIVATE)
async def cmd_reply(m: Message, command: CommandObject, bot: Bot):
    if not is_admin(m.from_user.id) or not command.args:
        return
    uid, _, text = command.args.partition(" ")
    try:
        await bot.send_message(int(uid), f"✉️ <b>رد من فريق الخيميائي</b>\n\n{escape(text)}")
        await m.answer("✅ تم الإرسال")
    except Exception as e:
        await m.answer(f"❌ {e}")


@router.message(Command("broadcast"), F.chat.type == ChatType.PRIVATE)
async def cmd_broadcast(m: Message, command: CommandObject, bot: Bot):
    """Reply to any message with /broadcast [all|ar|en|daily] to copy it to that segment."""
    if not is_admin(m.from_user.id):
        return
    if not m.reply_to_message:
        await m.answer("ردّ على الرسالة اللي بدك تبعتها بـ /broadcast all أو ar أو en أو daily")
        return
    seg = (command.args or "all").strip()
    q = {"all": "SELECT id FROM users WHERE NOT blocked",
         "ar": "SELECT id FROM users WHERE NOT blocked AND lang='ar'",
         "en": "SELECT id FROM users WHERE NOT blocked AND lang='en'",
         "daily": "SELECT u.id FROM users u JOIN daily_prefs d ON d.user_id=u.id WHERE d.subscribed AND NOT u.blocked",
         }.get(seg)
    if not q:
        await m.answer("الشرائح: all, ar, en, daily")
        return
    ids = [r["id"] for r in await db.pool().fetch(q)]
    await m.answer(f"⏳ جاري الإرسال لـ {len(ids)} مستخدم…")
    asyncio.create_task(_broadcast(bot, m.chat.id, m.reply_to_message, ids))


async def _broadcast(bot: Bot, admin_chat: int, src: Message, ids: list[int]):
    ok = fail = 0
    for uid in ids:
        try:
            await src.copy_to(uid)
            ok += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            try:
                await src.copy_to(uid)
                ok += 1
            except Exception:
                fail += 1
        except TelegramForbiddenError:
            fail += 1
            await db.pool().execute("UPDATE users SET blocked=TRUE WHERE id=$1", uid)
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)  # ~20 msg/s, under Telegram's limit
    await bot.send_message(admin_chat, f"✅ انتهى البث: وصل {ok}، فشل {fail}")


@router.message(Command("setdaily"), F.chat.type == ChatType.PRIVATE)
async def cmd_setdaily(m: Message, command: CommandObject):
    if not is_admin(m.from_user.id):
        return
    url = (command.args or "").strip()
    await db.kv_set("daily_url", url)
    from .. import scheduler as _sch
    _sch.set_url("daily_url", url)
    try:
        n = await content.fetch_daily(url)
        await m.answer(f"✅ تم حفظ الرابط وسحب {n} يوم")
    except Exception as e:
        await m.answer(f"⚠️ تم حفظ الرابط، بس السحب فشل: {e}")


@router.message(Command("fetch"), F.chat.type == ChatType.PRIVATE)
async def cmd_fetch(m: Message):
    """Pull both forecast files now (after editing them on GitHub)."""
    if not is_admin(m.from_user.id):
        return
    lines = []
    for kind, lang, key in content.FEEDS:
        label = content.FEED_LABELS[(kind, lang)]
        try:
            lines.append(f"✅ {label}: {await content.fetch_feed(kind, lang, await content.feed_url(key))}")
        except Exception as e:
            lines.append(f"❌ {label}: {escape(str(e))[:200]}")
    await m.answer("\n".join(lines))


@router.message(Command("grant"), F.chat.type == ChatType.PRIVATE)
async def cmd_grant(m: Message, command: CommandObject):
    """/grant <user_id> <days> [note] — manual premium (for users without Stars)."""
    if not is_admin(m.from_user.id):
        return
    parts = (command.args or "").split(maxsplit=2)
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        await m.answer("الاستخدام: /grant user_id days [ملاحظة]")
        return
    uid, days = int(parts[0]), int(parts[1])
    exists = await db.pool().fetchval("SELECT 1 FROM users WHERE id=$1", uid)
    if not exists:
        await m.answer("❌ المستخدم لازم يكون فاتح البوت مرة على الأقل")
        return
    await db.pool().execute(
        "INSERT INTO subscriptions(user_id,source,ends_at,granted_by,note) VALUES($1,'manual',$2,$3,$4)",
        uid, datetime.now(timezone.utc) + timedelta(days=days), m.from_user.id, parts[2] if len(parts) > 2 else None)
    await m.answer(f"✅ تمت ترقية {uid} لمدة {days} يوم")


# ───────────── Stars payments ─────────────

@router.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    ok = q.currency == "XTR" and q.invoice_payload in (f"premium:{q.from_user.id}", f"synrep:{q.from_user.id}",
                                                      f"natrep:{q.from_user.id}")
    await q.answer(ok=ok, error_message=None if ok else "Invalid invoice")


@router.message(F.successful_payment)
async def paid(m: Message):
    from ..monetize import record_payment
    lang = lang_of(m.from_user.language_code)
    if m.successful_payment.invoice_payload.startswith(("synrep:", "natrep:")):
        from ..monetize import record_report_payment
        await record_report_payment(m.from_user.id, m.successful_payment)
        syn = m.successful_payment.invoice_payload.startswith("synrep:")
        what_ar, what_en = ("«📄 تقرير التوافق»", "“📄 Compatibility report”") if syn else ("«📄 تقرير فلكي»", "“📄 Astrological report”")
        await m.answer(f"✅ تم الدفع. ارجع للتطبيق واضغط {what_ar} مرة تانية." if lang == "ar"
                       else f"✅ Paid. Go back to the app and tap {what_en} again.",
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[app_button(lang, "#synastry" if syn else "")]]))
        for a in settings.admin_ids:
            try:
                await m.bot.send_message(a, f"⭐ دفعة {m.successful_payment.total_amount} نجمة ({'تقرير توافق' if syn else 'تقرير فلكي'}) من "
                                            f"{escape(m.from_user.full_name)} (<code>{m.from_user.id}</code>)")
            except Exception:
                pass
        return
    await record_payment(m.from_user.id, m.successful_payment)
    first = not m.successful_payment.is_recurring or m.successful_payment.is_first_recurring
    if first:
        await m.answer("✨ <b>تم تفعيل الاشتراك المميز!</b> شكراً لدعمك. افتح التطبيق وجرّب الخرائط الفرعية والتوافق بلا إعلانات."
                       if lang == "ar" else "✨ <b>Premium is active!</b> Thanks for your support. Open the app to explore.",
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[app_button(lang, "#premium")]]))
    for a in settings.admin_ids:
        try:
            await m.bot.send_message(a, f"⭐ دفعة {m.successful_payment.total_amount} نجمة من "
                                        f"{escape(m.from_user.full_name)} (<code>{m.from_user.id}</code>)"
                                        + (" · تجديد" if not first else ""))
        except Exception:
            pass


@router.message(Command("setprice"), F.chat.type == ChatType.PRIVATE)
async def cmd_setprice(m: Message, command: CommandObject):
    if not is_admin(m.from_user.id):
        return
    v = (command.args or "").strip()
    if not v.isdigit() or not 1 <= int(v) <= 10000:
        await m.answer("الاستخدام: /setprice 300")
        return
    await db.kv_set("premium_stars", v)
    await m.answer(f"✅ سعر الاشتراك الجديد {v} نجمة (للاشتراكات الجديدة فقط)")


@router.message(Command("refund"), F.chat.type == ChatType.PRIVATE)
async def cmd_refund(m: Message, command: CommandObject, bot: Bot):
    """/refund <user_id> — refunds that user's latest Stars payment and ends the premium it bought."""
    if not is_admin(m.from_user.id) or not (command.args or "").strip().isdigit():
        await m.answer("الاستخدام: /refund user_id") if is_admin(m.from_user.id) else None
        return
    uid = int(command.args.strip())
    pid = await db.pool().fetchval(
        "SELECT id FROM payments WHERE user_id=$1 AND NOT refunded ORDER BY created_at DESC LIMIT 1", uid)
    if not pid:
        await m.answer("ما في دفعة قابلة للاسترداد")
        return
    try:
        await m.answer(await do_refund(bot, pid))
    except Exception as e:
        await m.answer(f"❌ {escape(str(e))[:300]}")


# ───────────── other payment methods (Stars resellers) ─────────────

async def send_pay_methods(m: Message, lang: str) -> None:
    from .. import paymethods
    items = paymethods.localized(await paymethods.load(), lang)
    head = {"sy": "🇸🇾 داخل سوريا" if lang == "ar" else "🇸🇾 Inside Syria",
            "intl": "🌍 بطاقات فيزا وماستر وغيرها" if lang == "ar" else "🌍 Visa, Mastercard and more"}
    blocks = []
    for region in ("sy", "intl"):
        rows = [f"• <a href=\"{escape(i['url'])}\">{escape(i['name'])}</a>{' ✅' if i['official'] else ''}\n   {escape(i['note'])}"
                for i in items if i["region"] == region]
        if rows:
            blocks.append(f"<b>{head[region]}</b>\n" + "\n".join(rows))
    others = [i for i in items if i["region"] not in head]
    if others:
        blocks.append("\n".join(f"• <a href=\"{escape(i['url'])}\">{escape(i['name'])}</a>\n   {escape(i['note'])}" for i in others))
    kb = [[InlineKeyboardButton(text=("🇸🇾 " if i["region"] == "sy" else "🌍 ") + i["name"], url=i["url"])] for i in items]
    kb.append([InlineKeyboardButton(text=t(lang, "pay_contact"), callback_data="paywrite")])
    kb.append([app_button(lang, "#premium")])
    await m.answer(t(lang, "pay_prompt", list="\n\n".join(blocks)),
                   reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), disable_web_page_preview=True)


@router.message(Command("pay"), F.chat.type == ChatType.PRIVATE)
async def cmd_pay(m: Message):
    await send_pay_methods(m, lang_of(m.from_user.language_code))


@router.callback_query(F.data == "paywrite")
async def cb_paywrite(c: CallbackQuery):
    _awaiting_payment_msg.add(c.from_user.id)
    _awaiting_suggestion.discard(c.from_user.id)
    _awaiting_paysupport.discard(c.from_user.id)
    await c.message.answer(t(lang_of(c.from_user.language_code), "pay_write"))
    await c.answer()


# ───────────── /paysupport (required by Telegram's Stars terms) ─────────────

def _what(lang: str, payload: str | None) -> str:
    kind = (payload or "premium:").split(":", 1)[0]
    return t(lang, f"what_{kind}") if kind in ("premium", "natrep", "synrep") else kind


async def _payments_list(uid: int, lang: str, limit: int = 5) -> tuple[list, str]:
    rows = await db.pool().fetch(
        "SELECT * FROM payments WHERE user_id=$1 ORDER BY created_at DESC LIMIT $2", uid, limit)
    if not rows:
        return rows, t(lang, "ps_none")
    return rows, "\n".join(t(lang, "ps_row", date=r["created_at"].strftime("%Y-%m-%d"), stars=r["stars"],
                                what=_what(lang, r["payload"]),
                                ref=t(lang, "ps_refunded") if r["refunded"] else "") for r in rows)


@router.message(Command("paysupport"), F.chat.type == ChatType.PRIVATE)
async def cmd_paysupport(m: Message):
    lang = lang_of(m.from_user.language_code)
    await db.upsert_user(m.from_user.id, m.from_user.first_name, m.from_user.username, m.from_user.language_code)
    _, lst = await _payments_list(m.from_user.id, lang)
    _awaiting_paysupport.add(m.from_user.id)
    _awaiting_suggestion.discard(m.from_user.id)
    _awaiting_payment_msg.discard(m.from_user.id)
    await m.answer(t(lang, "ps_intro", list=lst))


async def send_paysupport(bot: Bot, u, text: str) -> None:
    text = text.strip()[:3500]
    await db.pool().execute("INSERT INTO feedback(user_id,text) VALUES($1,$2)", u.id, f"🧾 [دعم دفع] {text}")
    rows, lst = await _payments_list(u.id, "ar", 8)
    prem = await db.pool().fetchval(
        "SELECT max(ends_at) FROM subscriptions WHERE user_id=$1 AND ends_at > now()", u.id)
    who = f"@{u.username}" if u.username else escape(u.first_name or "")
    msg = (f"🧾 <b>طلب دعم دفع</b>\nمن: {who} (<code>{u.id}</code>)\n"
           f"المميز فعّال لـ: {prem.strftime('%Y-%m-%d') if prem else 'لا'}\n\n<b>الدفعات:</b>\n{lst}\n\n"
           f"<b>الرسالة:</b>\n{escape(text)}\n\nللرد: <code>/reply {u.id} </code>نص الرد")
    kb = [[InlineKeyboardButton(text=f"↩️ استرداد {r['stars']}⭐ · {_what('ar', r['payload'])} · {r['created_at']:%m-%d}",
                                callback_data=f"rf:{r['id']}")] for r in rows if not r["refunded"]][:4]
    for admin in settings.admin_ids:
        try:
            await bot.send_message(admin, msg, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb) if kb else None)
        except Exception as e:
            log.warning("paysupport notify failed: %s", e)


async def do_refund(bot: Bot, payment_id: int) -> str:
    row = await db.pool().fetchrow("SELECT * FROM payments WHERE id=$1", payment_id)
    if not row:
        return "ما لقيت الدفعة"
    if row["refunded"]:
        return "هالدفعة مسترَدة من قبل"
    await bot.refund_star_payment(user_id=row["user_id"], telegram_payment_charge_id=row["charge_id"])
    p = db.pool()
    await p.execute("UPDATE payments SET refunded=TRUE WHERE id=$1", row["id"])
    payload = row["payload"] or ""
    if payload.startswith("natrep:"):
        await p.execute("UPDATE users SET report_credits=GREATEST(report_credits-1,0) WHERE id=$1", row["user_id"])
    elif payload.startswith("synrep:"):
        await p.execute("UPDATE users SET syn_report_credits=GREATEST(syn_report_credits-1,0) WHERE id=$1", row["user_id"])
    else:   # premium: end the period this payment bought
        await p.execute("UPDATE subscriptions SET ends_at=now() WHERE charge_id=$1 AND ends_at > now()", row["charge_id"])
    lang = await p.fetchval("SELECT lang FROM users WHERE id=$1", row["user_id"]) or "ar"
    try:
        await bot.send_message(row["user_id"], t(lang, "ps_refund_done", stars=row["stars"]))
    except Exception:
        pass
    return f"✅ استُرد {row['stars']} نجمة للمستخدم {row['user_id']} ({_what('ar', payload)})"


@router.callback_query(F.data.startswith("rf:"))
async def cb_refund_ask(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        return await c.answer()
    pid = c.data.split(":", 1)[1]
    await c.message.answer(f"متأكد بدك تسترد الدفعة #{pid}؟ الاسترداد نهائي، والمميز أو التقرير اللي اشتراه بينلغى.",
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                               InlineKeyboardButton(text="↩️ إي، استرد", callback_data=f"rfok:{pid}"),
                               InlineKeyboardButton(text="لا", callback_data="rfno")]]))
    await c.answer()


@router.callback_query(F.data.startswith("rfok:") | (F.data == "rfno"))
async def cb_refund_do(c: CallbackQuery, bot: Bot):
    if not is_admin(c.from_user.id):
        return await c.answer()
    if c.data == "rfno":
        await c.message.edit_text("تم الإلغاء.")
        return await c.answer()
    try:
        out = await do_refund(bot, int(c.data.split(":", 1)[1]))
    except Exception as e:
        out = f"❌ {escape(str(e))[:300]}"
    await c.message.edit_text(out)
    await c.answer()


# ───────────── privacy & delete my data ─────────────

def privacy_url() -> str:
    return f"{settings.public_url}/privacy" if settings.public_url else "/privacy"


@router.message(Command("privacy"), F.chat.type == ChatType.PRIVATE)
async def cmd_privacy(m: Message):
    await m.answer(t(lang_of(m.from_user.language_code), "privacy", url=privacy_url()))


@router.message(Command("deletemydata"), F.chat.type == ChatType.PRIVATE)
async def cmd_deletemydata(m: Message):
    from .. import privacy
    lang = lang_of(m.from_user.language_code)
    if is_admin(m.from_user.id):
        return await m.answer(t(lang, "del_admin"))
    s = await privacy.summary(m.from_user.id)
    await m.answer(t(lang, "del_confirm", n=s["profiles"], prem=t(lang, "del_prem") if s["premium"] else "",
                     url=privacy_url()),
                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                       [InlineKeyboardButton(text=t(lang, "del_yes"), callback_data="erase:yes")],
                       [InlineKeyboardButton(text=t(lang, "del_no"), callback_data="erase:no")]]),
                   disable_web_page_preview=True)


@router.callback_query(F.data.startswith("erase:"))
async def cb_erase(c: CallbackQuery):
    from .. import privacy
    lang = lang_of(c.from_user.language_code)
    if c.data == "erase:no" or is_admin(c.from_user.id):
        await c.message.edit_text(t(lang, "cancelled"))
        return await c.answer()
    await privacy.erase(c.from_user.id)
    for s in (_awaiting_suggestion, _awaiting_payment_msg, _awaiting_paysupport):
        s.discard(c.from_user.id)
    await c.message.edit_text(t(lang, "del_done"))
    await c.answer()


# ───────────── suggestion text capture (must stay after commands) ─────────────

@router.message(F.chat.type == ChatType.PRIVATE, F.text, ~F.text.startswith("/"))
async def any_text(m: Message, bot: Bot):
    if m.from_user.id in _awaiting_paysupport:
        _awaiting_paysupport.discard(m.from_user.id)
        await send_paysupport(bot, m.from_user, m.text)
        await m.answer(t(lang_of(m.from_user.language_code), "ps_thanks"))
        return
    if m.from_user.id in _awaiting_payment_msg:
        _awaiting_payment_msg.discard(m.from_user.id)
        await save_feedback(bot, m.from_user.id, m.from_user.first_name, m.from_user.username, m.text, kind="payment")
        await m.answer(t(lang_of(m.from_user.language_code), "pay_thanks"))
        return
    if m.from_user.id in _awaiting_suggestion:
        _awaiting_suggestion.discard(m.from_user.id)
        await save_feedback(bot, m.from_user.id, m.from_user.first_name, m.from_user.username, m.text)
        await m.answer(t(lang_of(m.from_user.language_code), "suggest_thanks"))
        return
    lang = lang_of(m.from_user.language_code)
    await m.answer(t(lang, "help"), reply_markup=main_keyboard(lang))


# ───────────── channels & groups ─────────────

@router.my_chat_member()
async def on_my_chat_member(ev: ChatMemberUpdated, bot: Bot):
    chat = ev.chat
    if chat.type == ChatType.PRIVATE:
        if ev.new_chat_member.status == ChatMemberStatus.KICKED:
            await db.pool().execute("UPDATE users SET blocked=TRUE WHERE id=$1", chat.id)
        return
    status = ev.new_chat_member.status
    adder = ev.from_user
    if status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
        await db.pool().execute("UPDATE broadcast_chats SET active=FALSE WHERE chat_id=$1", chat.id)
        from .. import scheduler as _sch
        _sch.invalidate()
        return
    can_post = status == ChatMemberStatus.ADMINISTRATOR and (
        chat.type != ChatType.CHANNEL or getattr(ev.new_chat_member, "can_post_messages", False))
    if chat.type != ChatType.CHANNEL and status == ChatMemberStatus.MEMBER:
        can_post = True
    lang = lang_of(adder.language_code) if adder else "ar"
    if not can_post:
        if adder:
            try:
                await bot.send_message(adder.id, t(lang, "chat_need_admin"))
            except Exception:
                pass
        return
    tz = None
    if adder:
        tz = await db.pool().fetchval("SELECT tz FROM daily_prefs WHERE user_id=$1", adder.id)
    tz = tz or settings.default_tz
    row = await db.pool().fetchrow(
        """INSERT INTO broadcast_chats(chat_id,title,kind,added_by,tz,lang,active)
           VALUES($1,$2,$3,$4,$5,$6,TRUE)
           ON CONFLICT(chat_id) DO UPDATE SET title=EXCLUDED.title, active=TRUE,
             added_by=coalesce(EXCLUDED.added_by, broadcast_chats.added_by)
           RETURNING *""", chat.id, chat.title, chat.type, adder.id if adder else None, tz, lang)
    await db.event(adder.id if adder else None, "chat_added")
    from .. import scheduler as _sch
    _sch.invalidate()
    try:
        await bot.send_message(chat.id, t(lang, "chat_added_post", time=row["send_time"]))
    except Exception as e:
        log.warning("cannot post in %s: %s", chat.id, e)
    if adder:
        try:
            await bot.send_message(adder.id, t(lang, "chat_added_dm", title=escape(chat.title or ""),
                                               time=row["send_time"], tz=row["tz"]))
        except Exception:
            pass
