"""Rule-based yoga detection on the sidereal (whole-sign) chart.

Keys match the interpretation database (vedic.yoga.<key>). Rules follow the `extra.detect` notes of each
entry, simplified where schools differ. Yogas that need data we do not collect (gender, combustion
degrees) are not detected.
"""
from __future__ import annotations

from ..astro.names import SIGN_KEYS

LORDS = {"aries": "mars", "taurus": "venus", "gemini": "mercury", "cancer": "moon", "leo": "sun",
         "virgo": "mercury", "libra": "venus", "scorpio": "mars", "sagittarius": "jupiter",
         "capricorn": "saturn", "aquarius": "saturn", "pisces": "jupiter"}
EXALT = {"sun": "aries", "moon": "taurus", "mars": "capricorn", "mercury": "virgo", "jupiter": "cancer",
         "venus": "pisces", "saturn": "libra", "rahu": "taurus", "ketu": "scorpio"}
DEBIL = {"sun": "libra", "moon": "scorpio", "mars": "cancer", "mercury": "pisces", "jupiter": "capricorn",
         "venus": "virgo", "saturn": "aries", "rahu": "scorpio", "ketu": "taurus"}
GRAHAS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
SEVEN = GRAHAS[:7]
BENEFICS = {"mercury", "jupiter", "venus"}
MALEFICS = {"sun", "mars", "saturn", "rahu", "ketu"}
DRISHTI = {"mars": (4, 7, 8), "jupiter": (5, 7, 9), "saturn": (3, 7, 10), "rahu": (5, 7, 9), "ketu": (5, 7, 9)}
KENDRA, TRIKONA, DUSTHANA = (1, 4, 7, 10), (1, 5, 9), (6, 8, 12)


class Chart:
    def __init__(self, signs: dict[str, int], lagna: int):
        self.s = signs          # graha -> sign index
        self.L = lagna          # lagna sign index

    def h(self, p: str, ref: str | None = None) -> int:
        base = self.L if ref is None else self.s[ref]
        return (self.s[p] - base) % 12 + 1

    def in_house(self, house: int, ref: str | None = None) -> list[str]:
        return [p for p in GRAHAS if self.h(p, ref) == house]

    def lord(self, house: int) -> str:
        return LORDS[SIGN_KEYS[(self.L + house - 1) % 12]]

    def owned(self, p: str) -> list[int]:
        return [n for n in range(1, 13) if self.lord(n) == p]

    def sign(self, p: str) -> str:
        return SIGN_KEYS[self.s[p]]

    def conj(self, a: str, b: str) -> bool:
        return a != b and self.s[a] == self.s[b]

    def aspects(self, a: str, b: str) -> bool:
        return a != b and ((self.s[b] - self.s[a]) % 12 + 1) in DRISHTI.get(a, (7,))

    def exchange(self, a: str, b: str) -> bool:
        return a != b and LORDS[self.sign(a)] == b and LORDS[self.sign(b)] == a

    def linked(self, a: str, b: str) -> bool:
        return a != b and (self.conj(a, b) or self.exchange(a, b) or (self.aspects(a, b) and self.aspects(b, a)))

    def dignity(self, p: str) -> str:
        if EXALT.get(p) == self.sign(p):
            return "exalted"
        if DEBIL.get(p) == self.sign(p):
            return "debilitated"
        if LORDS[self.sign(p)] == p:
            return "own"
        return ""

    def strong(self, p: str) -> bool:
        return self.dignity(p) in ("exalted", "own") or (self.h(p) in KENDRA + TRIKONA and self.dignity(p) != "debilitated")

    def weak(self, p: str) -> bool:
        return self.dignity(p) == "debilitated" or self.h(p) in DUSTHANA


def detect(signs: dict[str, int], lagna: int) -> list[tuple[str, str]]:
    """Returns [(yoga_key, short_reason)]; reason is a compact English note used for debugging/tests."""
    c = Chart(signs, lagna)
    out: list[tuple[str, str]] = []

    def add(key: str, why: str = ""):
        out.append((key, why))

    # Pancha Mahapurusha
    for key, p, signs_ in (("ruchaka", "mars", ("aries", "scorpio", "capricorn")),
                           ("bhadra", "mercury", ("gemini", "virgo")),
                           ("hamsa", "jupiter", ("sagittarius", "pisces", "cancer")),
                           ("malavya", "venus", ("taurus", "libra", "pisces")),
                           ("shasha", "saturn", ("capricorn", "aquarius", "libra"))):
        if c.sign(p) in signs_ and c.h(p) in KENDRA:
            add(key, f"{p} in {c.sign(p)} house {c.h(p)}")

    # Moon yogas
    if c.h("jupiter", "moon") in KENDRA:
        add("gajakesari", f"jupiter {c.h('jupiter', 'moon')} from moon")
    pl = [p for p in ("mars", "mercury", "jupiter", "venus", "saturn")]
    second = [p for p in pl if c.h(p, "moon") == 2]
    twelfth = [p for p in pl if c.h(p, "moon") == 12]
    if second and twelfth:
        add("durudhara", f"{second} / {twelfth}")
    elif second:
        add("sunapha", f"{second}")
    elif twelfth:
        add("anapha", f"{twelfth}")
    elif not [p for p in pl if c.conj(p, "moon")]:
        add("kemadruma", "2nd/12th from moon empty")
    if c.conj("moon", "mars") or (c.aspects("moon", "mars") and c.aspects("mars", "moon")):
        add("chandra_mangala")
    adhi = [p for p in BENEFICS if c.h(p, "moon") in (6, 7, 8)]
    if len(adhi) >= 2:
        add("adhi", f"{adhi}")
    if c.h("moon", "jupiter") in (6, 8, 12):
        add("shakata", f"moon {c.h('moon', 'jupiter')} from jupiter")
    if len([p for p in BENEFICS if c.h(p) in (3, 6, 10, 11)]) >= 2:
        add("vasumati")

    # Sun yogas
    sp = ["mars", "mercury", "jupiter", "venus", "saturn"]
    v2 = [p for p in sp if c.h(p, "sun") == 2]
    v12 = [p for p in sp if c.h(p, "sun") == 12]
    if v2 and v12:
        add("ubhayachari", f"{v2} / {v12}")
    elif v2:
        add("vesi", f"{v2}")
    elif v12:
        add("vosi", f"{v12}")
    if c.conj("sun", "mercury"):
        add("budha_aditya")

    # Raja / lordship yogas
    l9, l10 = c.lord(9), c.lord(10)
    if l9 != l10 and c.linked(l9, l10):
        add("dharma_karmadhipati", f"{l9}-{l10}")
    kt = [(a, b) for a in {c.lord(n) for n in (4, 7, 10)} for b in {c.lord(n) for n in (5, 9)} if c.linked(a, b)]
    if kt:
        add("kendra_trikona", f"{kt}")
    yk = [p for p in SEVEN if set(c.owned(p)) & {4, 7, 10} and set(c.owned(p)) & {5, 9}]
    if yk:
        add("yogakaraka", f"{yk}")

    # Neecha bhanga (simplified: dispositor or exaltation-lord of the debilitation sign in a kendra)
    for p in SEVEN:
        if c.dignity(p) != "debilitated":
            continue
        disp = LORDS[c.sign(p)]
        ex_lord = next((q for q, s in EXALT.items() if s == c.sign(p) and q in SEVEN), None)
        cancel = [q for q in {disp, ex_lord} if q and (c.h(q) in KENDRA or c.h(q, "moon") in KENDRA)]
        if cancel:
            add("neecha_bhanga", f"{p} cancelled by {cancel}")
            break

    # Parivartana
    seen = set()
    good = {1, 2, 4, 5, 7, 9, 10, 11}
    for a in SEVEN:
        for b in SEVEN:
            if a < b and c.exchange(a, b) and (a, b) not in seen:
                seen.add((a, b))
                houses = {c.h(a), c.h(b)}
                if houses & {6, 8, 12}:
                    add("dainya_parivartana", f"{a}<->{b}")
                elif 3 in houses:
                    add("khala_parivartana", f"{a}<->{b}")
                elif houses <= good:
                    add("maha_parivartana", f"{a}<->{b}")

    # Viparita raja
    for key, n in (("harsha", 6), ("sarala", 8), ("vimala", 12)):
        if c.h(c.lord(n)) in DUSTHANA:
            add(key, f"lord{n} {c.lord(n)} in {c.h(c.lord(n))}")

    # Wealth
    dl = {c.lord(n) for n in (2, 5, 9, 11)}
    dpairs = [(a, b) for a in dl for b in dl if a < b and c.linked(a, b)]
    if dpairs:
        add("dhana", f"{dpairs}")
    ll = c.lord(1)
    if c.dignity(l9) in ("exalted", "own") and c.h(l9) in KENDRA + TRIKONA and c.strong(ll):
        add("lakshmi")
    if c.h(c.lord(11)) in DUSTHANA and c.weak(ll):
        add("daridra")
    if all(c.h(p) in (1, 2, 4, 5, 7, 9, 10) for p in ("jupiter", "venus", "mercury")) and c.strong("jupiter"):
        add("saraswati")
    tenth = c.in_house(10)
    if tenth and all(p in BENEFICS for p in tenth):
        add("amala")
    kend = [p for p in GRAHAS if c.h(p) in KENDRA]
    if (any(p in BENEFICS for p in kend) and not any(p in MALEFICS for p in kend)
            and all(p in BENEFICS for p in c.in_house(6) + c.in_house(8))):
        add("parvata")
    if c.strong(ll):
        if (c.s[c.lord(4)] - c.s[l9]) % 12 + 1 in KENDRA:
            add("kahala")
        if (c.s[c.lord(5)] - c.s[c.lord(6)]) % 12 + 1 in KENDRA:
            add("shankha")
    if c.h("jupiter") in (2, 5) and all(c.conj(p, "jupiter") or c.aspects(p, "jupiter") for p in ("mercury", "venus")):
        add("kalanidhi")
    if c.dignity(ll) == "exalted" and c.h(ll) in KENDRA and (c.aspects("jupiter", ll) or c.conj("jupiter", ll)):
        add("chamara")

    # Kartari around the lagna
    h2, h12 = c.in_house(2), c.in_house(12)
    if h2 and h12:
        if all(p in BENEFICS for p in h2 + h12):
            add("shubha_kartari")
        elif all(p in MALEFICS for p in h2 + h12):
            add("papa_kartari")

    # Doshas / node yogas
    r = c.s["rahu"]
    arc = [(c.s[p] - r) % 12 for p in SEVEN]
    if all(0 < x < 6 for x in arc) or all(6 < x < 12 for x in arc):
        add("kala_sarpa")
    if c.conj("jupiter", "rahu") or c.conj("jupiter", "ketu"):
        add("guru_chandala")
    if c.conj("saturn", "rahu"):
        add("shrapit")
    if any(c.conj(a, n) for a in ("sun", "moon") for n in ("rahu", "ketu")):
        add("grahan")
    if c.conj("mars", "rahu"):
        add("angaraka")
    if c.conj("saturn", "moon") or (c.aspects("saturn", "moon") and c.aspects("moon", "saturn")):
        add("vish")
    if c.h("mars") in (1, 2, 4, 7, 8, 12):
        add("kuja_dosha", f"mars in {c.h('mars')}")
    if c.conj("sun", "rahu") or c.conj("sun", "saturn") or c.h("rahu") == 9:
        add("pitra_dosha")
    kd = [p for p in ("mercury", "jupiter", "venus") if set(c.owned(p)) & {4, 7, 10} and not set(c.owned(p)) & {1, 5, 9}]
    if kd:
        add("kendradhipati", f"{kd}")
    return out
