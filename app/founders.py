"""Founding members (first N members from a start date get a free Premium month), membership tiers,
monthly report caps, and the 3-day expiry reminder with an extension offer."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from . import db, privacy
from .config import settings

log = logging.getLogger(__name__)

FOUNDERS_TOTAL = int(os.getenv("FOUNDERS_TOTAL", "150"))
FOUNDERS_START = datetime.fromisoformat(os.getenv("FOUNDERS_START", "2026-11-28T00:00:00+03:00"))
FOUNDERS_DAYS = 30
CAPS = {  # rolling 30 days; extra reports are bought one by one with Stars
    "natal": {"trial": int(os.getenv("CAP_NATAL_TRIAL", "3")), "full": int(os.getenv("CAP_NATAL_FULL", "10"))},
    "synastry": {"trial": int(os.getenv("CAP_SYN_TRIAL", "5")), "full": int(os.getenv("CAP_SYN_FULL", "30"))},
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS founders (
  user_id    BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  number     INT NOT NULL UNIQUE,
  claimed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS notices (
  user_id BIGINT NOT NULL, kind TEXT NOT NULL, ref TEXT NOT NULL, sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, kind, ref)
);
"""


def now() -> datetime:
    return datetime.now(timezone.utc)


async def tier(uid: int) -> str | None:
    """'admin' | 'full' (paid, granted or earned) | 'trial' (founder month only) | None."""
    if uid in settings.admin_ids:
        return "admin"
    rows = await db.pool().fetch("SELECT source FROM subscriptions WHERE user_id=$1 AND ends_at > now()", uid)
    if not rows:
        return None
    return "trial" if all(r["source"] == "founder" for r in rows) else "full"


async def quota(uid: int, kind: str) -> dict:
    t = await tier(uid)
    limit = CAPS[kind]["trial" if t == "trial" else "full"] if t in ("trial", "full") else 0
    used = await db.pool().fetchval(
        """SELECT count(*) FROM report_log WHERE user_id=$1 AND kind=$2 AND paid_with='premium'
           AND created_at > now() - interval '30 days'""", uid, kind)
    col = "report_credits" if kind == "natal" else "syn_report_credits"
    credits = await db.pool().fetchval(f"SELECT {col} FROM users WHERE id=$1", uid) or 0
    key, default = ("natal_report_stars", "50") if kind == "natal" else ("syn_report_stars", "50")
    price = await db.kv_get(key, default)
    return {"tier": t, "used": used, "limit": limit, "left": max(0, limit - used), "credits": credits,
            "price": int(price) if price.isdigit() else 50}


async def decide(uid: int, kind: str) -> str:
    """How the next report is paid for: admin | premium | credit; raises PermissionError(code) otherwise."""
    q = await quota(uid, kind)
    if q["tier"] == "admin":
        return "admin"
    if q["tier"] in ("trial", "full") and q["left"] > 0:
        return "premium"
    if q["credits"] > 0 and (kind == "natal" or q["tier"]):
        return "credit"
    raise PermissionError("report_quota" if q["tier"] else "premium_required")


# ───────────── founding members ─────────────

async def status(uid: int | None = None) -> dict:
    p = db.pool()
    taken = await p.fetchval(
        "SELECT (SELECT count(*) FROM founders) + (SELECT count(*) FROM erased WHERE founder_no IS NOT NULL)")
    mine = await p.fetchrow("SELECT number, claimed_at FROM founders WHERE user_id=$1", uid) if uid else None
    started = now() >= FOUNDERS_START
    left = max(0, FOUNDERS_TOTAL - taken)
    out = {"start": FOUNDERS_START.isoformat(), "total": FOUNDERS_TOTAL, "taken": taken, "left": left,
           "started": started, "open": started and left > 0, "days": FOUNDERS_DAYS,
           "claimed": bool(mine), "number": mine["number"] if mine else None}
    if uid:
        out["has_chart"] = bool(await p.fetchval("SELECT 1 FROM profiles WHERE user_id=$1 LIMIT 1", uid))
        out["eligible"] = out["open"] and not mine and uid not in settings.admin_ids
    return out


async def claim(uid: int, bot: Bot | None = None) -> dict:
    if uid in settings.admin_ids:
        raise PermissionError("admin")
    if now() < FOUNDERS_START:
        raise PermissionError("not_started")
    p = db.pool()
    if not await p.fetchval("SELECT 1 FROM profiles WHERE user_id=$1 LIMIT 1", uid):
        raise PermissionError("need_chart")
    async with p.acquire() as c, c.transaction():
        await c.execute("SELECT pg_advisory_xact_lock(150150)")
        if await c.fetchval("SELECT number FROM founders WHERE user_id=$1", uid) or await privacy.was_erased(uid):
            raise PermissionError("already")
        taken = await c.fetchval(
            "SELECT (SELECT count(*) FROM founders) + (SELECT count(*) FROM erased WHERE founder_no IS NOT NULL)")
        if taken >= FOUNDERS_TOTAL:
            raise PermissionError("full")
        number = taken + 1
        await c.execute("INSERT INTO founders(user_id, number) VALUES($1,$2)", uid, number)
        end = await c.fetchval("SELECT max(ends_at) FROM subscriptions WHERE user_id=$1 AND ends_at > now()", uid)
        ends = (end or now()) + timedelta(days=FOUNDERS_DAYS)
        await c.execute("INSERT INTO subscriptions(user_id,source,ends_at) VALUES($1,'founder',$2)", uid, ends)
    await db.event(uid, "founder_claimed")
    if bot:
        lang = await p.fetchval("SELECT lang FROM users WHERE id=$1", uid)
        txt = (f"🌟 <b>مبروك! صرت العضو المؤسس رقم {number}</b>\n"
               f"اشتراكك المميز المجاني فعّال لمدة {FOUNDERS_DAYS} يوم: الخرائط التقسيمية، التوافق المفصّل، "
               f"الاختيارات الأسبوعية، و{CAPS['natal']['trial']} تقارير فلكية + {CAPS['synastry']['trial']} تقارير توافق."
               if lang == "ar" else
               f"🌟 <b>Welcome, founding member #{number}!</b>\nYour free Premium is active for {FOUNDERS_DAYS} days: "
               f"divisional charts, detailed compatibility, weekly picks, {CAPS['natal']['trial']} astrological "
               f"and {CAPS['synastry']['trial']} compatibility reports.")
        try:
            await bot.send_message(uid, txt, reply_markup=_kb(lang, [("open", "#premium")]))
        except Exception as e:
            log.info("founder notify failed: %s", e)
    return {"number": number, "ends_at": ends.isoformat()}


def _kb(lang: str, items: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    labels = {"open": ("🔭 افتح التطبيق", "🔭 Open the app"), "extend": ("⭐ مدّد اشتراكك", "⭐ Extend Premium"),
              "invite": ("🎁 ادعُ صديق واربح 3 أيام", "🎁 Invite a friend, earn 3 days")}
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=labels[k][0 if lang == "ar" else 1], web_app=WebAppInfo(url=f"{settings.public_url}/{path}"))]
        for k, path in items])


# ───────────── 3-day expiry reminder ─────────────

async def remind_expiring(bot: Bot) -> int:
    """Members whose Premium ends within 3 days (and won't renew by itself) get one reminder per end date."""
    p = db.pool()
    rows = await p.fetch(
        """WITH last AS (
             SELECT DISTINCT ON (user_id) user_id, ends_at, source FROM subscriptions
             WHERE ends_at > now() ORDER BY user_id, ends_at DESC)
           SELECT l.user_id, l.ends_at, l.source, u.lang, u.first_name FROM last l JOIN users u ON u.id=l.user_id
           WHERE l.ends_at <= now() + interval '3 days' AND NOT u.blocked
             AND NOT EXISTS (SELECT 1 FROM payments pm WHERE pm.user_id=l.user_id AND pm.recurring AND NOT pm.refunded
                             AND pm.expires_at >= l.ends_at - interval '1 day')""")
    price = await db.kv_get("premium_stars", str(settings.premium_stars))
    n = 0
    for r in rows:
        ref = r["ends_at"].date().isoformat()
        ins = await p.execute("INSERT INTO notices(user_id,kind,ref) VALUES($1,'expiry',$2) ON CONFLICT DO NOTHING",
                              r["user_id"], ref)
        if ins.endswith(" 0"):
            continue
        days = max(1, round((r["ends_at"] - now()).total_seconds() / 86400))
        founder = r["source"] == "founder"
        if r["lang"] == "en":
            txt = (f"⏳ Your {'founding-member ' if founder else ''}Premium ends in <b>{days} day{'s' if days > 1 else ''}</b> "
                   f"({ref}).\nKeep your divisional charts, detailed compatibility, weekly picks and monthly reports: "
                   f"extend for <b>{price} ⭐ a month</b>, or invite friends: every active friend adds 3 free days.")
        else:
            txt = (f"⏳ اشتراكك المميز{' كعضو مؤسس' if founder else ''} بيخلص بعد <b>{'يوم واحد' if days == 1 else 'يومين' if days == 2 else f'{days} أيام'}</b> ({ref}).\n"
                   f"حتى ما توقف عندك الخرائط التقسيمية والتوافق المفصّل والاختيارات الأسبوعية والتقارير الشهرية، "
                   f"مدّد اشتراكك بـ<b>{price} ⭐ بالشهر</b>، أو ادعُ أصحابك: كل صديق نشط بيزيدلك 3 أيام مجاناً.")
        try:
            await bot.send_message(r["user_id"], txt,
                                   reply_markup=_kb(r["lang"], [("extend", "#premium"), ("invite", "#invite")]))
            n += 1
        except Exception as e:
            log.info("expiry reminder failed for %s: %s", r["user_id"], e)
    return n
