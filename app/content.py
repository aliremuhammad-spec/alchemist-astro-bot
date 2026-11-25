"""Pull daily horoscopes / weekly elections from raw GitHub files and store them per day.

Accepted daily shapes (lenient, so the generator can evolve):
  {"date": "2026-12-01", "signs": {"aries": {"ar": "...", "en": "..."}, ...}}
  {"date": "2026-12-01", "signs": {"aries": "...", ...}}                 # one language
  {"days": [ <the object above>, ... ]}  or a top-level list of them
  {"2026-12-01": {"aries": ..., ...}, "2026-12-02": {...}}
Sign keys: english names (aries..pisces), case-insensitive; Arabic names also accepted.
"""
from __future__ import annotations

import json
import logging
from datetime import date

import httpx

from . import db
from .astro.names import SIGN_KEYS, SIGNS

log = logging.getLogger(__name__)
_AR_TO_KEY = {n: SIGN_KEYS[i] for i, n in enumerate(SIGNS["ar"])}


def _norm_sign(k: str) -> str | None:
    k2 = k.strip().lower()
    if k2 in SIGN_KEYS:
        return k2
    return _AR_TO_KEY.get(k.strip())


def _norm_signs(raw: dict) -> dict:
    out = {}
    for k, v in raw.items():
        key = _norm_sign(k)
        if not key:
            continue
        if isinstance(v, str):
            out[key] = {"ar": v, "en": v}
        elif isinstance(v, dict):
            text_ar = v.get("ar") or v.get("text") or v.get("en") or ""
            text_en = v.get("en") or v.get("text") or v.get("ar") or ""
            out[key] = {"ar": text_ar, "en": text_en, **{x: v[x] for x in ("title", "lucky") if x in v}}
    return out


def parse_daily(payload) -> dict[date, dict]:
    days: dict[date, dict] = {}

    def one(obj):
        if isinstance(obj, dict) and "date" in obj and "signs" in obj:
            signs = _norm_signs(obj["signs"])
            if len(signs) == 12:
                days[date.fromisoformat(str(obj["date"])[:10])] = {"signs": signs}

    if isinstance(payload, list):
        for o in payload:
            one(o)
    elif isinstance(payload, dict):
        if "days" in payload and isinstance(payload["days"], list):
            for o in payload["days"]:
                one(o)
        elif "date" in payload:
            one(payload)
        else:
            for k, v in payload.items():
                try:
                    d = date.fromisoformat(k[:10])
                except ValueError:
                    continue
                if isinstance(v, dict):
                    one({"date": d.isoformat(), "signs": v.get("signs", v)})
    return days


async def fetch_daily(url: str) -> int:
    if not url:
        return 0
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as c:
        r = await c.get(url, headers={"Cache-Control": "no-cache"})
        r.raise_for_status()
        payload = json.loads(r.text)
    days = parse_daily(payload)
    for d, data in days.items():
        await db.pool().execute(
            """INSERT INTO content_daily(day,data) VALUES($1,$2::jsonb)
               ON CONFLICT(day) DO UPDATE SET data=EXCLUDED.data, fetched_at=now()""",
            d, json.dumps(data, ensure_ascii=False))
    log.info("daily content: %d day(s) from %s", len(days), url)
    return len(days)


async def fetch_weekly(url: str) -> int:
    if not url:
        return 0
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as c:
        r = await c.get(url)
        r.raise_for_status()
        payload = r.json()
    ws = payload.get("week_start") if isinstance(payload, dict) else None
    if not ws or not isinstance(payload.get("items"), list):
        raise ValueError("weekly file needs week_start + items[]")
    await db.pool().execute(
        """INSERT INTO content_weekly(week_start,data) VALUES($1,$2::jsonb)
           ON CONFLICT(week_start) DO UPDATE SET data=EXCLUDED.data, fetched_at=now()""",
        date.fromisoformat(ws[:10]), json.dumps(payload, ensure_ascii=False))
    return len(payload["items"])


async def daily_for(d: date) -> dict | None:
    row = await db.pool().fetchval("SELECT data FROM content_daily WHERE day=$1", d)
    return json.loads(row) if isinstance(row, str) else row
