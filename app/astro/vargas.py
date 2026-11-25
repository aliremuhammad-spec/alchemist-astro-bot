"""Parashari divisional charts (vargas) from sidereal longitudes.

Each function maps (sign 0..11, degree within sign 0..30) to the varga sign.
Odd signs are Aries, Gemini, Leo... (index 0, 2, 4...).
"""
from __future__ import annotations

VARGAS = {
    1: ("Rashi", "الراشي (الأساسية)", "Body, overall life"),
    2: ("Hora", "الهورا", "Wealth"),
    3: ("Drekkana", "الدريكانا", "Siblings, courage"),
    4: ("Chaturthamsha", "التشاتورتامشا", "Home, property, fortune"),
    7: ("Saptamsha", "السابتامشا", "Children"),
    9: ("Navamsha", "النافامشا", "Marriage, dharma, inner strength"),
    10: ("Dashamsha", "الداشامشا", "Career, status"),
    12: ("Dwadashamsha", "الدوادشامشا", "Parents"),
    16: ("Shodashamsha", "الشوداشامشا", "Vehicles, comforts"),
    20: ("Vimshamsha", "الفيمشامشا", "Spiritual practice"),
    24: ("Chaturvimshamsha", "التشاتورفيمشامشا", "Learning, education"),
    27: ("Bhamsha", "البهامشا", "Strengths and weaknesses"),
    30: ("Trimshamsha", "الترمشامشا", "Misfortunes, character"),
    40: ("Khavedamsha", "الخافيدامشا", "Maternal legacy"),
    45: ("Akshavedamsha", "الأكشافيدامشا", "Paternal legacy, conduct"),
    60: ("Shashtiamsha", "الشاشتيامشا", "Past karma, overall"),
}


def _odd(s: int) -> bool:
    return s % 2 == 0


def varga_sign(n: int, lon: float) -> int:
    s, d = int(lon // 30) % 12, lon % 30
    if n == 1:
        return s
    if n == 2:  # Parashara hora: Sun's (Leo) and Moon's (Cancer)
        first = d < 15
        return (4 if first else 3) if _odd(s) else (3 if first else 4)
    if n == 3:
        return (s + 4 * int(d // 10)) % 12
    if n == 4:
        return (s + 3 * int(d // 7.5)) % 12
    if n == 7:
        p = int(d // (30 / 7))
        return (s + p) % 12 if _odd(s) else (s + 6 + p) % 12
    if n == 9:
        return (s * 9 + int(d // (10 / 3))) % 12
    if n == 10:
        p = int(d // 3)
        return (s + p) % 12 if _odd(s) else (s + 8 + p) % 12
    if n == 12:
        return (s + int(d // 2.5)) % 12
    if n == 16:
        return ([0, 4, 8][s % 3] + int(d // 1.875)) % 12
    if n == 20:
        return ([0, 8, 4][s % 3] + int(d // 1.5)) % 12
    if n == 24:
        return ((4 if _odd(s) else 3) + int(d // 1.25)) % 12
    if n == 27:
        return ([0, 3, 6, 9][s % 4] + int(d // (30 / 27))) % 12
    if n == 30:
        if _odd(s):
            for lim, sign in ((5, 0), (10, 10), (18, 8), (25, 2), (30, 6)):
                if d < lim:
                    return sign
        for lim, sign in ((5, 1), (12, 5), (20, 11), (25, 9), (30, 7)):
            if d < lim:
                return sign
        return 7
    if n == 40:
        return ((0 if _odd(s) else 6) + int(d // 0.75)) % 12
    if n == 45:
        return ([0, 4, 8][s % 3] + int(d // (2 / 3))) % 12
    if n == 60:
        return (s + int(d // 0.5)) % 12
    raise ValueError(f"unsupported varga D{n}")


def varga_chart(chart: dict, n: int) -> dict:
    """Sign placements for every Vedic point (+ lagna if known) in D-n."""
    v = chart["vedic"]
    pts = {k: {"sign": varga_sign(n, p["abs"]), "retro": p["retro"]} for k, p in v["points"].items()}
    lagna = varga_sign(n, v["lagna"]["abs"]) if v["lagna"] else None
    return {"n": n, "lagna": lagna, "points": pts}
