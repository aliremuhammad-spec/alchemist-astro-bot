from __future__ import annotations

import logging
import hashlib
import hmac
from contextlib import asynccontextmanager
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, MenuButtonWebApp, Update, WebAppInfo
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from . import db, interp, scheduler
from .api import router as api_router
from .monetize import router as monetize_router
from .admin import router as admin_router
from .bot.handlers import router as bot_router
from .config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app")
WEB_DIR = Path(__file__).resolve().parents[1] / "web"

# Stable across restarts: explicit secret, else derived from the bot token.
WEBHOOK_SECRET = settings.webhook_secret or hashlib.sha256(f"wh:{settings.bot_token}".encode()).hexdigest()[:48]

COMMANDS = {
    "ar": [("start", "البداية"), ("app", "فتح التطبيق"), ("invite", "ادعُ أصحابك واربح أيام مميز"), ("channel", "الأبراج لقناتك أو مجموعتك"),
           ("suggest", "اقتراح للتطوير"), ("paysupport", "دعم الدفعات والاسترداد"),
           ("privacy", "سياسة الخصوصية"), ("deletemydata", "مسح بياناتي"), ("about", "عن البوت والكود المصدري")],
    "en": [("start", "Start"), ("app", "Open the app"), ("invite", "Invite friends, earn Premium days"), ("channel", "Horoscopes for your channel"),
           ("suggest", "Suggest an improvement"), ("paysupport", "Payment support & refunds"),
           ("privacy", "Privacy policy"), ("deletemydata", "Delete my data"), ("about", "About & source code")],
}


DESCRIPTIONS = {
    "": {   # default (Arabic)
        "long": ("🔭 الخيميائي: فلك غربي وفيدي بحسابات دقيقة\n\n"
                 "• خارطتك الفلكية بالنظامين، بالشكل الهندي الشمالي أو الجنوبي\n"
                 "• برجك اليومي بيوصلك بالساعة اللي بتختارها، والأوقات بتوقيتك\n"
                 "• توافق مفصّل بين شخصين، وتقارير فلكية PDF\n"
                 "• اختيارات فلكية أسبوعية لأنسب الأوقات\n"
                 "• أبراج يومية مجانية لقناتك أو مجموعتك\n\n"
                 "اضغط «ابدأ» واطلع خارطتك بدقيقة 👇"),
        "short": "خارطتك الفلكية الغربية والفيدية، برجك اليومي بتوقيتك، وتوافق مفصّل بين شخصين 🔭",
    },
    "en": {
        "long": ("🔭 The Alchemist: Western and Vedic astrology, precisely calculated\n\n"
                 "• Your birth chart in both systems, North or South Indian style\n"
                 "• Your daily horoscope at the hour you pick, in your local time\n"
                 "• Detailed compatibility between two people, and PDF reports\n"
                 "• Weekly electional picks for the best times\n"
                 "• Free daily horoscopes for your channel or group\n\n"
                 "Tap Start and cast your chart in a minute 👇"),
        "short": "Your Western & Vedic birth chart, a daily horoscope in your time, and detailed compatibility 🔭",
    },
}
AVATAR_VERSION = "2026-11-27"


async def set_avatar(bot: Bot) -> None:
    """Upload the bot's profile photo once per AVATAR_VERSION (Telegram keeps every upload in the photo list)."""
    from aiogram.types import BufferedInputFile, InputProfilePhotoStatic
    try:
        if await db.kv_get("avatar_version", "") == AVATAR_VERSION:
            return
        raw = (WEB_DIR / "brand" / "avatar.jpg").read_bytes()
        await bot.set_my_profile_photo(InputProfilePhotoStatic(photo=BufferedInputFile(raw, "avatar.jpg")))
        await db.kv_set("avatar_version", AVATAR_VERSION)
        log.info("bot avatar set (%s)", AVATAR_VERSION)
    except Exception as e:
        log.warning("avatar not set: %s", e)


async def configure_bot(bot: Bot) -> None:
    if not settings.public_url:
        log.warning("PUBLIC_URL/RENDER_EXTERNAL_URL not set: webhook not registered")
        return
    await bot.set_webhook(f"{settings.public_url}/tg/webhook", secret_token=WEBHOOK_SECRET,
                          allowed_updates=["message", "callback_query", "my_chat_member",
                                           "pre_checkout_query"],
                          drop_pending_updates=False)
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(
        text="🔭 الخيميائي", web_app=WebAppInfo(url=settings.public_url)))
    await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS["ar"]])
    await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS["en"]],
                              language_code="en")
    for code, d in DESCRIPTIONS.items():
        try:
            await bot.set_my_description(d["long"], language_code=code)
            await bot.set_my_short_description(d["short"], language_code=code)
        except Exception as e:
            log.warning("description %s: %s", code or "default", e)
    await set_avatar(bot)
    log.info("webhook + menu registered at %s", settings.public_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init()
    try:
        await interp.load()
    except Exception:
        log.exception("interpretations not loaded")
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(bot_router)
    app.state.bot, app.state.dp = bot, dp
    try:
        await configure_bot(bot)
    except Exception:
        log.exception("bot configuration failed")
    sched = scheduler.start(bot)
    from . import reports
    reports.start(bot)
    yield
    sched.shutdown(wait=False)
    await bot.session.close()
    await db.close()


app = FastAPI(title="The Alchemist Astro", lifespan=lifespan, docs_url=None, redoc_url=None,
              openapi_url=None)
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    h = resp.headers
    h.setdefault("X-Content-Type-Options", "nosniff")
    h.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    h.setdefault("Strict-Transport-Security", "max-age=31536000")
    h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    # the Mini App may only be framed by Telegram's web clients
    h.setdefault("Content-Security-Policy", "frame-ancestors 'self' https://web.telegram.org https://*.telegram.org")
    return resp
app.include_router(api_router)
app.include_router(monetize_router)
app.include_router(admin_router)


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/tg/webhook")
async def webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(default="")):
    if not hmac.compare_digest(x_telegram_bot_api_secret_token.encode(), WEBHOOK_SECRET.encode()):
        raise HTTPException(403)
    update = Update.model_validate(await request.json(), context={"bot": request.app.state.bot})
    await request.app.state.dp.feed_update(request.app.state.bot, update)
    return {"ok": True}


_PRIVACY: str | None = None


def _privacy_html() -> str:
    global _PRIVACY
    if _PRIVACY is None:
        import markdown
        src = (Path(__file__).resolve().parents[1] / "docs" / "PRIVACY.md").read_text(encoding="utf-8")
        ar, en = src.split("\n---\n", 1)
        body = (f'<article lang="ar" dir="rtl" id="ar">{markdown.markdown(ar)}</article><hr>'
                f'<article lang="en" dir="ltr" id="en">{markdown.markdown(en)}</article>')
        _PRIVACY = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
                    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                    "<title>سياسة الخصوصية · Privacy Policy — The Alchemist Astro</title><style>"
                    "body{margin:0;background:#12142a;color:#e9e6f5;font:16px/1.75 system-ui,-apple-system,'Segoe UI',Tahoma,sans-serif}"
                    "article{max-width:44rem;margin:0 auto;padding:28px 20px}h1{font-size:1.5rem;line-height:1.35;color:#e8c77a}"
                    "h2{font-size:1.1rem;margin-top:1.8em;color:#e8c77a}a{color:#9fb7ff}li{margin:.3em 0}"
                    "hr{border:0;border-top:1px solid #2e3160;max-width:44rem;margin:0 auto}"
                    "nav{text-align:center;padding:14px}nav a{margin:0 10px}</style></head><body>"
                    "<nav><a href='#ar'>العربية</a><a href='#en'>English</a></nav>" + body + "</body></html>")
    return _PRIVACY


@app.get("/privacy")
async def privacy_page():
    from fastapi.responses import HTMLResponse
    return HTMLResponse(_privacy_html(), headers={"Cache-Control": "public, max-age=3600"})


@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html", headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
