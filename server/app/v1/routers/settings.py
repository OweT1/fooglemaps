from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from utils.deps import verify_google_token, get_session
from db.constants import SettingsResponse, SettingsUpdate
from db.models import User, UserSettings

router = APIRouter()


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    updates: SettingsUpdate,
    user_info: dict = Depends(verify_google_token),
    session: AsyncSession = Depends(get_session),
):
    sub = user_info["sub"]
    logger.info("Updating settings for sub={}", sub)

    result = await session.execute(select(User).where(User.google_sub == sub))
    u = result.scalar_one_or_none()
    if not u:
        logger.warning("User not found for settings update: sub={}", sub)
        raise HTTPException(status_code=404, detail="User not found")

    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        logger.warning("No fields to update for sub={}", sub)
        raise HTTPException(status_code=400, detail="No fields to update")

    logger.debug("Settings update for user={}: {}", u.id, update_data)
    result = await session.execute(
        update(UserSettings)
        .where(UserSettings.user_id == u.id)
        .values(**update_data)
        .returning(UserSettings)
    )
    row = result.scalar_one()
    await session.commit()
    logger.info("Settings updated for user={}", u.id)

    return SettingsResponse(
        id=str(row.id),
        user_id=str(row.user_id),
        theme=row.theme,
        default_zoom=row.default_zoom,
        map_type=row.map_type,
        notify_new_spots=row.notify_new_spots,
        notify_recommendations=row.notify_recommendations,
    )
