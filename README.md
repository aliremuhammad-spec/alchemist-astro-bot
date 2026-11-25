# The Alchemist Astro · بوت الخيميائي للفلك (Beta)

Telegram bot + Mini App: Western and Vedic birth charts (North/South Indian), daily horoscopes at the
user's chosen time, and free daily horoscope digests for channels and groups.

Bot: [@TheAlchemistAstroBot](https://t.me/TheAlchemistAstroBot) · Beta, developed by The Alchemist.

## Stack

| Piece | What |
|---|---|
| Calculations | Swiss Ephemeris via [kerykeion](https://github.com/g-battaglia/kerykeion): tropical/Placidus, sidereal Lahiri/whole sign, nakshatras, Vimshottari dasha |
| Charts | Western wheel from kerykeion; North/South Indian charts drawn as SVG (`app/astro/render.py`); PNG via `rsvg-convert` |
| Places | GeoNames cities over 1,000 people (built at image build time), continent → country → city, historical time zones via `zoneinfo` |
| Server | FastAPI + aiogram 3 (webhook) + APScheduler, one process |
| Database | PostgreSQL (Neon free tier) |
| Hosting | Render free web service (Docker), Mini App served from the same URL |

## Run locally

```bash
pip install -r requirements.txt
python scripts/build_cities.py data/geo
export DATABASE_URL=postgresql://... BOT_TOKEN=... DEV_AUTH=1
uvicorn app.main:app --port 8000
# open http://localhost:8000/?dev=1   (fake user id 1, only with DEV_AUTH=1)
python -m pytest -q
```

## Deploy (Render + Neon)

1. Neon: create a project, copy the pooled connection string.
2. Render: New → Blueprint → this repo. Set `BOT_TOKEN` and `DATABASE_URL`.
3. On boot the app registers the webhook, the menu button and the commands itself.
4. Free instances sleep after 15 idle minutes; `.github/workflows/keepalive.yml` pings every 13 minutes.

## Daily horoscope file

Set `DAILY_URL` (or send `/setdaily <raw url>` to the bot as admin). Accepted shape:

```json
{"date": "2026-12-01", "signs": {"aries": {"ar": "...", "en": "..."}, "...": {}}}
```

All 12 signs are required for a day to be accepted. See `content/sample_daily.json` and `app/content.py`
for the other accepted shapes. If today's file is missing, nothing is sent and admins get one alert.

## Admin commands

`/stats` · `/broadcast all|ar|en|daily` (reply to a message) · `/reply <user_id> <text>` ·
`/setdaily <url>` · `/fetch` · `/grant <user_id> <days> [note]`

## License

AGPL-3.0. The Swiss Ephemeris is licensed under AGPL or a commercial license from Astrodienst;
this project uses it under AGPL, so the full source of the running service is published here.
