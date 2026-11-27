"""Inline mode: normalisation, intent detection, placements, limits and the weekly teaser.
Uses a tiny synthetic interpretation payload (the real DB is private and not in the repo)."""
import asyncio
import re

import pytest

from app import interp
from app.bot import inline as il


def _e(eid, system, category, k1, k2=None, k3=None, extra=None, text="فقرة أولى.\n\nفقرة تانية."):
    return {"id": eid, "system": system, "category": category, "k1": k1, "k2": k2, "k3": k3, "tone": None,
            "ar": {"title": f"عنوان {eid}", "summary": f"ملخص {eid}", "text": text, "advice": "نصيحة"},
            "en": {"title": f"Title {eid}", "summary": f"Summary {eid}", "text": text, "advice": "Advice"},
            "extra": extra or {}}


REF = {"signs": {k: {"ar": a, "en": e, "element": {"ar": "نار", "en": "Fire"}, "modality": {"ar": "ثابت", "en": "Fixed"}}
                 for k, a, e in zip(il.SIGN_KEYS, il.SIGNS["ar"], il.SIGNS["en"])},
       "western_planets": {"sun": {"ar": "الشمس", "en": "Sun"}, "moon": {"ar": "القمر", "en": "Moon"},
                           "mercury": {"ar": "عطارد", "en": "Mercury"}, "uranus": {"ar": "أورانوس", "en": "Uranus"},
                           "neptune": {"ar": "نبتون", "en": "Neptune"}},
       "western_aspect_types": {"square": {"ar": "تربيع", "en": "Square"}, "trine": {"ar": "تثليث", "en": "Trine"}}}


@pytest.fixture(autouse=True)
def fake_db():
    interp.natal.load_payload({"meta": {}, "reference": REF, "entries": [
        _e("W.pis.moon.leo", "western", "planet_in_sign", "moon", "leo"),
        _e("W.pis.sun.scorpio", "western", "planet_in_sign", "sun", "scorpio"),
        _e("W.pih.sun.8", "western", "planet_in_house", "sun", "8"),
        _e("W.pih.moon.4", "western", "planet_in_house", "moon", "4"),
        _e("W.asc.capricorn", "western", "ascendant_in_sign", "capricorn"),
        _e("W.asp.sun.moon.square", "western", "aspect", "sun", "moon", "square", {"possible": True, "angle": 90}),
        _e("W.asp.sun.mercury.square", "western", "aspect", "sun", "mercury", "square", {"possible": False, "angle": 90}),
        _e("W.asp.uranus.neptune.trine", "western", "aspect", "uranus", "neptune", "trine",
           {"possible": True, "generational": True}),
        _e("V.lagna.leo", "vedic", "lagna_in_sign", "leo"),
        _e("W.pis.venus.pisces", "western", "planet_in_sign", "venus", "pisces", text=("كلمة " * 400 + "\n\n") * 6),
    ]})
    yield
    interp.natal.load_payload({"meta": {}, "reference": {}, "entries": []})


# ── normalisation ──

@pytest.mark.parametrize("word,key", [
    ("الأسد", "leo"), ("اسد", "leo"), ("الجوزاء", "gemini"), ("جوزا", "gemini"), ("العذرا", "virgo"),
    ("الجَدْي", "capricorn"), ("Sagitarius", "sagittarius"), ("aquarious", "aquarius"), ("Pices", "pisces"),
    ("بالأسد", "leo"), ("LEO", "leo"), ("الحـــوت", "pisces")])
def test_sign_names(word, key):
    assert il.sign_key(word) == key


@pytest.mark.parametrize("word,key", [
    ("الشمس", "sun"), ("القمر", "moon"), ("الزهرة", "venus"), ("الزهره", "venus"), ("المشترى", "jupiter"),
    ("والشمس", "sun"), ("Jupitor", "jupiter"), ("Mercury", "mercury"), ("يورانوس", "uranus")])
def test_planet_names(word, key):
    assert il.planet_key(word) == key


def test_normalize_unifies_letters_and_digits():
    assert il.normalize("إأآ ة ى ٨ ۴ ـــ") == "ااا ه ي 8 4"


# ── intent ──

@pytest.mark.parametrize("q,intent", [
    ("الأسد", "daily"), ("leo", "daily"), ("حمل ميزان", "daily"), ("برج اليوم", "daily"), ("horoscope", "daily"),
    ("القمر في الأسد", "place"), ("الشمس تربيع القمر", "place"), ("الطالع في الجدي", "place"),
    ("Aries rising", "place"), ("venus in house 7", "place"), ("الشمس في البيت الثامن", "place"),
    ("القمر في بيت ٤", "place"), ("لاغنا الأسد", "place"),
    ("الاختيارات الأسبوعية", "weekly"), ("weekly picks", "weekly"), ("اختيارات الأسبوع", "weekly"),
    ("", "empty"), ("   ", "empty"), ("كيفك شو الأخبار", "unknown")])
def test_intent(q, intent):
    assert il.parse(q).intent == intent


def test_lone_sign_vs_placement():
    assert il.parse("الأسد").signs == ["leo"]
    p = il.parse("القمر في الأسد")
    assert p.places == [il.Place("western", "planet_in_sign", ("moon", "leo"))]


def test_two_signs():
    assert il.parse("حمل ميزان").signs == ["aries", "libra"]


def test_houses_and_ascendant():
    assert il.parse("الشمس في البيت الثامن").places[0].keys == ("sun", "8")
    assert il.parse("Moon in the 4th house").places[0].keys == ("moon", "4")
    assert il.parse("الطالع في الجدي").places[0] == il.Place("western", "ascendant_in_sign", ("capricorn",))
    assert il.parse("فيدي طالع الأسد").places[0] == il.Place("vedic", "lagna_in_sign", ("leo",))


def test_aspect_parsing():
    p = il.parse("الشمس تربيع القمر").places[0]
    assert p.category == "aspect" and p.keys == ("sun", "moon", "square")
    assert il.parse("sun semi-square moon").places[0].keys[2] == "semisquare"
    assert il.parse("الشمس نصف تسديس القمر").places[0].keys[2] == "semisextile"


def test_multiple_placements():
    p = il.parse("القمر في الأسد، الشمس في العقرب")
    assert [x.keys for x in p.places] == [("moon", "leo"), ("sun", "scorpio")]
    p = il.parse("القمر في الأسد والشمس في العقرب")
    assert [x.keys for x in p.places] == [("moon", "leo"), ("sun", "scorpio")]
    many = "، ".join(["القمر في الأسد", "الشمس في العقرب", "القمر في الحمل", "الشمس في الثور",
                     "القمر في الثور", "الشمس في الجدي", "القمر في الحوت", "الشمس في الحوت"])
    assert len(il.parse(many).places) == il.MAX_PLACES


# ── results ──

def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def test_place_results_and_summary(monkeypatch):
    res, personal, lang = _run(il.build("القمر في الأسد، الشمس في العقرب", 1, "ar"))
    assert lang == "ar" and not personal and len(res) == 3
    assert res[0].id.startswith("place:sum:")
    assert res[1].id == "place:western:planet_in_sign:moon:leo:ar"
    msg = res[1].input_message_content.message_text
    assert "💡 نصيحة" in msg and "للتسلية والتأمل" in msg and res[1].description == "ملخص W.pis.moon.leo"
    assert res[1].reply_markup.inline_keyboard[0][0].url.endswith("?start=inline_place")


def test_impossible_and_generational():
    res, _, _ = _run(il.build("الشمس تربيع عطارد", 1, "ar"))
    assert "مستحيلة فلكياً" in res[0].input_message_content.message_text
    assert "فقرة" not in res[0].input_message_content.message_text
    res, _, _ = _run(il.build("Uranus trine Neptune", 1, "ar"))
    assert res[0].id.endswith(":en") and "generational" in res[0].input_message_content.message_text


def test_length_limit():
    res, _, _ = _run(il.build("الزهرة في الحوت", 1, "ar"))
    text = res[0].input_message_content.message_text
    assert len(text) <= il.MAX_TEXT and "تابع القراءة في البوت" in text and "للتسلية" in text


def test_fit_never_cuts_inside_a_tag():
    out = il.fit("<b>" + "x " * 5000 + "</b>", "ar", "daily")
    assert len(out) <= il.MAX_TEXT and not re.search(r"<[^>]*$", out.split("…")[0])


def test_result_ids_are_short_and_stable():
    for q in ("القمر في الأسد، الشمس في العقرب، الشمس تربيع القمر", "Uranus trine Neptune"):
        res, _, _ = _run(il.build(q, 1, "ar"))
        assert all(len(r.id.encode()) <= 64 for r in res)
        res2, _, _ = _run(il.build(q, 2, "en"))
        assert [r.id for r in res] == [r.id for r in res2]


def test_unknown_query():
    res, _, _ = _run(il.build("كيفك شو الأخبار", 1, "ar"))
    assert len(res) == 1 and res[0].title == "ما فهمت طلبك"


def test_language_from_text_then_client():
    assert il.detect_lang("leo", "ar") == "en"
    assert il.detect_lang("الأسد", "en") == "ar"
    assert il.detect_lang("", "en") == "en" and il.detect_lang("", None) == "ar"


DAILY = {"format": "md", "date": "2026-11-28", "overview": [],
         "signs": {k: {"parts": [{"k": "general", "label": "", "text": f"نهار {k} حلو. جملة تانية. الساعة 15:00 بتوقيت دبي."}]}
                   for k in il.SIGN_KEYS}}
WEEKLY = {"format": "md", "week_start": "2026-11-27", "week_end": "2026-12-03", "sections": [
    {"title": "أهم اختيار هالأسبوع", "body": "- **من `2026-11-28T11:21Z` إلى `2026-11-29T05:30Z` UTC**: سر الأسبوع"}],
    "events": [{"type": "top_pick", "start_utc": "2026-11-28T11:21Z"},
               {"type": "void_of_course", "tone": "avoid_new_starts", "start_utc": "2026-11-28T05:40Z"},
               {"type": "nakshatra", "tone": "favorable", "suits": ["السفر", "الدراسة"], "start_utc": "2026-11-28T07:20Z"}]}


def _patch_content(monkeypatch, daily=DAILY, weekly=WEEKLY, user=(None, None)):
    from app import content, scheduler

    async def _content(day, lang="ar"):
        return daily

    async def _weekly(lang="ar"):
        return weekly

    async def _known(uid):
        return user
    monkeypatch.setattr(scheduler, "_content", _content)
    monkeypatch.setattr(content, "weekly_current", _weekly)
    monkeypatch.setattr(il, "known_user", _known)


def test_weekly_teaser_never_has_details(monkeypatch):
    _patch_content(monkeypatch)
    res, _, _ = _run(il.build("الاختيارات الأسبوعية", 1, "ar"))
    msg = res[0].input_message_content.message_text
    assert "27/11 – 03/12" in res[0].title and "السفر" in msg
    assert not re.search(r"\d{1,2}:\d{2}", msg) and "سر الأسبوع" not in msg and "UTC" not in msg
    assert res[0].reply_markup.inline_keyboard[0][0].url.endswith("?start=inline_weekly")


def test_weekly_missing(monkeypatch):
    _patch_content(monkeypatch, weekly=None)
    res, _, _ = _run(il.build("weekly", 1, "en"))
    assert res[0].id == "weekly:none:en"


def test_daily_one_and_two_signs(monkeypatch):
    _patch_content(monkeypatch)
    res, _, _ = _run(il.build("الأسد", 1, "ar"))
    assert len(res) == 1 and "leo" in res[0].id
    msg = res[0].input_message_content.message_text
    assert "بتوقيت دمشق" in msg and "بتوقيتك" not in msg
    res, _, _ = _run(il.build("حمل ميزان", 1, "ar"))
    assert len(res) == 3 and res[2].id.startswith("daily:pair:aries:libra")


def test_daily_not_loaded(monkeypatch):
    _patch_content(monkeypatch, daily=None)
    res, _, _ = _run(il.build("الأسد", 1, "ar"))
    assert len(res) == 1 and "لسا ما نزلت" in res[0].title


def test_empty_query_unregistered_user(monkeypatch):
    _patch_content(monkeypatch)
    res, personal, _ = _run(il.build("", 999, "ar"))
    assert not personal and res[0].id.startswith("weekly:") and len(res) == 13


def test_empty_query_known_user_is_personal(monkeypatch):
    _patch_content(monkeypatch, user=("scorpio", "Europe/Berlin"))
    res, personal, _ = _run(il.build("", 5, "ar"))
    assert personal and res[0].id.startswith("daily:me:scorpio") and len(res) == 14
    assert "بتوقيت برلين" in res[0].input_message_content.message_text


def test_no_personal_data_in_messages(monkeypatch):
    _patch_content(monkeypatch, user=("scorpio", "Europe/Berlin"))
    res, _, _ = _run(il.build("", 5, "ar"))
    for r in res:
        assert not re.search(r"\b(19|20)\d{2}-\d{2}-\d{2}\b", r.input_message_content.message_text)
