import os
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session_factory

security = HTTPBearer(auto_error=False)


async def verify_google_token(credentials=Depends(security)):
    if not credentials:
        logger.warning("Missing token in request")
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        info = id_token.verify_oauth2_token(
            credentials.credentials,
            requests.Request(),
            os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        )
        logger.debug("Token verified for sub={}", info.get("sub"))
        return info
    except ValueError as e:
        logger.warning("Invalid or expired token: {}", e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = await get_session_factory()
    async with factory() as session:
        logger.trace("DB session yielded")
        yield session
        logger.trace("DB session closed")
