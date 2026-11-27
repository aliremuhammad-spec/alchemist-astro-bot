"""Inline mode: @TheAlchemistAstroBot <query> in any chat.

Three intents, in this priority:
  place  – an astrological placement read from the interpretation DB ("القمر في الأسد", "Sun square Moon")
  weekly – a short teaser of the weekly electional picks (never the windows themselves)
  daily  – today's horoscope for one or two signs (two signs add a short compatibility note)

Inline users may never have started the bot, so we never create a users row for them; usage goes to
`events` (inline_query / inline_pick) with the numeric id only, never the query text.
"""
from __future__ import annotations

import difflib
import hashlib
import html
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import date, datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, F, Router
from aiogram.types import (ChosenInlineResult, InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery,
                           InlineQueryResultArticle, InlineQueryResultsButton, InputTextMessageContent,
                           LinkPreviewOptions, WebAppInfo)

from .. import db
from ..astro.names import SIGN_GLYPH, SIGN_KEYS, SIGNS
from ..config import settings

log = logging.getLogger("inline")
router = Router(name="inline")

MAX_TEXT = 4096
MAX_RESULTS = 50
MAX_PLACES = 6
CACHE_PUBLIC = 300

# ───────────────────────── normalisation ─────────────────────────

_TASHKEEL = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")   # harakat + tatweel
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_AR = re.compile(r"[؀-ۿ]")
_LATIN = re.compile(r"[A-Za-z]")


def normalize(text: str) -> str:
    """Lower-case, no diacritics/tatweel, unified alef/hamza/ta marbuta/ya, western digits."""
    s = _TASHKEEL.sub("", (text or "").lower()).translate(_DIGITS)
    s = re.sub("[أإآٱ]", "ا", s)
    s = s.replace("ؤ", "و").replace("ئ", "ي").replace("ء", "").replace("ة", "ه").replace("ى", "ي")
    s = re.sub(r"[°º]", " ", s)
    s = re.sub(r"[^\w\s,،؛;+-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def detect_lang(query: str, language_code: str | None) -> str:
    ar, la = len(_AR.findall(query or "")), len(_LATIN.findall(query or ""))
    if ar or la:
        return "ar" if ar >= la else "en"
    return "ar" if (language_code or "ar").startswith("ar") else "en"


# vocabularies (normalised forms, without the article)
SIGN_WORDS = {
    "aries": ["حمل", "aries", "ari"], "taurus": ["ثور", "taurus", "tau"], "gemini": ["جوزاء", "جوزا", "جوزه", "gemini", "gem"],
    "cancer": ["سرطان", "cancer"], "leo": ["اسد", "leo"], "virgo": ["عذراء", "عذرا", "virgo", "vir"],
    "libra": ["ميزان", "libra", "lib"], "scorpio": ["عقرب", "scorpio", "scorpion", "sco"],
    "sagittarius": ["قوس", "رامي", "sagittarius", "sagitarius", "sagittarious", "sag"],
    "capricorn": ["جدي", "capricorn", "capricon", "capricorne", "cap"], "aquarius": ["دلو", "aquarius", "aquarious", "aqu"],
    "pisces": ["حوت", "pisces", "pices", "pisc", "pis"],
}
PLANET_WORDS = {
    "sun": ["شمس", "sun"], "moon": ["قمر", "moon"], "mercury": ["عطارد", "mercury"], "venus": ["زهره", "زهرا", "venus"],
    "mars": ["مريخ", "mars"], "jupiter": ["مشتري", "jupiter", "jupitor"], "saturn": ["زحل", "saturn", "saturne"],
    "uranus": ["اورانوس", "يورانوس", "uranus"], "neptune": ["نبتون", "نيبتون", "neptune"], "pluto": ["بلوتو", "pluto"],
}
ASPECT_WORDS = {
    "conjunction": ["اقتران", "مقترن", "مقترنه", "conjunction", "conjunct", "conj"],
    "sextile": ["تسديس", "سداسي", "sextile"], "square": ["تربيع", "مربع", "square"],
    "trine": ["تثليث", "مثلث", "ترين", "trine"], "opposition": ["مقابله", "مقابل", "تقابل", "opposition", "opposite", "opp"],
    "semisextile": ["نصف_تسديس", "semisextile"], "semisquare": ["نصف_تربيع", "semisquare"],
    "sesquiquadrate": ["تربيع_ونصف", "sesquiquadrate", "sesquisquare", "135"],
    "quincunx": ["كوينكانكس", "كوينكنكس", "quincunx", "inconjunct", "150"],
    "quintile": ["خمسي", "خماسي", "quintile"], "biquintile": ["ثنائي_الخمس", "ثنائي_خمسي", "biquintile"],
}
ASC_WORDS = ["طالع", "صاعد", "ascendant", "rising", "asc"]
LAGNA_WORDS = ["لاغنا", "لغنا", "لجنا", "lagna"]
VEDIC_WORDS = ["فيدي", "هندي", "vedic", "jyotish"]
HOUSE_WORDS = ["بيت", "house"]
WEEKLY_WORDS = ["اختيارات", "اختيار", "اسبوعيه", "اسبوعي", "اسبوع", "توقيت", "electional", "elections",
                "election", "weekly", "week"]
DAILY_WORDS = ["برج", "ابراج", "يومي", "يوميه", "اليوم", "horoscope", "horoscopes", "daily", "today", "sign"]
FILLERS = ["في", "ب", "in", "on", "the", "of", "مع", "and", "with", "and"]
ORDINALS = {
    "اول": 1, "ثاني": 2, "تاني": 2, "ثالث": 3, "تالت": 3, "رابع": 4, "خامس": 5, "سادس": 6, "سابع": 7, "ثامن": 8,
    "تامن": 8, "تاسع": 9, "عاشر": 10, "حادي_عشر": 11, "ثاني_عشر": 12, "تاني_عشر": 12,
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
    "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12,
}
# multi-word terms joined before tokenising (applied on normalised text)
_PHRASES = [
    (r"\bنصف\s+(?:ال)?تسديس\b", "نصف_تسديس"), (r"\bنصف\s+(?:ال)?تربيع\b", "نصف_تربيع"),
    (r"\b(?:ال)?تربيع\s+و\s*نصف\b", "تربيع_ونصف"), (r"\bثنائي\s+(?:ال)?خم(?:س|سي)\b", "ثنائي_الخمس"),
    (r"\bsemi[\s-]?sextile\b", "semisextile"), (r"\bsemi[\s-]?square\b", "semisquare"),
    (r"\bsesqui[\s-]?(?:quadrate|square)\b", "sesquiquadrate"), (r"\bbi[\s-]?quintile\b", "biquintile"),
    (r"\b(?:ال)?حادي\s+عشر\b", "حادي_عشر"), (r"\b(?:ال)?(?:ثاني|تاني)\s+عشر\b", "ثاني_عشر"),
    (r"\b(\d{1,2})(?:st|nd|rd|th)\b", r"\1"),
]


def _vocab(groups: dict[str, list[str]]) -> dict[str, str]:
    return {w: k for k, ws in groups.items() for w in ws}


_SIGN_V, _PLANET_V, _ASPECT_V = _vocab(SIGN_WORDS), _vocab(PLANET_WORDS), _vocab(ASPECT_WORDS)


def _variants(tok: str) -> list[str]:
    """tok, then without a leading و / ب / ل, then without the article ال."""
    out = [tok]
    for p in ("و", "ب", "ل", "وب", "وال", "بال", "لل"):
        if tok.startswith(p) and len(tok) > len(p) + 1:
            out.append(tok[len(p):])
    for v in list(out):
        if v.startswith("ال") and len(v) > 3:
            out.append(v[2:])
    return list(dict.fromkeys(out))


def _lookup(tok: str, vocab: dict[str, str], fuzzy: bool = True) -> str | None:
    for v in _variants(tok):
        if v in vocab:
            return vocab[v]
    if fuzzy:
        for v in _variants(tok):
            if len(v) >= 4:
                m = difflib.get_close_matches(v, [w for w in vocab if len(w) >= 4], n=1, cutoff=0.8)
                if m:
                    return vocab[m[0]]
    return None


def _in(tok: str, words: list[str]) -> bool:
    return any(v in words for v in _variants(tok))


def sign_key(word: str) -> str | None:
    return _lookup(normalize(word), _SIGN_V)


def planet_key(word: str) -> str | None:
    return _lookup(normalize(word), _PLANET_V)


@dataclass
class Tok:
    kind: str            # planet, sign, aspect, house, asc, lagna, vedic, weekly, daily, num, fill, word
    value: object = None
    raw: str = ""


def tokenize(query: str) -> list[list[Tok]]:
    """Split into comma-separated segments of classified tokens."""
    s = normalize(query)
    for pat, rep in _PHRASES:
        s = re.sub(pat, rep, s)
    segments = []
    for seg in re.split(r"[,،؛;+]", s):
        toks = []
        for w in seg.split():
            toks.append(_classify(w))
        if toks:
            segments.append(toks)
    return segments


def _classify(w: str) -> Tok:
    if w.isdigit():
        return Tok("num", int(w), w)
    if w in FILLERS:
        return Tok("fill", None, w)
    # order matters: specific vocabularies first, exact before fuzzy
    for kind, vocab in (("planet", _PLANET_V), ("sign", _SIGN_V), ("aspect", _ASPECT_V)):
        k = _lookup(w, vocab, fuzzy=False)
        if k:
            return Tok(kind, k, w)
    if _in(w, ASC_WORDS):
        return Tok("asc", None, w)
    if _in(w, LAGNA_WORDS):
        return Tok("lagna", None, w)
    if _in(w, VEDIC_WORDS):
        return Tok("vedic", None, w)
    if _in(w, HOUSE_WORDS):
        return Tok("house", None, w)
    for v in _variants(w):
        if v in ORDINALS:
            return Tok("num", ORDINALS[v], w)
    if _in(w, WEEKLY_WORDS):
        return Tok("weekly", None, w)
    if _in(w, DAILY_WORDS):
        return Tok("daily", None, w)
    if w in ("و", "w"):
        return Tok("fill", None, w)
    for kind, vocab in (("planet", _PLANET_V), ("sign", _SIGN_V), ("aspect", _ASPECT_V)):
        k = _lookup(w, vocab, fuzzy=True)
        if k:
            return Tok(kind, k, w)
    return Tok("word", None, w)


@dataclass(frozen=True)
class Place:
    system: str          # western | vedic
    category: str        # planet_in_sign | planet_in_house | ascendant_in_sign | aspect | lagna_in_sign
    keys: tuple

    @property
    def key_str(self) -> str:
        return ":".join(str(k) for k in self.keys)


@dataclass
class Parsed:
    intent: str                       # place | weekly | daily | empty | unknown
    places: list[Place] = field(default_factory=list)
    signs: list[str] = field(default_factory=list)


def parse(query: str) -> Parsed:
    if not normalize(query):
        return Parsed("empty")
    segs = tokenize(query)
    toks_all = [t for s in segs for t in s]
    vedic = any(t.kind == "vedic" for t in toks_all)
    places: list[Place] = []
    lone_signs: list[str] = []
    for seg in segs:
        ts = [t for t in seg if t.kind not in ("fill", "word", "vedic", "daily", "weekly")]
        i = 0
        while i < len(ts):
            t = ts[i]
            nxt = ts[i + 1] if i + 1 < len(ts) else None
            nn = ts[i + 2] if i + 2 < len(ts) else None
            if t.kind == "planet":
                if nxt and nxt.kind == "aspect" and nn and nn.kind == "planet" and nn.value != t.value:
                    places.append(Place("western", "aspect", (t.value, nn.value, nxt.value)))
                    i += 3
                    continue
                if nxt and nxt.kind == "sign":
                    places.append(Place("western", "planet_in_sign", (t.value, nxt.value)))
                    i += 2
                    continue
                if nxt and nxt.kind == "house":
                    if nn and nn.kind == "num" and 1 <= nn.value <= 12:
                        places.append(Place("western", "planet_in_house", (t.value, str(nn.value))))
                        i += 3
                        continue
                if nxt and nxt.kind == "num" and 1 <= nxt.value <= 12:
                    nn_house = nn is not None and nn.kind == "house"
                    places.append(Place("western", "planet_in_house", (t.value, str(nxt.value))))
                    i += 3 if nn_house else 2
                    continue
                i += 1
                continue
            if t.kind in ("asc", "lagna"):
                if nxt and nxt.kind == "sign":
                    ved = t.kind == "lagna" or vedic
                    places.append(Place("vedic", "lagna_in_sign", (nxt.value,)) if ved
                                  else Place("western", "ascendant_in_sign", (nxt.value,)))
                    i += 2
                    continue
                i += 1
                continue
            if t.kind == "sign":
                if nxt and nxt.kind in ("asc", "lagna"):           # "aries rising", "الحمل طالع"
                    ved = nxt.kind == "lagna" or vedic
                    places.append(Place("vedic", "lagna_in_sign", (t.value,)) if ved
                                  else Place("western", "ascendant_in_sign", (t.value,)))
                    i += 2
                    continue
                lone_signs.append(t.value)
            i += 1
    places = list(dict.fromkeys(places))[:MAX_PLACES]
    if places:
        return Parsed("place", places=places)
    if any(t.kind == "weekly" for t in toks_all):
        return Parsed("weekly")
    if lone_signs or any(t.kind == "daily" for t in toks_all):
        return Parsed("daily", signs=list(dict.fromkeys(lone_signs))[:2])
    return Parsed("unknown")


# ───────────────────────── texts ─────────────────────────

TX = {
    "ar": {
        "chart_btn": "🔭 اعرف خارطتك كاملة", "week_btn": "🔓 اعرف التفاصيل في التطبيق", "open": "🔭 افتح الخيميائي",
        "daily_title": "{g} {s} · برج اليوم", "daily_head": "{g} <b>برج {s}</b> · {d}",
        "my_title": "✨ برجك اليوم: {s}", "my_desc": "حسب خارطتك المحفوظة",
        "daily_none_t": "أبراج اليوم لسا ما نزلت", "daily_none_d": "جرّب بعد شوي",
        "daily_none_m": "🌅 أبراج اليوم لسا ما نزلت. منحطها كل يوم بالبوت، جرّب بعد شوي.",
        "pair_title": "💞 {a} و{b} · توافق سريع",
        "elem": "{a}: {ea} · {ma}\n{b}: {eb} · {mb}",
        "week_title": "🗓 الاختيارات الفلكية لأسبوع {r}",
        "week_desc": "أفضل أوقات الأسبوع للبدايات والعقود والسفر، مجانية بالتطبيق",
        "week_lines": "فيه {top} للبدايات، و{avoid} يُفضّل ما تبدأ فيها شي جديد.",
        "week_suits": "مناسبة هالأسبوع لـ: {s}.", "week_more": "الأوقات الدقيقة بتوقيتك، مجاناً بالتطبيق 👇",
        "week_none_t": "الاختيارات الأسبوعية لسا ما نزلت", "week_none_d": "منحطها بالتطبيق أول ما تجهز",
        "week_none_m": "🗓 الاختيارات الفلكية لهالأسبوع لسا ما نزلت. أول ما تجهز بتلاقيها بالتطبيق مجاناً.",
        "sum_title": "📜 ملخّص {n} مواقع", "disclaimer": "للتسلية والتأمل، مش نصيحة طبية أو مالية أو قانونية",
        "impossible": "هالزاوية مستحيلة فلكياً", "impossible_why": "{a} و{b} ما بيبعدوا عن بعض بالسما قد زاوية {x}، فهالزاوية ما بتصير بأي خارطة.",
        "generational": "🌐 زاوية جيلية، بتأثر على جيل كامل",
        "more": "… <a href=\"{u}\">تابع القراءة في البوت</a>",
        "unknown_t": "ما فهمت طلبك", "unknown_d": "جرّب: الأسد، أو القمر في الحمل، أو الاختيارات الأسبوعية",
        "unknown_m": "🔭 <b>الخيميائي للفلك</b>\nبرجك اليوم، الاختيارات الفلكية الأسبوعية، وتفسير المواقع الفلكية. "
                     "اكتب اسم البوت بأي محادثة وجرّب: «الأسد»، أو «القمر في الحمل».",
        "nodb_t": "التفسيرات مو جاهزة هلأ", "nodb_d": "جرّب بعد شوي",
        "missing_t": "ما لقيت تفسير لهالموقع", "missing_d": "جرّب صيغة تانية",
        "tz_label": "بتوقيت {c}",
    },
    "en": {
        "chart_btn": "🔭 Get your full chart", "week_btn": "🔓 See the details in the app", "open": "🔭 Open The Alchemist",
        "daily_title": "{g} {s} · today's horoscope", "daily_head": "{g} <b>{s}</b> · {d}",
        "my_title": "✨ Your horoscope today: {s}", "my_desc": "Based on your saved chart",
        "daily_none_t": "Today's horoscopes aren't out yet", "daily_none_d": "Try again in a little while",
        "daily_none_m": "🌅 Today's horoscopes aren't out yet. They land in the bot every day; try again shortly.",
        "pair_title": "💞 {a} & {b} · quick compatibility",
        "elem": "{a}: {ea} · {ma}\n{b}: {eb} · {mb}",
        "week_title": "🗓 Electional picks for the week {r}",
        "week_desc": "The week's best windows for beginnings, contracts and travel, free in the app",
        "week_lines": "{top} for new beginnings, and {avoid} when it's better not to start anything new.",
        "week_suits": "This week favours: {s}.", "week_more": "Exact times in your time zone, free in the app 👇",
        "week_none_t": "This week's picks aren't out yet", "week_none_d": "They'll be in the app as soon as they're ready",
        "week_none_m": "🗓 This week's electional picks aren't out yet. They'll be free in the app as soon as they're ready.",
        "sum_title": "📜 Summary of {n} placements", "disclaimer": "For reflection and fun, not medical, financial or legal advice",
        "impossible": "This aspect is astronomically impossible",
        "impossible_why": "{a} and {b} never get {x} apart in the sky, so this aspect can't occur in any chart.",
        "generational": "🌐 A generational aspect, shared by a whole generation",
        "more": "… <a href=\"{u}\">Continue reading in the bot</a>",
        "unknown_t": "I didn't get that", "unknown_d": "Try: Leo, Moon in Aries, or weekly picks",
        "unknown_m": "🔭 <b>The Alchemist Astro</b>\nToday's horoscope, weekly electional picks and astrological placements explained. "
                     "Type the bot's name in any chat and try “Leo” or “Moon in Aries”.",
        "nodb_t": "Interpretations aren't ready right now", "nodb_d": "Try again shortly",
        "missing_t": "No interpretation for that placement", "missing_d": "Try another wording",
        "tz_label": "{c} time",
    },
}
CITY_AR = {"Damascus": "دمشق", "Beirut": "بيروت", "Amman": "عمّان", "Baghdad": "بغداد", "Riyadh": "الرياض",
           "Dubai": "دبي", "Cairo": "القاهرة", "Istanbul": "إسطنبول", "Moscow": "موسكو", "Berlin": "برلين",
           "London": "لندن", "Paris": "باريس", "Kuwait": "الكويت", "Qatar": "قطر", "Muscat": "مسقط",
           "Jerusalem": "القدس", "Gaza": "غزة", "Hebron": "الخليل", "Tunis": "تونس", "Algiers": "الجزائر",
           "Casablanca": "الدار البيضاء", "Stockholm": "ستوكهولم", "Amsterdam": "أمستردام", "Vienna": "فيينا",
           "New_York": "نيويورك", "Toronto": "تورونتو", "Erbil": "أربيل", "Bahrain": "البحرين"}


def _esc(s: str) -> str:
    return html.escape(s or "", quote=False)


def tx(lang: str, key: str, **kw) -> str:
    s = TX.get(lang, TX["ar"])[key]
    return s.format(**kw) if kw else s


def deep_link(intent: str) -> str:
    return f"https://t.me/{settings.bot_username}?start=inline_{intent}"


def kb(lang: str, intent: str) -> InlineKeyboardMarkup:
    text = tx(lang, "week_btn") if intent == "weekly" else tx(lang, "chart_btn")
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=deep_link(intent))]])


def fit(body: str, lang: str, intent: str, tail: str = "") -> str:
    """Keep the message within Telegram's 4096 characters, cutting at paragraph boundaries."""
    text = body + tail
    if len(text) <= MAX_TEXT:
        return text
    more = "\n\n" + tx(lang, "more", u=deep_link(intent))
    room = MAX_TEXT - len(more) - len(tail)
    paras, out = body.split("\n\n"), ""
    for p in paras:
        cand = f"{out}\n\n{p}" if out else p
        if len(cand) > room:
            break
        out = cand
    if not out:   # one huge paragraph: cut at a word, never inside a tag
        out = re.sub(r"<[^>]*$", "", body[:room].rsplit(" ", 1)[0])
    return out + more + tail


def _plain(s: str, n: int = 120) -> str:
    s = re.sub(r"<[^>]+>", "", html.unescape(s or "")).replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def thumb() -> str | None:
    return f"{settings.public_url}/static/brand/avatar.jpg" if settings.public_url else None


def article(rid: str, title: str, desc: str, text: str, markup: InlineKeyboardMarkup | None) -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        id=rid[:64], title=title[:256], description=desc[:256] or None, thumbnail_url=thumb(),
        input_message_content=InputTextMessageContent(message_text=text[:MAX_TEXT], parse_mode="HTML",
                                                      link_preview_options=LinkPreviewOptions(is_disabled=True)),
        reply_markup=markup)


# ───────────────────────── (a) daily ─────────────────────────

def tz_label(tz: str, lang: str) -> str:
    city = tz.split("/")[-1]
    if lang == "ar":
        city = CITY_AR.get(city, city.replace("_", " "))
    else:
        city = "UTC" if tz == "UTC" else city.replace("_", " ")
    return tx(lang, "tz_label", c=city)


def _relabel(text: str, tz: str, lang: str) -> str:
    """Daily texts say "your time"; an inline message is read by others, so name the zone instead."""
    lab = tz_label(tz, lang)
    return text.replace("بتوقيتك", lab).replace("your time", lab)


async def daily_data(lang: str, tz: str) -> tuple[dict | None, date]:
    from .. import scheduler
    day = datetime.now(ZoneInfo(tz)).date()
    return await scheduler._content(day, lang), day


def daily_result(data: dict, day: date, key: str, lang: str, tz: str, personal: bool = False) -> InlineQueryResultArticle:
    from .. import forecasts
    i = SIGN_KEYS.index(key)
    name = SIGNS[lang][i]
    body = _relabel(forecasts.daily_sign_html(data, key, lang, tz), tz, lang)
    head = tx(lang, "daily_head", g=SIGN_GLYPH[i], s=name, d=day.strftime("%d/%m"))
    text = fit(f"{head}\n\n{body}", lang, "daily")
    short = _plain(_relabel(forecasts.daily_sign_short(data, key, lang, tz, 1), tz, lang))
    if personal:
        return article(f"daily:me:{key}:{day}:{lang}", tx(lang, "my_title", s=name), tx(lang, "my_desc") + " · " + short,
                       text, kb(lang, "daily"))
    return article(f"daily:{key}:{day}:{lang}", tx(lang, "daily_title", g=SIGN_GLYPH[i], s=name), short, text,
                   kb(lang, "daily"))


def pair_result(a: str, b: str, day: date, lang: str) -> InlineQueryResultArticle | None:
    """Short compatibility of two sun signs: element and modality, plus the compat DB's note when present."""
    from .. import interp
    ref = interp.natal.reference.get("signs") or {}
    ia, ib = SIGN_KEYS.index(a), SIGN_KEYS.index(b)
    na, nb = SIGNS[lang][ia], SIGNS[lang][ib]
    ra, rb = ref.get(a) or {}, ref.get(b) or {}
    if not (ra and rb):
        return None
    lines = [f"💞 <b>{_esc(na)} و{_esc(nb)}</b>" if lang == "ar" else f"💞 <b>{_esc(na)} &amp; {_esc(nb)}</b>",
             _esc(tx(lang, "elem", a=na, b=nb, ea=ra["element"][lang], ma=ra["modality"][lang],
                            eb=rb["element"][lang], mb=rb["modality"][lang]))]
    e = interp.compat.get("western", "sign_pair", "sun_sun", a, b) or interp.compat.get("western", "sign_pair", "sun_sun", b, a)
    desc = f"{ra['element'][lang]} + {rb['element'][lang]}"
    if e:
        d = e.get(lang) or e.get("ar") or {}
        paras = [p for p in (d.get("text") or "").split("\n\n") if "{X}" not in p and "{Y}" not in p][:2]
        lines += [_esc(p) for p in paras]
        if d.get("advice"):
            lines.append("💡 " + _esc(d["advice"]))
        desc = d.get("summary") or desc
    lines.append(f"<i>{tx(lang, 'disclaimer')}</i>")
    return article(f"daily:pair:{a}:{b}:{day}:{lang}", tx(lang, "pair_title", a=na, b=nb), _plain(desc),
                   fit("\n\n".join(lines), lang, "daily"), kb(lang, "daily"))


def none_daily(lang: str) -> InlineQueryResultArticle:
    return article(f"daily:none:{lang}", tx(lang, "daily_none_t"), tx(lang, "daily_none_d"), tx(lang, "daily_none_m"),
                   kb(lang, "daily"))


# ───────────────────────── (b) weekly teaser ─────────────────────────

def _count(n: int, what: str, lang: str) -> str:
    """Arabic number agreement: وقت مميز / وقتين مميزين / 3 أوقات مميزة …"""
    if lang == "en":
        return {"top": f"{n} standout window{'s' if n != 1 else ''}",
                "avoid": f"{n} stretch{'es' if n != 1 else ''}"}[what]
    if what == "top":
        return "وقت مميز" if n == 1 else "وقتين مميزين" if n == 2 else f"{n} أوقات مميزة" if n <= 10 else f"{n} وقت مميز"
    return "فترة" if n == 1 else "فترتين" if n == 2 else f"{n} فترات" if n <= 10 else f"{n} فترة"


def weekly_teaser(data: dict, lang: str) -> InlineQueryResultArticle:
    """Never includes windows, times, or best/avoid lists: only counts and general themes."""
    ev = data.get("events") or []
    top = sum(1 for e in ev if e.get("type") == "top_pick") or 1
    avoid = sum(1 for e in ev if e.get("type") == "void_of_course")
    suits: list[str] = []
    for e in ev:
        if e.get("tone") == "favorable":
            for s in e.get("suits") or []:
                if s not in suits and bool(_AR.search(s)) == (lang == "ar"):
                    suits.append(s)
    top_t, avoid_t = _count(top, "top", lang), _count(avoid, "avoid", lang)
    ws, we = data["week_start"], data.get("week_end") or data["week_start"]
    rng = f"{ws[8:10]}/{ws[5:7]} – {we[8:10]}/{we[5:7]}"
    lines = [f"<b>{_esc(tx(lang, 'week_title', r=rng))}</b>",
             _esc(tx(lang, "week_lines", top=top_t, avoid=avoid_t))]
    if suits:
        lines.append(_esc(tx(lang, "week_suits", s=("، " if lang == "ar" else ", ").join(suits[:4]))))
    lines.append(tx(lang, "week_more"))
    return article(f"weekly:{ws}:{lang}", tx(lang, "week_title", r=rng), tx(lang, "week_desc"),
                   "\n\n".join(lines), kb(lang, "weekly"))


def none_weekly(lang: str) -> InlineQueryResultArticle:
    return article(f"weekly:none:{lang}", tx(lang, "week_none_t"), tx(lang, "week_none_d"), tx(lang, "week_none_m"),
                   kb(lang, "weekly"))


# ───────────────────────── (c) placements ─────────────────────────

def lookup_place(p: Place) -> dict | None:
    from .. import interp
    if p.category == "aspect":
        a, b, typ = p.keys
        return interp.get_pair("western", "aspect", a, b, typ)
    return interp.get(p.system, p.category, *p.keys)


def place_title(p: Place, lang: str) -> str:
    from .. import interp
    ref = interp.natal.reference
    pl = lambda k: (ref.get("western_planets", {}).get(k) or {}).get(lang, k)       # noqa: E731
    sg = lambda k: (ref.get("signs", {}).get(k) or {}).get(lang, k)                 # noqa: E731
    if p.category == "aspect":
        a, b, typ = p.keys
        return f"{pl(a)} {(ref.get('western_aspect_types', {}).get(typ) or {}).get(lang, typ)} {pl(b)}"
    if p.category == "planet_in_sign":
        return f"{pl(p.keys[0])} {'في' if lang == 'ar' else 'in'} {sg(p.keys[1])}"
    if p.category == "planet_in_house":
        return f"{pl(p.keys[0])} {'في البيت' if lang == 'ar' else 'in house'} {p.keys[1]}"
    if p.category == "lagna_in_sign":
        return f"{'لاغنا' if lang == 'ar' else 'Lagna'} {sg(p.keys[0])}"
    return f"{'الطالع في' if lang == 'ar' else 'Ascendant in'} {sg(p.keys[0])}"


def place_result(p: Place, lang: str) -> tuple[InlineQueryResultArticle, dict | None]:
    rid = f"place:{p.system}:{p.category}:{p.key_str}:{lang}"
    e = lookup_place(p)
    if not e:
        t = place_title(p, lang)
        return article(rid, f"{t} · {tx(lang, 'missing_t')}", tx(lang, "missing_d"),
                       f"🔭 {_esc(t)}\n\n{tx(lang, 'missing_t')}", kb(lang, "place")), None
    d = e.get(lang) or e.get("ar") or {}
    extra = e.get("extra") or {}
    title = d.get("title") or place_title(p, lang)
    if p.category == "aspect" and extra.get("possible") is False:
        from .. import interp
        ref = interp.natal.reference
        a, b, _ = p.keys
        pa = (ref.get("western_planets", {}).get(a) or {}).get(lang, a)
        pb = (ref.get("western_planets", {}).get(b) or {}).get(lang, b)
        why = tx(lang, "impossible_why", a=pa, b=pb, x=f"{extra.get('angle', '')}°")
        text = f"🚫 <b>{_esc(title)}</b>\n\n{_esc(tx(lang, 'impossible'))}. {_esc(why)}"
        return article(rid, f"🚫 {title}", tx(lang, "impossible"), text, kb(lang, "place")), {"title": title,
                                                                                              "summary": tx(lang, "impossible")}
    body = "\n\n".join(_esc(x) for x in (d.get("text") or "").split("\n\n") if x.strip())
    head = f"🔭 <b>{_esc(title)}</b>"
    if extra.get("generational"):
        head += f"\n<i>{tx(lang, 'generational')}</i>"
    tail = ""
    if d.get("advice"):
        tail += f"\n\n💡 {_esc(d['advice'])}"
    tail += f"\n\n<i>{tx(lang, 'disclaimer')}</i>"
    text = fit(f"{head}\n\n{body}", lang, "place", tail)
    return article(rid, title, _plain(d.get("summary") or ""), text, kb(lang, "place")), {
        "title": title, "summary": d.get("summary") or ""}


def summary_result(items: list[dict], places: list[Place], lang: str) -> InlineQueryResultArticle:
    lines = [f"<b>{_esc(i['title'])}</b>\n{_esc(i['summary'])}" for i in items]
    text = fit("📜 " + "\n\n".join(lines), lang, "place", f"\n\n<i>{tx(lang, 'disclaimer')}</i>")
    h = hashlib.sha1("|".join(f"{p.system}:{p.category}:{p.key_str}" for p in places).encode()).hexdigest()[:16]
    return article(f"place:sum:{h}:{lang}", tx(lang, "sum_title", n=len(items)), _plain(" · ".join(i["title"] for i in items)),
                   text, kb(lang, "place"))


# ───────────────────────── personal sign & throttled logging ─────────────────────────

_user_cache: dict[int, tuple[float, tuple[str | None, str | None]]] = {}
_logged: dict[int, float] = {}


async def known_user(uid: int) -> tuple[str | None, str | None]:
    """(sign key, tz) for users already in the DB, from their daily settings or their main chart. Read only."""
    hit = _user_cache.get(uid)
    if hit and hit[0] > time.monotonic():
        return hit[1]
    sign = tz = None
    row = await db.pool().fetchrow(
        """SELECT d.sign, d.tz, (SELECT birth_date FROM profiles p WHERE p.user_id=u.id AND p.is_main LIMIT 1) bd
           FROM users u LEFT JOIN daily_prefs d ON d.user_id=u.id WHERE u.id=$1""", uid)
    if row:
        tz = row["tz"]
        if row["sign"] is not None:
            sign = SIGN_KEYS[row["sign"]]
        elif row["bd"]:
            from starlette.concurrency import run_in_threadpool

            from ..astro.engine import sun_sign
            sign = SIGN_KEYS[await run_in_threadpool(sun_sign, row["bd"].year, row["bd"].month, row["bd"].day)]
    _user_cache[uid] = (time.monotonic() + 600, (sign, tz))
    if len(_user_cache) > 5000:
        _user_cache.clear()
    return sign, tz


async def log_query(uid: int) -> None:
    """One inline_query event per user per 10 minutes: inline fires on every keystroke."""
    now = time.monotonic()
    if _logged.get(uid, 0) > now:
        return
    _logged[uid] = now + 600
    if len(_logged) > 20000:
        _logged.clear()
    try:
        await db.event(uid, "inline_query")
    except Exception as e:
        log.warning("inline_query event: %s", e)


# ───────────────────────── build & handlers ─────────────────────────

def default_tz(lang: str) -> str:
    return "Asia/Damascus" if lang == "ar" else "UTC"


async def build(query: str, uid: int, language_code: str | None) -> tuple[list, bool, str]:
    """Return (results, is_personal, lang)."""
    from .. import content, interp
    lang = detect_lang(query, language_code)
    p = parse(query)
    results: list = []
    personal = False

    if p.intent == "place":
        if not interp.ready():
            return [article(f"place:nodb:{lang}", tx(lang, "nodb_t"), tx(lang, "nodb_d"),
                            tx(lang, "unknown_m"), kb(lang, "place"))], False, lang
        items, places = [], []
        for pl in p.places:
            r, info = place_result(pl, lang)
            results.append(r)
            if info:
                items.append(info)
                places.append(pl)
        if len(items) > 1:
            results.insert(0, summary_result(items, places, lang))
        return results[:MAX_RESULTS], False, lang

    if p.intent == "weekly":
        w = await content.weekly_current(lang)
        return [weekly_teaser(w, lang) if w else none_weekly(lang)], False, lang

    if p.intent == "unknown":
        return [article(f"unknown:{lang}", tx(lang, "unknown_t"), tx(lang, "unknown_d"), tx(lang, "unknown_m"),
                        kb(lang, "daily"))], False, lang

    my_sign, my_tz = (None, None)
    if p.intent == "empty":
        my_sign, my_tz = await known_user(uid)
    tz = my_tz or default_tz(lang)
    data, day = await daily_data(lang, tz)

    if p.intent == "daily":
        if not data:
            return [none_daily(lang)], False, lang
        keys = p.signs or SIGN_KEYS
        for k in keys:
            results.append(daily_result(data, day, k, lang, tz))
        if len(p.signs) == 2:
            pr = pair_result(p.signs[0], p.signs[1], day, lang)
            if pr:
                results.append(pr)
        return results[:MAX_RESULTS], False, lang

    # empty query: personal sign, weekly teaser, then the 12 signs
    if data and my_sign:
        results.append(daily_result(data, day, my_sign, lang, tz, personal=True))
        personal = True
    w = await content.weekly_current(lang)
    results.append(weekly_teaser(w, lang) if w else none_weekly(lang))
    if data:
        results += [daily_result(data, day, k, lang, tz) for k in SIGN_KEYS]
    else:
        results.append(none_daily(lang))
    return results[:MAX_RESULTS], personal, lang


@router.inline_query()
async def on_inline(q: InlineQuery, bot: Bot):
    try:
        results, personal, lang = await build(q.query or "", q.from_user.id, q.from_user.language_code)
    except Exception:
        log.exception("inline build failed")
        results, personal, lang = [], False, detect_lang(q.query or "", q.from_user.language_code)
    button = InlineQueryResultsButton(text=tx(lang, "open"), web_app=WebAppInfo(url=f"{settings.public_url}/")) \
        if settings.public_url else None
    try:
        await q.answer(results, cache_time=0 if personal else CACHE_PUBLIC, is_personal=personal, button=button)
    except Exception as e:
        log.warning("answer_inline_query: %s", e)
    await log_query(q.from_user.id)


@router.chosen_inline_result()
async def on_chosen(r: ChosenInlineResult):
    try:
        await db.event(r.from_user.id, "inline_pick", r.result_id[:64])
    except Exception as e:
        log.warning("inline_pick event: %s", e)


__all__ = ["router", "parse", "normalize", "build", "F"]
