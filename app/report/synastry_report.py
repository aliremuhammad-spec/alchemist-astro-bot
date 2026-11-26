"""Compatibility (synastry) report PDF: western themes + house overlays, vedic Ashtakoota + Manglik.

Uses the natal report's visual identity (report.css). Interpretive texts for synastry will come from a
dedicated database later; until then each section carries a concise explanation of what is being measured.
"""
from __future__ import annotations

from datetime import date

from .. import interp
from ..astro.names import ASPECTS, PLANETS, SIGN_GLYPH, SIGNS
from ..astro.render import synastry_wheel_svg
from .builder import HERE, SIGIL, e, ltr, png_uri, tvs

L = {
    "ar": {
        "brand": "الخيميائي", "title": "تقرير التوافق الفلكي", "and": "و",
        "ak": "الأشتاكوتا (فيدي)", "harm": "الانسجام الغربي", "score": "مؤشر الاتصالات",
        "part_w": "التوافق الغربي", "part_w_sub": "الاتصالات بين الخارطتين، والبيوت اللي بيفعّلها كل طرف عند التاني",
        "part_v": "التوافق الفيدي", "part_v_sub": "مطابقة الغونا (36 نقطة) وفحص المانغاليك من القمر النجمي",
        "themes_h": "محاور العلاقة", "soft": "متناغم", "hard": "متوتر", "intense": "مكثّف",
        "no_contacts": "ما في اتصالات رئيسية بهالمحور، فهو مو محور أساسي بالعلاقة.",
        "elements_h": "توازن العناصر عند الطرفين", "overlays_h": "البيوت اللي بيفعّلها كل طرف",
        "overlay_line": "كواكب {b} ببيوت {a}", "no_time": "بحاجة لوقت ميلاد {a} الدقيق.",
        "house": "البيت", "planet": "الكوكب", "aspects_h": "أقوى الاتصالات",
        "ak_h": "مطابقة الأشتاكوتا", "koota": "الكوتا", "points": "النقاط",
        "ak_note": "الحساب التقليدي بيقرا الخارطة الأولى كطرف الرجل والتانية كطرف المرأة بخمس كوتات (فارنا، فاشيا، تارا، يوني، غانا).",
        "verdict": {"excellent": "ممتاز (33 وفوق)", "good": "جيد (25–32)", "average": "مقبول (18–24)",
                    "low": "ضعيف (أقل من 18)"},
        "dosha_h": "تنبيهات", "dosha": {"nadi": "نادي دوشا: نفس النادي عند الطرفين، ويُنصح بمراجعة فلكي مختص.",
                                         "bhakoot": "بهاكوت دوشا: علاقة البرجين القمريين 2/12 أو 5/9 أو 6/8.",
                                         "gana": "تباين الغانا: طباع أساسية مختلفة بتحتاج صبر وتفاهم."},
        "manglik_h": "فحص المانغاليك (كوجا دوشا)", "manglik_yes": "مانغاليك", "manglik_no": "غير مانغاليك",
        "from_lagna": "من الطالع", "from_moon": "من القمر",
        "manglik_bal": "الحالة متوازنة بين الطرفين، وهاد بيخفف الأثر بحسب التقليد.",
        "manglik_unbal": "الحالة غير متوازنة بين الطرفين؛ بيُستحسن مراجعة التوقيت والخارطة الكاملة.",
        "moon_h": "القمر النجمي", "closing_h": "قبل أن تُغلق التقرير",
        "closing": "التوافق مو حكم على علاقة، بل خريطة لنقاط السهولة ونقاط الجهد. المحاور المتوترة بتصير مصدر نضج لما "
                   "ينتبهلها الطرفين، والمتناغمة بتحتاج رعاية حتى ما تنعطى كأمر مسلّم.",
        "disc": "المحتوى لأغراض ثقافية وتأملية، ولا يغني عن قرار الطرفين واستشارة مختص.",
        "prepared": "أُعدّ في", "fire": "نار", "earth": "تراب", "air": "هواء", "water": "ماء",
    },
    "en": {
        "brand": "The Alchemist", "title": "Compatibility Report", "and": "&",
        "ak": "Ashtakoota (Vedic)", "harm": "Western harmony", "score": "Contact score",
        "part_w": "Western compatibility", "part_w_sub": "Contacts between the two charts and the houses each activates",
        "part_v": "Vedic compatibility", "part_v_sub": "Guna matching (36 points) and Manglik check from the sidereal Moon",
        "themes_h": "Relationship themes", "soft": "Harmonious", "hard": "Tense", "intense": "Intense",
        "no_contacts": "No major contacts here, so this is not a central theme of the bond.",
        "elements_h": "Element balance", "overlays_h": "Houses each person activates",
        "overlay_line": "{b}'s planets in {a}'s houses", "no_time": "Needs {a}'s exact birth time.",
        "house": "House", "planet": "Planet", "aspects_h": "Strongest contacts",
        "ak_h": "Ashtakoota matching", "koota": "Koota", "points": "Points",
        "ak_note": "Classically the first chart is read as the groom and the second as the bride for five kootas "
                   "(Varna, Vashya, Tara, Yoni, Gana).",
        "verdict": {"excellent": "Excellent (33+)", "good": "Good (25–32)", "average": "Acceptable (18–24)",
                    "low": "Low (under 18)"},
        "dosha_h": "Flags", "dosha": {"nadi": "Nadi dosha: both share the same Nadi; a specialist review is advised.",
                                       "bhakoot": "Bhakoot dosha: the Moon signs are 2/12, 5/9 or 6/8 apart.",
                                       "gana": "Gana contrast: different core temperaments that need patience."},
        "manglik_h": "Manglik check (Kuja dosha)", "manglik_yes": "Manglik", "manglik_no": "Not Manglik",
        "from_lagna": "from Lagna", "from_moon": "from Moon",
        "manglik_bal": "Balanced between both, which traditionally softens the effect.",
        "manglik_unbal": "Unbalanced between both; review timing and the full charts.",
        "moon_h": "Sidereal Moon", "closing_h": "Before you close this report",
        "closing": "Compatibility is not a verdict on a relationship; it maps where things flow and where effort is "
                   "needed. Tense themes become growth when both notice them; easy ones still need care.",
        "disc": "For cultural and reflective purposes; it does not replace the couple's own judgment or professional advice.",
        "prepared": "Prepared on", "fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water",
    },
}
HOUSES_FALLBACK = {
    "ar": ["الذات", "المال والقيم", "التواصل", "البيت والجذور", "الحب والإبداع", "العمل اليومي والصحة",
           "الشراكة", "العمق والمشاركة", "الرؤية والسفر", "المكانة والمهنة", "الأصدقاء والأحلام", "الباطن والعزلة"],
    "en": ["Self", "Money & values", "Communication", "Home & roots", "Love & creativity", "Daily work & health",
           "Partnership", "Intimacy & shared resources", "Vision & travel", "Career & status", "Friends & hopes",
           "Inner life & retreat"],
}


class SynReport:
    def __init__(self, names: list[str], base: dict, det: dict, lang: str = "ar"):
        self.names, self.base, self.d = names, base, det
        self.lang = "ar" if lang == "ar" else "en"
        self.t = L[self.lang]

    def pn(self, k: str) -> str:
        return PLANETS[k][1 if self.lang == "ar" else 2] if k in PLANETS else k

    def sign(self, i: int) -> str:
        return SIGNS[self.lang][i % 12]

    def house_name(self, n: int) -> str:
        ref = (interp._reference or {}).get("western_houses") or {}
        h = (ref.get(str(n)) or {}).get("name") or {}
        return h.get(self.lang) or HOUSES_FALLBACK[self.lang][n - 1]

    def cover(self) -> str:
        t, a, b = self.t, *self.names
        ak = self.d["vedic"]["ashtakoota"]
        w = self.d["western"]
        harm = round(100 * w["soft"] / (w["soft"] + w["hard"])) if (w["soft"] + w["hard"]) else 0
        cells = [(t["ak"], f"{ak['total']:g}/36"), (t["harm"], f"{harm}%"), (t["score"], str(self.base["score"]["value"]))]
        big = "".join(f'<div class="bt"><span class="btl">{e(l)}</span><span class="btv">{ltr(v)}</span></div>' for l, v in cells)
        return f"""<section class="cover"><div class="cv-brand">{t['brand']}</div>{SIGIL}
<div class="cv-kicker">{t['title']}</div><h1 class="cv-name syn">{e(a)} <span class="amp">{t['and']}</span> {e(b)}</h1>
<div class="bigthree">{big}</div></section>"""

    def opener(self, title: str, sub: str, num: str) -> str:
        return f'<section class="opener"><div class="op-num">{num}</div><h2>{e(title)}</h2><p>{e(sub)}</p></section>'

    def pill(self, nat: str) -> str:
        cls = {"soft": "good", "hard": "hard", "intense": "mixed"}[nat]
        return f'<span class="pill {cls}">{self.t[nat]}</span>'

    def aspect_row(self, x: dict) -> str:
        g = ASPECTS[x["type"]]
        a, b = self.names
        return (f'<tr><td>{tvs(PLANETS[x["a"]][0])} {e(self.pn(x["a"]))} <small>({e(a)})</small></td>'
                f'<td class="ag">{tvs(g[0])} {e(g[1] if self.lang == "ar" else g[2])}</td>'
                f'<td>{tvs(PLANETS[x["b"]][0])} {e(self.pn(x["b"]))} <small>({e(b)})</small></td>'
                f'<td>{ltr(f"{x["orb"]:.1f}°")}</td><td>{self.pill(x["nature"])}</td></tr>')

    def western(self) -> str:
        t, w = self.t, self.d["western"]
        a, b = self.names
        out = [self.opener(t["part_w"], t["part_w_sub"], "I"), '<section class="part">']
        wheel = png_uri(synastry_wheel_svg(self.base["_data"], "light"), 1300)
        if wheel:
            out.append(f'<img class="wheel" src="{wheel}">')
        out.append(f'<h2 class="sh">{t["themes_h"]}</h2>')
        for th in w["themes"]:
            sc = th["score"]
            bar = (f'<div class="bar"><span class="track"><span class="fill water" style="width:{max(3, sc)}%"></span></span>'
                   f'<span class="bv">{ltr(f"{sc}%")}</span></div>') if sc is not None else ""
            rows = "".join(self.aspect_row(x) for x in th["aspects"])
            intense = f' · {t["intense"]} {th["intense"]}' if th["intense"] else ""
            body = (f'<table class="pos syn">{rows}</table>' if rows else f'<p class="note">{t["no_contacts"]}</p>')
            out.append(f'<article class="entry theme"><header class="eh"><h4>{e(th[self.lang])}</h4>'
                       f'<span class="tc">{t["soft"]} {th["soft"]} · {t["hard"]} {th["hard"]}'
                       f'{intense}</span></header>'
                       f'<p class="summary">{e(th["about_" + self.lang])}</p>{bar}{body}</article>')

        out.append(f'<h2 class="sh">{t["elements_h"]}</h2><div class="balance">')
        for i, nm in enumerate(self.names):
            el = w["elements"][i]
            rows = "".join(
                f'<div class="bar"><span class="bl">{t[k]}</span><span class="track"><span class="fill {k}" '
                f'style="width:{max(2, el[k])}%"></span></span><span class="bv">{ltr(f"{el[k]:.0f}%")}</span></div>'
                for k in ("fire", "earth", "air", "water"))
            out.append(f'<div class="bars"><h3 class="bn">{e(nm)}</h3>{rows}</div>')
        out.append("</div>")

        out.append(f'<h2 class="sh">{t["overlays_h"]}</h2><div class="cols">')
        for owner, guest, key in ((a, b, "overlays_ab"), (b, a, "overlays_ba")):
            ov = w[key]
            head = f'<h3 class="bn">{e(t["overlay_line"].format(a=owner, b=guest))}</h3>'
            if not ov:
                out.append(f'<div>{head}<p class="note">{e(t["no_time"].format(a=owner))}</p></div>')
                continue
            rows = "".join(f'<tr><td>{tvs(PLANETS[o["planet"]][0])} {e(self.pn(o["planet"]))}</td>'
                           f'<td>{t["house"]} {o["house"]}</td><td>{e(self.house_name(o["house"]))}</td></tr>' for o in ov)
            out.append(f'<div>{head}<table class="pos">{rows}</table></div>')
        out.append("</div>")

        top = sorted(w["aspects"], key=lambda z: z["orb"])[:14]
        out.append(f'<h2 class="sh">{t["aspects_h"]}</h2><table class="pos syn">{"".join(self.aspect_row(x) for x in top)}</table>')
        out.append("</section>")
        return "".join(out)

    def vedic(self) -> str:
        t, v = self.t, self.d["vedic"]
        ak = v["ashtakoota"]
        out = [self.opener(t["part_v"], t["part_v_sub"], "II"), '<section class="part">']
        moons = "".join(
            f'<div class="mc"><span class="ml">{e(nm)}</span><span class="mv">{tvs(SIGN_GLYPH[m["sign"]])} '
            f'{e(self.sign(m["sign"]))}</span><span class="ml">{e(m["nak"]["name_ar"] if self.lang == "ar" else m["nak"]["name"])} · {m["nak"]["pada"]}</span></div>'
            for nm, m in zip(self.names, v["moon"]))
        out.append(f'<h2 class="sh">{t["moon_h"]}</h2><div class="moons">{moons}</div>')
        out.append(f'<h2 class="sh">{t["ak_h"]}</h2>')
        out.append(f'<div class="dasha"><div class="now"><div><span>{t["ak"]}</span><b class="tot">{ltr(f"{ak["total"]:g} / 36")}</b>'
                   f'<span>{e(t["verdict"][ak["verdict"]])}</span></div></div></div>')
        rows = []
        for k in ak["kootas"]:
            det = ak["detail"].get(k["key"], {})
            pair = ""
            if "a" in det:
                def nm(x):
                    if isinstance(x, (tuple, list)):
                        return x[0] if self.lang == "ar" else x[1]
                    return self.pn(x)
                pair = f'{e(nm(det["a"]))} · {e(nm(det["b"]))}'
            elif "pair" in det:
                pair = ltr(det["pair"])
            full = k["points"] >= k["max"]
            rows.append(f'<tr class="{"cur" if full else ""}"><td><b>{e(k[self.lang])}</b><br><small>{e(k["about_" + self.lang])}</small></td>'
                        f'<td>{pair}</td><td class="pts">{ltr(f"{k["points"]:g} / {k["max"]}")}</td></tr>')
        out.append(f'<table class="pos ak"><thead><tr><th>{t["koota"]}</th><th>{e(self.names[0])} · {e(self.names[1])}</th>'
                   f'<th>{t["points"]}</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')
        out.append(f'<p class="note">{e(t["ak_note"])}</p>')
        if ak["doshas"]:
            out.append(f'<h3 class="bn">{t["dosha_h"]}</h3>' + "".join(
                f'<aside class="advice">{e(t["dosha"][d])}</aside>' for d in ak["doshas"]))
        out.append(f'<h2 class="sh">{t["manglik_h"]}</h2><div class="cols">')
        for nm, m in zip(self.names, v["manglik"]):
            st = t["manglik_yes"] if m["is"] else t["manglik_no"]
            lines = [f'{t["from_moon"]}: {t["house"]} {m["from_moon"]}']
            if m["from_lagna"]:
                lines.insert(0, f'{t["from_lagna"]}: {t["house"]} {m["from_lagna"]}')
            out.append(f'<div class="facet"><b>{e(nm)} · {st}</b><span>{" · ".join(lines)}</span></div>')
        out.append("</div>")
        out.append(f'<p class="note">{t["manglik_bal"] if v["manglik_balanced"] else t["manglik_unbal"]}</p>')
        out.append("</section>")
        return "".join(out)

    def closing(self) -> str:
        t = self.t
        return (f'<section class="closing"><h2 class="sh">{t["closing_h"]}</h2><p class="lead">{e(t["closing"])}</p>'
                f'<p class="disc">{e(t["disc"])}</p><div class="follow"><b>{t["brand"]}</b> '
                f'{ltr("@TheAlchemistAstroBot")} · {ltr("instagram.com/the.alchemist.astro")}</div></section>')

    def html(self) -> str:
        css = (HERE / "report.css").read_text(encoding="utf-8") + EXTRA_CSS
        running = f'{self.t["brand"]} · {self.names[0]} {self.t["and"]} {self.names[1]}'
        return f"""<!DOCTYPE html><html lang="{self.lang}" dir="{'rtl' if self.lang == 'ar' else 'ltr'}"><head><meta charset="utf-8">
<title>{e(self.t['title'])}</title><style>{css}</style></head><body><div class="running">{e(running)}</div>
{self.cover()}{self.western()}{self.vedic()}{self.closing()}
<div class="stamp">{self.t['prepared']} {ltr(date.today().isoformat())}</div></body></html>"""

    def pdf(self) -> bytes:
        from weasyprint import HTML
        return HTML(string=self.html(), base_url=str(HERE)).write_pdf()


EXTRA_CSS = """
.cv-name.syn { font-size: 34pt; } .cv-name .amp { color: var(--brass-lt); font-size: 24pt; }
.entry.theme { break-inside: avoid; border-top: 0.4pt solid #dcdae6; padding-top: 3mm; }
.tc { font-size: 8.4pt; color: var(--mute); white-space: nowrap; }
table.syn td { font-size: 8.6pt; } table.syn td.ag { color: var(--brass); white-space: nowrap; }
table.syn small { color: var(--mute); }
h3.bn { font-size: 10.5pt; color: var(--verd); margin: 2mm 0 2mm; }
.moons { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
.mc { background: var(--mist); padding: 3mm 4mm; border-radius: 1.5mm; }
.mc span { display: block; } .ml { font-size: 8.6pt; color: var(--mute); }
.mv { font: 700 13pt "PlexLat", "PlexAr", "DejaVu Sans"; color: var(--night); }
.cover .btv { font-size: 16pt; } .cover .btl { font-size: 9pt; }
.dasha .now b.tot .ltr { font-size: 20pt; color: #fff; }
table.ak td.pts { white-space: nowrap; font-weight: 600; color: var(--verd); }
table.ak td small { color: var(--mute); }
"""


def build_synastry_pdf(names, base, det, lang="ar") -> bytes:
    return SynReport(names, base, det, lang).pdf()

