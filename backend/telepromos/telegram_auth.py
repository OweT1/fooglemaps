import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode

from fastapi import Depends, HTTPException, Request
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commons import settings
from commons.db import get_db_session
from telepromos.models import TelegramUser


def _hmac_sha256(key: bytes, message: str | bytes) -> bytes:
    if isinstance(message, str):
        message = message.encode()
    return hmac.new(key, message, hashlib.sha256).digest()


def _secret_key(bot_token: str) -> bytes:
    return _hmac_sha256(b"WebAppData", bot_token)


def _data_check_string(params: dict[str, str]) -> str:
    ordered = sorted((k, v) for k, v in params.items() if k != "hash")
    return "\n".join(f"{k}={v}" for k, v in ordered)


def build_init_data(user: dict, bot_token: str | None = None, auth_date: int | None = None) -> str:
    """Build a signed initData string (used for local dev and tests)."""
    token = bot_token or settings.telegram_bot_token
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    if auth_date is None:
        auth_date = int(datetime.now(timezone.utc).timestamp())

    params = {
        "auth_date": str(auth_date),
        "query_id": "AA_dev",
        "user": json.dumps(user, separators=(",", ":")),
    }
    params["hash"] = _hash_for(token, params)
    # Telegram encodes the payload with URL encoding (use_plus=False → no '+').
    return urlencode(params)


def _hash_for(bot_token: str, params: dict[str, str]) -> str:
    return _hmac_sha256(_secret_key(bot_token), _data_check_string(params)).hex()


def validate_init_data(init_data: str) -> dict:
    """Validate Telegram WebApp initData and return the decoded user object."""
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing X-Telegram-Init-Data")

    params = dict(parse_qsl(init_data, keep_blank_values=True))
    expected = params.get("hash")
    if not expected:
        raise HTTPException(status_code=401, detail="Missing initData hash")

    token = settings.telegram_bot_token or ""
    actual = _hash_for(token, params)
    if not hmac.compare_digest(actual, expected):
        raise HTTPException(status_code=401, detail="Invalid initData signature")

    auth_date = params.get("auth_date")
    if auth_date:
        age_seconds = datetime.now(timezone.utc).timestamp() - int(auth_date)
        if age_seconds > settings.telegram_initdata_max_age_seconds:
            raise HTTPException(status_code=401, detail="InitData expired")

    try:
        user = json.loads(params.get("user", "{}"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid initData user")
    if not isinstance(user, dict) or user.get("id") is None:
        raise HTTPException(status_code=401, detail="Invalid initData user")
    return user


async def get_current_telegram_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> TelegramUser:
    user = validate_init_data(request.headers.get("X-Telegram-Init-Data", ""))
    telegram_id = int(user["id"])

    result = await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
    )
    row = result.scalar_one_or_none()

    if row:
        row.username = user.get("username")
        row.first_name = user.get("first_name")
        await session.commit()
        return row

    row = TelegramUser(
        telegram_id=telegram_id,
        username=user.get("username"),
        first_name=user.get("first_name"),
    )
    session.add(row)
    await session.commit()
    logger.info("Created telegram user: {}", telegram_id)
    return row