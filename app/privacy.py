"""“Delete my data”: erase everything we hold about a user.

What stays, and why (also stated in the privacy policy):
- payments: Telegram's charge id, amount and date, needed to answer refund requests and Telegram
  disputes; the row keeps only the numeric id, no name or chart.
- erased: a salted one-way hash of the id, so a deleted account cannot claim the founder gift or an
  invite gift a second time. It cannot be turned back into the id without the server's salt."""
from __future__ import annotations

import hashlib
import hmac
import secrets

from . import db


_salt: bytes | None = None


async def _key() -> bytes:
    global _salt
    if _salt is None:
        s = await db.kv_get("erase_salt", "")
        if not s:
            s = secrets.token_hex(32)
            await db.pool().execute("INSERT INTO kv(key,value) VALUES('erase_salt',$1) ON CONFLICT DO NOTHING", s)
            s = await db.kv_get("erase_salt", s)
        _salt = bytes.fromhex(s)
    return _salt


async def id_hash(uid: int) -> str:
    return hmac.new(await _key(), str(uid).encode(), hashlib.sha256).hexdigest()


async def was_erased(uid: int) -> bool:
    return bool(await db.pool().fetchval("SELECT 1 FROM erased WHERE id_hash=$1", await id_hash(uid)))


async def summary(uid: int) -> dict:
    p = db.pool()
    return {"profiles": await p.fetchval("SELECT count(*) FROM profiles WHERE user_id=$1", uid),
            "premium": bool(await p.fetchval(
                "SELECT 1 FROM subscriptions WHERE user_id=$1 AND ends_at > now() LIMIT 1", uid))}


async def erase(uid: int) -> dict:
    h = await id_hash(uid)
    out = await summary(uid)
    async with db.pool().acquire() as c, c.transaction():
        founder_no = await c.fetchval("SELECT number FROM founders WHERE user_id=$1", uid)
        await c.execute("""INSERT INTO erased(id_hash, founder_no) VALUES($1,$2)
                           ON CONFLICT (id_hash) DO UPDATE SET erased_at=now(),
                           founder_no=COALESCE(erased.founder_no, EXCLUDED.founder_no)""", h, founder_no)
        # tables without a foreign key to users
        for t in ("feedback", "events", "ad_events", "ad_tickets", "report_log", "notices"):
            await c.execute(f"DELETE FROM {t} WHERE user_id=$1", uid)
        await c.execute("UPDATE broadcast_chats SET added_by=NULL WHERE added_by=$1", uid)
        # profiles, daily_prefs, subscriptions, referrals, founders go with the user (ON DELETE CASCADE)
        await c.execute("DELETE FROM users WHERE id=$1", uid)
    await db.event(None, "data_erased")
    return out
