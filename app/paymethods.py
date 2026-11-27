"""Other ways to get Telegram Stars (resellers). Digital goods in the bot are paid in Stars only,
so "other payment methods" means: buy Stars elsewhere, then pay here. Editable by admins via kv."""
import json

from . import db

KEY = "stars_resellers"

DEFAULT = [
    {"id": "s7sh", "region": "sy", "url": "https://s7sh.com/services/telegram-stars",
     "name_ar": "شحنك S7SH", "name_en": "S7SH (Syria)",
     "note_ar": "داخل سوريا · الدفع بشام كاش · بيوصلوا النجوم لحسابك بس باسم المستخدم (@username)، بدون كلمة سر",
     "note_en": "Inside Syria · pay with Sham Cash · Stars delivered to your @username, no password needed",
     "official": False},
    {"id": "telegram", "region": "intl", "url": "https://t.me/PremiumBot",
     "name_ar": "تلغرام نفسه (الرسمي)", "name_en": "Telegram itself (official)",
     "note_ar": "إذا بطاقتك بتشتغل بتلغرام: الإعدادات ← نجومي ← شراء، أو عبر @PremiumBot. أضمن طريقة",
     "note_en": "If your card works in Telegram: Settings → My Stars → Buy, or via @PremiumBot. The safest way",
     "official": True},
    {"id": "starsfast", "region": "intl", "url": "https://starsfast.com/en/",
     "name_ar": "StarsFast (فيزا وماستر)", "name_en": "StarsFast (Visa / Mastercard)",
     "note_ar": "أوروبا وأمريكا وغيرها · فيزا، ماستر، Apple Pay وGoogle Pay · التسليم باسم المستخدم",
     "note_en": "Europe, US and more · Visa, Mastercard, Apple Pay, Google Pay · delivered to your @username",
     "official": False},
    {"id": "fragment", "region": "intl", "url": "https://fragment.com/stars/buy",
     "name_ar": "Fragment (بعملة TON)", "name_en": "Fragment (pay in TON)",
     "note_ar": "منصة تلغرام الرسمية للنجوم بالعملة الرقمية TON، بتحتاج محفظة TON",
     "note_en": "Telegram's official Stars marketplace, paid in TON crypto; needs a TON wallet",
     "official": True},
]


def _valid(items) -> list[dict]:
    out = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        url = str(it.get("url", ""))
        if not (url.startswith("https://") or url.startswith("tg://")):
            continue
        out.append({k: (bool(it.get(k)) if k == "official" else str(it.get(k, ""))[:300])
                    for k in ("id", "region", "url", "name_ar", "name_en", "note_ar", "note_en", "official")})
    return out[:12]


async def load() -> list[dict]:
    raw = await db.kv_get(KEY, "")
    if raw:
        try:
            got = _valid(json.loads(raw))
            if got:
                return got
        except ValueError:
            pass
    return DEFAULT


async def save(items) -> list[dict]:
    got = _valid(items)
    await db.kv_set(KEY, json.dumps(got, ensure_ascii=False) if got else "")
    return got or DEFAULT


def localized(items: list[dict], lang: str) -> list[dict]:
    en = lang == "en"
    return [{"id": i["id"], "region": i["region"], "url": i["url"], "official": i["official"],
             "name": i["name_en" if en else "name_ar"] or i["name_ar"],
             "note": i["note_en" if en else "note_ar"] or i["note_ar"]} for i in items]
