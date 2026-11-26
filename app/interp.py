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
CREATE TABLE IF NOT EXISTS {table} (
  id TEXT PRIMARY KEY, system TEXT NOT NULL, category TEXT NOT NULL,
  k1 TEXT, k2 TEXT, k3 TEXT, tone TEXT, data JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS {table}_lookup ON {table}(system, category, k1, k2, k3);
"""

_index: dict[tuple, dict] = {}
_meta: dict = {}
_reference: dict = {}


def _norm(v):
    if v is None:
        return None
    v = str(v)
    return None if v in ("", "None", "null") else v


def kind_of(payload: dict) -> str:
    """'compat' for the compatibility database, 'natal' for the chart-interpretation database."""
    name = str((payload.get("meta") or {}).get("name", "")).lower()
    if "compat" in name or any(e.get("category") == "syn_aspect" for e in payload["entries"][:400]):
        return "compat"
    return "natal"


def _flatten_tree(data: dict) -> list[dict]:
    """The compat JSON is a tree (western/vedic/combined -> category -> keys...); leaves carry an 'id'."""
    out = []

    def walk(node, system, category, keys):
        if isinstance(node, dict) and "id" in node and ("ar" in node or "en" in node):
            ks = (keys + [None, None, None])[:3]
            out.append({"id": node["id"], "system": system, "category": category, "k1": ks[0], "k2": ks[1],
                        "k3": ks[2], "tone": node.get("tone"), "ar": node.get("ar") or {}, "en": node.get("en") or {},
                        "extra": node.get("extra") or {}})
            return
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, system, category, keys + [k])
    for system in ("western", "vedic", "combined"):
        for category, node in (data.get(system) or {}).items():
            walk(node, system, category, [])
    return out


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
            try:
                bi = c.execute("SELECT json FROM bot_instructions").fetchone()
                if bi:
                    reference["_bot_instructions"] = json.loads(bi[0])
            except sqlite3.OperationalError:
                pass
            c.close()
        for e in entries:
            e["extra"] = json.loads(e["extra"]) if e.get("extra") else {}
        return {"meta": meta, "reference": reference, "entries": entries}
    data = json.loads(raw.decode("utf-8"))
    if "entries" in data and isinstance(data["entries"], list):
        return data
    if "western" in data and "reference" in data:  # hierarchical compat export
        ref = dict(data["reference"])
        if data.get("bot_instructions"):
            ref["_bot_instructions"] = data["bot_instructions"]
        return {"meta": data.get("meta") or {}, "reference": ref, "entries": _flatten_tree(data)}
    raise ValueError("unsupported file: upload astro_db.sqlite or its .json.gz export")


def _row_to_data(e: dict) -> dict:
    if "ar" in e and isinstance(e["ar"], dict):
        ar, en = e["ar"], e["en"]
    else:
        ar = {k: e.get(f"ar_{k}") for k in ("title", "summary", "text", "advice")}
        en = {k: e.get(f"en_{k}") for k in ("title", "summary", "text", "advice")}
    return {"ar": ar, "en": en, "extra": e.get("extra") or {}}


class Store:
    """One interpretation database in Postgres + an in-memory index."""

    def __init__(self, table: str, kv_prefix: str):
        self.table, self.kv = table, kv_prefix
        self.index: dict[tuple, dict] = {}
        self.meta: dict = {}
        self.reference: dict = {}

    async def import_payload(self, payload: dict) -> int:
        rows = [(e["id"], e["system"], e["category"], _norm(e.get("k1")), _norm(e.get("k2")), _norm(e.get("k3")),
                 _norm(e.get("tone")), json.dumps(_row_to_data(e), ensure_ascii=False)) for e in payload["entries"]]
        async with db.pool().acquire() as c:
            async with c.transaction():
                await c.execute(SCHEMA.format(table=self.table))
                await c.execute(f"DELETE FROM {self.table}")
                await c.executemany(
                    f"INSERT INTO {self.table}(id,system,category,k1,k2,k3,tone,data) VALUES($1,$2,$3,$4,$5,$6,$7,$8::jsonb)",
                    rows)
        await db.kv_set(f"{self.kv}_meta", json.dumps(payload.get("meta") or {}, ensure_ascii=False))
        await db.kv_set(f"{self.kv}_reference", json.dumps(payload.get("reference") or {}, ensure_ascii=False))
        await self.load()
        return len(rows)

    async def load(self) -> int:
        await db.pool().execute(SCHEMA.format(table=self.table))
        rows = await db.pool().fetch(f"SELECT id, system, category, k1, k2, k3, tone, data FROM {self.table}")
        idx = {}
        for r in rows:
            d = r["data"] if isinstance(r["data"], dict) else json.loads(r["data"])
            d["tone"], d["id"] = r["tone"], r["id"]
            idx[(r["system"], r["category"], r["k1"], r["k2"], r["k3"])] = d
            idx[("id", r["id"])] = d
        self.index.clear()
        self.index.update(idx)
        self.meta.clear()
        self.meta.update(json.loads(await db.kv_get(f"{self.kv}_meta", "{}")))
        self.reference.clear()
        self.reference.update(json.loads(await db.kv_get(f"{self.kv}_reference", "{}")))
        log.info("%s loaded: %d", self.table, len(rows))
        return len(rows)

    def load_payload(self, payload: dict) -> None:
        """Index a payload in memory without a database (tests / local previews)."""
        self.index.clear()
        for e in payload["entries"]:
            d = _row_to_data(e)
            d["tone"], d["id"] = _norm(e.get("tone")), e["id"]
            self.index[(e["system"], e["category"], _norm(e.get("k1")), _norm(e.get("k2")), _norm(e.get("k3")))] = d
            self.index[("id", e["id"])] = d
        self.meta.clear()
        self.meta.update(payload.get("meta") or {})
        self.reference.clear()
        self.reference.update(payload.get("reference") or {})

    def ready(self) -> bool:
        return bool(self.index)

    def status(self) -> dict:
        return {"entries": sum(1 for k in self.index if k[0] != "id"), "version": self.meta.get("version"),
                "generated": self.meta.get("generated")}

    def get(self, system: str, category: str, k1=None, k2=None, k3=None) -> dict | None:
        return self.index.get((system, category, _norm(k1), _norm(k2), _norm(k3)))

    def by_id(self, entry_id: str) -> dict | None:
        return self.index.get(("id", entry_id))


natal = Store("interp_entries", "interp")
compat = Store("compat_entries", "compat")
_index, _meta, _reference = natal.index, natal.meta, natal.reference


async def import_payload(payload: dict) -> int:
    return await (compat if kind_of(payload) == "compat" else natal).import_payload(payload)


async def load() -> int:
    n = await natal.load()
    await compat.load()
    return n


def ready() -> bool:
    return natal.ready()


def status() -> dict:
    return natal.status()


def get(system: str, category: str, k1=None, k2=None, k3=None) -> dict | None:
    return natal.get(system, category, k1, k2, k3)


def get_pair(system: str, category: str, a: str, b: str, k3=None) -> dict | None:
    """Pairs are stored in canonical planet order; try both orders."""
    return get(system, category, a, b, k3) or get(system, category, b, a, k3)


def offsets_for(aspector: str) -> list[int]:
    """Drishti offsets the database defines for a planet (7 for all, specials for Mars/Jupiter/Saturn/nodes)."""
    return sorted({int(k[4]) for k in natal.index if len(k) == 5 and k[1] == "drishti" and k[2] == aspector
                   and k[4] and k[4].isdigit()})


def load_for_tests(payload: dict) -> None:
    (compat if kind_of(payload) == "compat" else natal).load_payload(payload)
