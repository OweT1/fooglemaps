from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commons.db import get_db_session
from fooglemaps.models import Cuisine
from fooglemaps.schemas import CuisineResponse

router = APIRouter()


@router.get("/", response_model=list[CuisineResponse])
async def list_cuisines(session: AsyncSession = Depends(get_db_session)):
    logger.debug("Listing cuisines")
    result = await session.execute(select(Cuisine.name).order_by(Cuisine.name))
    return [CuisineResponse(name=name) for name in result.scalars().all()]
