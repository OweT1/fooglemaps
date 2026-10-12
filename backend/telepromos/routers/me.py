from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from commons.db import get_db_session
from telepromos.telegram_auth import get_current_telegram_user
from telepromos.models import TelegramUser

router = APIRouter(prefix="/api/me", tags=["me"])


class UpdateNotifications(BaseModel):
    notify_enabled: bool


@router.get("")
async def get_me(user: TelegramUser = Depends(get_current_telegram_user)):
    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "notify_enabled": user.notify_enabled,
    }


@router.put("/notifications")
async def update_notifications(
    payload: UpdateNotifications,
    user: TelegramUser = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db_session),
):
    user.notify_enabled = payload.notify_enabled
    await session.commit()
    return {"notify_enabled": user.notify_enabled}