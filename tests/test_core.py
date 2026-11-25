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
