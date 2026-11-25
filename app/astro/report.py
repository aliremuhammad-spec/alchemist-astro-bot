"""Telegram HTML text report for a computed chart (Arabic / English)."""
from __future__ import annotations

from html import escape

from .names import (ASPECTS, DASHA_NAMES, ELEMENTS, MOON_PHASES, PLANETS, QUALITIES, SIGN_GLYPH,
                    VEDIC_NAMES, sign_name)

L = {
    "ar": {
        "west": "🌍 <b>الخارطة الغربية</b> <i>(تروبيكال · بلاسيدوس)</i>",
        "vedic": "🕉 <b>الخارطة الفيدية</b> <i>(سايديريال · لاهيري · بيوت البرج الكامل)</i>",
        "house": "البيت", "asc": "الطالع", "mc": "وسط السماء (MC)", "lagna": "اللغنا (الطالع)",
        "aspects": "الاتصالات الرئيسية", "elements": "العناصر", "qualities": "الصفات",
        "moon_phase": "طور القمر", "retro": "تراجع", "nak": "نكشترا", "pada": "بادا",
        "moon_nak": "نكشترا القمر", "dasha": "الدشا الحالية (فمشوتاري)", "maha": "مها دشا",
        "antar": "أنتار دشا", "to": "حتى", "no_time": "⚠️ وقت الولادة غير معروف: حُسبت الخارطة على الظهر، بدون طالع وبيوت.",
        "moon_sign_changes": "⚠️ القمر غيّر برجه بهذا اليوم، فبرج القمر غير مؤكد بدون وقت الولادة.",
        "vedic_moon_sign_changes": "⚠️ برج القمر الفيدي تغيّر بهذا اليوم.",
        "nakshatra_changes": "⚠️ نكشترا القمر تغيّرت بهذا اليوم، والدشا تقريبية.",
        "applying": "يقترب", "separating": "يبتعد",
    },
    "en": {
        "west": "🌍 <b>Western chart</b> <i>(Tropical · Placidus)</i>",
        "vedic": "🕉 <b>Vedic chart</b> <i>(Sidereal · Lahiri · Whole Sign)</i>",
        "house": "House", "asc": "Ascendant", "mc": "Midheaven (MC)", "lagna": "Lagna",
        "aspects": "Major aspects", "elements": "Elements", "qualities": "Modalities",
        "moon_phase": "Moon phase", "retro": "Rx", "nak": "Nakshatra", "pada": "pada",
        "moon_nak": "Moon nakshatra", "dasha": "Current dasha (Vimshottari)", "maha": "Mahadasha",
        "antar": "Antardasha", "to": "until", "no_time": "⚠️ Birth time unknown: chart cast for noon, no Ascendant or houses.",
        "moon_sign_changes": "⚠️ The Moon changed sign that day, so the Moon sign is uncertain.",
        "vedic_moon_sign_changes": "⚠️ The sidereal Moon changed sign that day.",
        "nakshatra_changes": "⚠️ The Moon changed nakshatra that day; dashas are approximate.",
        "applying": "applying", "separating": "separating",
    },
}


def dms(deg: float) -> str:
    d = int(deg)
    m = int(round((deg - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"\u2066{d}°{m:02d}′\u2069"  # isolate so it reads correctly inside Arabic


def _pos(p: dict, lang: str) -> str:
    return f"{SIGN_GLYPH[p['sign']]} {sign_name(p['sign'], lang)} {dms(p['deg'])}"


def header(chart: dict, lang: str) -> str:
    m = chart["meta"]
    place = m.get("city") or ""
    return f"✨ <b>{escape(m.get('name') or '')}</b>\n🗓 {m['local']} · 📍 {escape(place)}"


def western_text(chart: dict, lang: str) -> str:
    t = L[lang]
    w = chart["western"]
    out = [header(chart, lang), "", t["west"], ""]
    if not chart["meta"]["time_known"]:
        out += [t["no_time"], ""]
    if w["asc"]:
        out.append(f"⬆️ {t['asc']}: {_pos(w['asc'], lang)}")
        out.append(f"🔝 {t['mc']}: {_pos(w['mc'], lang)}")
        out.append("")
    for key, p in w["points"].items():
        g, ar, en = PLANETS[key]
        line = f"{g} {ar if lang == 'ar' else en}: {_pos(p, lang)}"
        if p.get("house"):
            line += f" · {t['house']} {p['house']}"
        if p["retro"] and "node" not in key:
            line += f" · ℞ {t['retro']}"
        out.append(line)
    out.append("")
    out.append(f"<b>{t['aspects']}</b>")
    for a in [a for a in w["aspects"] if a["major"]][:14]:
        n1 = _pname(a["p1"], lang)
        n2 = _pname(a["p2"], lang)
        g, ar, en = ASPECTS.get(a["type"], ("·", a["type"], a["type"]))
        mv = t["applying"] if a["applying"] else t["separating"]
        out.append(f"{n1} {g} {n2} — {ar if lang == 'ar' else en} (\u2066{a['orb']:.1f}°\u2069، {mv})"
                   if lang == "ar" else f"{n1} {g} {n2} — {en} ({a['orb']:.1f}°, {mv})")
    out.append("")
    el = " · ".join(f"{ELEMENTS[lang][k]} {v}%" for k, v in w["elements"].items())
    ql = " · ".join(f"{QUALITIES[lang][k]} {v}%" for k, v in w["qualities"].items())
    mp = w["moon_phase"]
    out += [f"🔥 {t['elements']}: {el}", f"⚖️ {t['qualities']}: {ql}",
            f"{mp['emoji']} {t['moon_phase']}: {MOON_PHASES.get(mp['name'], mp['name']) if lang == 'ar' else mp['name']}"]
    for wkey in chart["warnings"]:
        if wkey == "moon_sign_changes":
            out.append(t[wkey])
    return "\n".join(out)


def vedic_text(chart: dict, lang: str) -> str:
    t = L[lang]
    v = chart["vedic"]
    out = [t["vedic"], ""]
    if v["lagna"]:
        nk = v["lagna"]["nakshatra"]
        out.append(f"⬆️ {t['lagna']}: {_pos(v['lagna'], lang)} · {_nak(nk, lang)}")
        out.append("")
    for key, p in v["points"].items():
        _, ar, en = VEDIC_NAMES[key]
        line = f"• {ar if lang == 'ar' else en}: {_pos(p, lang)}"
        if p.get("house"):
            line += f" · {t['house']} {p['house']}"
        if p["retro"] and "node" not in key:
            line += " ℞"
        line += f"\n   {t['nak']}: {_nak(p['nakshatra'], lang)}"
        out.append(line)
    out.append("")
    out.append(f"🌙 {t['moon_nak']}: {_nak(v['moon_nakshatra'], lang)}")
    d = v["dasha"]
    out.append("")
    out.append(f"<b>{t['dasha']}</b>")
    out.append(f"• {t['maha']}: {_dn(d['maha']['lord'], lang)} — {t['to']} {d['maha']['end']}")
    if d["antar"]:
        out.append(f"• {t['antar']}: {_dn(d['antar']['lord'], lang)} — {t['to']} {d['antar']['end']}")
    for wkey in chart["warnings"]:
        if wkey != "moon_sign_changes":
            out.append(t[wkey])
    return "\n".join(out)


def _nak(nk: dict, lang: str) -> str:
    name = nk["name_ar"] if lang == "ar" else nk["name"]
    lord = _dn(nk["lord"], lang)
    return f"{name} ({L[lang]['pada']} {nk['pada']}) · {lord}"


def _dn(lord: str, lang: str) -> str:
    ar, en = DASHA_NAMES[lord]
    return ar if lang == "ar" else en


def _pname(key: str, lang: str) -> str:
    if key in PLANETS:
        g, ar, en = PLANETS[key]
        return ar if lang == "ar" else en
    return {"ascendant": ("الطالع", "Asc"), "medium_coeli": ("MC", "MC")}.get(key, (key, key))[0 if lang == "ar" else 1]
