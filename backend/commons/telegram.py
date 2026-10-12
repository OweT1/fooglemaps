from functools import lru_cache

import httpx
from loguru import logger

from commons import settings


class TelegramBot:
    """Minimal async Telegram Bot API client (raw httpx, no framework).

    Subclass to add application-specific behavior (e.g. Mini App buttons,
    update handlers). Most methods return ``None`` when the bot token is
    unset or the API call fails, so callers can degrade gracefully.
    """

    BASE_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str | None = None):
        self.token = token if token is not None else settings.telegram_bot_token

    async def _call(self, method: str, **payload) -> object | None:
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN not set, skipping {}", method)
            return None
        url = self.BASE_URL.format(token=self.token, method=method)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=payload)
                data = resp.json()
        except Exception as e:
            logger.error("Telegram {} request failed: {}", method, e)
            return None
        if not data.get("ok"):
            logger.warning("Telegram {} failed: {}", method, data)
            return None
        return data.get("result")

    async def get_me(self) -> object | None:
        return await self._call("getMe")

    async def send_message(self, chat_id: int, text: str, reply_markup: dict | None = None) -> bool:
        payload: dict = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return await self._call("sendMessage", **payload) is not None

    async def set_webhook(
        self,
        url: str,
        secret_token: str | None = None,
        allowed_updates: list[str] | None = None,
    ) -> bool:
        payload: dict = {"url": url}
        if secret_token:
            payload["secret_token"] = secret_token
        if allowed_updates is not None:
            payload["allowed_updates"] = allowed_updates
        return await self._call("setWebhook", **payload) is not None

    async def delete_webhook(self) -> bool:
        return await self._call("deleteWebhook") is not None

    async def set_chat_menu_button(self, text: str, web_app_url: str) -> bool:
        payload = {
            "menu_button": {
                "type": "web_app",
                "text": text,
                "web_app": {"url": web_app_url},
            }
        }
        return await self._call("setChatMenuButton", **payload) is not None

    @staticmethod
    def web_app_button(text: str, url: str) -> dict:
        return {"text": text, "web_app": {"url": url}}

    @staticmethod
    def inline_keyboard(buttons: list[list[dict]]) -> dict:
        return {"inline_keyboard": buttons}


@lru_cache
def get_telegram_bot() -> TelegramBot:
    return TelegramBot()