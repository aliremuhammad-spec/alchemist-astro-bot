from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import content, db, forecasts
from .astro.names import SIGN_GLYPH, SIGN_KEYS, sign_name
from .bot.handlers import app_button
from .bot.texts import add_channel_link, t
from .config import settings

log = logging.getLogger(__name__)
_lock = asyncio.Lock()


def _due(send_time: str, tz: str, last_sent) -> tuple[bool, datetime]:
    now = datetime.now(ZoneInfo(tz))
    return (now.strftime("%H:%M") >= send_time and last_sent != now.date()), now


def daily_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [app_button(lang)],
        [InlineKeyboardButton(text=t(lang, "add_channel"), url=add_channel_link())]])


def split_text(text: str, limit: int = 4000) -> list[str]:
    """Split on paragraph boundaries so each piece fits a Telegram message."""
    out, cur = [], ""
    for para in text.split("\n\n"):
        while len(para) > limit:
            out.append(para[:limit])
            para = para[limit:]
        if cur and len(cur) + len(para) + 2 > limit:
            out.append(cur)
            cur = ""
        cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        out.append(cur)
    return out


def user_messages(lang: str, sign: int, day, data: dict, tz: str) -> list[str]:
    body = forecasts.daily_sign_html(data, SIGN_KEYS[sign], lang, tz)
    text = (t(lang, "daily_title", sign=sign_name(sign, lang), glyph=SIGN_GLYPH[sign], date=day.isoformat())
            + f"\n\n{body}\n\n<i>{t(lang, 'daily_footer')}</i>")
    return split_text(text)


def digest_messages(lang: str, day, data: dict, tz: str = "Asia/Damascus", limit: int = 3900) -> list[str]:
    parts = [t(lang, "digest_title", date=day.isoformat())]
    ov = forecasts.daily_overview_html(data, lang, tz)
    if ov:
        parts.append(ov)
    for i, key in enumerate(SIGN_KEYS):
        parts.append(f"{SIGN_GLYPH[i]} <b>{sign_name(i, lang)}</b>\n{forecasts.daily_sign_short(data, key, lang, tz)}")
    if data.get("format") == "md":
        parts.append(t(lang, "digest_more", link=f"https://t.me/{settings.bot_username}?start=daily"))
    parts.append(t(lang, "digest_footer", link=f"https://t.me/{settings.bot_username}?start=channel"))
    msgs, cur = [], ""
    for p in parts:
        if len(cur) + len(p) + 2 > limit and cur:
            msgs.append(cur)
            cur = ""
        cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        msgs.append(cur)
    return msgs


async def _send(bot: Bot, chat_id: int, text: str, kb=None) -> bool | None:
    """True sent, False permanently unreachable, None transient failure."""
    try:
        await bot.send_message(chat_id, text, reply_markup=kb, disable_web_page_preview=True)
        return True
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after + 1)
        return None
    except (TelegramForbiddenError, TelegramBadRequest) as e:
        log.info("unreachable %s: %s", chat_id, e)
        return False
    except Exception as e:
        log.warning("send %s failed: %s", chat_id, e)
        return None


async def _alert_missing(bot: Bot, day) -> None:
    key = f"alert_missing:{day.isoformat()}"
    if await db.kv_get(key):
        return
    await db.kv_set(key, "1")
    for a in settings.admin_ids:
        try:
            await bot.send_message(a, f"⚠️ ما في أبراج ليوم {day.isoformat()} بالملف. ما بعتت شي لهلأ. "
                                      f"تأكد من ملف GitHub أو استخدم /fetch بعد التحديث.")
        except Exception:
            pass


async def dispatch_users(bot: Bot) -> None:
    rows = await db.pool().fetch(
        """SELECT d.user_id, d.send_time, d.tz, d.sign, d.last_sent, u.lang
           FROM daily_prefs d JOIN users u ON u.id=d.user_id
           WHERE d.subscribed AND NOT u.blocked""")
    cache: dict = {}
    for r in rows:
        due, now = _due(r["send_time"], r["tz"], r["last_sent"])
        if not due:
            continue
        day = now.date()
        if day not in cache:
            cache[day] = await content.daily_for(day)
        data = cache[day]
        if not data:
            await _alert_missing(bot, day)
            continue
        msgs = user_messages(r["lang"], r["sign"], day, data, r["tz"])
        ok = True
        for i, m in enumerate(msgs):
            ok = await _send(bot, r["user_id"], m, daily_keyboard(r["lang"]) if i == len(msgs) - 1 else None)
            if not ok:
                break
        if ok:
            await db.pool().execute("UPDATE daily_prefs SET last_sent=$2 WHERE user_id=$1", r["user_id"], day)
        elif ok is False:
            await db.pool().execute("UPDATE users SET blocked=TRUE WHERE id=$1", r["user_id"])
        await asyncio.sleep(0.05)


async def dispatch_chats(bot: Bot) -> None:
    rows = await db.pool().fetch("SELECT * FROM broadcast_chats WHERE active")
    for r in rows:
        due, now = _due(r["send_time"], r["tz"], r["last_sent"])
        if not due:
            continue
        day = now.date()
        data = await content.daily_for(day)
        if not data:
            await _alert_missing(bot, day)
            continue
        okall = True
        for msg in digest_messages(r["lang"], day, data, r["tz"]):
            ok = await _send(bot, r["chat_id"], msg)
            if ok is False:
                await db.pool().execute("UPDATE broadcast_chats SET active=FALSE WHERE chat_id=$1", r["chat_id"])
            okall = okall and bool(ok)
            await asyncio.sleep(0.3)
        if okall:
            await db.pool().execute("UPDATE broadcast_chats SET last_sent=$2 WHERE chat_id=$1", r["chat_id"], day)


async def tick(bot: Bot) -> None:
    if _lock.locked():
        return
    async with _lock:
        try:
            await dispatch_users(bot)
            await dispatch_chats(bot)
        except Exception:
            log.exception("dispatch failed")


async def pull_content() -> None:
    url = (await db.kv_get("daily_url", settings.daily_url) or settings.daily_url)
    try:
        await content.fetch_daily(url)
    except Exception as e:
        log.warning("daily fetch failed: %s", e)
    wurl = (await db.kv_get("weekly_url", settings.weekly_url) or settings.weekly_url)
    try:
        await content.fetch_weekly(wurl)
    except Exception as e:
        log.warning("weekly fetch failed: %s", e)


async def keepalive() -> None:
    """Render free instances sleep after 15 idle minutes; an inbound hit every 13 keeps us up."""
    if not settings.public_url:
        return
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            await c.get(f"{settings.public_url}/health")
    except Exception as e:
        log.info("keepalive failed: %s", e)


def start(bot: Bot) -> AsyncIOScheduler:
    s = AsyncIOScheduler(timezone="UTC")
    s.add_job(tick, "interval", minutes=1, args=[bot], id="tick", max_instances=1, coalesce=True)
    s.add_job(pull_content, "interval", minutes=30, id="pull", next_run_time=datetime.now(ZoneInfo("UTC")))
    s.add_job(keepalive, "interval", minutes=settings.keepalive_minutes, id="keepalive")
    s.start()
    return s
