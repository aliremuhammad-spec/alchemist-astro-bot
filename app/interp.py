"""Interpretation database (Astro Interpretation Database, AR/EN).

The content is private: it is NOT shipped in this public repository. An admin uploads it once from the
dashboard (.sqlite, .json or .json.gz export); it is stored in Postgres and kept in memory for lookups.
"""
from __future__ import annotations

import gzip
import json
import logging
import sqlite3
import tempfile

from . import db

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS interp_entries (
  id TEXT PRIMARY KEY, system TEXT NOT NULL, category TEXT NOT NULL,
  k1 TEXT, k2 TEXT, k3 TEXT, tone TEXT, data JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS interp_lookup ON interp_entries(system, category, k1, k2, k3);
"""

_index: dict[tuple, dict] = {}
_meta: dict = {}
_reference: dict = {}


def _norm(v):
    if v is None:
        return None
    v = str(v)
    return None if v in ("", "None", "null") else v


def parse_upload(raw: bytes, filename: str = "") -> dict:
    """Accepts the SQLite file, the JSON export, or our compact .json.gz; returns {meta, reference, entries}."""
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    if raw[:15] == b"SQLite format 3":
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as f:
            f.write(raw)
            f.flush()
            c = sqlite3.connect(f.name)
            cols = [d[0] for d in c.execute("SELECT * FROM entries LIMIT 1").description]
            entries = [dict(zip(cols, r)) for r in c.execute("SELECT * FROM entries")]
            reference = {n: json.loads(j) for n, j in c.execute("SELECT name, json FROM reference")}
            meta = json.loads(c.execute("SELECT json FROM meta").fetchone()[0])
            c.close()
        for e in entries:
            e["extra"] = json.loads(e["extra"]) if e.get("extra") else {}
        return {"meta": meta, "reference": reference, "entries": entries}
    data = json.loads(raw.decode("utf-8"))
    if "entries" in data and isinstance(data["entries"], list):
        return data
    raise ValueError("unsupported file: upload astro_db.sqlite or its .json.gz export")


def _row_to_data(e: dict) -> dict:
    if "ar" in e and isinstance(e["ar"], dict):
        ar, en = e["ar"], e["en"]
    else:
        ar = {k: e.get(f"ar_{k}") for k in ("title", "summary", "text", "advice")}
        en = {k: e.get(f"en_{k}") for k in ("title", "summary", "text", "advice")}
    return {"ar": ar, "en": en, "extra": e.get("extra") or {}}


async def import_payload(payload: dict) -> int:
    rows = []
    for e in payload["entries"]:
        rows.append((e["id"], e["system"], e["category"], _norm(e.get("k1")), _norm(e.get("k2")), _norm(e.get("k3")),
                     _norm(e.get("tone")), json.dumps(_row_to_data(e), ensure_ascii=False)))
    async with db.pool().acquire() as c:
        async with c.transaction():
            await c.execute(SCHEMA)
            await c.execute("DELETE FROM interp_entries")
            await c.executemany(
                "INSERT INTO interp_entries(id,system,category,k1,k2,k3,tone,data) VALUES($1,$2,$3,$4,$5,$6,$7,$8::jsonb)",
                rows)
    await db.kv_set("interp_meta", json.dumps(payload.get("meta") or {}, ensure_ascii=False))
    await db.kv_set("interp_reference", json.dumps(payload.get("reference") or {}, ensure_ascii=False))
    await load()
    return len(rows)


async def load() -> int:
    global _meta, _reference
    await db.pool().execute(SCHEMA)
    rows = await db.pool().fetch("SELECT system, category, k1, k2, k3, tone, data FROM interp_entries")
    idx = {}
    for r in rows:
        d = r["data"] if isinstance(r["data"], dict) else json.loads(r["data"])
        d["tone"] = r["tone"]
        idx[(r["system"], r["category"], r["k1"], r["k2"], r["k3"])] = d
    _index.clear()
    _index.update(idx)
    _meta = json.loads(await db.kv_get("interp_meta", "{}"))
    _reference = json.loads(await db.kv_get("interp_reference", "{}"))
    log.info("interpretations loaded: %d", len(_index))
    return len(_index)


def ready() -> bool:
    return bool(_index)


def status() -> dict:
    return {"entries": len(_index), "version": _meta.get("version"), "generated": _meta.get("generated")}


def get(system: str, category: str, k1=None, k2=None, k3=None) -> dict | None:
    key = (system, category, _norm(k1), _norm(k2), _norm(k3))
    return _index.get(key)


def get_pair(system: str, category: str, a: str, b: str, k3=None) -> dict | None:
    """Pairs are stored in canonical planet order; try both orders."""
    return get(system, category, a, b, k3) or get(system, category, b, a, k3)


def offsets_for(aspector: str) -> list[int]:
    """Drishti offsets the database defines for a planet (7 for all, specials for Mars/Jupiter/Saturn/nodes)."""
    return sorted({int(k[4]) for k in _index if k[1] == "drishti" and k[2] == aspector and k[4] and k[4].isdigit()})


def load_for_tests(payload: dict) -> None:
    """Index a payload in memory without a database (tests / local previews)."""
    _index.clear()
    for e in payload["entries"]:
        d = _row_to_data(e)
        d["tone"] = _norm(e.get("tone"))
        _index[(e["system"], e["category"], _norm(e.get("k1")), _norm(e.get("k2")), _norm(e.get("k3")))] = d
    _meta.clear()
    _meta.update(payload.get("meta") or {})
