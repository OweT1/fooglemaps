import asyncio

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telepromos.models import Deal, TelegramUser

from .bot import TelePromosBot, get_bot

_PER_MESSAGE = 5
_SEND_DELAY_SECONDS = 0.15


async def notify_new_deals(
    session: AsyncSession,
    new_deals: list[Deal],
    bot: TelePromosBot | None = None,
) -> int:
    bot = bot or get_bot()
    if not new_deals:
        return 0

    result = await session.execute(
        select(TelegramUser).where(
            TelegramUser.notify_enabled.is_(True),
            TelegramUser.chat_id.is_not(None),
        )
    )
    recipients = result.scalars().all()
    if not recipients:
        logger.debug("No telegram recipients, skipping deal notifications")
        return 0

    sent = 0
    for chunk in (new_deals[i:i + _PER_MESSAGE] for i in range(0, len(new_deals), _PER_MESSAGE)):
        lines = []
        for deal in chunk:
            line = f"- {deal.title} — {deal.venue_name}"
            if deal.valid_until:
                line += f" (until {deal.valid_until.date().isoformat()})"
            lines.append(line)
        text = f"{len(new_deals)} new deal(s) found:\n" + "\n".join(lines)

        for user in recipients:
            chat_id = user.chat_id
            if chat_id is not None and await bot.send_message(
                chat_id, text, reply_markup=bot.app_reply_markup()
            ):
                sent += 1
            await asyncio.sleep(_SEND_DELAY_SECONDS)

    logger.info("Sent deal notifications: {}/{} recipients", sent, len(recipients))
    return sent