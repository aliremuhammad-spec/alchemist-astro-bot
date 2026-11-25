"""Admin dashboard API (inside the Mini App). Every route checks the caller's Telegram id."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from html import escape

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from . import content, db
from .api import current_user
from .config import settings

router = APIRouter(prefix="/api/admin")

SEGMENTS = {
    "all": "SELECT id FROM users WHERE NOT blocked",
    "ar": "SELECT id FROM users WHERE NOT blocked AND lang='ar'",
    "en": "SELECT id FROM users WHERE NOT blocked AND lang='en'",
    "daily": "SELECT u.id FROM users u JOIN daily_prefs d ON d.user_id=u.id WHERE d.subscribed AND NOT u.blocked",
    "premium": """SELECT DISTINCT u.id FROM users u JOIN subscriptions s ON s.user_id=u.id
                  WHERE s.ends_at > now() AND NOT u.blocked""",
    "free": """SELECT id FROM users WHERE NOT blocked AND id NOT IN
               (SELECT user_id FROM subscriptions WHERE ends_at > now())""",
    "inactive7": "SELECT id FROM users WHERE NOT blocked AND last_seen < now() - interval '7 days'",
}


async def admin_user(user: dict = Depends(current_user)) -> dict:
    if user["id"] not in settings.admin_ids:
        raise HTTPException(403, "admins only")
    return user


@router.get("/overview")
async def overview(_: dict = Depends(admin_user)):
    p = db.pool()
    q = p.fetchval
    out = {
        "users": await q("SELECT count(*) FROM users"),
        "new_today": await q("SELECT count(*) FROM users WHERE created_at > now() - interval '1 day'"),
        "active7": await q("SELECT count(*) FROM users WHERE last_seen > now() - interval '7 days'"),
        "blocked": await q("SELECT count(*) FROM users WHERE blocked"),
        "daily_subs": await q("SELECT count(*) FROM daily_prefs WHERE subscribed"),
        "chats": await q("SELECT count(*) FROM broadcast_chats WHERE active"),
        "charts": await q("SELECT count(*) FROM events WHERE name='chart'"),
        "synastry": await q("SELECT count(*) FROM events WHERE name='synastry'"),
        "profiles": await q("SELECT count(*) FROM profiles"),
        "premium": await q("SELECT count(DISTINCT user_id) FROM subscriptions WHERE ends_at > now()"),
        "stars": await q("SELECT coalesce(sum(stars),0) FROM payments WHERE NOT refunded"),
        "feedback": await q("SELECT count(*) FROM feedback"),
    }
    out["ads"] = [dict(r) for r in await p.fetch(
        """SELECT provider, status, count(*) n FROM ad_events
           WHERE created_at > now() - interval '30 days' AND status <> 'requested'
           GROUP BY provider, status ORDER BY n DESC""")]
    out["ads_requested"] = await q(
        "SELECT count(*) FROM ad_events WHERE status='requested' AND created_at > now() - interval '30 days'")
    series = await p.fetch(
        """SELECT d::date AS day,
             (SELECT count(*) FROM users WHERE created_at::date = d::date) AS users,
             (SELECT count(*) FROM events WHERE name='chart' AND created_at::date = d::date) AS charts
           FROM generate_series(now()::date - 13, now()::date, interval '1 day') d ORDER BY day""")
    out["series"] = [{"day": r["day"].isoformat(), "users": r["users"], "charts": r["charts"]} for r in series]
    out["countries"] = [dict(r) for r in await p.fetch(
        """SELECT country, count(DISTINCT user_id) n FROM profiles WHERE is_main AND country IS NOT NULL
           GROUP BY country ORDER BY n DESC LIMIT 12""")]
    out["timezones"] = [dict(r) for r in await p.fetch(
        "SELECT tz, count(*) n FROM users WHERE tz IS NOT NULL GROUP BY tz ORDER BY n DESC LIMIT 8")]
    out["langs"] = [dict(r) for r in await p.fetch("SELECT lang, count(*) n FROM users GROUP BY lang ORDER BY n DESC")]
    out["sources"] = [dict(r) for r in await p.fetch(
        "SELECT coalesce(start_param,'—') src, count(*) n FROM users GROUP BY src ORDER BY n DESC LIMIT 8")]
    return out


@router.get("/users")
async def users(q: str = "", _: dict = Depends(admin_user)):
    q = q.strip().lstrip("@")
    base = """SELECT u.id, u.first_name, u.username, u.lang, u.blocked, u.created_at, u.last_seen,
                (SELECT max(ends_at) FROM subscriptions s WHERE s.user_id=u.id AND s.ends_at > now()) AS premium_until,
                (SELECT count(*) FROM profiles p WHERE p.user_id=u.id) AS profiles
              FROM users u"""
    if q.isdigit():
        rows = await db.pool().fetch(base + " WHERE u.id=$1", int(q))
    elif q:
        rows = await db.pool().fetch(base + " WHERE u.username ILIKE $1 OR u.first_name ILIKE $1 ORDER BY u.last_seen DESC LIMIT 50",
                                     f"%{q}%")
    else:
        rows = await db.pool().fetch(base + " ORDER BY u.last_seen DESC LIMIT 50")
    return [{**dict(r), "created_at": r["created_at"].isoformat(), "last_seen": r["last_seen"].isoformat(),
             "premium_until": r["premium_until"].isoformat() if r["premium_until"] else None} for r in rows]


class GrantIn(BaseModel):
    user_id: int
    days: int = Field(ge=1, le=3650)
    note: str = Field("", max_length=200)


@router.post("/grant")
async def grant(body: GrantIn, request: Request, admin: dict = Depends(admin_user)):
    if not await db.pool().fetchval("SELECT 1 FROM users WHERE id=$1", body.user_id):
        raise HTTPException(404, "user must open the bot first")
    until = datetime.now(timezone.utc) + timedelta(days=body.days)
    await db.pool().execute(
        "INSERT INTO subscriptions(user_id,source,ends_at,granted_by,note) VALUES($1,'manual',$2,$3,$4)",
        body.user_id, until, admin["id"], body.note or None)
    try:
        await request.app.state.bot.send_message(
            body.user_id, f"✨ تم تفعيل الاشتراك المميز لحسابك لمدة {body.days} يوم. افتح التطبيق وجرّب المزايا الجديدة.")
    except Exception:
        pass
    return {"ok": True, "until": until.isoformat()}


@router.post("/revoke")
async def revoke(body: dict, _: dict = Depends(admin_user)):
    uid = int(body.get("user_id", 0))
    await db.pool().execute("UPDATE subscriptions SET ends_at=now() WHERE user_id=$1 AND ends_at > now()", uid)
    return {"ok": True}


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    user_id: int | None = None
    segment: str | None = None


@router.post("/message")
async def message(body: MessageIn, request: Request, admin: dict = Depends(admin_user)):
    bot: Bot = request.app.state.bot
    text = body.text  # sent as HTML: admins may use <b>, <i>, <a>
    if body.user_id:
        try:
            await bot.send_message(body.user_id, text, disable_web_page_preview=True)
        except Exception as e:
            raise HTTPException(400, f"send failed: {e}")
        return {"queued": 1}
    sql = SEGMENTS.get(body.segment or "")
    if not sql:
        raise HTTPException(400, "segment")
    ids = [r["id"] for r in await db.pool().fetch(sql)]
    asyncio.create_task(_broadcast(bot, admin["id"], text, ids))
    return {"queued": len(ids)}


async def _broadcast(bot: Bot, admin_id: int, text: str, ids: list[int]) -> None:
    ok = fail = 0
    for uid in ids:
        for _ in range(2):
            try:
                await bot.send_message(uid, text, disable_web_page_preview=True)
                ok += 1
                break
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
            except TelegramForbiddenError:
                fail += 1
                await db.pool().execute("UPDATE users SET blocked=TRUE WHERE id=$1", uid)
                break
            except Exception:
                fail += 1
                break
        await asyncio.sleep(0.05)
    try:
        await bot.send_message(admin_id, f"✅ انتهى الإرسال من لوحة الإدارة: وصل {ok}، فشل {fail}")
    except Exception:
        pass


@router.get("/feedback")
async def feedback(_: dict = Depends(admin_user)):
    rows = await db.pool().fetch(
        """SELECT f.id, f.user_id, f.text, f.created_at, u.first_name, u.username FROM feedback f
           LEFT JOIN users u ON u.id=f.user_id ORDER BY f.created_at DESC LIMIT 60""")
    return [{**dict(r), "created_at": r["created_at"].isoformat()} for r in rows]


@router.get("/chats")
async def chats(_: dict = Depends(admin_user)):
    rows = await db.pool().fetch(
        """SELECT c.chat_id, c.title, c.kind, c.active, c.send_time, c.tz, c.lang, c.last_sent,
             u.first_name AS owner, u.username AS owner_username
           FROM broadcast_chats c LEFT JOIN users u ON u.id=c.added_by ORDER BY c.created_at DESC""")
    return [{**dict(r), "last_sent": r["last_sent"].isoformat() if r["last_sent"] else None} for r in rows]


@router.get("/content")
async def content_status(_: dict = Depends(admin_user)):
    days = await db.pool().fetch("SELECT day, fetched_at FROM content_daily ORDER BY day DESC LIMIT 7")
    weeks = await db.pool().fetch("SELECT week_start, fetched_at FROM content_weekly ORDER BY week_start DESC LIMIT 3")
    today = datetime.now(timezone.utc).date()
    return {
        "daily_url": await db.kv_get("daily_url", settings.daily_url),
        "weekly_url": await db.kv_get("weekly_url", settings.weekly_url),
        "premium_stars": int(await db.kv_get("premium_stars", str(settings.premium_stars))),
        "days": [{"day": r["day"].isoformat(), "fetched_at": r["fetched_at"].isoformat()} for r in days],
        "weeks": [{"week_start": r["week_start"].isoformat(), "fetched_at": r["fetched_at"].isoformat()} for r in weeks],
        "has_today": any(r["day"] == today for r in days),
    }


class SettingsIn(BaseModel):
    daily_url: str | None = None
    weekly_url: str | None = None
    premium_stars: int | None = Field(None, ge=1, le=10000)


@router.post("/settings")
async def save_settings(body: SettingsIn, _: dict = Depends(admin_user)):
    if body.daily_url is not None:
        await db.kv_set("daily_url", body.daily_url.strip())
    if body.weekly_url is not None:
        await db.kv_set("weekly_url", body.weekly_url.strip())
    if body.premium_stars is not None:
        await db.kv_set("premium_stars", str(body.premium_stars))
    return {"ok": True}


@router.post("/fetch")
async def fetch_now(_: dict = Depends(admin_user)):
    out = {}
    for kind, fn, key, default in (("daily", content.fetch_daily, "daily_url", settings.daily_url),
                                    ("weekly", content.fetch_weekly, "weekly_url", settings.weekly_url)):
        url = await db.kv_get(key, default)
        if not url:
            out[kind] = "no url"
            continue
        try:
            out[kind] = f"ok: {await fn(url)}"
        except Exception as e:
            out[kind] = f"error: {escape(str(e))[:200]}"
    return out
