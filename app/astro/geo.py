"""Continent -> country -> city lookup over the prebuilt GeoNames files."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from .names import CONTINENTS

GEO_DIR = Path(os.getenv("GEO_DIR", Path(__file__).resolve().parents[2] / "data" / "geo"))


@lru_cache(maxsize=1)
def countries() -> list[dict]:
    return json.loads((GEO_DIR / "countries.json").read_text())


def continents(lang: str) -> list[dict]:
    order = ["AS", "AF", "EU", "NA", "SA", "OC"]
    return [{"code": c, "name": CONTINENTS[c][0 if lang == "ar" else 1]} for c in order]


def countries_in(continent: str) -> list[dict]:
    return [{"iso": c["iso"], "name": c["name"]} for c in countries() if c["continent"] == continent]


@lru_cache(maxsize=24)
def _cities(cc: str) -> list[list]:
    p = GEO_DIR / "cities" / f"{cc.upper()}.json"
    if not cc.isalpha() or len(cc) != 2 or not p.exists():
        return []
    return json.loads(p.read_text())


def _row(r: list) -> dict:
    return {"id": r[0], "name": r[1], "ar": r[2], "lat": r[3], "lng": r[4], "tz": r[5], "pop": r[6]}


def search_cities(cc: str, q: str = "", limit: int = 60) -> list[dict]:
    q = (q or "").strip().lower()
    out = []
    for r in _cities(cc):
        if not q or q in r[1].lower() or (r[2] and q in r[2]):
            out.append(_row(r))
            if len(out) >= limit:
                break
    return out


def city_by_id(cc: str, city_id: int) -> dict | None:
    for r in _cities(cc):
        if r[0] == city_id:
            return _row(r)
    return None
