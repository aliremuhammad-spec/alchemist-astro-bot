"""Telegram Mini App initData validation (HMAC-SHA256, per core.telegram.org/bots/webapps)."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException

from .config import settings

MAX_AGE = 24 * 3600


def validate_init_data(init_data: str, bot_token: str, max_age: int = MAX_AGE) -> dict:
    pairs = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=False))
    received = pairs.pop("hash", None)
    if not received:
        raise ValueError("no hash")
    check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received):
        raise ValueError("bad hash")
    auth_date = int(pairs.get("auth_date", "0"))
    if max_age and time.time() - auth_date > max_age:
        raise ValueError("expired")
    user = json.loads(pairs.get("user", "{}"))
    if not user.get("id"):
        raise ValueError("no user")
    return {"user": user, "start_param": pairs.get("start_param"), "auth_date": auth_date}


async def tg_user(authorization: str = Header(default="")) -> dict:
    """FastAPI dependency: `Authorization: tma <initData>`."""
    if settings.dev_auth and authorization.startswith("dev "):
        uid = int(authorization[4:] or 1)
        return {"user": {"id": uid, "first_name": "Dev", "language_code": "ar"}, "start_param": None}
    if not authorization.startswith("tma "):
        raise HTTPException(401, "missing initData")
    try:
        return validate_init_data(authorization[4:], settings.bot_token)
    except ValueError as e:
        raise HTTPException(401, f"invalid initData: {e}")
