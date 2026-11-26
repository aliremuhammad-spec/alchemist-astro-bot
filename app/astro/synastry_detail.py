"""Premium synastry: themed western inter-aspects, house overlays, element balance, and the vedic layer
(Ashtakoota + Manglik). Pure computation; texts live in the UI/report."""
from __future__ import annotations

from .ashtakoota import ashtakoota, manglik
from .engine import BirthInput, compute

THEMES = [  # key, planets that define the theme, ar, en, ar about, en about
    ("attraction", {"venus", "mars"}, "الانجذاب والرغبة", "Attraction & desire",
     "اتصالات الزهرة والمريخ: الكيمياء والجاذبية وطريقة التعبير عن الرغبة.",
     "Venus–Mars contacts: chemistry, magnetism and how desire is expressed."),
    ("emotions", {"moon"}, "المشاعر والأمان", "Emotions & safety",
     "اتصالات القمر: الراحة العاطفية والشعور بالبيت والأمان مع بعض.",
     "Moon contacts: emotional ease, feeling at home and safe together."),
    ("communication", {"mercury"}, "التواصل والتفاهم", "Communication",
     "اتصالات عطارد: الحوار وطريقة التفكير وحل الخلافات بالكلام.",
     "Mercury contacts: conversation, ways of thinking and talking things through."),
    ("identity", {"sun"}, "الهوية والدعم", "Identity & support",
     "اتصالات الشمس: كيف كل طرف بيشوف التاني وبيدعم حضوره وأهدافه.",
     "Sun contacts: how each sees the other and supports their goals."),
    ("commitment", {"saturn"}, "الالتزام والاستمرار", "Commitment",
     "اتصالات زحل: الثبات والمسؤولية، وأحيانًا الثقل أو الحذر.",
     "Saturn contacts: stability and responsibility, sometimes weight or caution."),
    ("growth", {"jupiter"}, "النمو والكرم", "Growth & generosity",
     "اتصالات المشتري: التفاؤل والدعم والتوسع المشترك.",
     "Jupiter contacts: optimism, support and growing together."),
    ("transformation", {"uranus", "neptune", "pluto"}, "التحول والعمق", "Transformation",
     "اتصالات الكواكب البعيدة: الإثارة والمثالية والتغيير العميق، بإيجابياتها وتحدياتها.",
     "Outer-planet contacts: excitement, idealism and deep change, with gifts and challenges."),
]
HARD = {"square", "opposition"}
SOFT = {"trine", "sextile"}
HEAVY = {"saturn", "mars", "pluto", "uranus"}
OVERLAY_POINTS = ["sun", "moon", "venus", "mars", "mercury", "jupiter", "saturn"]


def nature(a: str, b: str, kind: str) -> str:
    if kind in SOFT:
        return "soft"
    if kind in HARD:
        return "hard"
    return "intense" if {a, b} & HEAVY else "soft"


def themes(aspects: list[dict]) -> list[dict]:
    out = []
    for key, planets, ar, en, about_ar, about_en in THEMES:
        if key == "attraction":
            items = [x for x in aspects if x["a"] in planets and x["b"] in planets]
        else:
            items = [x for x in aspects if x["a"] in planets or x["b"] in planets]
        soft = sum(1 for x in items if x["nature"] == "soft")
        hard = sum(1 for x in items if x["nature"] == "hard")
        intense = sum(1 for x in items if x["nature"] == "intense")
        total = soft + hard + intense
        score = round(100 * (soft + 0.5 * intense) / total) if total else None
        out.append({"key": key, "ar": ar, "en": en, "about_ar": about_ar, "about_en": about_en,
                    "soft": soft, "hard": hard, "intense": intense, "score": score,
                    "aspects": sorted(items, key=lambda z: z["orb"])[:6]})
    return out


def _house_of(lon: float, cusps: list[float]) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        span = (b - a) % 360
        if (lon - a) % 360 < span:
            return i + 1
    return 12


def overlays(owner: dict, guest: dict) -> list[dict] | None:
    """Guest's planets in the owner's houses (needs the owner's birth time)."""
    cusps = owner["western"]["houses"]
    if not cusps:
        return None
    return [{"planet": k, "house": _house_of(guest["western"]["points"][k]["abs"], cusps)} for k in OVERLAY_POINTS]


def detail(a_in: BirthInput, b_in: BirthInput, base: dict) -> dict:
    """base = compute_synastry() result (western inter-aspects + kerykeion score)."""
    ca, cb = compute(a_in), compute(b_in)
    asp = [{**x, "nature": nature(x["a"], x["b"], x["type"])} for x in base["aspects"]
           if x["a"] not in ("ascendant", "medium_coeli") and x["b"] not in ("ascendant", "medium_coeli")]
    soft = sum(1 for x in asp if x["nature"] == "soft")
    hard = sum(1 for x in asp if x["nature"] == "hard")
    va, vb = ca["vedic"], cb["vedic"]
    ak = ashtakoota({"moon_lon": va["points"]["moon"]["abs"], "moon_nak": va["moon_nakshatra"]["index"]},
                    {"moon_lon": vb["points"]["moon"]["abs"], "moon_nak": vb["moon_nakshatra"]["index"]})
    ma, mb = manglik(ca), manglik(cb)
    return {
        "western": {
            "themes": themes(asp), "aspects": asp[:40], "soft": soft, "hard": hard,
            "elements": [ca["western"]["elements"], cb["western"]["elements"]],
            "overlays_ab": overlays(ca, cb), "overlays_ba": overlays(cb, ca),
            "time_known": [ca["meta"]["time_known"], cb["meta"]["time_known"]],
            "signs": [{k: ca["western"]["points"][k]["sign"] for k in ("sun", "moon", "venus", "mars")},
                      {k: cb["western"]["points"][k]["sign"] for k in ("sun", "moon", "venus", "mars")}],
        },
        "vedic": {
            "ashtakoota": ak,
            "manglik": [ma, mb],
            "manglik_balanced": ma["is"] == mb["is"],
            "moon": [{"sign": va["points"]["moon"]["sign"], "nak": va["moon_nakshatra"]},
                     {"sign": vb["points"]["moon"]["sign"], "nak": vb["moon_nakshatra"]}],
        },
        "_charts": (ca, cb),
    }
