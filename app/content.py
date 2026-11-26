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

from . import db, forecasts
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


async def fetch_text(url: str) -> str:
    """GitHub files: try the contents API first (no CDN cache, edits show up at once), then raw."""
    api = forecasts.gh_api(url)
    async with httpx.AsyncClient(timeout=20, follow_redirects=True,
                                 headers={"User-Agent": "alchemist-astro-bot", "Cache-Control": "no-cache"}) as c:
        if api:
            try:
                r = await c.get(api, headers={"Accept": "application/vnd.github.raw"})
                if r.status_code == 200:
                    return r.text
                log.info("github api %s -> %s, falling back to raw", api, r.status_code)
            except httpx.HTTPError as e:
                log.info("github api failed: %s", e)
        r = await c.get(forecasts.gh_raw(url))
        r.raise_for_status()
        return r.text


_last_hash: dict[str, str] = {}


def _unchanged(url: str, text: str) -> bool:
    import hashlib
    h = hashlib.sha256(text.encode()).hexdigest()
    if _last_hash.get(url) == h:
        return True
    _last_hash[url] = h
    return False


async def fetch_daily(url: str, only_if_changed: bool = False) -> int:
    if not url:
        return 0
    text = await fetch_text(url)
    if only_if_changed and _unchanged(url, text):
        return 0
    days = forecasts.parse_daily_md(text) if forecasts.is_markdown(text) else parse_daily(json.loads(text))
    if not days:
        raise ValueError("daily file has no complete day (12 signs)")
    for d, data in days.items():
        await db.pool().execute(
            """INSERT INTO content_daily(day,data) VALUES($1,$2::jsonb)
               ON CONFLICT(day) DO UPDATE SET data=EXCLUDED.data, fetched_at=now()""",
            d, json.dumps(data, ensure_ascii=False))
    from . import scheduler
    scheduler.forget_content()
    log.info("daily content: %d day(s) from %s", len(days), url)
    return len(days)


async def fetch_weekly(url: str, only_if_changed: bool = False) -> int:
    if not url:
        return 0
    text = await fetch_text(url)
    if only_if_changed and _unchanged(url, text):
        return 0
    if forecasts.is_markdown(text):
        payload = forecasts.parse_weekly_md(text)
        n = sum(len(s.get("days", [])) for s in payload["sections"]) or len(payload["sections"])
    else:
        payload = json.loads(text)
        ws = payload.get("week_start") if isinstance(payload, dict) else None
        if not ws or not isinstance(payload.get("items"), list):
            raise ValueError("weekly file needs week_start + items[]")
        n = len(payload["items"])
    await db.pool().execute(
        """INSERT INTO content_weekly(week_start,data) VALUES($1,$2::jsonb)
           ON CONFLICT(week_start) DO UPDATE SET data=EXCLUDED.data, fetched_at=now()""",
        date.fromisoformat(payload["week_start"][:10]), json.dumps(payload, ensure_ascii=False))
    return n


async def weekly_current() -> dict | None:
    rows = await db.pool().fetch("SELECT data FROM content_weekly ORDER BY week_start DESC LIMIT 2")
    for r in rows:
        d = json.loads(r["data"]) if isinstance(r["data"], str) else r["data"]
        if d.get("format") == "md" and forecasts.weekly_is_current(d):
            return d
    return None


async def daily_for(d: date) -> dict | None:
    row = await db.pool().fetchval("SELECT data FROM content_daily WHERE day=$1", d)
    return json.loads(row) if isinstance(row, str) else row
