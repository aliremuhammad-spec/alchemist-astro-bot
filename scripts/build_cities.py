"""Build compact per-country city files from GeoNames (via the geonamescache package).

Run at image build time:  python scripts/build_cities.py data/geo
Output: countries.json + cities/<CC>.json (sorted by population, biggest first).
"""
import json
import re
import sys
from pathlib import Path

import geonamescache

ARABIC = re.compile(r"^[؀-ۿ\s\-']+$")


def main(out_dir: str) -> None:
    out = Path(out_dir)
    (out / "cities").mkdir(parents=True, exist_ok=True)
    gc = geonamescache.GeonamesCache(min_city_population=1000)
    countries = gc.get_countries()
    by_cc: dict[str, list] = {}
    for c in gc.get_cities().values():
        cands = [n for n in c.get("alternatenames", []) if n and ARABIC.match(n)]
        ar = next((n for n in cands if " " not in n), cands[0] if cands else "")
        by_cc.setdefault(c["countrycode"], []).append(
            [c["geonameid"], c["name"], ar, round(c["latitude"], 4), round(c["longitude"], 4),
             c["timezone"], c["population"]])
    meta = []
    for cc, info in countries.items():
        cities = sorted(by_cc.get(cc, []), key=lambda r: -r[6])
        if not cities:
            continue
        (out / "cities" / f"{cc}.json").write_text(json.dumps(cities, ensure_ascii=False, separators=(",", ":")))
        meta.append({"iso": cc, "name": info["name"], "continent": info["continentcode"], "n": len(cities)})
    meta.sort(key=lambda m: m["name"])
    (out / "countries.json").write_text(json.dumps(meta, ensure_ascii=False))
    print(f"{len(meta)} countries, {sum(m['n'] for m in meta)} cities -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/geo")
