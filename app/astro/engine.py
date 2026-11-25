"""Chart computation: western (tropical, Placidus) and vedic (sidereal Lahiri, whole sign)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from kerykeion import AstrologicalSubjectFactory, ChartDataFactory

from .names import DASHA_LORDS, DASHA_YEARS, MAJOR_ASPECTS, NAKSHATRAS

ENGINE_VERSION = 1

WESTERN_POINTS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
                  "uranus", "neptune", "pluto", "mean_north_lunar_node", "chiron"]
VEDIC_POINTS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
                "mean_north_lunar_node", "mean_south_lunar_node"]

_ACTIVE_WESTERN = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus",
                   "Neptune", "Pluto", "Mean_North_Lunar_Node", "Mean_South_Lunar_Node", "Chiron",
                   "Ascendant", "Medium_Coeli"]
_ACTIVE_WESTERN_NO_TIME = [p for p in _ACTIVE_WESTERN if p not in ("Ascendant", "Medium_Coeli")]
_ACTIVE_VEDIC = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                 "Mean_North_Lunar_Node", "Mean_South_Lunar_Node", "Ascendant", "Medium_Coeli"]

_HOUSE_NUM = {n: i + 1 for i, n in enumerate(
    ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth",
     "Ninth", "Tenth", "Eleventh", "Twelfth"])}

NAK_SPAN = 360 / 27
YEAR_DAYS = 365.2425


@dataclass
class BirthInput:
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    time_known: bool
    lat: float
    lng: float
    tz: str
    city: str = ""
    country: str = ""


def _house_num(h) -> int | None:
    if not h:
        return None
    return _HOUSE_NUM.get(str(h).split("_")[0])


def _subject(b: BirthInput, vedic: bool, hour: int, minute: int):
    kw = dict(lng=b.lng, lat=b.lat, tz_str=b.tz, online=False,
              city=b.city or "-", nation=b.country or "-")
    if vedic:
        kw.update(zodiac_type="Sidereal", sidereal_mode="LAHIRI",
                  houses_system_identifier="W", active_points=_ACTIVE_VEDIC)
    else:
        kw.update(active_points=_ACTIVE_WESTERN if b.time_known else _ACTIVE_WESTERN_NO_TIME)
    return AstrologicalSubjectFactory.from_birth_data(
        b.name or "Chart", b.year, b.month, b.day, hour, minute, **kw)


def _pt(p, with_house: bool) -> dict:
    return {
        "sign": int(p.abs_pos // 30),
        "deg": round(p.abs_pos % 30, 4),
        "abs": round(p.abs_pos, 4),
        "house": _house_num(p.house) if with_house else None,
        "retro": bool(getattr(p, "retrograde", False)),
        "speed": round(getattr(p, "speed", 0) or 0, 4),
    }


def nakshatra_of(lon: float) -> dict:
    idx = int(lon // NAK_SPAN) % 27
    within = lon % NAK_SPAN
    pada = int(within // (NAK_SPAN / 4)) + 1
    return {"index": idx, "name": NAKSHATRAS[idx][0], "name_ar": NAKSHATRAS[idx][1],
            "pada": pada, "lord": DASHA_LORDS[idx % 9]}


def vimshottari(moon_lon: float, birth_utc: datetime, at: datetime | None = None) -> dict:
    """Current mahadasha + antardasha, and the full mahadasha list from birth."""
    at = at or datetime.now(timezone.utc)
    idx = int(moon_lon // NAK_SPAN) % 27
    lord_i = idx % 9
    frac = (moon_lon % NAK_SPAN) / NAK_SPAN
    first = DASHA_LORDS[lord_i]
    start = birth_utc - timedelta(days=frac * DASHA_YEARS[first] * YEAR_DAYS)
    periods = []
    t = start
    for k in range(9 * 2):  # two full cycles = 240 years, plenty
        lord = DASHA_LORDS[(lord_i + k) % 9]
        end = t + timedelta(days=DASHA_YEARS[lord] * YEAR_DAYS)
        periods.append({"lord": lord, "start": t, "end": end})
        t = end
        if t > birth_utc + timedelta(days=120 * YEAR_DAYS):
            break
    cur = next((p for p in periods if p["start"] <= at < p["end"]), periods[-1])
    m_years = DASHA_YEARS[cur["lord"]]
    mi = DASHA_LORDS.index(cur["lord"])
    t = cur["start"]
    antar = None
    for k in range(9):
        lord = DASHA_LORDS[(mi + k) % 9]
        end = t + timedelta(days=m_years * DASHA_YEARS[lord] / 120 * YEAR_DAYS)
        if t <= at < end:
            antar = {"lord": lord, "start": t, "end": end}
            break
        t = end

    def ser(p):
        return {"lord": p["lord"], "start": p["start"].date().isoformat(), "end": p["end"].date().isoformat()}

    return {
        "maha": ser(cur),
        "antar": ser(antar) if antar else None,
        "timeline": [ser(p) for p in periods if p["end"] > birth_utc],
        "balance_years_at_birth": round(DASHA_YEARS[first] * (1 - frac), 2),
    }


def compute(b: BirthInput) -> dict:
    hour, minute = (b.hour, b.minute) if b.time_known else (12, 0)
    w = _subject(b, False, hour, minute)
    v = _subject(b, True, hour, minute)
    wdata = ChartDataFactory.create_natal_chart_data(w)

    western = {"points": {}, "asc": None, "mc": None, "houses": []}
    for key in WESTERN_POINTS:
        p = getattr(w, key, None)
        if p is not None:
            western["points"][key] = _pt(p, b.time_known)
    if b.time_known:
        western["asc"] = _pt(w.ascendant, False)
        western["mc"] = _pt(w.medium_coeli, False)
        western["houses"] = [round(getattr(w, f"{n.lower()}_house").abs_pos, 4) for n in _HOUSE_NUM]
    aspects = []
    for a in wdata.aspects:
        n1, n2 = a.p1_name.lower(), a.p2_name.lower()
        if not b.time_known and ("ascendant" in (n1, n2) or "medium_coeli" in (n1, n2)):
            continue
        if "south" in n1 or "south" in n2 or {n1, n2} == {"ascendant", "medium_coeli"}:
            continue
        aspects.append({"p1": n1, "p2": n2, "type": a.aspect, "orb": round(abs(a.orbit), 2),
                        "major": a.aspect in MAJOR_ASPECTS,
                        "applying": getattr(a, "aspect_movement", "") == "Applying"})
    aspects.sort(key=lambda x: (not x["major"], x["orb"]))
    western["aspects"] = aspects
    western["elements"] = {k: getattr(wdata.element_distribution, f"{k}_percentage")
                           for k in ("fire", "earth", "air", "water")}
    western["qualities"] = {k: getattr(wdata.quality_distribution, f"{k}_percentage")
                            for k in ("cardinal", "fixed", "mutable")}
    lp = w.lunar_phase
    western["moon_phase"] = {"name": lp.moon_phase_name, "emoji": lp.moon_emoji}

    vedic = {"points": {}, "lagna": None}
    for key in VEDIC_POINTS:
        p = getattr(v, key, None)
        if p is None:
            continue
        d = _pt(p, b.time_known)
        if key == "mean_south_lunar_node" and b.time_known:
            # whole-sign house from lagna
            d["house"] = (d["sign"] - int(v.first_house.abs_pos // 30)) % 12 + 1
        d["nakshatra"] = nakshatra_of(p.abs_pos)
        vedic["points"][key] = d
    if b.time_known:
        vedic["lagna"] = _pt(v.ascendant, False)
        vedic["lagna"]["nakshatra"] = nakshatra_of(v.ascendant.abs_pos)
    birth_utc = datetime.fromisoformat(w.iso_formatted_utc_datetime)
    moon_lon = vedic["points"]["moon"]["abs"]
    vedic["moon_nakshatra"] = vedic["points"]["moon"]["nakshatra"]
    vedic["dasha"] = vimshottari(moon_lon, birth_utc)
    vedic["ayanamsa"] = "Lahiri"

    warnings = []
    if not b.time_known:
        warnings.extend(_day_range_warnings(b))

    return {
        "engine": ENGINE_VERSION,
        "meta": {
            "name": b.name, "local": f"{b.year:04d}-{b.month:02d}-{b.day:02d}"
            + (f" {b.hour:02d}:{b.minute:02d}" if b.time_known else ""),
            "utc": w.iso_formatted_utc_datetime, "time_known": b.time_known,
            "city": b.city, "country": b.country, "lat": b.lat, "lng": b.lng, "tz": b.tz,
        },
        "western": western,
        "vedic": vedic,
        "warnings": warnings,
        "_subjects": {"western": w, "vedic": v, "western_data": wdata},
    }


def _day_range_warnings(b: BirthInput) -> list[str]:
    """When birth time is unknown, flag Moon sign / nakshatra changes during that day."""
    out = []
    early = _subject(b, False, 0, 0).moon.abs_pos
    late = _subject(b, False, 23, 59).moon.abs_pos
    if int(early // 30) != int(late // 30):
        out.append("moon_sign_changes")
    ve = _subject(b, True, 0, 0).moon.abs_pos
    vl = _subject(b, True, 23, 59).moon.abs_pos
    if int(ve // 30) != int(vl // 30):
        out.append("vedic_moon_sign_changes")
    if int(ve // NAK_SPAN) != int(vl // NAK_SPAN):
        out.append("nakshatra_changes")
    return out


def sun_sign(year: int, month: int, day: int) -> int:
    """Tropical sun sign index at local noon UTC — good enough for sign selection."""
    s = AstrologicalSubjectFactory.from_birth_data(
        "s", year, month, day, 12, 0, lng=0, lat=0, tz_str="UTC", online=False,
        city="-", nation="-", active_points=["Sun", "Moon"])
    return int(s.sun.abs_pos // 30)


def local_now(tz: str) -> datetime:
    return datetime.now(ZoneInfo(tz))


_SKY_CACHE: dict = {}


def sky_now() -> dict:
    """Current sky (UTC, geocentric): tropical signs, retrogrades, moon phase, sidereal moon nakshatra. Cached 10 min."""
    now = datetime.now(timezone.utc)
    key = now.strftime("%Y%m%d%H") + str(now.minute // 10)
    if key in _SKY_CACHE:
        return _SKY_CACHE[key]
    kw = dict(lng=0.0, lat=0.0, tz_str="UTC", online=False, city="-", nation="-")
    w = AstrologicalSubjectFactory.from_birth_data("sky", now.year, now.month, now.day, now.hour, now.minute,
                                                   active_points=_ACTIVE_WESTERN_NO_TIME, **kw)
    v = AstrologicalSubjectFactory.from_birth_data("sky", now.year, now.month, now.day, now.hour, now.minute,
                                                   zodiac_type="Sidereal", sidereal_mode="LAHIRI",
                                                   active_points=["Sun", "Moon"], **kw)
    pts = {}
    for k in WESTERN_POINTS:
        p = getattr(w, k, None)
        if p is not None:
            pts[k] = {"sign": int(p.abs_pos // 30), "deg": round(p.abs_pos % 30, 2), "retro": bool(p.retrograde)}
    out = {"at": now.isoformat(), "points": pts,
           "moon_phase": {"name": w.lunar_phase.moon_phase_name, "emoji": w.lunar_phase.moon_emoji},
           "moon_nakshatra": nakshatra_of(v.moon.abs_pos),
           "retrograde": [k for k, p in pts.items() if p["retro"] and "node" not in k]}
    _SKY_CACHE.clear()
    _SKY_CACHE[key] = out
    return out
