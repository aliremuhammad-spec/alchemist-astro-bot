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
    premium_stars: int = int(os.getenv("PREMIUM_STARS", "300"))
    # Ad network IDs are public (they ship in the page). Empty = network off.
    ads: dict = field(default_factory=lambda: {
        "adexium": os.getenv("ADEXIUM_WID", "81f20334-653b-4b3f-9ae4-de0b4736bc1b"),
        "tads": os.getenv("TADS_WIDGET_ID", "13523"),
        "onclicka": os.getenv("ONCLICKA_SPOT_ID", ""),
        "monetag": os.getenv("MONETAG_ZONE", ""),
        "adsgram": os.getenv("ADSGRAM_BLOCK_ID", ""),
    })
    chart_ad: bool = os.getenv("CHART_AD", "") == "1"  # optional ad after a new chart (off by default)
    ad_min_seconds: int = 8
    ad_daily_cap: int = 10
    nofill_daily_cap: int = 3  # synastries allowed per day when no network has an ad


settings = Settings()
