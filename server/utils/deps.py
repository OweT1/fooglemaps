import os
from typing import AsyncGenerator
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session_factory

security = HTTPBearer(auto_error=False)


async def verify_google_token(credentials=Depends(security)):
    if not credentials:
        logger.warning("Missing token in request")
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {credentials.credentials}"},
            timeout=10,
        )
        if resp.status_code != 200:
            logger.warning("Invalid access token: {}", resp.text)
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user_info = resp.json()
        logger.debug("Token verified for sub={}", user_info.get("sub"))
        return user_info
    except requests.RequestException as e:
        logger.warning("Failed to verify token: {}", e)
        raise HTTPException(status_code=401, detail="Token verification failed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = await get_session_factory()
    async with factory() as session:
        logger.trace("DB session yielded")
        yield session
        logger.trace("DB session closed")
