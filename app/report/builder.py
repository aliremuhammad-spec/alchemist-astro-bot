"""Automated natal report: chart data + interpretation database -> branded PDF (WeasyPrint)."""
from __future__ import annotations

import base64
import html
from datetime import date
from pathlib import Path

from .. import interp
from ..astro.names import (DASHA_NAMES, NAKSHATRAS, PLANETS, SIGN_GLYPH, SIGN_KEYS, SIGNS, VEDIC_NAMES)
from ..astro.render import indian_svg, svg_to_png, western_wheel_svg
from ..astro.vargas import varga_chart
from .yogas import detect

HERE = Path(__file__).parent
W_PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
V_KEYS = {"sun": "sun", "moon": "moon", "mars": "mars", "mercury": "mercury", "jupiter": "jupiter",
          "venus": "venus", "saturn": "saturn", "mean_north_lunar_node": "rahu", "mean_south_lunar_node": "ketu"}
V_ORDER = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
V_GLYPH = {"rahu": "☊", "ketu": "☋"}
ASPECT_KEY = {"semi-sextile": "semisextile", "semi-square": "semisquare"}
VARGAS_IN_REPORT = (9, 10)

T = {
    "ar": {
        "title": "تقرير الخارطة الفلكية", "brand": "الخيميائي", "prepared": "أُعدّ في",
        "born": "الميلاد", "place": "المكان", "time_unknown": "وقت الميلاد غير معروف",
        "sun": "الشمس", "moon": "القمر", "asc": "الطالع", "lagna": "اللاغنا (فيدي)", "nak": "نكشترا القمر",
        "contents": "محتوى التقرير",
        "part_w": "الفلك الغربي", "part_w_sub": "الأبراج الاستوائية وبيوت بلاسيدوس",
        "part_v": "الفلك الفيدي", "part_v_sub": "الأبراج النجمية (لاهيري) والبيوت بالبرج الكامل",
        "asc_h": "الطالع: الواجهة والجسد وطريقة الدخول إلى الحياة", "planets_h": "الكواكب في الأبراج والبيوت",
        "aspects_h": "الجوانب بين الكواكب", "balance_h": "توازن العناصر والطبائع",
        "in_sign": "في البرج", "in_house": "في البيت", "house": "البيت", "retro": "متراجع",
        "advice": "نصيحة",
        "lagna_h": "اللاغنا", "nak_h": "نكشترا الطالع", "grahas_h": "الكواكب التسعة حسب الطالع",
        "table_h": "مواقع الكواكب", "yogas_h": "اليوغات المكتشفة", "conj_h": "الاقترانات",
        "drishti_h": "النظرات (دريشتي)", "vargas_h": "الخرائط التقسيمية", "dasha_h": "أدوار الدشا (فمشوتاري)",
        "planet": "الكوكب", "sign": "البرج", "degree": "الدرجة", "nakshatra": "النكشترا", "pada": "الربع",
        "maha": "الدشا الكبرى الحالية", "antar": "الدشا الفرعية", "from": "من", "to": "إلى",
        "no_yogas": "لم تُكتشف يوغات من القائمة المعتمدة.",
        "moon_lagna": "وقت الميلاد غير معروف، فاعتُمد برج القمر طالعًا (تشاندرا لاغنا). مواضع البيوت تقريبية، "
                      "وأُسقطت الخرائط التقسيمية لأنها تحتاج وقتًا دقيقًا.",
        "w_no_time": "وقت الميلاد غير معروف: حُسبت المواقع لمنتصف النهار، فلا طالع ولا بيوت في القسم الغربي.",
        "fire": "نار", "earth": "تراب", "air": "هواء", "water": "ماء",
        "cardinal": "كاردينال", "fixed": "ثابت", "mutable": "متحول",
        "closing_h": "قبل أن تُغلق التقرير",
        "closing": "الخارطة لا تحكم عليك، بل تصف المواد التي تعمل بها. اقرأ ما يتكرر في أكثر من قسم، "
                   "فهو الأوضح في حياتك. وما لا يشبهك اليوم قد يتضح في دور كوكبي لاحق.",
        "method": "طريقة الحساب",
        "method_txt": "حُسبت المواقع بمكتبة Swiss Ephemeris عبر Kerykeion. الغربي: استوائي، بيوت بلاسيدوس. "
                      "الفيدي: نجمي بأيانامشا لاهيري وبيوت البرج الكامل والعقد المتوسطة. "
                      "النصوص من قاعدة تفسيرات الخيميائي (الإصدار {v}).",
        "follow": "تابعنا", "page": "صفحة",
        "tone": {"strong": "قوي", "very_favorable": "مواتٍ جدًا", "favorable": "مواتٍ", "supportive": "داعم",
                 "neutral": "محايد", "mixed": "مختلط", "challenging": "يتطلب وعيًا", "difficult": "صعب"},
    },
    "en": {
        "title": "Natal Chart Report", "brand": "The Alchemist", "prepared": "Prepared on",
        "born": "Born", "place": "Place", "time_unknown": "Birth time unknown",
        "sun": "Sun", "moon": "Moon", "asc": "Ascendant", "lagna": "Lagna (Vedic)", "nak": "Moon nakshatra",
        "contents": "In this report",
        "part_w": "Western astrology", "part_w_sub": "Tropical zodiac, Placidus houses",
        "part_v": "Vedic astrology", "part_v_sub": "Sidereal zodiac (Lahiri), whole-sign houses",
        "asc_h": "Ascendant: persona, body and approach to life", "planets_h": "Planets in signs and houses",
        "aspects_h": "Aspects between planets", "balance_h": "Elements and modalities",
        "in_sign": "in sign", "in_house": "in house", "house": "House", "retro": "retrograde",
        "advice": "Advice",
        "lagna_h": "Lagna", "nak_h": "Ascendant nakshatra", "grahas_h": "The nine grahas by lagna",
        "table_h": "Planetary positions", "yogas_h": "Detected yogas", "conj_h": "Conjunctions",
        "drishti_h": "Aspects (drishti)", "vargas_h": "Divisional charts", "dasha_h": "Dasha periods (Vimshottari)",
        "planet": "Planet", "sign": "Sign", "degree": "Degree", "nakshatra": "Nakshatra", "pada": "Pada",
        "maha": "Current mahadasha", "antar": "Antardasha", "from": "From", "to": "To",
        "no_yogas": "No yogas from the supported list were detected.",
        "moon_lagna": "Birth time unknown: the Moon sign is used as lagna (Chandra lagna). House placements are "
                      "approximate and divisional charts are omitted because they need an exact time.",
        "w_no_time": "Birth time unknown: positions cast for noon, so no Ascendant or houses in the western part.",
        "fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water",
        "cardinal": "Cardinal", "fixed": "Fixed", "mutable": "Mutable",
        "closing_h": "Before you close this report",
        "closing": "A chart does not judge you; it describes the material you work with. Notice what repeats "
                   "across sections: that is the clearest thread. What feels unlike you today may surface in a "
                   "later planetary period.",
        "method": "Method",
        "method_txt": "Positions from the Swiss Ephemeris via Kerykeion. Western: tropical, Placidus. Vedic: "
                      "sidereal Lahiri, whole-sign houses, mean nodes. Texts from The Alchemist interpretation "
                      "database (v{v}).",
        "follow": "Follow us", "page": "Page",
        "tone": {"strong": "Strong", "very_favorable": "Very favorable", "favorable": "Favorable",
                 "supportive": "Supportive", "neutral": "Neutral", "mixed": "Mixed",
                 "challenging": "Needs awareness", "difficult": "Difficult"},
    },
}
TONE_CLASS = {"strong": "good", "very_favorable": "good", "favorable": "good", "supportive": "good",
              "neutral": "calm", "mixed": "mixed", "challenging": "hard", "difficult": "hard"}


TEXT_VS = "\ufe0e"


def tvs(s: str) -> str:
    """Force text (not emoji) presentation for astrological glyphs."""
    return "".join(ch + TEXT_VS if 0x2600 <= ord(ch) <= 0x26FF else ch for ch in s)


def e(s) -> str:
    return html.escape(str(s or ""))


def paras(text: str | None) -> str:
    if not text:
        return ""
    return "".join(f"<p>{e(p.strip())}</p>" for p in text.split("\n") if p.strip())


def ltr(s: str) -> str:
    return f'<span class="ltr">\u2066{e(s)}\u2069</span>'


def dms(deg: float) -> str:
    d = int(deg)
    m = int(round((deg - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"{d}°{m:02d}′"


def png_uri(svg: str, width: int = 1400) -> str:
    png = svg_to_png(svg, width)
    if not png:
        return ""
    return "data:image/png;base64," + base64.b64encode(png).decode()


class Report:
    def __init__(self, chart: dict, lang: str = "ar", style: str = "north"):
        self.c = chart
        self.lang = "ar" if lang == "ar" else "en"
        self.t = T[self.lang]
        self.style = style if style in ("north", "south") else "north"

    # ---------- helpers ----------
    def loc(self, d: dict | None, field: str) -> str:
        return ((d or {}).get(self.lang) or {}).get(field) or ""

    def sign(self, idx: int) -> str:
        return SIGNS[self.lang][idx % 12]

    def pname(self, key: str) -> str:
        if key in ("rahu", "ketu"):
            return {"rahu": ("راهو", "Rahu"), "ketu": ("كيتو", "Ketu")}[key][self.lang == "en"]
        return PLANETS[key][1 if self.lang == "ar" else 2]

    def glyph(self, key: str) -> str:
        return V_GLYPH.get(key) or PLANETS[key][0]

    def pill(self, tone: str | None) -> str:
        if not tone or tone not in self.t["tone"]:
            return ""
        return f'<span class="pill {TONE_CLASS[tone]}">{e(self.t["tone"][tone])}</span>'

    def entry(self, d: dict | None, glyph: str = "", meta: str = "", full: bool = True, cls: str = "") -> str:
        if not d:
            return ""
        title = self.loc(d, "title")
        out = [f'<article class="entry {cls}">',
               '<header class="eh">',
               f'<span class="glyph">{tvs(e(glyph))}</span>' if glyph else "",
               f'<h4>{e(title)}</h4>{self.pill(d.get("tone"))}</header>']
        if meta:
            out.append(f'<div class="meta">{meta}</div>')
        summary = self.loc(d, "summary")
        if summary:
            out.append(f'<p class="summary">{e(summary)}</p>')
        if full:
            out.append(f'<div class="body">{paras(self.loc(d, "text"))}</div>')
            adv = self.loc(d, "advice")
            if adv:
                out.append(f'<aside class="advice"><b>{self.t["advice"]}</b> {e(adv)}</aside>')
        out.append("</article>")
        return "".join(out)

    # ---------- sections ----------
    def cover(self) -> str:
        m, w, v, t = self.c["meta"], self.c["western"], self.c["vedic"], self.t
        y, mo, d = m["local"][:10].split("-")
        when = f"{int(d)}/{int(mo)}/{y}" + (f" · {m['local'][11:]}" if m["time_known"] else "")
        big = [(t["sun"], self.sign(w["points"]["sun"]["sign"]), SIGN_GLYPH[w["points"]["sun"]["sign"]]),
               (t["moon"], self.sign(w["points"]["moon"]["sign"]), SIGN_GLYPH[w["points"]["moon"]["sign"]])]
        if w["asc"]:
            big.append((t["asc"], self.sign(w["asc"]["sign"]), SIGN_GLYPH[w["asc"]["sign"]]))
        if v["lagna"]:
            big.append((t["lagna"], self.sign(v["lagna"]["sign"]), SIGN_GLYPH[v["lagna"]["sign"]]))
        nk = v["moon_nakshatra"]
        big.append((t["nak"], nk["name_ar"] if self.lang == "ar" else nk["name"], "✶"))
        cells = "".join(f'<div class="bt"><span class="btg">{g_}</span><span class="btl">{e(l)}</span>'
                        f'<span class="btv">{e(val)}</span></div>' for l, val, g_ in ((a, b, tvs(c)) for a, b, c in big))
        place = ", ".join(x for x in (m.get("city"), m.get("country")) if x)
        unknown = f'<p class="cv-warn">{t["time_unknown"]}</p>' if not m["time_known"] else ""
        return f"""
<section class="cover">
  <div class="cv-brand">{t['brand']}</div>
  {SIGIL}
  <div class="cv-kicker">{t['title']}</div>
  <h1 class="cv-name">{e(m['name'])}</h1>
  <div class="cv-data"><span>{t['born']}: {ltr(when)}</span><span>{t['place']}: {e(place)}</span></div>
  {unknown}
  <div class="bigthree">{cells}</div>
</section>"""

    def contents(self) -> str:
        t = self.t
        items_w = [t["asc_h"] if self.c["meta"]["time_known"] else None, t["planets_h"], t["aspects_h"], t["balance_h"]]
        items_v = [t["lagna_h"], t["table_h"], t["grahas_h"], t["yogas_h"], t["conj_h"], t["drishti_h"],
                   t["vargas_h"] if self.c["meta"]["time_known"] else None, t["dasha_h"]]

        def lst(xs):
            return "".join(f"<li>{e(x)}</li>" for x in xs if x)
        wheel = png_uri(western_wheel_svg(self.c, "light"))
        img = f'<img class="wheel" src="{wheel}">' if wheel else ""
        return f"""
<section class="contents">
  <h2 class="ch">{t['contents']}</h2>
  {img}
  <div class="toc"><div><h3>{t['part_w']}</h3><ul>{lst(items_w)}</ul></div>
  <div><h3>{t['part_v']}</h3><ul>{lst(items_v)}</ul></div></div>
</section>"""

    def opener(self, title: str, sub: str, numeral: str) -> str:
        return f'<section class="opener"><div class="op-num">{numeral}</div><h2>{e(title)}</h2><p>{e(sub)}</p></section>'

    def western(self) -> str:
        w, t = self.c["western"], self.t
        tk = self.c["meta"]["time_known"]
        out = [self.opener(t["part_w"], t["part_w_sub"], "I"), '<section class="part" data-part="w">']
        if tk and w["asc"]:
            s = SIGN_KEYS[w["asc"]["sign"]]
            d = interp.get("western", "ascendant_in_sign", s)
            out.append(f'<h2 class="sh">{t["asc_h"]}</h2>')
            out.append(self.entry(d, SIGN_GLYPH[w["asc"]["sign"]], ltr(dms(w["asc"]["deg"])) + " " + e(self.sign(w["asc"]["sign"]))))
            secs = ((d or {}).get("extra") or {}).get("sections") or {}
            if secs:
                labels = {"ar": {"persona": "الانطباع", "look": "الملامح", "strengths": "نقاط القوة",
                                 "challenges": "التحديات", "career": "العمل", "love": "الحب", "health": "الصحة"},
                          "en": {"persona": "Persona", "look": "Look", "strengths": "Strengths",
                                 "challenges": "Challenges", "career": "Career", "love": "Love", "health": "Health"}}[self.lang]
                cells = "".join(f'<div class="facet"><b>{labels.get(k, k)}</b><span>{e(v.get(self.lang))}</span></div>'
                                for k, v in secs.items())
                out.append(f'<div class="facets">{cells}</div>')
        else:
            out.append(f'<p class="note">{t["w_no_time"]}</p>')

        out.append(f'<h2 class="sh">{t["planets_h"]}</h2>')
        for p in W_PLANETS:
            pt = w["points"].get(p)
            if not pt:
                continue
            sk = SIGN_KEYS[pt["sign"]]
            meta = f'{ltr(dms(pt["deg"]))} {e(self.sign(pt["sign"]))}'
            if tk and pt.get("house"):
                meta += f' · {t["house"]} {pt["house"]}'
            if pt.get("retro"):
                meta += f' · <span class="retro">{t["retro"]} ℞</span>'
            block = [f'<div class="planet">', self.entry(interp.get("western", "planet_in_sign", p, sk), PLANETS[p][0], meta)]
            if tk and pt.get("house"):
                block.append(self.entry(interp.get("western", "planet_in_house", p, pt["house"]), "", "", cls="sub"))
            block.append("</div>")
            out.append("".join(block))

        # aspects among the ten planets, canonical key order, tightest first
        asp = []
        for a in w["aspects"]:
            p1, p2 = a["p1"], a["p2"]
            if p1 not in W_PLANETS or p2 not in W_PLANETS:
                continue
            k1, k2 = sorted((p1, p2), key=W_PLANETS.index)
            d = interp.get("western", "aspect", k1, k2, ASPECT_KEY.get(a["type"], a["type"]))
            if d:
                asp.append((a, k1, k2, d))
        if asp:
            out.append(f'<h2 class="sh">{t["aspects_h"]}</h2><div class="cols">')
            for a, k1, k2, d in asp[:16]:
                g = f"{PLANETS[k1][0]} {PLANETS[k2][0]}"
                out.append(self.entry(d, g, f'orb {ltr(f"{a["orb"]:.1f}°")}', cls="compact"))
            out.append("</div>")

        out.append(f'<h2 class="sh">{t["balance_h"]}</h2><div class="balance">')
        for group, keys in (("elements", ("fire", "earth", "air", "water")), ("qualities", ("cardinal", "fixed", "mutable"))):
            rows = "".join(
                f'<div class="bar"><span class="bl">{t[k]}</span><span class="track"><span class="fill {k}" '
                f'style="width:{max(2, w[group][k])}%"></span></span><span class="bv">{ltr(f"{w[group][k]:.0f}%")}</span></div>'
                for k in keys)
            out.append(f'<div class="bars">{rows}</div>')
        out.append("</div></section>")
        return "".join(out)

    def vedic(self) -> str:
        v, t = self.c["vedic"], self.t
        tk = self.c["meta"]["time_known"] and v["lagna"]
        signs = {V_KEYS[k]: p["sign"] for k, p in v["points"].items()}
        L = v["lagna"]["sign"] if tk else signs["moon"]
        lk = SIGN_KEYS[L]
        house = {p: (s - L) % 12 + 1 for p, s in signs.items()}
        out = [self.opener(t["part_v"], t["part_v_sub"], "II"), '<section class="part" data-part="v">']
        if not tk:
            out.append(f'<p class="note">{t["moon_lagna"]}</p>')

        out.append(f'<h2 class="sh">{t["lagna_h"]}</h2>')
        meta = e(self.sign(L)) + (f' {ltr(dms(v["lagna"]["deg"]))}' if tk else "")
        out.append(self.entry(interp.get("vedic", "lagna_in_sign", lk), SIGN_GLYPH[L], meta))
        if tk:
            nk = v["lagna"]["nakshatra"]
            key = NAKSHATRAS[nk["index"]][0].lower().replace(" ", "_")
            d = interp.get("vedic", "lagna_in_nakshatra", key)
            if d:
                pada = (((d.get("extra") or {}).get("padas") or {}).get(str(nk["pada"])) or {}).get(self.lang)
                out.append(self.entry(d, "✶", f'{t["pada"]} {nk["pada"]}'))
                if pada:
                    out.append(f'<aside class="advice pada">{e(pada)}</aside>')

        d1 = png_uri(indian_svg(self.c, self.style, self.lang, "light"), 1200)
        rows = []
        for k, p in v["points"].items():
            g = V_KEYS[k]
            nk = p["nakshatra"]
            rows.append((V_ORDER.index(g),
                         f'<tr><td>{tvs(self.glyph(g))} {e(self.pname(g))}'
                         f'{" ℞" if p["retro"] and g not in ("rahu", "ketu") else ""}</td>'
                         f'<td>{e(self.sign(p["sign"]))}</td><td>{ltr(dms(p["deg"]))}</td><td>{house[g]}</td>'
                         f'<td>{e(nk["name_ar"] if self.lang == "ar" else nk["name"])} · {nk["pada"]}</td></tr>'))
        table = "".join(r for _, r in sorted(rows))
        out.append(f'<h2 class="sh">{t["table_h"]}</h2><div class="d1">'
                   + (f'<img src="{d1}">' if d1 else "")
                   + f'<table class="pos"><thead><tr><th>{t["planet"]}</th><th>{t["sign"]}</th><th>{t["degree"]}</th>'
                     f'<th>{t["house"]}</th><th>{t["nakshatra"]}</th></tr></thead><tbody>{table}</tbody></table></div>')

        out.append(f'<h2 class="sh">{t["grahas_h"]}</h2>')
        for g in V_ORDER:
            d = interp.get("vedic", "planet_in_house_by_lagna", lk, g, house[g])
            meta = f'{e(self.sign(signs[g]))} · {t["house"]} {house[g]}'
            out.append(self.entry(d, self.glyph(g), meta))

        out.append(f'<h2 class="sh">{t["yogas_h"]}</h2>')
        found = [interp.get("vedic", "yoga", k) for k, _ in detect(signs, L)]
        found = [d for d in found if d]
        if found:
            out.append('<div class="cols">' + "".join(self.entry(d, "✧", cls="compact") for d in found) + "</div>")
        else:
            out.append(f'<p class="note">{t["no_yogas"]}</p>')

        conj = []
        for i, a in enumerate(V_ORDER):
            for b in V_ORDER[i + 1:]:
                if signs[a] == signs[b] and {a, b} != {"rahu", "ketu"}:
                    d = interp.get_pair("vedic", "conjunction", a, b)
                    if d:
                        conj.append(self.entry(d, f"{self.glyph(a)} {self.glyph(b)}", cls="compact"))
        if conj:
            out.append(f'<h2 class="sh">{t["conj_h"]}</h2><div class="cols">{"".join(conj)}</div>')

        dr = []
        for a in V_ORDER:
            for off in interp.offsets_for(a):
                tgt = (signs[a] + off - 1) % 12
                for b in V_ORDER:
                    if b != a and signs[b] == tgt:
                        d = interp.get("vedic", "drishti", a, b, off)
                        if d:
                            dr.append(f'<tr><td>{tvs(self.glyph(a))} ← {tvs(self.glyph(b))}</td><td>{e(self.loc(d, "title"))}</td>'
                                      f'<td>{e(self.loc(d, "summary"))}</td><td>{self.pill(d.get("tone"))}</td></tr>')
        if dr:
            out.append(f'<h2 class="sh">{t["drishti_h"]}</h2><table class="drishti"><tbody>{"".join(dr)}</tbody></table>')

        if tk:
            for i, n in enumerate(VARGAS_IN_REPORT):
                vc = varga_chart(self.c, n)
                code = f"D{n}"
                intro = interp.get("vedic", "varga", code)
                img = png_uri(indian_svg(self.c, self.style, self.lang, "light", varga=vc), 1000)
                out.append('<div class="varga">' + (f'<h2 class="sh">{t["vargas_h"]}</h2>' if i == 0 else ""))
                out.append(self.entry(intro, code, e(self.sign(vc["lagna"])) if vc["lagna"] is not None else "", cls="varga-intro"))
                if img:
                    out.append(f'<img class="vimg" src="{img}">')
                out.append('<div class="cols">')
                for k, p in sorted(vc["points"].items(), key=lambda kv: V_ORDER.index(V_KEYS[kv[0]])):
                    g = V_KEYS[k]
                    h = (p["sign"] - vc["lagna"]) % 12 + 1
                    d = interp.get("vedic", "varga_planet_in_house", code, g, h)
                    out.append(self.entry(d, self.glyph(g),
                                          f'{e(self.sign(p["sign"]))} · {t["house"]} {h}', full=False, cls="compact"))
                out.append("</div></div>")

        da = v["dasha"]
        out.append(f'<h2 class="sh">{t["dasha_h"]}</h2><div class="dasha">')

        def dn(lord):
            return DASHA_NAMES[lord][0 if self.lang == "ar" else 1]
        out.append(f'<div class="now"><div><span>{t["maha"]}</span><b>{e(dn(da["maha"]["lord"]))}</b>'
                   f'{ltr(da["maha"]["start"] + " → " + da["maha"]["end"])}</div>')
        if da.get("antar"):
            out.append(f'<div><span>{t["antar"]}</span><b>{e(dn(da["antar"]["lord"]))}</b>'
                       f'{ltr(da["antar"]["start"] + " → " + da["antar"]["end"])}</div>')
        out.append("</div>")
        rows = "".join(
            f'<tr class="{"cur" if p["lord"] == da["maha"]["lord"] and p["start"] == da["maha"]["start"] else ""}">'
            f'<td>{e(dn(p["lord"]))}</td><td>{ltr(p["start"])}</td><td>{ltr(p["end"])}</td></tr>'
            for p in da["timeline"][:9])
        out.append(f'<table class="pos"><thead><tr><th>{t["planet"]}</th><th>{t["from"]}</th><th>{t["to"]}</th></tr>'
                   f'</thead><tbody>{rows}</tbody></table></div>')
        out.append("</section>")
        return "".join(out)

    def closing(self) -> str:
        t = self.t
        st = interp.status()
        disc = (interp._meta.get("disclaimer") or {}).get(self.lang, "")
        return f"""
<section class="closing">
  <h2 class="sh">{t['closing_h']}</h2>
  <p class="lead">{e(t['closing'])}</p>
  <h3>{t['method']}</h3><p>{e(t['method_txt'].format(v=st.get('version') or '-'))}</p>
  <p class="disc">{e(disc)}</p>
  <div class="follow"><b>{t['follow']}</b> {ltr('@TheAlchemistAstroBot')} · {ltr('instagram.com/the.alchemist.astro')}</div>
</section>"""

    def html(self) -> str:
        css = (HERE / "report.css").read_text(encoding="utf-8")
        m = self.c["meta"]
        running = f'{self.t["brand"]} · {m["name"]}'
        return f"""<!DOCTYPE html>
<html lang="{self.lang}" dir="{'rtl' if self.lang == 'ar' else 'ltr'}"><head><meta charset="utf-8">
<title>{e(self.t['title'])} - {e(m['name'])}</title><style>{css}</style></head>
<body><div class="running">{e(running)}</div><div class="pageno-label">{self.t['page']}</div>
{self.cover()}{self.contents()}{self.western()}{self.vedic()}{self.closing()}
<div class="stamp">{self.t['prepared']} {ltr(date.today().isoformat())}</div>
</body></html>"""

    def pdf(self) -> bytes:
        from weasyprint import HTML
        return HTML(string=self.html(), base_url=str(HERE)).write_pdf()


SIGIL = """<svg class="sigil" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#c9a464">
<circle cx="100" cy="100" r="92" stroke-width="0.8"/><circle cx="100" cy="100" r="84" stroke-width="0.4"/>
<circle cx="100" cy="100" r="58" stroke-width="1.2"/>
<path d="M100 22 L167.5 139 L32.5 139 Z" stroke-width="1"/><path d="M100 178 L32.5 61 L167.5 61 Z" stroke-width="1"/>
<circle cx="100" cy="100" r="16" stroke-width="1.4"/><circle cx="100" cy="100" r="2.5" fill="#c9a464"/>
<g stroke-width="0.6">""" + "".join(
    f'<line x1="100" y1="8" x2="100" y2="16" transform="rotate({i * 30} 100 100)"/>' for i in range(12)) + "</g></svg>"


def build_pdf(chart: dict, lang: str = "ar", style: str = "north") -> bytes:
    return Report(chart, lang, style).pdf()
