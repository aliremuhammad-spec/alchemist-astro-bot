"""Compatibility engine driven by the Astro Compatibility Database (v1.x).

Implements the flow and scoring documented in the database's `reference` (scoring, koota, balance, composite):
cross-chart aspects, house overlays, sign pairs, element/modality balance, composite chart, Ashtakoota
(gender-neutral 'mean' policy by default), doshas and their school-dependent cancellations, Manglik, a
western score, five dimensions, and the overall 60/40 percentage. Every text is resolved to an entry of the
database, with {X}/{Y} replaced by the two names.
"""
from __future__ import annotations

import math

from .. import interp

ORDER = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "asc"]
PLANETS10 = ORDER[:10]
SIGNS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn",
         "aquarius", "pisces"]
MOON_REL = {1: "same", 2: "2_12", 12: "2_12", 3: "3_11", 11: "3_11", 4: "4_10", 10: "4_10", 5: "5_9", 9: "5_9",
            6: "6_8", 8: "6_8", 7: "7_1"}


def store():
    return interp.compat


def ready() -> bool:
    return store().ready() and bool(store().reference.get("scoring"))


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def _mid(a: float, b: float) -> float:
    """Midpoint on the shorter arc."""
    d = (b - a) % 360
    return (a + d / 2) % 360 if d <= 180 else (b + (360 - d) / 2) % 360


def _points(chart: dict) -> dict[str, float]:
    w = chart["western"]
    pts = {k: w["points"][k]["abs"] for k in PLANETS10 if k in w["points"]}
    if w.get("asc"):
        pts["asc"] = w["asc"]["abs"]
    return pts


def _house_of(lon: float, cusps: list[float]) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 12


def fill(text: str | None, x: str, y: str) -> str:
    return (text or "").replace("{X}", x).replace("{Y}", y)


def _text(entry: dict | None, lang: str, x: str = "", y: str = "") -> dict | None:
    if not entry:
        return None
    loc = entry.get(lang) or entry.get("ar") or {}
    return {"id": entry["id"], "tone": entry.get("tone"),
            "title": fill(loc.get("title"), x, y), "summary": fill(loc.get("summary"), x, y),
            "text": fill(loc.get("text"), x, y), "advice": fill(loc.get("advice"), x, y)}


# ───────────────────────── western ─────────────────────────

def cross_aspects(pa: dict, pb: dict, sc: dict) -> list[dict]:
    orbs, angles = sc["aspect_orbs"], sc["aspect_angles"]
    out = []
    for p, lp in pa.items():
        for q, lq in pb.items():
            if p == "asc" and q == "asc":
                continue
            sep = _sep(lp, lq)
            best = None
            for kind, ang in angles.items():
                orb = abs(sep - ang)
                if orb <= orbs[kind] and (best is None or orb < best[1]):
                    best = (kind, orb)
            if not best:
                continue
            kind, orb = best
            if ORDER.index(p) <= ORDER.index(q):
                k1, k2, x_is_a = p, q, True
            else:
                k1, k2, x_is_a = q, p, False
            e = store().get("western", "syn_aspect", k1, k2, kind)
            if not e:
                continue
            ex = e.get("extra") or {}
            tight = max(0.25, 1 - orb / orbs[kind])
            contrib = 0.0 if ex.get("generational") else ex.get("weight", 0) * ex.get("valence", 0) * tight
            out.append({"a": p, "b": q, "k1": k1, "k2": k2, "type": kind, "orb": round(orb, 2), "x_is_a": x_is_a,
                        "contrib": contrib, "dims": ex.get("dims") or {}, "generational": bool(ex.get("generational")),
                        "entry": e})
    out.sort(key=lambda z: -abs(z["contrib"]))
    return out


def overlays(owner_chart: dict, guest_pts: dict, sc: dict) -> list[dict] | None:
    cusps = owner_chart["western"]["houses"]
    if not cusps:
        return None
    imp = sc["planet_importance"]
    out = []
    for k in PLANETS10:
        if k not in guest_pts:
            continue
        h = _house_of(guest_pts[k], cusps)
        e = store().get("western", "house_overlay", k, h)
        if not e:
            continue
        ex = e.get("extra") or {}
        out.append({"planet": k, "house": h, "entry": e,
                    "contrib": imp.get(k, 0) / 10 * ex.get("weight", 0) * ex.get("valence", 0)})
    return out


def sign_pairs(ca: dict, cb: dict) -> list[dict]:
    wa, wb = ca["western"]["points"], cb["western"]["points"]
    out = []
    for kind, pa, pb in (("sun_sun", "sun", "sun"), ("moon_moon", "moon", "moon")):
        sa, sb = wa[pa]["sign"], wb[pb]["sign"]
        x_is_a = sa <= sb
        s1, s2 = (sa, sb) if x_is_a else (sb, sa)
        e = store().get("western", "sign_pair", kind, SIGNS[s1], SIGNS[s2])
        if e:
            out.append({"kind": kind, "x_is_a": x_is_a, "entry": e, "score": (e.get("extra") or {}).get("score", 55)})
    for x_is_a, (vx, my) in ((True, (wa, wb)), (False, (wb, wa))):  # X owns Venus, Y owns Mars
        e = store().get("western", "sign_pair", "venus_mars", SIGNS[vx["venus"]["sign"]], SIGNS[my["mars"]["sign"]])
        if e:
            out.append({"kind": "venus_mars", "x_is_a": x_is_a, "entry": e,
                        "score": (e.get("extra") or {}).get("score", 55)})
    return out


def balance(ca: dict, cb: dict) -> list[dict]:
    ref = store().reference.get("signs") or {}
    signs = []
    for c in (ca, cb):
        w = c["western"]
        signs += [w["points"][k]["sign"] for k in PLANETS10 if k in w["points"]]
        if w.get("asc"):
            signs.append(w["asc"]["sign"])
    n = len(signs) or 1
    out = []
    for group, names in (("element", ("fire", "earth", "air", "water")), ("modality", ("cardinal", "fixed", "mutable"))):
        counts = {k: 0 for k in names}
        for s in signs:
            counts[(ref.get(SIGNS[s]) or {}).get(group, names[0])] += 1
        flagged = []
        for k in names:
            share = counts[k] / n
            if share >= 0.36:
                flagged.append((k, "dominant", share))
            elif share <= 0.09:
                flagged.append((k, "lacking", share))
        if flagged:
            for k, lvl, share in flagged:
                e = store().get("western", "balance", group, k, lvl)
                if e:
                    out.append({"group": group, "name": k, "level": lvl, "share": round(share * 100), "entry": e})
        else:
            e = store().get("western", "balance", group, "all", "balanced")
            if e:
                out.append({"group": group, "name": "all", "level": "balanced", "share": None, "entry": e})
    return out


def composite(ca: dict, cb: dict) -> dict:
    pa, pb = _points(ca), _points(cb)
    mids = {k: _mid(pa[k], pb[k]) for k in PLANETS10 if k in pa and k in pb}
    asc = _mid(pa["asc"], pb["asc"]) if "asc" in pa and "asc" in pb else None
    out = {"asc": None, "planets": []}
    if asc is not None:
        out["asc"] = {"sign": int(asc // 30), "entry": store().get("western", "composite_ascendant_in_sign",
                                                                   SIGNS[int(asc // 30)])}
    for k, lon in mids.items():
        s = int(lon // 30)
        h = (s - int(asc // 30)) % 12 + 1 if asc is not None else None
        out["planets"].append({"planet": k, "sign": s, "house": h,
                               "sign_entry": store().get("western", "composite_planet_in_sign", k, SIGNS[s]),
                               "house_entry": store().get("western", "composite_planet_in_house", k, h) if h else None})
    return out


# ───────────────────────── vedic ─────────────────────────

def _rel(nf: dict, a: str, b: str) -> str:
    t = nf[a]
    return "f" if b in t["f"] else "e" if b in t["e"] else "n"


def ashtakoota(ma: dict, mb: dict, policy: str = "mean") -> dict:
    """ma/mb: {'sign': 0..11, 'nak': 0..26, 'deg': degree within sign, 'pada': 1..4}."""
    K = store().reference["koota"]
    naks = K["nakshatras"]
    sa, sb = SIGNS[ma["sign"]], SIGNS[mb["sign"]]
    na, nb = naks[ma["nak"]], naks[mb["nak"]]

    def vashya_type(sign: str, deg: float | None) -> str:
        halves = K.get("vashya_halves", {}).get(sign)
        if halves and deg is not None:
            return halves[0] if deg < 15 else halves[1]
        return K["sign_vashya"][sign]

    va_t, vb_t = vashya_type(sa, ma.get("deg")), vashya_type(sb, mb.get("deg"))
    vorder, vm = K["vashya_order"], K["vashya_matrix"]
    rank = K["varna_rank"]
    rva, rvb = rank[K["sign_varna"][sa]], rank[K["sign_varna"][sb]]

    def directional(first: str, second: str):
        """first = classic first role (bride), second = classic second role (groom)."""
        F, S = (ma, mb) if first == "a" else (mb, ma)
        rf, rs = (rva, rvb) if first == "a" else (rvb, rva)
        vf, vs = (va_t, vb_t) if first == "a" else (vb_t, va_t)
        nf_, ns_ = (na, nb) if first == "a" else (nb, na)
        return {"varna": 1 if rs >= rf else 0,
                "vashya": vm[vorder.index(vf)][vorder.index(vs)],
                "gana": K["gana_matrix"][f"{nf_['gana']}-{ns_['gana']}"]}

    if policy == "classic":
        d = directional("b", "a")          # person A in the classic second role
        varna, vashya, gana = d["varna"], d["vashya"], d["gana"]
    else:
        d1, d2 = directional("a", "b"), directional("b", "a")
        varna = (d1["varna"] + d2["varna"]) / 2
        vashya = (d1["vashya"] + d2["vashya"]) / 2
        gana = (d1["gana"] + d2["gana"]) / 2

    bad = set(K.get("tara_bad", [3, 5, 7]))

    def tara_type(frm: int, to: int) -> int:
        t = ((to - frm) % 27 + 1) % 9
        return 9 if t == 0 else t
    ta, tb = tara_type(ma["nak"], mb["nak"]), tara_type(mb["nak"], ma["nak"])
    tara = 1.5 * (ta not in bad) + 1.5 * (tb not in bad)

    yo = K["yoni_order"]
    yoni = K["yoni_matrix"][yo.index(na["yoni"])][yo.index(nb["yoni"])]

    nf = K["natural_friendship"]
    la, lb = K["sign_lord"][sa], K["sign_lord"][sb]
    if la == lb:
        maitri = 5
    else:
        key = "".join(sorted(_rel(nf, la, lb) + _rel(nf, lb, la)))
        maitri = {"ff": 5, "fn": 4, "nn": 3, "ef": 1, "en": 0.5, "ee": 0}[key]

    dist = (ma["sign"] - mb["sign"]) % 12 + 1   # count of A's moon sign from B's
    dist2 = (mb["sign"] - ma["sign"]) % 12 + 1
    pair = frozenset((dist, dist2))
    bh_kind = {frozenset((2, 12)): "2_12", frozenset((5, 9)): "5_9", frozenset((6, 8)): "6_8"}.get(pair)
    bhakoot = 0 if bh_kind else 7
    nadi = 0 if na["nadi"] == nb["nadi"] else 8

    pts = {"varna": varna, "vashya": vashya, "tara": tara, "yoni": yoni, "graha_maitri": maitri, "gana": gana,
           "bhakoot": bhakoot, "nadi": nadi}
    total = round(sum(pts.values()), 2)

    def band(k: str, v: float) -> str:
        if k == "varna":
            return "full" if v >= 1 else "partial"
        if k == "vashya":
            return "high" if v >= 1.5 else "mid" if v >= 0.75 else "low"
        if k == "tara":
            return "full" if v >= 3 else "partial" if v >= 1.5 else "none"
        if k == "yoni":
            return str(int(round(v)))
        if k == "graha_maitri":
            return "full" if v >= 5 else "good" if v >= 4 else "mid" if v >= 3 else "low" if v > 0 else "none"
        if k == "gana":
            return "same" if v >= 6 else "blend" if v >= 5 else "strain" if v > 0 else "clash"
        return "full" if v > 0 else "none"

    types = {"varna": (K["sign_varna"][sa], K["sign_varna"][sb]), "vashya": (va_t, vb_t),
             "yoni": (na["yoni"], nb["yoni"]), "gana": (na["gana"], nb["gana"]), "nadi": (na["nadi"], nb["nadi"])}
    maxp = K["max_points"]
    kootas = [{"key": k, "points": v, "max": maxp[k], "band": band(k, v),
               "entry": store().get("vedic", "koota", k, band(k, v)), "types": types.get(k)} for k, v in pts.items()]

    doshas = []
    if nadi == 0:
        doshas.append("nadi")
    if bh_kind:
        doshas.append(f"bhakoot_{bh_kind}")
    if gana <= 0.5:
        doshas.append("gana")
    friendly = la == lb or (_rel(nf, la, lb) != "e" and _rel(nf, lb, la) != "e" and "f" in _rel(nf, la, lb) + _rel(nf, lb, la))
    cancels = []
    if "nadi" in doshas:
        if ma["sign"] == mb["sign"] and ma["nak"] != mb["nak"]:
            cancels.append(("nadi", "same_rashi_diff_nakshatra"))
        if ma["nak"] == mb["nak"] and ma.get("pada") and ma.get("pada") != mb.get("pada"):
            cancels.append(("nadi", "same_nakshatra_diff_pada"))
        if friendly:
            cancels.append(("nadi", "lords_friendly"))
    if bh_kind:
        if friendly:
            cancels.append(("bhakoot", "lords_same_or_friends"))
        if la == lb:
            cancels.append(("bhakoot", "same_lord_signs"))
        if nadi == 8 and maitri >= 4:
            cancels.append(("bhakoot", "strong_nadi_and_graha"))
    if "gana" in doshas:
        if maitri >= 4:
            cancels.append(("gana", "lords_friendly"))
        if tara >= 3 and yoni >= 3:
            cancels.append(("gana", "strong_tara_yoni"))

    bands = K.get("band_thresholds", {}).get("score_bands", {})
    sband = next((b for b, r in bands.items() if r["min"] <= total <= r["max"]), "b1")
    yp = store().get("vedic", "yoni_pair", na["yoni"], nb["yoni"]) or store().get("vedic", "yoni_pair", nb["yoni"], na["yoni"])
    return {
        "total": total, "max": 36, "policy": policy, "points": pts, "kootas": kootas,
        "dosha_keys": doshas,
        "doshas": [store().get("vedic", "dosha", d) for d in doshas],
        "cancels": [store().get("vedic", "dosha_cancel", d, r) for d, r in cancels],
        "score_band": store().get("vedic", "score_band", sband),
        "moon_relation": store().get("vedic", "moon_relation", MOON_REL[dist2]),
        "tara": [store().get("vedic", "tara", str(ta)), store().get("vedic", "tara", str(tb))],
        "yoni_pair": yp,
        "type_entries": {k: (store().get("vedic", "koota_type", k, a), store().get("vedic", "koota_type", k, b))
                         for k, (a, b) in types.items()},
    }


def manglik(chart: dict) -> dict:
    v = chart["vedic"]
    mars, moon = v["points"]["mars"]["sign"], v["points"]["moon"]["sign"]
    houses = (1, 2, 4, 7, 8, 12)
    from_moon = (mars - moon) % 12 + 1
    from_lagna = (mars - v["lagna"]["sign"]) % 12 + 1 if v.get("lagna") else None
    is_m = (from_lagna in houses) if from_lagna else (from_moon in houses)
    house = from_lagna if from_lagna else from_moon
    return {"is": bool(is_m), "from_lagna": from_lagna, "from_moon": from_moon, "house": house,
            "house_entry": store().get("vedic", "manglik_house", house) if is_m else None}


# ───────────────────────── scoring ─────────────────────────

def _tanh_scale(v: float, mu: float, sd: float, base: float = 55, amp: float = 40) -> float:
    return base + amp * math.tanh(((v - mu) / sd) / 3)


# Calibration of the raw western sum by how many birth times are known (simulated on random couples so the
# score keeps mean ~55 / SD ~12 in every case). The database's own W_MU/W_SD (2.475/1.115) matches the
# one-time case almost exactly (2.466/1.113), so that case keeps the database values.
CAL_BY_TIMES = {2: (3.214, 1.183), 1: None, 0: (1.717, 1.016)}


def score(aspects: list[dict], ovs: list[list[dict] | None], pairs: list[dict], sc: dict,
          times_known: int = 1) -> tuple[float, dict]:
    cal = sc["calibration"]
    S = sum(a["contrib"] for a in aspects)
    over = [o for lst in ovs if lst for o in lst]
    S += sum(o["contrib"] for o in over)
    sp = sc.get("sign_pair") or {}
    S += sum((p["score"] - 55) / 55 for p in pairs) * sp.get("sign_scores_weight", 0.6)
    mu, sd = CAL_BY_TIMES.get(times_known) or (cal["W_MU"], cal["W_SD"])
    western = _tanh_scale(S, mu, sd)
    dims = {}
    for d in ("attraction", "communication", "values", "stability"):
        D = sum(a["contrib"] * a["dims"].get(d, 0) for a in aspects)
        dims[d] = _tanh_scale(D, cal["D_MU"][d], cal["D_SD"][d])
    F = sum(-a["contrib"] for a in aspects if a["contrib"] < 0) + sum(-o["contrib"] for o in over if o["contrib"] < 0)
    dims["friction"] = _tanh_scale(F, cal["F_MU"], cal["F_SD"], base=50, amp=45)
    return round(western, 1), {k: round(v, 1) for k, v in dims.items()}


def level(v: float) -> str:
    return "high" if v >= 65 else "mid" if v >= 45 else "low"


# ───────────────────────── report assembly ─────────────────────────

def analyse(ca: dict, cb: dict, names: tuple[str, str], lang: str = "ar", policy: str = "mean",
            footer_ctx: dict | None = None) -> dict:
    """Everything the UI and the PDF need, already localised."""
    sc = store().reference["scoring"]
    A, B = names
    pa, pb = _points(ca), _points(cb)
    asp = cross_aspects(pa, pb, sc)
    ov_ab = overlays(ca, pb, sc)     # B's planets in A's houses
    ov_ba = overlays(cb, pa, sc)     # A's planets in B's houses
    pairs = sign_pairs(ca, cb)
    western, dims = score(asp, [ov_ab, ov_ba], pairs, sc,
                          times_known=int(bool(ca["meta"]["time_known"])) + int(bool(cb["meta"]["time_known"])))

    va, vb = ca["vedic"], cb["vedic"]
    moon = lambda v: {"sign": v["points"]["moon"]["sign"], "nak": v["moon_nakshatra"]["index"],  # noqa: E731
                      "deg": v["points"]["moon"]["deg"], "pada": v["moon_nakshatra"]["pada"]}
    ak = ashtakoota(moon(va), moon(vb), policy)
    vedic_pct = ak["total"] / 36 * 100
    ov = sc.get("overall") or {"western_weight": 0.6, "vedic_weight": 0.4}
    overall = round(ov["western_weight"] * western + ov["vedic_weight"] * vedic_pct)
    bands = ov.get("bands") or {}
    oband = next((b for b, r in bands.items() if r["min"] <= overall <= r["max"]), "needs_effort")
    ma, mb = manglik(ca), manglik(cb)
    mstate = "both" if ma["is"] and mb["is"] else "one" if ma["is"] or mb["is"] else "none"
    comp = composite(ca, cb)

    def xy(x_is_a: bool) -> tuple[str, str]:
        return (A, B) if x_is_a else (B, A)

    T = lambda e, x="", y="": _text(e, lang, x, y)  # noqa: E731
    return {
        "names": [A, B], "policy": policy,
        "overall": overall, "overall_band": oband, "overall_entry": T(store().get("combined", "overall_band", oband)),
        "western_score": western, "vedic_percent": round(vedic_pct), "ashtakoota_total": ak["total"],
        "dimensions": [{"key": k, "score": v, "level": level(v),
                        "entry": T(store().get("combined", "dimension", k, level(v)))} for k, v in dims.items()],
        "aspects": [{"a": a["a"], "b": a["b"], "type": a["type"], "orb": a["orb"],
                     "nature": "soft" if a["contrib"] > 0.05 else "hard" if a["contrib"] < -0.05 else "neutral",
                     "weight": round(a["contrib"], 3), "entry": T(a["entry"], *xy(a["x_is_a"]))}
                    for a in asp if not a["generational"]],
        "overlays": {"ab": [{"planet": o["planet"], "house": o["house"], "entry": T(o["entry"], B, A)} for o in ov_ab]
                     if ov_ab is not None else None,
                     "ba": [{"planet": o["planet"], "house": o["house"], "entry": T(o["entry"], A, B)} for o in ov_ba]
                     if ov_ba is not None else None},
        "sign_pairs": [{"kind": p["kind"], "score": p["score"], "entry": T(p["entry"], *xy(p["x_is_a"]))} for p in pairs],
        "balance": [{"group": b["group"], "name": b["name"], "level": b["level"], "share": b["share"],
                     "entry": T(b["entry"])} for b in balance(ca, cb)],
        "composite": {"asc": T(comp["asc"]["entry"]) if comp["asc"] else None,
                      "planets": [{"planet": p["planet"], "sign": p["sign"], "house": p["house"],
                                   "sign_entry": T(p["sign_entry"]), "house_entry": T(p["house_entry"])}
                                  for p in comp["planets"]]},
        "vedic": {
            "total": ak["total"], "points": ak["points"],
            "kootas": [{"key": k["key"], "points": k["points"], "max": k["max"], "band": k["band"],
                        "entry": T(k["entry"]),
                        "types": [T(e) for e in ak["type_entries"].get(k["key"], (None, None))]} for k in ak["kootas"]],
            "score_band": T(ak["score_band"]), "doshas": [T(d) for d in ak["doshas"] if d],
            "cancels": [T(c) for c in ak["cancels"] if c], "moon_relation": T(ak["moon_relation"]),
            "tara": [T(t) for t in ak["tara"]], "yoni_pair": T(ak["yoni_pair"]),
            "manglik": {"state": mstate, "entry": T(store().get("vedic", "manglik", mstate)),
                        "people": [{"is": m["is"], "house": m["house"], "from_lagna": m["from_lagna"] is not None,
                                    "entry": T(m["house_entry"])} for m in (ma, mb)]},
            "moons": [{"sign": m["sign"], "nak": m["nak"]} for m in (moon(va), moon(vb))],
        },
        "time_known": [ca["meta"]["time_known"], cb["meta"]["time_known"]],
        "footer": footer(lang, **(footer_ctx or {})),
    }


def footer(lang: str, booking: str | None = None, instagram: str | None = None) -> str:
    """Mandatory closing note of the compatibility database (never shortened or reworded)."""
    bi = (store().reference.get("_bot_instructions") or {}).get("report_footer") or {}
    text = bi.get(lang) or bi.get("ar")
    if not text:
        e = store().get("combined", "footer", "report")
        text = ((e or {}).get(lang) or {}).get("text") or ""
    for ph, val in (("{BOT_BOOKING_COMMAND}", booking), ("{INSTAGRAM_HANDLE}", instagram)):
        if val:
            text = text.replace(ph, val)
        else:
            text = text.replace(f" ({ph})", "").replace(f"({ph})", "").replace(ph, "")
    return text
