"""Parse the Markdown forecast files (daily horoscopes, weekly elections) and localise their times.

Source files (written by the astrologer, updated periodically):
  daily-forecast.md   — one Dubai day: "**التاريخ:** ... YYYY-MM-DD", "## أجواء اليوم العامة", then "## <sign>" × 12
                         with "**عامة:** / **عاطفية:** / **مالية:** / **مهنية:** / **نصيحة اليوم:**" paragraphs.
                         Clock times appear as "18:29 بتوقيت دبي".
  weekly-elections.md — "## ..." sections, "### <weekday> D/M/YYYY" days, times as `2026-11-28T11:21Z` (UTC) followed
                         by a Dubai copy "(دبي ...)", plus a ```json``` block with machine-readable events.

All times are converted to the reader's time zone at send/render time, so one stored copy serves everyone.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .astro.names import SIGN_KEYS, SIGNS

SOURCE_TZ = ZoneInfo("Asia/Dubai")
_AR_SIGN = {n: SIGN_KEYS[i] for i, n in enumerate(SIGNS["ar"])}
WEEKDAYS_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
WEEKDAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ───────────────────────── helpers ─────────────────────────


def gh_raw(url: str) -> str:
    """github.com/<o>/<r>/blob/<branch>/<path>  ->  raw.githubusercontent.com/<o>/<r>/<branch>/<path>."""
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.+)", url.strip())
    if m:
        return f"https://raw.githubusercontent.com/{m[1]}/{m[2]}/{m[3]}/{m[4]}"
    return url.strip()


def gh_api(url: str) -> str | None:
    """Contents-API URL for a GitHub file (not CDN-cached, so edits show up immediately)."""
    m = re.match(r"https?://(?:github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.+)"
                 r"|raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+))", url.strip())
    if not m:
        return None
    o, r, b, p = (m[1], m[2], m[3], m[4]) if m[1] else (m[5], m[6], m[7], m[8])
    return f"https://api.github.com/repos/{o}/{r}/contents/{p}?ref={b}"


def _md_inline(s: str) -> str:
    """Escape, then **bold** -> <b>, `code` -> plain."""
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = s.replace("`", "")
    return s.replace("\x02", "<b class='t'>").replace("\x03", "</b>")


def _sections(md: str, level: str) -> list[tuple[str, str]]:
    """Split on headings of exactly this level ('## ' or '### '); returns [(title, body)]; preamble title=''."""
    out, title, buf = [], "", []
    for line in md.splitlines():
        if line.startswith(level) and not line.startswith(level + "#"):
            out.append((title, "\n".join(buf).strip()))
            title, buf = line[len(level):].strip(), []
        else:
            buf.append(line)
    out.append((title, "\n".join(buf).strip()))
    return out


def fmt_local(dt_utc: datetime, tz: str, ref_day: date | None, lang: str = "ar") -> str:
    """'15:21', or '15:21 (السبت 28/11)' when the local date differs from the reference day."""
    loc = dt_utc.astimezone(ZoneInfo(tz))
    hm = loc.strftime("%H:%M")
    if ref_day is not None and loc.date() == ref_day:
        return hm
    wd = (WEEKDAYS_AR if lang == "ar" else WEEKDAYS_EN)[loc.weekday()]
    return f"{hm} ({wd} {loc.day}/{loc.month})"


def _strip_paren_group(s: str, start: int) -> int:
    """Given s[start] == '(', return index after the matching ')'."""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(s)


def _drop_dubai_parens(s: str) -> str:
    """Remove every parenthesised group that carries a Dubai copy of a time, e.g. '(دبي 28/11 15:21 ثم الأسد)'."""
    while True:
        k = s.find("دبي")
        while k >= 0:
            j = s.rfind("(", 0, k)
            if j >= 0 and s.find(")", j, k) < 0:
                break
            k = s.find("دبي", k + 1)
        if k < 0:
            return s
        end = _strip_paren_group(s, j)
        s = s[:j].rstrip(" ") + s[end:]


# ───────────────────────── daily ─────────────────────────

DAILY_LABELS = {"عامة": "general", "عاطفية": "love", "مالية": "money", "مهنية": "career", "نصيحة اليوم": "advice"}


def is_markdown(text: str) -> bool:
    t = text.lstrip("﻿ \n")
    return not t.startswith(("{", "["))


def parse_daily_md(md: str) -> dict[date, dict]:
    m = re.search(r"\*\*التاريخ:\*\*[^\n]*?(\d{4}-\d{2}-\d{2})", md)
    if not m:
        raise ValueError("daily file: missing '**التاريخ:** YYYY-MM-DD'")
    day = date.fromisoformat(m[1])
    secs = _sections(md, "## ")
    intro = [ln[1:].strip() for ln in secs[0][1].splitlines() if ln.startswith(">")]
    data = {"format": "md", "source_tz": "Asia/Dubai", "date": day.isoformat(), "intro": " ".join(intro),
            "overview": [], "signs": {}}
    for title, body in secs[1:]:
        key = _AR_SIGN.get(title.strip())
        if key:
            parts = []
            for para in re.split(r"\n\s*\n", body):
                para = " ".join(x.strip() for x in para.splitlines() if x.strip())
                pm = re.match(r"\*\*(.+?):\*\*\s*(.*)", para)
                if pm:
                    label, text = pm[1].strip(), pm[2].strip()
                    if text.startswith(label + ":"):  # "**نصيحة اليوم:** نصيحة اليوم: ..."
                        text = text[len(label) + 1:].strip()
                    parts.append({"k": DAILY_LABELS.get(label, "other"), "label": label, "text": text})
                elif para:
                    parts.append({"k": "other", "label": "", "text": para})
            data["signs"][key] = {"parts": parts}
        elif "أجواء" in title:
            data["overview"] = [ln[1:].strip() for ln in body.splitlines() if ln.startswith("- ")]
            notes = [ln[1:].strip() for ln in body.splitlines() if ln.startswith(">")]
            if notes:
                data["overview_note"] = " ".join(notes)
    if len(data["signs"]) != 12:
        raise ValueError(f"daily file: found {len(data['signs'])} of 12 signs")
    return {day: data}


_DUBAI_CLOCK = re.compile(r"(\d{1,2}):(\d{2})\s*بتوقيت\s+دبي")


def localise_daily(text: str, day: date, tz: str, lang: str = "ar") -> str:
    def rep(m):
        src = datetime(day.year, day.month, day.day, int(m[1]), int(m[2]), tzinfo=SOURCE_TZ)
        return f"{fmt_local(src.astimezone(timezone.utc), tz, day, lang)} بتوقيتك"
    text = _DUBAI_CLOCK.sub(rep, text)
    return re.sub(r"بتوقيت\s+دبي(\s*\(\+04\))?", "بتوقيتك", text)


def daily_sign_html(data: dict, key: str, lang: str, tz: str) -> str:
    """Telegram-HTML body for one sign (Markdown format) or the legacy plain text."""
    entry = data["signs"].get(key) or {}
    if data.get("format") != "md":
        return entry.get(lang) or entry.get("ar") or ""
    day = date.fromisoformat(data["date"])
    icons = {"general": "🌗", "love": "💞", "money": "💰", "career": "💼", "advice": "🗝"}
    out = []
    for p in entry.get("parts", []):
        txt = _md_inline(localise_daily(p["text"], day, tz, lang))
        if p["label"]:
            out.append(f"{icons.get(p['k'], '•')} <b>{html.escape(p['label'])}</b>\n{txt}")
        else:
            out.append(txt)
    return "\n\n".join(out)


def daily_sign_short(data: dict, key: str, lang: str, tz: str, sentences: int = 2) -> str:
    """Compact text for channel digests: first sentences of the general paragraph."""
    entry = data["signs"].get(key) or {}
    if data.get("format") != "md":
        return entry.get(lang) or entry.get("ar") or ""
    day = date.fromisoformat(data["date"])
    gen = next((p["text"] for p in entry.get("parts", []) if p["k"] == "general"), "")
    gen = localise_daily(gen, day, tz, lang)
    sent = re.split(r"(?<=[.!؟?])\s+", gen)
    return _md_inline(" ".join(sent[:sentences]))


def daily_overview_html(data: dict, lang: str, tz: str) -> str:
    if data.get("format") != "md" or not data.get("overview"):
        return ""
    day = date.fromisoformat(data["date"])
    return "\n".join("• " + _md_inline(localise_daily(x, day, tz, lang)) for x in data["overview"])


# ───────────────────────── weekly ─────────────────────────

WEEKLY_SKIP = ("كيف تُقرأ", "مصادر", "ملاحظات الدشاس", "بيانات للبوت")
_ISO = re.compile(r"`(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z)`(?:\s*UTC\b)?")
_DUBAI_COPY = re.compile(r"[،,]\s*دبي\s+\d{1,2}:\d{2}(?:\s*\(\d{1,2}/\d{1,2}\))?")
B0, B1 = "\x02", "\x03"  # markers for localised times, turned into <b> after escaping
_DAY_HEAD = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_DUBAI_HM = re.compile(r"(?<![\d:])(\d{1,2}):(\d{2})\s+دبي")


def parse_weekly_md(md: str) -> dict:
    m = re.search(r"```json\s*(\{.*?\})\s*```", md, re.S)
    events = json.loads(m[1]) if m else {}
    rng = re.search(r"\*\*الأسبوع:\*\*[^\n]*?(\d{4}-\d{2}-\d{2})[^\n]*?(\d{4}-\d{2}-\d{2})", md)
    if not rng and not events.get("week_start_utc"):
        raise ValueError("weekly file: missing '**الأسبوع:** من YYYY-MM-DD إلى YYYY-MM-DD'")
    week_start = date.fromisoformat(rng[1]) if rng else date.fromisoformat(events["week_start_utc"][:10])
    week_end = date.fromisoformat(rng[2]) if rng else None
    md_wo_json = md[:m.start()] if m else md
    secs = _sections(md_wo_json, "## ")
    intro = " ".join(ln[1:].strip() for ln in secs[0][1].splitlines() if ln.startswith(">"))
    sections = []
    for title, body in secs[1:]:
        if any(title.startswith(s) for s in WEEKLY_SKIP):
            continue
        if "تفصيل الأيام" in title:
            days = []
            for dt, db_ in _sections(body, "### ")[1:]:
                dm = _DAY_HEAD.search(dt)
                d = date(int(dm[3]), int(dm[2]), int(dm[1])) if dm else None
                days.append({"title": dt, "day": d.isoformat() if d else None, "body": db_})
            sections.append({"title": title, "days": days})
        else:
            sections.append({"title": title, "body": body})
    return {"format": "md", "source_tz": "Asia/Dubai", "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat() if week_end else None, "intro": intro, "sections": sections,
            "events": events.get("events", []), "week_start_utc": events.get("week_start_utc"),
            "week_end_utc": events.get("week_end_utc")}


def localise_weekly(text: str, tz: str, ref_day: date | None, lang: str = "ar") -> str:
    def iso(m):
        dt = datetime.strptime(m[1].replace("Z", "+0000"),
                               "%Y-%m-%dT%H:%M%z" if len(m[1]) == 17 else "%Y-%m-%dT%H:%M:%S%z")
        return f"{B0}{fmt_local(dt, tz, ref_day, lang)}{B1}"
    text = _DUBAI_COPY.sub("", _drop_dubai_parens(text))

    def dubai_hm(m):
        if ref_day is None:
            return m[0]
        src = datetime(ref_day.year, ref_day.month, ref_day.day, int(m[1]), int(m[2]), tzinfo=SOURCE_TZ)
        return f"{B0}{fmt_local(src.astimezone(timezone.utc), tz, ref_day, lang)}{B1}"
    text = _DUBAI_HM.sub(dubai_hm, text)
    text = _ISO.sub(iso, text)
    text = re.sub(r"\s+UTC\b", "", text)
    text = re.sub(r"\.\.", ".", text)
    return text


def _md_block_html(md: str) -> str:
    """Minimal Markdown (paragraphs, '- ' lists, **bold**) -> HTML for the Mini App."""
    out, items = [], []

    def flush():
        if items:
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items.clear()
    for ln in md.splitlines():
        s = ln.strip()
        if not s:
            flush()
            continue
        if s.startswith("- "):
            items.append(_md_inline(s[2:]))
        elif s.startswith(">"):
            flush()
            out.append(f"<p class='note'>{_md_inline(s[1:].strip())}</p>")
        else:
            flush()
            out.append(f"<p>{_md_inline(s)}</p>")
    flush()
    return "".join(out)


def weekly_view(data: dict, tz: str, lang: str = "ar") -> dict:
    """Localised, render-ready weekly elections for the Mini App."""
    secs = []
    for s in data["sections"]:
        if "days" in s:
            days = []
            for d in s["days"]:
                ref = date.fromisoformat(d["day"]) if d["day"] else None
                days.append({"title": d["title"], "html": _md_block_html(localise_weekly(d["body"], tz, ref, lang))})
            secs.append({"title": s["title"], "days": days})
        else:
            secs.append({"title": s["title"], "html": _md_block_html(localise_weekly(s["body"], tz, None, lang))})
    return {"week_start": data["week_start"], "week_end": data.get("week_end"), "tz": tz,
            "intro": _md_inline(data.get("intro", "")), "sections": secs}


def weekly_is_current(data: dict, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    end = data.get("week_end_utc")
    if end:
        return now < datetime.fromisoformat(end.replace("Z", "+00:00")) + timedelta(days=1)
    we = data.get("week_end") or data["week_start"]
    return now.date() <= date.fromisoformat(we) + timedelta(days=1)
