import os
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session_factory

security = HTTPBearer(auto_error=False)


async def verify_google_token(credentials=Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        info = id_token.verify_oauth2_token(
            credentials.credentials,
            requests.Request(),
            os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        )
        return info
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = await get_session_factory()
    async with factory() as session:
        yield session
