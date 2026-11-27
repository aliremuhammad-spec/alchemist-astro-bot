"""Restore a nightly backup into a database.

    DATABASE_URL=postgresql://... python scripts/restore_backup.py alchemist-backup-....json.gz [--wipe]

Runs app/schema.sql first (so an empty Neon database works), then inserts every table in order.
Existing rows are kept (ON CONFLICT DO NOTHING) unless --wipe is given, which empties the
backed-up tables first. Interpretation DBs are not in the backup: upload them again from the admin panel."""
import asyncio
import gzip
import json
import os
import sys
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parent.parent


async def main(path: str, wipe: bool) -> None:
    doc = json.loads(gzip.decompress(Path(path).read_bytes()))
    tables: dict = doc["tables"]
    con = await asyncpg.connect(os.environ["DATABASE_URL"], statement_cache_size=0)
    try:
        await con.execute((ROOT / "app" / "schema.sql").read_text())
        async with con.transaction():
            if wipe:
                await con.execute("TRUNCATE " + ", ".join(tables) + " CASCADE")
            for t, rows in tables.items():
                if not rows:
                    continue
                n = await con.fetchval(
                    f"WITH ins AS (INSERT INTO {t} SELECT * FROM json_populate_recordset(NULL::{t}, $1::json) "
                    f"ON CONFLICT DO NOTHING RETURNING 1) SELECT count(*) FROM ins", json.dumps(rows))
                print(f"{t}: {n}/{len(rows)}")
            # move id sequences past the restored ids
            for t in tables:
                seq = await con.fetchval(
                    "SELECT pg_get_serial_sequence($1, 'id') WHERE EXISTS (SELECT 1 FROM information_schema.columns "
                    "WHERE table_name=$1 AND column_name='id')", t)
                if seq:
                    await con.execute(f"SELECT setval('{seq}', GREATEST((SELECT COALESCE(max(id), 0) FROM {t}), 1))")
    finally:
        await con.close()
    print("done, backup from", doc.get("created_at"))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1], "--wipe" in sys.argv))
