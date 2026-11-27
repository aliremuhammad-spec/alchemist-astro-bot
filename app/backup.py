"""Nightly backup of the user data, sent to the admins on Telegram as a .json.gz file.

The private interpretation databases and the GitHub forecast tables are left out:
they are big and can be uploaded / fetched again. Restore with scripts/restore_backup.py."""
from __future__ import annotations

import gzip
import json
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.types import BufferedInputFile

from . import db
from .config import settings

log = logging.getLogger("backup")

# parents before children, so a restore can insert in this order
TABLES = ["users", "profiles", "daily_prefs", "broadcast_chats", "subscriptions", "payments",
          "referrals", "founders", "report_log", "notices", "feedback", "kv", "ad_tickets", "ad_events", "erased"]
SKIP_KV = ("interp", "compat")      # never put kv keys of the private DBs in a file that leaves the server


async def dump() -> tuple[bytes, dict[str, int]]:
    data: dict[str, list] = {}
    counts: dict[str, int] = {}
    async with db.pool().acquire() as c:
        for t in TABLES:
            rows = await c.fetch(f"SELECT row_to_json(x)::text AS j FROM {t} x")
            items = [json.loads(r["j"]) for r in rows]
            if t == "kv":
                items = [i for i in items if not str(i.get("key", "")).startswith(SKIP_KV)]
            data[t] = items
            counts[t] = len(items)
    doc = {"app": "alchemist-astro-bot", "version": 1,
           "created_at": datetime.now(timezone.utc).isoformat(), "tables": data}
    return gzip.compress(json.dumps(doc, ensure_ascii=False, default=str).encode(), 9), counts


async def send(bot: Bot, to: list[int] | None = None) -> dict[str, int]:
    raw, counts = await dump()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    caption = (f"🗄 نسخة احتياطية {stamp} UTC\n"
               f"مستخدمين {counts['users']} · خرائط {counts['profiles']} · اشتراكات {counts['subscriptions']} · "
               f"دفعات {counts['payments']}\nالحجم {len(raw) / 1024:.0f} KB · للاسترجاع: scripts/restore_backup.py")
    for uid in to or sorted(settings.admin_ids):
        try:
            await bot.send_document(uid, BufferedInputFile(raw, filename=f"alchemist-backup-{stamp}.json.gz"),
                                    caption=caption, disable_notification=True)
        except Exception as e:  # an admin who never opened the bot, etc.
            log.warning("backup to %s failed: %s", uid, e)
    return counts


async def nightly(bot: Bot) -> None:
    try:
        await send(bot)
    except Exception as e:
        log.exception("nightly backup failed")
        for uid in settings.admin_ids:
            try:
                await bot.send_message(uid, f"⚠️ فشلت النسخة الاحتياطية الليلية: {str(e)[:300]}")
            except Exception:
                pass
