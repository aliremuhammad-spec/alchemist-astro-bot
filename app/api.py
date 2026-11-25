from __future__ import annotations

import re
from datetime import date, time
from zoneinfo import ZoneInfo, available_timezones

from aiogram import Bot
from aiogram.types import BufferedInputFile, InputMediaPhoto
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from . import db
from .astro import geo
from .astro.engine import BirthInput, compute, sun_sign
from .astro.render import indian_svg, svg_to_png, western_wheel_svg
from .astro.report import vedic_text, western_text
from .auth import tg_user
from .bot.handlers import save_feedback
from .bot.texts import add_channel_link, add_group_link, t
from .config import settings

router = APIRouter(prefix="/api")
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_TZS = available_timezones()


async def current_user(auth: dict = Depends(tg_user)) -> dict:
    u = auth["user"]
    row = await db.upsert_user(u["id"], u.get("first_name"), u.get("username"), u.get("language_code"),
                               auth.get("start_param"))
    return dict(row)


def _lang(req_lang: str | None, user: dict) -> str:
    return req_lang if req_lang in ("ar", "en") else user["lang"]


# ───────────── session & meta ─────────────

@router.post("/session")
async def session(user: dict = Depends(current_user)):
    profiles = await db.pool().fetch("SELECT * FROM profiles WHERE user_id=$1 ORDER BY is_main DESC, id", user["id"])
    daily = await db.pool().fetchrow("SELECT * FROM daily_prefs WHERE user_id=$1", user["id"])
    return {
        "user": {"id": user["id"], "first_name": user["first_name"], "lang": user["lang"], "tz": user["tz"]},
        "premium": await db.is_premium(user["id"]),
        "profiles": [_profile_out(p) for p in profiles],
        "daily": _daily_out(daily),
        "meta": meta(),
    }


def _profile_out(p) -> dict:
    return {"id": p["id"], "name": p["name"], "birth_date": p["birth_date"].isoformat(),
            "birth_time": p["birth_time"].strftime("%H:%M") if p["birth_time"] else None,
            "city": p["city"], "country": p["country"], "indian_style": p["indian_style"], "is_main": p["is_main"]}


def meta() -> dict:
    return {
        "bot": settings.bot_username, "source": settings.source_url, "beta": True,
        "instagram_main": settings.instagram_main,
        "instagram_partner": settings.instagram_partner, "instagram_partner_label": settings.instagram_partner_label,
        "add_channel": add_channel_link(), "add_group": add_group_link(),
        "free_profiles": settings.free_profiles,
    }


@router.post("/lang")
async def set_lang(body: dict, user: dict = Depends(current_user)):
    lang = body.get("lang")
    if lang not in ("ar", "en"):
        raise HTTPException(400, "lang")
    await db.pool().execute("UPDATE users SET lang=$2 WHERE id=$1", user["id"], lang)
    return {"ok": True}


# ───────────── geo ─────────────

@router.get("/geo/continents")
async def geo_continents(lang: str = "ar"):
    return geo.continents(lang)


@router.get("/geo/countries")
async def geo_countries(continent: str):
    return geo.countries_in(continent.upper())


@router.get("/geo/cities")
async def geo_cities(country: str, q: str = ""):
    return geo.search_cities(country, q)


# ───────────── charts ─────────────

class ChartIn(BaseModel):
    name: str = Field("", max_length=60)
    day: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1800, le=2100)
    hour: int = Field(0, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    time_known: bool = True
    country: str = Field(min_length=2, max_length=2)
    city_id: int
    indian_style: str = "north"
    theme: str = "dark"
    lang: str | None = None
    save: bool = True


def _birth(name, d: date, tm: time | None, city: dict, country: str) -> BirthInput:
    return BirthInput(name=name, year=d.year, month=d.month, day=d.day,
                      hour=tm.hour if tm else 12, minute=tm.minute if tm else 0, time_known=tm is not None,
                      lat=city["lat"], lng=city["lng"], tz=city["tz"],
                      city=city.get("ar") or city["name"], country=country)


def _chart_out(chart: dict, style: str, lang: str, theme: str) -> dict:
    theme = "light" if theme == "light" else "dark"
    out = {k: v for k, v in chart.items() if k != "_subjects"}
    wsvg = re.sub(r"^\s*<\?xml[^>]*>\s*", "", western_wheel_svg(chart, theme))
    out["svg"] = {"western": wsvg, "indian": indian_svg(chart, style, lang, theme)}
    out["text"] = {"western": western_text(chart, lang), "vedic": vedic_text(chart, lang)}
    return out


@router.post("/chart")
async def chart(body: ChartIn, user: dict = Depends(current_user)):
    lang = _lang(body.lang, user)
    try:
        d = date(body.year, body.month, body.day)
    except ValueError:
        raise HTTPException(400, "invalid date")
    city = geo.city_by_id(body.country, body.city_id)
    if not city:
        raise HTTPException(400, "unknown city")
    tm = time(body.hour, body.minute) if body.time_known else None
    style = "south" if body.indian_style == "south" else "north"
    b = _birth(body.name.strip(), d, tm, city, body.country.upper())
    c = await run_in_threadpool(compute, b)
    profile_id = None
    if body.save:
        n = await db.pool().fetchval("SELECT count(*) FROM profiles WHERE user_id=$1", user["id"])
        limit_hit = n >= settings.free_profiles and not await db.is_premium(user["id"])
        if not limit_hit:
            profile_id = await db.pool().fetchval(
                """INSERT INTO profiles(user_id,name,birth_date,birth_time,city_id,city,country,lat,lng,tz,
                     indian_style,is_main) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12) RETURNING id""",
                user["id"], b.name or (user["first_name"] or "—"), d, tm, body.city_id, b.city, b.country,
                b.lat, b.lng, b.tz, style, n == 0)
    await db.event(user["id"], "chart")
    out = await run_in_threadpool(_chart_out, c, style, lang, body.theme)
    out["profile_id"] = profile_id
    out["profile_limit_hit"] = body.save and profile_id is None
    out["sun_sign"] = c["western"]["points"]["sun"]["sign"]
    return out


async def _load_profile(pid: int, uid: int) -> dict:
    p = await db.pool().fetchrow("SELECT * FROM profiles WHERE id=$1 AND user_id=$2", pid, uid)
    if not p:
        raise HTTPException(404, "profile")
    return dict(p)


def _profile_birth(p: dict) -> BirthInput:
    city = {"lat": p["lat"], "lng": p["lng"], "tz": p["tz"], "name": p["city"], "ar": p["city"]}
    return _birth(p["name"], p["birth_date"], p["birth_time"], city, p["country"])


@router.get("/profiles/{pid}/chart")
async def profile_chart(pid: int, style: str | None = None, theme: str = "dark", lang: str | None = None,
                        user: dict = Depends(current_user)):
    p = await _load_profile(pid, user["id"])
    style = style if style in ("north", "south") else p["indian_style"]
    c = await run_in_threadpool(compute, _profile_birth(p))
    out = await run_in_threadpool(_chart_out, c, style, _lang(lang, user), theme)
    out["profile_id"] = pid
    return out


@router.delete("/profiles/{pid}")
async def delete_profile(pid: int, user: dict = Depends(current_user)):
    await db.pool().execute("DELETE FROM profiles WHERE id=$1 AND user_id=$2", pid, user["id"])
    return {"ok": True}


@router.post("/profiles/{pid}/send")
async def send_profile(pid: int, request: Request, body: dict | None = None, user: dict = Depends(current_user)):
    """Send chart images + full text to the user's private chat with the bot."""
    bot: Bot = request.app.state.bot
    p = await _load_profile(pid, user["id"])
    lang = _lang((body or {}).get("lang"), user)
    style = (body or {}).get("style") or p["indian_style"]
    c = await run_in_threadpool(compute, _profile_birth(p))
    wpng = await run_in_threadpool(svg_to_png, western_wheel_svg(c, "dark"), 1100)
    ipng = await run_in_threadpool(svg_to_png, indian_svg(c, style, lang, "dark"), 900)
    caption = t(lang, "chart_caption", name=p["name"])
    if wpng and ipng:
        await bot.send_media_group(user["id"], [
            InputMediaPhoto(media=BufferedInputFile(wpng, "western.png"), caption=caption),
            InputMediaPhoto(media=BufferedInputFile(ipng, "vedic.png"))])
    await bot.send_message(user["id"], western_text(c, lang))
    await bot.send_message(user["id"], vedic_text(c, lang))
    await db.event(user["id"], "chart_sent")
    return {"ok": True}


# ───────────── daily horoscope ─────────────

def _daily_out(row) -> dict | None:
    if not row:
        return None
    return {"subscribed": row["subscribed"], "send_time": row["send_time"], "tz": row["tz"], "sign": row["sign"]}


class DailyIn(BaseModel):
    subscribed: bool = True
    send_time: str = "08:00"
    tz: str
    sign: int | None = Field(None, ge=0, le=11)


@router.post("/daily")
async def set_daily(body: DailyIn, user: dict = Depends(current_user)):
    if not HHMM.match(body.send_time):
        raise HTTPException(400, "send_time must be HH:MM")
    if body.tz not in _TZS:
        raise HTTPException(400, "unknown timezone")
    sign = body.sign
    if sign is None:
        main = await db.pool().fetchrow(
            "SELECT birth_date FROM profiles WHERE user_id=$1 ORDER BY is_main DESC, id LIMIT 1", user["id"])
        if not main:
            raise HTTPException(400, "choose a sign")
        bd = main["birth_date"]
        sign = await run_in_threadpool(sun_sign, bd.year, bd.month, bd.day)
    await db.pool().execute(
        """INSERT INTO daily_prefs(user_id,subscribed,send_time,tz,sign) VALUES($1,$2,$3,$4,$5)
           ON CONFLICT(user_id) DO UPDATE SET subscribed=$2, send_time=$3, tz=$4, sign=$5""",
        user["id"], body.subscribed, body.send_time, body.tz, sign)
    await db.pool().execute("UPDATE users SET tz=$2 WHERE id=$1", user["id"], body.tz)
    await db.event(user["id"], "daily_on" if body.subscribed else "daily_off")
    row = await db.pool().fetchrow("SELECT * FROM daily_prefs WHERE user_id=$1", user["id"])
    return _daily_out(row)


# ───────────── channels / groups ─────────────

@router.get("/channels")
async def my_channels(user: dict = Depends(current_user)):
    rows = await db.pool().fetch(
        "SELECT chat_id,title,kind,active,send_time,tz,lang FROM broadcast_chats WHERE added_by=$1 ORDER BY created_at",
        user["id"])
    return [dict(r) for r in rows]


class ChannelIn(BaseModel):
    send_time: str
    tz: str
    lang: str = "ar"
    active: bool = True


@router.post("/channels/{chat_id}")
async def update_channel(chat_id: int, body: ChannelIn, user: dict = Depends(current_user)):
    if not HHMM.match(body.send_time) or body.tz not in _TZS or body.lang not in ("ar", "en"):
        raise HTTPException(400, "invalid settings")
    r = await db.pool().execute(
        """UPDATE broadcast_chats SET send_time=$3, tz=$4, lang=$5, active=$6,
             last_sent = CASE WHEN send_time <> $3 THEN NULL ELSE last_sent END
           WHERE chat_id=$1 AND added_by=$2""",
        chat_id, user["id"], body.send_time, body.tz, body.lang, body.active)
    if r.endswith(" 0"):
        raise HTTPException(404, "chat")
    return {"ok": True}


# ───────────── feedback ─────────────

class FeedbackIn(BaseModel):
    text: str = Field(min_length=3, max_length=3500)


@router.post("/feedback")
async def feedback(body: FeedbackIn, request: Request, user: dict = Depends(current_user)):
    await save_feedback(request.app.state.bot, user["id"], user["first_name"], user["username"], body.text)
    return {"ok": True}


@router.get("/timezones")
async def timezones():
    return sorted(z for z in _TZS if "/" in z and not z.startswith(("Etc/", "SystemV/", "posix/", "right/")))


def tz_ok(tz: str) -> bool:
    try:
        ZoneInfo(tz)
        return True
    except Exception:
        return False
