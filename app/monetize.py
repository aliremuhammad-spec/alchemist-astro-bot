"""Rewarded-ad tickets, synastry, divisional charts and the Stars premium subscription."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.types import LabeledPrice
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from . import db
from .api import _lang, _load_profile, _profile_birth, current_user
from .astro.engine import compute
from .astro.render import indian_svg, synastry_wheel_svg
from .astro.synastry import compute_synastry, synastry_text
from .astro.vargas import VARGAS, varga_chart
from .config import settings

router = APIRouter(prefix="/api")
SUB_PERIOD = 30 * 24 * 3600  # Telegram allows exactly 30 days for Star subscriptions
PLACEMENTS = {"synastry", "chart"}


async def premium_price() -> int:
    v = await db.kv_get("premium_stars", str(settings.premium_stars))
    return int(v) if v.isdigit() else settings.premium_stars


# ───────────── rewarded ads ─────────────

class AdStart(BaseModel):
    placement: str


@router.post("/ads/start")
async def ad_start(body: AdStart, user: dict = Depends(current_user)):
    if body.placement not in PLACEMENTS:
        raise HTTPException(400, "placement")
    n = await db.pool().fetchval(
        "SELECT count(*) FROM ad_tickets WHERE user_id=$1 AND created_at > now() - interval '1 day'", user["id"])
    if n >= settings.ad_daily_cap * 2:
        raise HTTPException(429, "daily_limit")
    tid = secrets.token_urlsafe(16)
    await db.pool().execute("INSERT INTO ad_tickets(id,user_id,placement) VALUES($1,$2,$3)", tid, user["id"], body.placement)
    await db.pool().execute("INSERT INTO ad_events(user_id,provider,placement,status) VALUES($1,'-',$2,'requested')",
                            user["id"], body.placement)
    return {"ticket": tid, "min_seconds": settings.ad_min_seconds}


class AdDone(BaseModel):
    ticket: str
    provider: str          # adexium | tads | onclicka | monetag | adsgram | none
    status: str            # completed | skipped | nofill


@router.post("/ads/complete")
async def ad_complete(body: AdDone, user: dict = Depends(current_user)):
    t = await db.pool().fetchrow("SELECT * FROM ad_tickets WHERE id=$1 AND user_id=$2", body.ticket, user["id"])
    if not t or t["completed_at"]:
        raise HTTPException(400, "ticket")
    provider = body.provider[:20]
    status = body.status[:20]
    if status == "completed" and (datetime.now(timezone.utc) - t["created_at"]).total_seconds() < settings.ad_min_seconds:
        status = "rejected_fast"
    await db.pool().execute("INSERT INTO ad_events(user_id,provider,placement,status) VALUES($1,$2,$3,$4)",
                            user["id"], provider, t["placement"], status)
    if status == "rejected_fast":
        raise HTTPException(400, "too_fast")
    if body.status == "completed":
        pass
    elif body.status == "nofill":
        used = await db.pool().fetchval(
            """SELECT count(*) FROM ad_tickets WHERE user_id=$1 AND provider='none'
               AND completed_at > now() - interval '1 day'""", user["id"])
        if used >= settings.nofill_daily_cap:
            raise HTTPException(429, "nofill_limit")
        provider = "none"
    else:
        return {"granted": False}
    await db.pool().execute("UPDATE ad_tickets SET completed_at=now(), provider=$2 WHERE id=$1", body.ticket, provider)
    return {"granted": True}


async def _consume_ticket(uid: int, ticket: str | None) -> None:
    if uid in settings.admin_ids or await db.is_premium(uid):
        return  # premium users never see ads
    if not ticket:
        raise HTTPException(402, "ad_required")
    r = await db.pool().execute(
        """UPDATE ad_tickets SET used_at=now() WHERE id=$1 AND user_id=$2 AND placement='synastry'
           AND completed_at IS NOT NULL AND used_at IS NULL""", ticket, uid)
    if r.endswith(" 0"):
        raise HTTPException(402, "ad_required")


# ───────────── synastry ─────────────

class SynIn(BaseModel):
    a: int
    b: int
    ticket: str | None = None
    theme: str = "dark"
    lang: str | None = None


@router.post("/synastry")
async def synastry(body: SynIn, user: dict = Depends(current_user)):
    if body.a == body.b:
        raise HTTPException(400, "same_profile")
    pa = await _load_profile(body.a, user["id"])
    pb = await _load_profile(body.b, user["id"])
    await _consume_ticket(user["id"], body.ticket)
    lang = _lang(body.lang, user)
    ba, bb = _profile_birth(pa), _profile_birth(pb)
    s = await run_in_threadpool(compute_synastry, ba, bb)
    svg = await run_in_threadpool(synastry_wheel_svg, s["_data"], "light" if body.theme == "light" else "dark")
    await db.event(user["id"], "synastry")
    out = {"names": s["names"], "score": s["score"], "aspects": s["aspects"][:30],
           "text": synastry_text(s, lang), "svg": svg.split("?>", 1)[-1], "a": body.a, "b": body.b}
    from .astro import compat
    member = await _is_member(user["id"])
    if compat.ready():
        r = await run_in_threadpool(_compat_analysis, ba, bb, [pa["name"], pb["name"]], lang, await footer_ctx())
        if member:
            out["compat"] = _slim(r)
        else:
            out["compat_teaser"] = {
                "overall": r["overall"], "band": (r["overall_entry"] or {}).get("title"),
                "summary": (r["overall_entry"] or {}).get("summary"),
                "dimensions": [{"key": d["key"], "level": d["level"]} for d in r["dimensions"]]}
    if member:
        if not compat.ready():
            from .astro.synastry_detail import detail
            d = await run_in_threadpool(detail, ba, bb, s)
            d.pop("_charts", None)
            out["detail"] = d
        out["report_quota"] = await synastry_quota(user["id"])
    else:
        out["locked"] = True
    return out


def _slim(r: dict) -> dict:
    """The app shows the strongest items; the PDF keeps everything."""
    r = dict(r)
    r["aspects"] = r["aspects"][:12]
    r["composite"] = {"asc": r["composite"]["asc"],
                      "planets": [{k: v for k, v in p.items() if k != "house_entry"} for p in r["composite"]["planets"][:7]]}
    return r


def _compat_analysis(ba, bb, names, lang, fctx):
    from .astro import compat
    from .astro.engine import compute as _compute
    return compat.analyse(_compute(ba), _compute(bb), tuple(names), lang, footer_ctx=fctx)


async def footer_ctx() -> dict:
    """Placeholders of the compatibility database's mandatory footer."""
    booking = await db.kv_get("booking_command", "")
    return {"booking": booking or None, "instagram": f"@{settings.instagram_main}" if settings.instagram_main else None}


async def _is_member(uid: int) -> bool:
    return uid in settings.admin_ids or await db.is_premium(uid)


SYN_MONTHLY = 30


async def synastry_quota(uid: int) -> dict:
    used = await db.pool().fetchval(
        """SELECT count(*) FROM report_log WHERE user_id=$1 AND kind='synastry' AND paid_with='premium'
           AND created_at >= date_trunc('month', now())""", uid)
    credits = await db.pool().fetchval("SELECT syn_report_credits FROM users WHERE id=$1", uid) or 0
    return {"used": used, "limit": SYN_MONTHLY, "credits": credits, "price": await syn_report_price()}


async def syn_report_price() -> int:
    v = await db.kv_get("syn_report_stars", "50")
    return int(v) if v.isdigit() else 50


# ───────────── premium: divisional charts ─────────────

@router.get("/vargas")
async def vargas_list(lang: str = "ar"):
    return [{"n": n, "name": v[0], "ar": v[1], "about": v[2]} for n, v in VARGAS.items()]


@router.get("/profiles/{pid}/varga/{n}")
async def profile_varga(pid: int, n: int, style: str = "north", theme: str = "dark", lang: str | None = None,
                        user: dict = Depends(current_user)):
    if n not in VARGAS:
        raise HTTPException(400, "varga")
    if n not in (1, 9) and not await db.is_premium(user["id"]):  # D9 is a free taste
        raise HTTPException(402, "premium_required")
    p = await _load_profile(pid, user["id"])
    c = await run_in_threadpool(compute, _profile_birth(p))
    vc = varga_chart(c, n)
    svg = indian_svg(c, "south" if style == "south" else "north", _lang(lang, user),
                     "light" if theme == "light" else "dark", vc)
    return {"n": n, "svg": svg, "lagna": vc["lagna"], "points": vc["points"]}


# ───────────── premium: Stars subscription ─────────────

@router.get("/premium")
async def premium_info(user: dict = Depends(current_user)):
    row = await db.pool().fetchrow(
        "SELECT source, ends_at FROM subscriptions WHERE user_id=$1 AND ends_at > now() ORDER BY ends_at DESC LIMIT 1",
        user["id"])
    return {"active": bool(row), "until": row["ends_at"].isoformat() if row else None,
            "source": row["source"] if row else None, "stars": await premium_price()}


@router.post("/premium/invoice")
async def premium_invoice(request: Request, user: dict = Depends(current_user)):
    bot: Bot = request.app.state.bot
    lang = user["lang"]
    link = await bot.create_invoice_link(
        title="الخيميائي المميز" if lang == "ar" else "Alchemist Premium",
        description=("اشتراك شهري: الخرائط الفرعية D2–D60، التوافق بلا إعلانات، ملفات غير محدودة، والمزايا المميزة القادمة."
                     if lang == "ar" else
                     "Monthly: divisional charts D2–D60, ad-free synastry, unlimited profiles, and upcoming premium features."),
        payload=f"premium:{user['id']}",
        currency="XTR",
        prices=[LabeledPrice(label="Premium", amount=await premium_price())],
        subscription_period=SUB_PERIOD,
    )
    return {"link": link}


async def record_payment(uid: int, sp) -> None:
    """Called from the bot's successful_payment handler (first payment and every renewal)."""
    expires = getattr(sp, "subscription_expiration_date", None)
    if isinstance(expires, int):
        expires = datetime.fromtimestamp(expires, timezone.utc)
    await db.pool().execute(
        """INSERT INTO payments(user_id,stars,charge_id,payload,recurring,first_recurring,expires_at)
           VALUES($1,$2,$3,$4,$5,$6,$7) ON CONFLICT(charge_id) DO NOTHING""",
        uid, sp.total_amount, sp.telegram_payment_charge_id, sp.invoice_payload,
        getattr(sp, "is_recurring", None), getattr(sp, "is_first_recurring", None), expires)
    if expires is None:
        from datetime import timedelta
        expires = datetime.now(timezone.utc) + timedelta(seconds=SUB_PERIOD)
    await db.pool().execute(
        "INSERT INTO subscriptions(user_id,source,ends_at,charge_id) VALUES($1,'stars',$2,$3)",
        uid, expires, sp.telegram_payment_charge_id)


# ───────────── PDF report (premium) ─────────────

_report_busy: set[int] = set()


def _place(p: dict, lang: str, country_name: str | None) -> tuple[str, str]:
    """City and country written in the report's language (not the language the profile was saved in)."""
    from .astro import geo
    row = geo.city_by_id(p["country"], p["city_id"]) if p.get("city_id") else None
    city = ((row.get("ar") if lang == "ar" else None) or row["name"]) if row else p["city"]
    cn = (country_name or "").strip()
    if not cn or len(cn) > 60 or any(ch in cn for ch in "<>{}"):
        cn = next((x["name"] for x in geo.countries() if x["iso"] == p["country"]), p["country"]) if lang == "en" else p["country"]
    return city, cn


@router.post("/profiles/{pid}/report")
async def profile_report(pid: int, request: Request, body: dict | None = None, user: dict = Depends(current_user)):
    """Build the automated natal report as a PDF and send it to the user's chat with the bot."""
    from aiogram.types import BufferedInputFile

    from . import interp
    from .report.builder import build_pdf

    uid = user["id"]
    if uid in settings.admin_ids:
        paid_with = "admin"
    elif await db.is_premium(uid):
        paid_with = "premium"
    elif (await db.pool().fetchval("SELECT report_credits FROM users WHERE id=$1", uid) or 0) > 0:
        paid_with = "credit"
    else:
        raise HTTPException(402, "premium_required")
    if not interp.ready():
        raise HTTPException(503, "report_unavailable")
    if uid in _report_busy:
        raise HTTPException(429, "report_in_progress")
    p = await _load_profile(pid, uid)
    lang = _lang((body or {}).get("lang"), user)
    style = (body or {}).get("style") or p["indian_style"]
    _report_busy.add(uid)
    try:
        c = await run_in_threadpool(compute, _profile_birth(p))
        c["meta"]["city"], c["meta"]["country"] = _place(p, lang, (body or {}).get("country_name"))
        pdf = await run_in_threadpool(build_pdf, c, lang, style)
    finally:
        _report_busy.discard(uid)
    bot: Bot = request.app.state.bot
    safe = "".join(ch for ch in p["name"] if ch.isalnum() or ch in " _-").strip().replace(" ", "_") or "chart"
    caption = (f"📄 التقرير الفلكي لخارطة <b>{p['name']}</b>\nمن الخيميائي 🜍" if lang == "ar"
               else f"📄 Astrological report: <b>{p['name']}</b>\nfrom The Alchemist 🜍")
    await bot.send_document(uid, BufferedInputFile(pdf, f"Alchemist_astrological_report_{safe}.pdf"), caption=caption)
    if paid_with == "credit":
        await db.pool().execute("UPDATE users SET report_credits=greatest(report_credits-1,0) WHERE id=$1", uid)
    await db.pool().execute("INSERT INTO report_log(user_id,kind,paid_with) VALUES($1,'natal',$2)", uid, paid_with)
    await db.event(uid, "report_sent")
    return {"ok": True, "pages_bytes": len(pdf)}


# ───────────── weekly electional picks (premium) ─────────────

@router.get("/weekly")
async def weekly(tz: str = "Asia/Damascus", lang: str | None = None, user: dict = Depends(current_user)):
    from zoneinfo import available_timezones

    from . import content, forecasts
    data = await content.weekly_current()
    if not data:
        return {"available": False}
    head = {"available": True, "week_start": data["week_start"], "week_end": data.get("week_end")}
    if user["id"] not in settings.admin_ids and not await db.is_premium(user["id"]):
        return {**head, "locked": True}
    tz = tz if tz in available_timezones() else "Asia/Damascus"
    await db.event(user["id"], "weekly_view")
    return {**head, "locked": False, **forecasts.weekly_view(data, tz, _lang(lang, user))}



# ───────────── compatibility report (premium: 30/month free, then paid; free users: no) ─────────────

class SynReportIn(BaseModel):
    a: int
    b: int
    lang: str | None = None


_syn_busy: set[int] = set()


@router.post("/synastry/report")
async def synastry_report(body: SynReportIn, request: Request, user: dict = Depends(current_user)):
    from aiogram.types import BufferedInputFile

    from .astro.synastry_detail import detail
    from .report.synastry_report import build_synastry_pdf

    uid = user["id"]
    if body.a == body.b:
        raise HTTPException(400, "same_profile")
    if uid in settings.admin_ids:
        paid_with = "admin"
    elif await db.is_premium(uid):
        q = await synastry_quota(uid)
        if q["used"] < q["limit"]:
            paid_with = "premium"
        elif q["credits"] > 0:
            paid_with = "credit"
        else:
            raise HTTPException(402, "report_quota")
    else:
        raise HTTPException(402, "premium_required")
    if uid in _syn_busy:
        raise HTTPException(429, "report_in_progress")
    pa = await _load_profile(body.a, uid)
    pb = await _load_profile(body.b, uid)
    lang = _lang(body.lang, user)
    _syn_busy.add(uid)
    try:
        from .astro import compat
        ba, bb = _profile_birth(pa), _profile_birth(pb)
        s = await run_in_threadpool(compute_synastry, ba, bb)
        if compat.ready():
            from .report.synastry_report import build_compat_pdf
            r = await run_in_threadpool(_compat_analysis, ba, bb, [pa["name"], pb["name"]], lang, await footer_ctx())
            pdf = await run_in_threadpool(build_compat_pdf, r, s, lang)
        else:
            d = await run_in_threadpool(detail, ba, bb, s)
            pdf = await run_in_threadpool(build_synastry_pdf, [pa["name"], pb["name"]], s, d, lang)
    finally:
        _syn_busy.discard(uid)
    bot: Bot = request.app.state.bot
    safe = "_".join("".join(ch for ch in n if ch.isalnum()) or "x" for n in (pa["name"], pb["name"]))
    cap = (f"💞 تقرير التوافق الفلكي: <b>{pa['name']}</b> و<b>{pb['name']}</b>\nمن الخيميائي 🜍" if lang == "ar"
           else f"💞 Compatibility report: <b>{pa['name']}</b> & <b>{pb['name']}</b>\nfrom The Alchemist 🜍")
    await bot.send_document(uid, BufferedInputFile(pdf, f"Alchemist_compatibility_{safe}.pdf"), caption=cap)
    if paid_with == "credit":
        await db.pool().execute("UPDATE users SET syn_report_credits=greatest(syn_report_credits-1,0) WHERE id=$1", uid)
    await db.pool().execute("INSERT INTO report_log(user_id,kind,paid_with) VALUES($1,'synastry',$2)", uid, paid_with)
    await db.event(uid, "syn_report_sent")
    return {"ok": True, "quota": await synastry_quota(uid)}


@router.post("/synastry/report/invoice")
async def synastry_report_invoice(request: Request, user: dict = Depends(current_user)):
    if not await _is_member(user["id"]):
        raise HTTPException(402, "premium_required")
    bot: Bot = request.app.state.bot
    ar = user["lang"] == "ar"
    price = await syn_report_price()
    link = await bot.create_invoice_link(
        title="تقرير توافق إضافي" if ar else "Extra compatibility report",
        description=("تقرير توافق فلكي إضافي (غربي + فيدي) بعد استهلاك الـ30 تقرير الشهرية." if ar
                     else "One extra compatibility report (Western + Vedic) beyond the monthly 30."),
        payload=f"synrep:{user['id']}", currency="XTR",
        prices=[LabeledPrice(label="Report", amount=price)])
    return {"link": link, "stars": price}


async def record_report_payment(uid: int, sp) -> None:
    r = await db.pool().execute(
        """INSERT INTO payments(user_id,stars,charge_id,payload,recurring,first_recurring,expires_at)
           VALUES($1,$2,$3,$4,FALSE,FALSE,NULL) ON CONFLICT(charge_id) DO NOTHING""",
        uid, sp.total_amount, sp.telegram_payment_charge_id, sp.invoice_payload)
    if not r.endswith(" 0"):
        await db.pool().execute("UPDATE users SET syn_report_credits=syn_report_credits+1 WHERE id=$1", uid)


# ───────────── invites ─────────────

@router.get("/invite")
async def invite(user: dict = Depends(current_user)):
    from . import referral
    return await referral.stats(user["id"])
