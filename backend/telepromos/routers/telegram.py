import hmac

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from commons import settings
from commons.db import get_db_session
from telepromos.bot import get_bot

router = APIRouter(tags=["telegram"])


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    expected = settings.telegram_webhook_secret
    if not expected or not secret or not hmac.compare_digest(secret, expected):
        raise HTTPException(status_code=404, detail="Not found")

    update = await request.json()
    logger.debug("Telegram webhook update: {}", update.get("update_id"))
    await get_bot().handle_update(update, session)
    return {"ok": True}