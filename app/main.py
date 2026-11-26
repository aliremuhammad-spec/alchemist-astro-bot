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
           ("suggest", "اقتراح للتطوير"), ("about", "عن البوت والكود المصدري")],
    "en": [("start", "Start"), ("app", "Open the app"), ("invite", "Invite friends, earn Premium days"), ("channel", "Horoscopes for your channel"),
           ("suggest", "Suggest an improvement"), ("about", "About & source code")],
}


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
    await bot.set_my_description(
        "✨ بوت الخيميائي للفلك (نسخة تجريبية Beta)\n"
        "خارطتك الفلكية بالنظامين الغربي والفيدي، أبراج يومية بالوقت اللي بيناسبك، "
        "وأبراج يومية مجانية لقناتك أو مجموعتك.")
    await bot.set_my_short_description("خارطتك الفلكية الغربية والفيدية + أبراج يومية · Beta من تطوير الخيميائي")
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


app = FastAPI(title="The Alchemist Astro", lifespan=lifespan, docs_url=None, redoc_url=None)
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


@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html", headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
