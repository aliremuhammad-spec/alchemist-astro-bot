"""Ashtakoota (Guna Milan, 36 points) and Manglik check from two sidereal charts.

Convention: the first chart is read as the groom and the second as the bride (the classical tables are
directional for Varna, Vashya, Tara, Yoni and Gana). Inputs are Moon sidereal sign (0-11), Moon nakshatra (0-26)
and the Moon's sidereal longitude (for the half-sign Vashya splits).
"""
from __future__ import annotations

from ..report.yogas import LORDS
from .names import SIGN_KEYS

# Varna by Moon sign: Brahmin 4, Kshatriya 3, Vaishya 2, Shudra 1
VARNA = {0: 3, 1: 2, 2: 1, 3: 4, 4: 3, 5: 2, 6: 1, 7: 4, 8: 3, 9: 2, 10: 1, 11: 4}
VARNA_NAMES = {4: ("براهمن", "Brahmin"), 3: ("كشاتريا", "Kshatriya"), 2: ("فايشيا", "Vaishya"), 1: ("شودرا", "Shudra")}

# Vashya groups: 0 quadruped, 1 human, 2 water, 3 wild (Leo), 4 insect (Scorpio)
VASHYA_NAMES = [("رباعي", "Quadruped"), ("إنساني", "Human"), ("مائي", "Water"), ("بري", "Wild"), ("حشري", "Insect")]
VASHYA_TABLE = [  # groom row, bride column
    [2, 1, 1, 0.5, 1],
    [1, 2, 0.5, 0, 1],
    [1, 0.5, 2, 1, 1],
    [0.5, 0, 1, 2, 0],
    [1, 1, 1, 0, 2],
]


def vashya_group(lon: float) -> int:
    s, d = int(lon // 30) % 12, lon % 30
    if s in (0, 1):
        return 0
    if s == 8:
        return 1 if d < 15 else 0
    if s == 9:
        return 0 if d < 15 else 2
    if s in (2, 5, 6, 10):
        return 1
    if s in (3, 11):
        return 2
    if s == 4:
        return 3
    return 4  # scorpio


YONI_ANIMALS = ["horse", "elephant", "sheep", "serpent", "dog", "cat", "rat", "cow", "buffalo", "tiger", "deer",
                "monkey", "mongoose", "lion"]
YONI_AR = {"horse": "حصان", "elephant": "فيل", "sheep": "خروف", "serpent": "أفعى", "dog": "كلب", "cat": "قط",
           "rat": "فأر", "cow": "بقرة", "buffalo": "جاموس", "tiger": "نمر", "deer": "غزال", "monkey": "قرد",
           "mongoose": "نمس", "lion": "أسد"}
NAK_YONI = ["horse", "elephant", "sheep", "serpent", "serpent", "dog", "cat", "sheep", "cat", "rat", "rat", "cow",
            "buffalo", "tiger", "buffalo", "tiger", "deer", "deer", "dog", "monkey", "mongoose", "monkey", "lion",
            "horse", "lion", "cow", "elephant"]
YONI_TABLE = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1],
    [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
    [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
    [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
    [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4],
]

FRIENDS = {
    "sun": {"f": {"moon", "mars", "jupiter"}, "e": {"venus", "saturn"}},
    "moon": {"f": {"sun", "mercury"}, "e": set()},
    "mars": {"f": {"sun", "moon", "jupiter"}, "e": {"mercury"}},
    "mercury": {"f": {"sun", "venus"}, "e": {"moon"}},
    "jupiter": {"f": {"sun", "moon", "mars"}, "e": {"mercury", "venus"}},
    "venus": {"f": {"mercury", "saturn"}, "e": {"sun", "moon"}},
    "saturn": {"f": {"mercury", "venus"}, "e": {"sun", "moon", "mars"}},
}


def _rel(a: str, b: str) -> str:
    return "f" if b in FRIENDS[a]["f"] else "e" if b in FRIENDS[a]["e"] else "n"


def maitri_points(la: str, lb: str) -> float:
    if la == lb:
        return 5
    key = "".join(sorted(_rel(la, lb) + _rel(lb, la)))
    return {"ff": 5, "fn": 4, "nn": 3, "ef": 1, "en": 0.5, "ee": 0}[key]


# Gana: 0 deva, 1 manushya, 2 rakshasa
NAK_GANA = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]
GANA_NAMES = [("ديفا (إلهي)", "Deva"), ("مانوشيا (إنساني)", "Manushya"), ("راكشاسا (حاد)", "Rakshasa")]
GANA_TABLE = [[6, 6, 1], [5, 6, 0], [1, 0, 6]]  # groom row, bride column
NADI_NAMES = [("آدي", "Adi"), ("مادهيا", "Madhya"), ("أنتيا", "Antya")]


def nadi_of(nak: int) -> int:
    return [0, 1, 2, 2, 1, 0][nak % 6]


KOOTAS = [  # key, max, ar name, en name, ar meaning, en meaning
    ("varna", 1, "فارنا", "Varna", "الانسجام بالقيم والطموح الروحي ونظرة كل طرف للدور والمسؤولية.",
     "Harmony of values, spiritual outlook and sense of role."),
    ("vashya", 2, "فاشيا", "Vashya", "التأثير المتبادل والانجذاب، ومين بيلين للتاني بسهولة.",
     "Mutual influence and attraction; how easily each yields to the other."),
    ("tara", 3, "تارا", "Tara", "الحظ والراحة بالحياة المشتركة، محسوبة من نكشترا القمر عند الطرفين.",
     "Fortune and well-being of the shared life, from both Moon nakshatras."),
    ("yoni", 4, "يوني", "Yoni", "التوافق الجسدي والغريزي والطبع اليومي.",
     "Physical and instinctive compatibility, everyday temperament."),
    ("maitri", 5, "غراها مايتري", "Graha Maitri", "الصداقة الذهنية: مدى تفاهم سيدي برجي القمر.",
     "Mental friendship: how well the two Moon-sign lords get along."),
    ("gana", 6, "غانا", "Gana", "الطبع والمزاج الأساسي وطريقة التعامل مع الخلاف.",
     "Basic nature and temper; how conflict is handled."),
    ("bhakoot", 7, "بهاكوت", "Bhakoot", "الانسجام العاطفي والمادي والأسري على المدى الطويل.",
     "Long-term emotional, financial and family harmony."),
    ("nadi", 8, "نادي", "Nadi", "التوازن الصحي والطاقي ونسل العائلة؛ أعلى كوتا وزنًا.",
     "Health, energy balance and progeny; the most weighted koota."),
]


def ashtakoota(a: dict, b: dict) -> dict:
    """a/b: {"moon_lon": float (sidereal), "moon_nak": int}. a = groom, b = bride."""
    sa, sb = int(a["moon_lon"] // 30) % 12, int(b["moon_lon"] // 30) % 12
    na, nb = a["moon_nak"], b["moon_nak"]
    pts: dict[str, float] = {}
    detail: dict[str, dict] = {}

    va, vb = VARNA[sa], VARNA[sb]
    pts["varna"] = 1 if va >= vb else 0
    detail["varna"] = {"a": VARNA_NAMES[va], "b": VARNA_NAMES[vb]}

    ga, gb = vashya_group(a["moon_lon"]), vashya_group(b["moon_lon"])
    pts["vashya"] = VASHYA_TABLE[ga][gb]
    detail["vashya"] = {"a": VASHYA_NAMES[ga], "b": VASHYA_NAMES[gb]}

    def tara_ok(frm: int, to: int) -> bool:
        return ((to - frm) % 27 + 1) % 9 not in (3, 5, 7)
    pts["tara"] = 1.5 * tara_ok(nb, na) + 1.5 * tara_ok(na, nb)
    detail["tara"] = {}

    ya, yb = NAK_YONI[na], NAK_YONI[nb]
    pts["yoni"] = YONI_TABLE[YONI_ANIMALS.index(ya)][YONI_ANIMALS.index(yb)]
    detail["yoni"] = {"a": (YONI_AR[ya], ya.title()), "b": (YONI_AR[yb], yb.title())}

    la, lb = LORDS[SIGN_KEYS[sa]], LORDS[SIGN_KEYS[sb]]
    pts["maitri"] = maitri_points(la, lb)
    detail["maitri"] = {"a": la, "b": lb}

    gna, gnb = NAK_GANA[na], NAK_GANA[nb]
    pts["gana"] = GANA_TABLE[gna][gnb]
    detail["gana"] = {"a": GANA_NAMES[gna], "b": GANA_NAMES[gnb]}

    d1, d2 = (sb - sa) % 12 + 1, (sa - sb) % 12 + 1
    bad = {frozenset((2, 12)), frozenset((5, 9)), frozenset((6, 8))}
    pts["bhakoot"] = 0 if frozenset((d1, d2)) in bad else 7
    detail["bhakoot"] = {"pair": f"{d1}/{d2}"}

    nda, ndb = nadi_of(na), nadi_of(nb)
    pts["nadi"] = 0 if nda == ndb else 8
    detail["nadi"] = {"a": NADI_NAMES[nda], "b": NADI_NAMES[ndb]}

    total = round(sum(pts.values()), 1)
    verdict = "excellent" if total >= 33 else "good" if total >= 25 else "average" if total >= 18 else "low"
    doshas = []
    if pts["nadi"] == 0:
        doshas.append("nadi")
    if pts["bhakoot"] == 0:
        doshas.append("bhakoot")
    if pts["gana"] == 0:
        doshas.append("gana")
    return {"total": total, "max": 36, "verdict": verdict, "points": pts, "detail": detail, "doshas": doshas,
            "kootas": [{"key": k, "max": m, "ar": ar, "en": en, "about_ar": aa, "about_en": ae, "points": pts[k]}
                       for k, m, ar, en, aa, ae in KOOTAS]}


def manglik(chart: dict) -> dict:
    """Mars in 1,2,4,7,8,12 from lagna (if time known) and from the Moon."""
    v = chart["vedic"]
    mars, moon = v["points"]["mars"]["sign"], v["points"]["moon"]["sign"]
    houses = (1, 2, 4, 7, 8, 12)
    from_moon = (mars - moon) % 12 + 1
    from_lagna = (mars - v["lagna"]["sign"]) % 12 + 1 if v.get("lagna") else None
    return {"from_lagna": from_lagna, "from_moon": from_moon,
            "lagna": from_lagna in houses if from_lagna else None, "moon": from_moon in houses,
            "is": bool((from_lagna in houses) if from_lagna else False) or from_moon in houses}
