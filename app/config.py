import os
from dataclasses import dataclass, field


def _ids(v: str) -> set[int]:
    return {int(x) for x in v.replace(" ", "").split(",") if x.strip().lstrip("-").isdigit()}


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    bot_username: str = os.getenv("BOT_USERNAME", "TheAlchemistAstroBot")
    database_url: str = os.getenv("DATABASE_URL", "")
    # Render sets RENDER_EXTERNAL_URL automatically; PUBLIC_URL overrides it.
    public_url: str = (os.getenv("PUBLIC_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "")
    admin_ids: set[int] = field(default_factory=lambda: _ids(os.getenv("ADMIN_IDS", "")))
    daily_url: str = os.getenv("DAILY_URL", "")
    weekly_url: str = os.getenv("WEEKLY_URL", "")
    default_tz: str = os.getenv("DEFAULT_TZ", "Asia/Damascus")
    source_url: str = os.getenv("SOURCE_URL", "https://github.com/aliremuhammad-spec/alchemist-astro-bot")
    instagram_main: str = os.getenv("INSTAGRAM_MAIN") or "the.alchemist.astro"
    instagram_partner: str = os.getenv("INSTAGRAM_PARTNER") or "the.emerland.tablet"
    instagram_partner_label: str = os.getenv("INSTAGRAM_PARTNER_LABEL", "لوح الزمرد")
    keepalive_minutes: int = int(os.getenv("KEEPALIVE_MINUTES", "13"))
    dev_auth: bool = os.getenv("DEV_AUTH", "") == "1"  # local browser testing only
    free_profiles: int = int(os.getenv("FREE_PROFILES", "3"))


settings = Settings()
