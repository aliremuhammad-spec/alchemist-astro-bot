"""Synastry between two birth charts (western, tropical)."""
from __future__ import annotations

from html import escape

from kerykeion import ChartDataFactory

from .engine import BirthInput, _subject
from .names import ASPECTS, MAJOR_ASPECTS, PLANETS

_SKIP = {"mean_south_lunar_node", "true_south_lunar_node", "descendant", "imum_coeli"}

RULES_AR = {
    "destiny_sign": "برجا الشمس من نفس الصفة (كاردينال/ثابت/متحول)",
    "sun_sun": "اتصال بين الشمسين", "sun_moon": "اتصال بين الشمس والقمر",
    "sun_ascendant": "اتصال الشمس بالطالع", "moon_ascendant": "اتصال القمر بالطالع",
    "venus_mars": "اتصال الزهرة بالمريخ", "moon_moon": "اتصال بين القمرين",
}
LEVELS_AR = {"Minimal": "ضعيف", "Medium": "متوسط", "Important": "مهم", "Very Important": "مهم جداً",
             "Exceptional": "استثنائي", "Rare Exceptional": "نادر واستثنائي"}


def _name(key: str, lang: str) -> str:
    if key in PLANETS:
        return PLANETS[key][1 if lang == "ar" else 2]
    return {"ascendant": ("الطالع", "Asc"), "medium_coeli": ("MC", "MC")}.get(key, (key, key))[0 if lang == "ar" else 1]


def compute_synastry(a: BirthInput, b: BirthInput) -> dict:
    sa = _subject(a, False, a.hour if a.time_known else 12, a.minute if a.time_known else 0)
    sb = _subject(b, False, b.hour if b.time_known else 12, b.minute if b.time_known else 0)
    data = ChartDataFactory.create_synastry_chart_data(sa, sb)
    aspects = []
    for x in data.aspects:
        k1, k2 = x.p1_name.lower(), x.p2_name.lower()
        if k1 in _SKIP or k2 in _SKIP or x.aspect not in MAJOR_ASPECTS:
            continue
        if (not a.time_known and k1 in ("ascendant", "medium_coeli")) or (not b.time_known and k2 in ("ascendant", "medium_coeli")):
            continue
        aspects.append({"a": k1, "b": k2, "type": x.aspect, "orb": round(abs(x.orbit), 2)})
    aspects.sort(key=lambda z: z["orb"])
    rs = data.relationship_score
    score = {"value": rs.score_value, "level": rs.score_description,
             "breakdown": [{"rule": r.rule, "points": r.points, "details": r.details} for r in rs.score_breakdown]}
    return {"names": [a.name, b.name], "aspects": aspects, "score": score,
            "elements": {k: getattr(data.element_distribution, f"{k}_percentage") for k in ("fire", "earth", "air", "water")},
            "_data": data}


def synastry_text(s: dict, lang: str) -> str:
    a, b = (escape(n or "—") for n in s["names"])
    sc = s["score"]
    if lang == "ar":
        out = [f"💞 <b>التوافق بين {a} و{b}</b>",
               f"المؤشر: <b>{sc['value']}</b> · {LEVELS_AR.get(sc['level'], sc['level'])}", ""]
        for r in sc["breakdown"]:
            out.append(f"• {RULES_AR.get(r['rule'], r['details'])} (+{r['points']})")
        out += ["", f"<b>أقوى الاتصالات</b> <i>(كوكب {a} ← كوكب {b})</i>"]
    else:
        out = [f"💞 <b>Synastry: {a} & {b}</b>", f"Score: <b>{sc['value']}</b> · {sc['level']}", ""]
        for r in sc["breakdown"]:
            out.append(f"• {r['details']} (+{r['points']})")
        out += ["", f"<b>Closest aspects</b> <i>({a}'s planet → {b}'s planet)</i>"]
    for x in s["aspects"][:16]:
        g, ar, en = ASPECTS[x["type"]]
        out.append(f"{_name(x['a'], lang)} {g} {_name(x['b'], lang)} — {ar if lang == 'ar' else en} "
                   f"(‎{x['orb']:.1f}‎°‎)")
    return "\n".join(out)
