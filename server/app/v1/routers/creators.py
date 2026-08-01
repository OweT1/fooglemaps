from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils import get_db_session
from db import CreatorResponse, Creator

router = APIRouter()


@router.get("/", response_model=list[CreatorResponse])
async def list_creators(session: AsyncSession = Depends(get_db_session)):
    logger.debug("Listing creators")
    result = await session.execute(select(Creator).order_by(Creator.created_at.desc()))
    creators = result.scalars().all()
    return [
        CreatorResponse(
            id=str(c.id),
            username=c.username,
            is_active=c.is_active,
            last_checked_at=c.last_checked_at,
            created_at=c.created_at,
        )
        for c in creators
    ]
