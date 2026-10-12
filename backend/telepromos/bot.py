from functools import lru_cache
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commons import settings
from commons.telegram import TelegramBot
from telepromos.models import Deal, TelegramUser


class TelePromosBot(TelegramBot):
    """TelePromos bot: WebApp launcher + /start deep-link handling."""

    def app_button(self, text: str = "Open TelePromos") -> dict:
        return self.web_app_button(text, settings.telegram_app_url)

    def app_reply_markup(self, button_text: str = "Open TelePromos") -> dict:
        return self.inline_keyboard([[self.app_button(button_text)]])

    async def set_chat_menu_button(self) -> bool:
        return await super().set_chat_menu_button("Open TelePromos", settings.telegram_app_url)

    async def _deal_teaser(self, session: AsyncSession, deal_id: str) -> str:
        try:
            result = await session.execute(
                select(Deal).where(Deal.id == UUID(deal_id))
            )
        except ValueError:
            return ""
        deal = result.scalar_one_or_none()
        if not deal:
            return ""
        line = f"{deal.title} at {deal.venue_name}"
        if deal.valid_until:
            line += f"\nValid until {deal.valid_until.date().isoformat()}"
        return line

    async def handle_update(self, update: dict, session: AsyncSession) -> bool:
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if not chat_id:
            return False

        text = (message.get("text") or "").strip()
        if not (text == "/start" or text.startswith("/start ")):
            return False

        sender = message.get("from") or {}
        telegram_id = sender.get("id")
        start_param = text.split(maxsplit=1)[1] if " " in text else None

        if telegram_id is not None:
            result = await session.execute(
                select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
            )
            user_row = result.scalar_one_or_none()
            if user_row:
                user_row.chat_id = chat_id
                if sender.get("username"):
                    user_row.username = sender["username"]
                if sender.get("first_name"):
                    user_row.first_name = sender["first_name"]
            else:
                user_row = TelegramUser(
                    telegram_id=telegram_id,
                    chat_id=chat_id,
                    username=sender.get("username"),
                    first_name=sender.get("first_name"),
                )
                session.add(user_row)
            await session.commit()
            logger.info("Telegram /start from user {}", telegram_id)

        if start_param and start_param.startswith("deal_"):
            teaser = await self._deal_teaser(session, start_param[len("deal_"):])
            if teaser:
                message_text = f"{teaser}\n\nOpen TelePromos for full details and more deals."
            else:
                message_text = "Welcome to TelePromos! Tap below to browse Singapore food deals."
        else:
            message_text = "Welcome to TelePromos! Tap below to browse Singapore food deals."

        await self.send_message(chat_id, message_text, reply_markup=self.app_reply_markup())
        return True


@lru_cache
def get_bot() -> TelePromosBot:
    return TelePromosBot()