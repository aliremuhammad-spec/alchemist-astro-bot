"""Per-user sliding-window limits for CPU-heavy endpoints (the free instance has 0.1 CPU, so one script
hammering /api/chart would slow the bot down for everyone)."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException

from .config import settings

_hits: dict[tuple[int, str], deque] = defaultdict(deque)
LIMITS = {"chart": (12, 60), "view": (40, 60), "synastry": (10, 60), "light": (60, 60)}


def check(uid: int, kind: str) -> None:
    if uid in settings.admin_ids:
        return
    n, window = LIMITS[kind]
    q = _hits[(uid, kind)]
    now = time.monotonic()
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= n:
        raise HTTPException(429, "too_many_requests")
    q.append(now)
    if len(_hits) > 50_000:  # keep memory bounded
        for k in [k for k, v in _hits.items() if not v or now - v[-1] > 600]:
            _hits.pop(k, None)
