"""Personal invites: the newcomer gets one free astrological report; the inviter gets 3 premium days
once the newcomer is *active* (saved a birth chart and came back on another day within 30 days)."""
from __future__ import annotations

import logging
import re
from datetime import timedelta

from aiogram import Bot

from . import db
from .config import settings

log = logging.getLogger(__name__)
REWARD_DAYS = 3
MONTHLY_CAP = 10          # rewards per inviter per 30 days (anti-abuse)
_PARAM = re.compile(r"^r(\d{4,15})$")


def link(uid: int) -> str:
    return f"https://t.me/{settings.bot_username}?start=r{uid}"


def inviter_from(param: str | None) -> int | None:
    m = _PARAM.match(param or "")
    return int(m[1]) if m else None


async def attach(invitee: int, param: str | None) -> bool:
    """Link a brand-new user to their inviter and give the welcome gift. Idempotent."""
    inviter = inviter_from(param)
    if not inviter or inviter == invitee:
        return False
    p = db.pool()
    fresh = await p.fetchval(
        """SELECT created_at > now() - interval '15 minutes'
                  AND NOT EXISTS (SELECT 1 FROM profiles WHERE user_id=$1)
                  AND NOT EXISTS (SELECT 1 FROM referrals WHERE invitee_id=$1)
           FROM users WHERE id=$1""", invitee)
    if not fresh or not await p.fetchval("SELECT 1 FROM users WHERE id=$1", inviter):
        return False
    async with p.acquire() as c, c.transaction():
        r = await c.execute("INSERT INTO referrals(invitee_id,inviter_id) VALUES($1,$2) ON CONFLICT DO NOTHING",
                            invitee, inviter)
        if r.endswith(" 0"):
            return False
        await c.execute("UPDATE users SET report_credits=report_credits+1 WHERE id=$1", invitee)
    await db.event(invitee, "ref_joined")
    return True


async def grant_days(uid: int, days: int, source: str) -> None:
    """Extend premium from the later of now / current end."""
    p = db.pool()
    end = await p.fetchval("SELECT max(ends_at) FROM subscriptions WHERE user_id=$1 AND ends_at > now()", uid)
    start = end or await p.fetchval("SELECT now()")
    await p.execute("INSERT INTO subscriptions(user_id,source,ends_at) VALUES($1,$2,$3)",
                    uid, source, start + timedelta(days=days))


async def check_activations(bot: Bot | None = None) -> int:
    """Reward inviters whose invitees became active. Runs from the scheduler."""
    p = db.pool()
    rows = await p.fetch(
        """SELECT r.invitee_id, r.inviter_id, u.first_name FROM referrals r JOIN users u ON u.id=r.invitee_id
           WHERE r.activated_at IS NULL AND r.created_at > now() - interval '30 days' AND NOT u.blocked
             AND EXISTS (SELECT 1 FROM profiles pr WHERE pr.user_id=r.invitee_id)
             AND u.last_seen::date > r.created_at::date""")
    n = 0
    for r in rows:
        recent = await p.fetchval(
            "SELECT count(*) FROM referrals WHERE inviter_id=$1 AND reward_days>0 AND activated_at > now()-interval '30 days'",
            r["inviter_id"])
        days = REWARD_DAYS if recent < MONTHLY_CAP else 0
        await p.execute("UPDATE referrals SET activated_at=now(), reward_days=$2 WHERE invitee_id=$1",
                        r["invitee_id"], days)
        if days:
            await grant_days(r["inviter_id"], days, "referral")
            n += 1
            if bot:
                lang = await p.fetchval("SELECT lang FROM users WHERE id=$1", r["inviter_id"])
                from html import escape
                name = escape(r["first_name"] or ("صديقك" if lang == "ar" else "your friend"))
                txt = (f"🎉 <b>{name}</b> صار مستخدم نشط بالخيميائي، وربحت <b>{days} أيام مميز</b>! "
                       f"كمّل دعوات وكل صديق نشط بيزيدلك 3 أيام."
                       if lang == "ar" else
                       f"🎉 <b>{name}</b> is now active on The Alchemist: you earned <b>{days} Premium days</b>! "
                       f"Every active friend adds 3 more.")
                try:
                    await bot.send_message(r["inviter_id"], txt)
                except Exception as e:
                    log.info("referral notify failed: %s", e)
    return n


async def stats(uid: int) -> dict:
    p = db.pool()
    row = await p.fetchrow(
        """SELECT count(*) invited, count(activated_at) active, coalesce(sum(reward_days),0) days
           FROM referrals WHERE inviter_id=$1""", uid)
    credits = await p.fetchval("SELECT report_credits FROM users WHERE id=$1", uid)
    return {"link": link(uid), "invited": row["invited"], "active": row["active"], "days": row["days"],
            "report_credits": credits or 0, "reward_days": REWARD_DAYS}
