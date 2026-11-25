from __future__ import annotations

from pathlib import Path

import asyncpg

from .config import settings

_pool: asyncpg.Pool | None = None


async def init(dsn: str | None = None) -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(dsn or settings.database_url, min_size=1, max_size=5,
                                      command_timeout=30)
    async with _pool.acquire() as c:
        await c.execute((Path(__file__).parent / "schema.sql").read_text())
    return _pool


def pool() -> asyncpg.Pool:
    assert _pool is not None, "db not initialised"
    return _pool


async def close() -> None:
    if _pool:
        await _pool.close()


async def upsert_user(uid: int, first_name: str | None, username: str | None, lang: str | None,
                      start_param: str | None = None) -> asyncpg.Record:
    lang = "ar" if (lang or "ar").startswith("ar") else ("en" if lang else "ar")
    return await pool().fetchrow(
        """INSERT INTO users (id, first_name, username, lang, start_param)
           VALUES ($1,$2,$3,$4,$5)
           ON CONFLICT (id) DO UPDATE SET first_name=EXCLUDED.first_name, username=EXCLUDED.username,
             last_seen=now(), blocked=FALSE
           RETURNING *""", uid, first_name, username, lang, start_param)


async def kv_get(key: str, default: str = "") -> str:
    v = await pool().fetchval("SELECT value FROM kv WHERE key=$1", key)
    return v if v is not None else default


async def kv_set(key: str, value: str) -> None:
    await pool().execute("INSERT INTO kv(key,value) VALUES($1,$2) ON CONFLICT(key) DO UPDATE SET value=$2",
                         key, value)


async def event(uid: int | None, name: str) -> None:
    await pool().execute("INSERT INTO events(user_id,name) VALUES($1,$2)", uid, name)


async def is_premium(uid: int) -> bool:
    return bool(await pool().fetchval(
        "SELECT 1 FROM subscriptions WHERE user_id=$1 AND ends_at > now() LIMIT 1", uid))
