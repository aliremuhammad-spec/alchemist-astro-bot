import hashlib
import hmac
import json
import time
from datetime import date, datetime, timezone
from urllib.parse import urlencode

import pytest

from app.astro.engine import BirthInput, compute, nakshatra_of, vimshottari
from app.auth import validate_init_data
from app.content import parse_daily
from app.scheduler import digest_messages

TOKEN = "123456:TEST"


def signed(user_id=42, age=0, token=TOKEN, tamper=False):
    data = {"auth_date": str(int(time.time()) - age), "query_id": "q",
            "user": json.dumps({"id": user_id, "first_name": "A"})}
    check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    data["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if tamper:
        data["user"] = json.dumps({"id": 999, "first_name": "A"})
    return urlencode(data)


def test_initdata_valid():
    assert validate_init_data(signed(), TOKEN)["user"]["id"] == 42


@pytest.mark.parametrize("kw", [{"tamper": True}, {"age": 2 * 86400}, {"token": "999:OTHER"}])
def test_initdata_rejects(kw):
    with pytest.raises(ValueError):
        validate_init_data(signed(**kw), TOKEN)


def _signs(v="x"):
    keys = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
            "sagittarius", "capricorn", "aquarius", "pisces"]
    return {k: v for k in keys}


def test_parse_daily_shapes():
    d = date(2026, 12, 1)
    assert d in parse_daily({"date": "2026-12-01", "signs": _signs()})
    assert d in parse_daily({"days": [{"date": "2026-12-01", "signs": _signs()}]})
    assert d in parse_daily({"2026-12-01": _signs()})
    assert parse_daily({"date": "2026-12-01", "signs": {"aries": "x"}}) == {}  # incomplete day rejected
    ar = {"الحمل": "a", "الثور": "a", "الجوزاء": "a", "السرطان": "a", "الأسد": "a", "العذراء": "a",
          "الميزان": "a", "العقرب": "a", "القوس": "a", "الجدي": "a", "الدلو": "a", "الحوت": "a"}
    assert d in parse_daily({"date": "2026-12-01", "signs": ar})


def test_digest_splits_under_telegram_limit():
    data = parse_daily({"date": "2026-12-01", "signs": _signs("نص " * 300)})[date(2026, 12, 1)]
    msgs = digest_messages("ar", date(2026, 12, 1), data)
    assert len(msgs) > 1 and all(len(m) <= 4096 for m in msgs)


def test_nakshatra_boundaries():
    assert nakshatra_of(0)["name"] == "Ashwini" and nakshatra_of(0)["pada"] == 1
    assert nakshatra_of(359.99)["name"] == "Revati" and nakshatra_of(359.99)["pada"] == 4


def test_dasha_reference_chart():
    # Moon 219.06° (Anuradha, Saturn) for 1995-05-15 → Saturn balance ~10.8y, Ketu maha 2023-2030
    d = vimshottari(219.06, datetime(1995, 5, 15, 11, 30, tzinfo=timezone.utc),
                    at=datetime(2026, 11, 26, tzinfo=timezone.utc))
    assert d["maha"]["lord"] == "ketu" and d["maha"]["start"].startswith("2023")
    assert 10.5 < d["balance_years_at_birth"] < 11


def test_reference_positions():
    c = compute(BirthInput("T", 1995, 5, 15, 14, 30, True, 33.5138, 36.2765, "Asia/Damascus"))
    w, v = c["western"], c["vedic"]
    assert w["points"]["sun"]["sign"] == 1 and abs(w["points"]["sun"]["deg"] - 24.18) < 0.02
    assert w["asc"]["sign"] == 5 and abs(w["asc"]["deg"] - 22.81) < 0.05
    assert v["lagna"]["sign"] == 4 and abs(v["lagna"]["deg"] - 29.01) < 0.05
    assert v["points"]["moon"]["house"] == 4 and v["moon_nakshatra"]["name"] == "Anuradha"


def test_unknown_time_has_no_angles():
    c = compute(BirthInput("T", 1995, 5, 15, 0, 0, False, 33.5, 36.3, "Asia/Damascus"))
    assert c["western"]["asc"] is None and c["vedic"]["lagna"] is None
    assert all(p["house"] is None for p in c["western"]["points"].values())


def test_vargas_reference():
    from app.astro.vargas import varga_sign, varga_chart, VARGAS
    # Navamsha: Taurus 0°23' -> Capricorn; Scorpio 9°04' -> Virgo; Leo 29° -> Sagittarius
    assert varga_sign(9, 30 + 0.38) == 9
    assert varga_sign(9, 210 + 9.06) == 5
    assert varga_sign(9, 120 + 29.0) == 8
    # Hora: odd sign first half -> Leo, even sign first half -> Cancer
    assert varga_sign(2, 5) == 4 and varga_sign(2, 35) == 3
    # Trimshamsha: odd sign 0-5° -> Aries, even sign 0-5° -> Taurus
    assert varga_sign(30, 2) == 0 and varga_sign(30, 32) == 1
    # Shashtiamsha last part of Aries -> Aries + 59 = Pisces (59 % 12 = 11)
    assert varga_sign(60, 29.9) == 11
    c = compute(BirthInput("T", 1995, 5, 15, 14, 30, True, 33.5138, 36.2765, "Asia/Damascus"))
    for n in VARGAS:
        vc = varga_chart(c, n)
        assert all(0 <= p["sign"] < 12 for p in vc["points"].values())


def test_synastry_score():
    from app.astro.synastry import compute_synastry, synastry_text
    a = BirthInput("A", 1995, 5, 15, 14, 30, True, 33.51, 36.27, "Asia/Damascus")
    b = BirthInput("B", 1993, 8, 2, 9, 10, False, 33.89, 35.5, "Asia/Beirut")
    s = compute_synastry(a, b)
    assert s["score"]["value"] >= 0 and s["aspects"]
    assert all(x["b"] not in ("ascendant", "medium_coeli") for x in s["aspects"])  # B has no birth time
    assert "التوافق" in synastry_text(s, "ar")


def test_yoga_detection_basic():
    from app.report.yogas import detect
    # Cancer lagna; Sun+Mercury+Saturn in Aries (10th), Mars in Libra (4th), Jupiter in Pisces (9th)
    signs = {"sun": 0, "moon": 10, "mars": 6, "mercury": 0, "jupiter": 11, "venus": 2,
             "saturn": 0, "rahu": 3, "ketu": 9}
    keys = {k for k, _ in detect(signs, 3)}
    assert {"budha_aditya", "yogakaraka", "neecha_bhanga", "kuja_dosha"} <= keys
    assert "gajakesari" not in keys


def test_report_html_without_db():
    from app import interp
    from app.astro.engine import BirthInput, compute
    from app.report.builder import Report
    interp.load_for_tests({"meta": {}, "entries": [
        {"id": "W.planet_in_sign.sun.taurus", "system": "western", "category": "planet_in_sign", "k1": "sun",
         "k2": "taurus", "k3": None, "tone": "neutral", "ar_title": "الشمس في الثور", "ar_summary": "ثبات",
         "ar_text": "نص", "ar_advice": None, "en_title": "Sun in Taurus", "en_summary": "s", "en_text": "t",
         "en_advice": None, "extra": {}}]})
    c = compute(BirthInput("T", 1999, 5, 11, 10, 45, True, 33.51, 36.29, "Asia/Damascus"))
    h = Report(c, "ar").html()
    assert "الشمس في الثور" in h and 'dir="rtl"' in h


def test_daily_markdown_localised():
    from pathlib import Path

    from app import forecasts as F
    from app.scheduler import digest_messages, user_messages
    md = (Path(__file__).parent / "fixtures" / "daily-forecast.md").read_text(encoding="utf-8")
    days = F.parse_daily_md(md)
    (day, data), = days.items()
    assert len(data["signs"]) == 12
    damascus = F.daily_sign_html(data, "aries", "ar", "Asia/Damascus")
    assert "17:29 بتوقيتك" in damascus and "دبي" not in damascus      # Dubai 18:29 -> Damascus (UTC+3)
    assert "نصيحة اليوم: نصيحة" not in damascus                        # duplicated label removed
    assert all(len(x) <= 4096 for x in user_messages("ar", 0, day, data, "Asia/Damascus"))
    assert all(len(x) <= 4096 for x in digest_messages("ar", day, data, "Europe/Berlin"))


def test_weekly_markdown_localised():
    from pathlib import Path

    from app import forecasts as F
    md = (Path(__file__).parent / "fixtures" / "weekly-elections.md").read_text(encoding="utf-8")
    w = F.parse_weekly_md(md)
    assert w["week_start"] == "2026-11-27" and w["events"]
    for tz in ("Asia/Damascus", "America/New_York", "Asia/Tokyo"):
        v = str(F.weekly_view(w, tz))
        assert "دبي" not in v and "UTC" not in v and "`" not in v
    top = next(s for s in F.weekly_view(w, "Asia/Damascus")["sections"] if s["title"].startswith("أهم"))
    assert "14:21 (السبت 28/11)" in top["html"]                        # 11:21Z -> Damascus 14:21


def test_github_urls():
    from app import forecasts as F
    u = "https://github.com/the-alchemist-astro/astro-forecasts/blob/main/daily-forecast.md"
    assert F.gh_raw(u) == "https://raw.githubusercontent.com/the-alchemist-astro/astro-forecasts/main/daily-forecast.md"
    assert F.gh_api(u) == "https://api.github.com/repos/the-alchemist-astro/astro-forecasts/contents/daily-forecast.md?ref=main"
