"""SVG rendering: western wheel (kerykeion) and Indian North/South square charts (own SVG)."""
from __future__ import annotations

import shutil
import subprocess
from html import escape

from kerykeion import ChartDrawer

from .names import SIGNS, VEDIC_SHORT

FONT = "Readex Pro, Noto Sans Arabic, Noto Naskh Arabic, DejaVu Sans, Arial, sans-serif"
LRI, PDI = "⁦", "⁩"  # isolate numbers inside Arabic text

THEMES = {
    "dark": {"bg": "#0f1629", "line": "#c9a45c", "grid": "#3a4466", "text": "#e9e4d8",
             "muted": "#9aa3bf", "accent": "#e2b866", "asc": "#e2b866", "panel": "#141d36"},
    "light": {"bg": "#fbf8f1", "line": "#8a6a2c", "grid": "#d8cdb5", "text": "#1f2233",
              "muted": "#6b6f80", "accent": "#a5741c", "asc": "#a5741c", "panel": "#f3eee2"},
}


def western_wheel_svg(chart: dict, theme: str = "dark") -> str:
    subj = chart["_subjects"]["western_data"]
    d = ChartDrawer(subj, theme="dark" if theme == "dark" else "classic",
                    transparent_background=False)
    return d.generate_wheel_only_svg_string(remove_css_variables=True)


def _placements(chart: dict, lang: str) -> tuple[int | None, dict[int, list[str]]]:
    v = chart["vedic"]
    asc = v["lagna"]["sign"] if v["lagna"] else None
    by_sign: dict[int, list[str]] = {i: [] for i in range(12)}
    for key, p in v["points"].items():
        label = VEDIC_SHORT["ar" if lang == "ar" else "en"][key]
        txt = f"{label} {LRI}{int(p['deg'])}°{PDI}"
        if p["retro"] and "node" not in key:
            txt += " R"
        by_sign[p["sign"]].append(txt)
    return asc, by_sign


def _lines(cx, cy, lines, size, fill, weight="400"):
    out, n = [], len(lines)
    y0 = cy - (n - 1) * size * 0.62
    for i, t in enumerate(lines):
        out.append(f'<text x="{cx:.1f}" y="{y0 + i * size * 1.24:.1f}" font-size="{size}" font-weight="{weight}" '
                   f'text-anchor="middle" dominant-baseline="middle" fill="{fill}">{escape(t)}</text>')
    return "".join(out)


def _frame(body: str, c: dict, size: int = 440) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" '
            f'font-family="{FONT}"><rect width="100%" height="100%" rx="18" fill="{c["bg"]}"/>{body}</svg>')


# North Indian: houses fixed, signs rotate. (text centre, sign-number position)
_NORTH = {
    1: ((200, 96), (200, 172)), 2: ((100, 40), (100, 82)), 3: ((40, 100), (82, 100)),
    4: ((100, 200), (172, 200)), 5: ((40, 300), (82, 300)), 6: ((100, 360), (100, 318)),
    7: ((200, 304), (200, 228)), 8: ((300, 360), (300, 318)), 9: ((360, 300), (318, 300)),
    10: ((300, 200), (228, 200)), 11: ((360, 100), (318, 100)), 12: ((300, 40), (300, 82)),
}


def north_indian_svg(chart: dict, lang: str = "ar", theme: str = "dark") -> str:
    c = THEMES[theme]
    asc, by_sign = _placements(chart, lang)
    asc_sign = asc if asc is not None else chart["vedic"]["points"]["moon"]["sign"]
    b = [f'<g transform="translate(20,20)">',
         f'<rect width="400" height="400" rx="6" fill="{c["panel"]}" stroke="{c["line"]}" stroke-width="2"/>',
         f'<path d="M0,0 L400,400 M400,0 L0,400" stroke="{c["line"]}" stroke-width="1.3"/>',
         f'<path d="M200,0 L400,200 L200,400 L0,200 Z" stroke="{c["line"]}" stroke-width="1.3" fill="none"/>']
    for house, ((tx, ty), (sx, sy)) in _NORTH.items():
        sign = (asc_sign + house - 1) % 12
        b.append(f'<text x="{sx}" y="{sy}" font-size="12" text-anchor="middle" dominant-baseline="middle" '
                 f'fill="{c["muted"]}">{sign + 1}</text>')
        lines = list(by_sign[sign])
        if house == 1:
            lines.insert(0, ("الطالع" if lang == "ar" else "Asc") if asc is not None
                         else ("القمر" if lang == "ar" else "Moon ↑"))
        size = 13 if len(lines) <= 3 else 11
        b.append(_lines(tx, ty, lines, size, c["text"]))
    b.append("</g>")
    return _frame("".join(b), c)


_SOUTH_POS = {11: (0, 0), 0: (0, 1), 1: (0, 2), 2: (0, 3), 3: (1, 3), 4: (2, 3),
              5: (3, 3), 6: (3, 2), 7: (3, 1), 8: (3, 0), 9: (2, 0), 10: (1, 0)}


def south_indian_svg(chart: dict, lang: str = "ar", theme: str = "dark") -> str:
    c = THEMES[theme]
    asc, by_sign = _placements(chart, lang)
    names = SIGNS["ar" if lang == "ar" else "en"]
    s = 100
    b = ['<g transform="translate(20,20)">']
    for sign, (r, col) in _SOUTH_POS.items():
        x, y = col * s, r * s
        b.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c["panel"]}" '
                 f'stroke="{c["line"]}" stroke-width="1.3"/>')
        b.append(f'<text x="{x + s / 2}" y="{y + 14}" font-size="10" text-anchor="middle" '
                 f'fill="{c["muted"]}">{escape(names[sign])}</text>')
        lines = list(by_sign[sign])
        if asc is not None and sign == asc:
            b.append(f'<path d="M{x},{y + 22} L{x + 22},{y} L{x},{y} Z" fill="{c["asc"]}"/>')
            lines.insert(0, "الطالع" if lang == "ar" else "Asc")
        size = 12 if len(lines) <= 3 else 10.5
        b.append(_lines(x + s / 2, y + s / 2 + 8, lines, size, c["text"]))
    # centre panel
    m = chart["meta"]
    nak = chart["vedic"]["moon_nakshatra"]
    nak_name = nak["name_ar"] if lang == "ar" else nak["name"]
    centre = [m.get("name") or "", m["local"], m.get("city") or "",
              ("\u202b" + f"نكشترا القمر: {nak_name} (بادا {nak['pada']})" + "\u202c" if lang == "ar"
               else f"Moon: {nak_name} pada {nak['pada']}")]
    b.append(f'<rect x="{s + 1}" y="{s + 1}" width="{2 * s - 2}" height="{2 * s - 2}" fill="{c["bg"]}"/>')
    b.append(_lines(2 * s, 2 * s - 10, [t for t in centre if t], 12.5, c["text"]))
    b.append(f'<text x="{2 * s}" y="{3 * s - 14}" font-size="10" text-anchor="middle" fill="{c["accent"]}">'
             f'Lahiri · Whole Sign</text>')
    b.append(f'<rect width="400" height="400" fill="none" stroke="{c["line"]}" stroke-width="2"/>')
    b.append("</g>")
    return _frame("".join(b), c)


def indian_svg(chart: dict, style: str, lang: str, theme: str) -> str:
    return (south_indian_svg if style == "south" else north_indian_svg)(chart, lang, theme)


def svg_to_png(svg: str, width: int = 1000) -> bytes | None:
    exe = shutil.which("rsvg-convert")
    if not exe:
        return None
    r = subprocess.run([exe, "-w", str(width), "-f", "png"], input=svg.encode(),
                       capture_output=True, timeout=30)
    return r.stdout if r.returncode == 0 else None
