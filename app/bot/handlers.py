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
    if command.args == "channel":
        await m.answer(t(lang, "channel_info"), reply_markup=channel_keyboard(lang))
        return
    await m.answer(t(lang, "welcome", name=escape(u.first_name or "")), reply_markup=main_keyboard(lang),
                   disable_web_page_preview=True)


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
    await m.answer(t(lang_of(m.from_user.language_code), "cancelled"))


async def save_feedback(bot: Bot, uid: int, first_name: str | None, username: str | None, text: str) -> None:
    text = text.strip()[:3500]
    await db.pool().execute("INSERT INTO feedback(user_id,text) VALUES($1,$2)", uid, text)
    who = f"@{username}" if username else escape(first_name or "")
    msg = (f"💡 <b>اقتراح جديد</b>\nمن: {who} (<code>{uid}</code>)\n\n{escape(text)}\n\n"
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
    try:
        n = await content.fetch_daily(url)
        await m.answer(f"✅ تم حفظ الرابط وسحب {n} يوم")
    except Exception as e:
        await m.answer(f"⚠️ تم حفظ الرابط، بس السحب فشل: {e}")


@router.message(Command("fetch"), F.chat.type == ChatType.PRIVATE)
async def cmd_fetch(m: Message):
    if not is_admin(m.from_user.id):
        return
    url = await db.kv_get("daily_url", settings.daily_url)
    try:
        await m.answer(f"✅ سحبت {await content.fetch_daily(url)} يوم من {url or '(لا يوجد رابط)'}")
    except Exception as e:
        await m.answer(f"❌ {e}")


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
    ok = q.currency == "XTR" and q.invoice_payload == f"premium:{q.from_user.id}"
    await q.answer(ok=ok, error_message=None if ok else "Invalid invoice")


@router.message(F.successful_payment)
async def paid(m: Message):
    from ..monetize import record_payment
    await record_payment(m.from_user.id, m.successful_payment)
    lang = lang_of(m.from_user.language_code)
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
    row = await db.pool().fetchrow(
        "SELECT * FROM payments WHERE user_id=$1 AND NOT refunded ORDER BY created_at DESC LIMIT 1", uid)
    if not row:
        await m.answer("ما في دفعة قابلة للاسترداد")
        return
    try:
        await bot.refund_star_payment(user_id=uid, telegram_payment_charge_id=row["charge_id"])
    except Exception as e:
        await m.answer(f"❌ {e}")
        return
    await db.pool().execute("UPDATE payments SET refunded=TRUE WHERE id=$1", row["id"])
    await db.pool().execute("UPDATE subscriptions SET ends_at=now() WHERE charge_id=$1", row["charge_id"])
    await m.answer(f"✅ استُرد {row['stars']} نجمة للمستخدم {uid}")


# ───────────── suggestion text capture (must stay after commands) ─────────────

@router.message(F.chat.type == ChatType.PRIVATE, F.text, ~F.text.startswith("/"))
async def any_text(m: Message, bot: Bot):
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
