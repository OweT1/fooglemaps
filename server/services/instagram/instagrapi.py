from __future__ import annotations

from datetime import timezone
from typing import Optional

from instagrapi import Client
from loguru import logger

from core import settings
from .commons import InstagramMedia, InstagramUser


class InstagramClient:
    def __init__(self) -> None:
        self._client = Client()
        self._logged_in = False

    async def _ensure_session(self) -> None:
        if self._logged_in:
            return

        username = settings.instagram_username
        password = settings.instagram_password

        if not username or not password:
            raise RuntimeError(
                "Instagram credentials not configured. Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in environment."
            )

        try:
            self._client.login(username, password)
            self._logged_in = True
            logger.info("Instagram login successful as @{}", username)
        except Exception as e:
            logger.error("Instagram login failed: {}", e)
            raise

    async def lookup_user(self, username: str) -> InstagramUser:
        await self._ensure_session()
        try:
            user = self._client.user_info_by_username(username)
            return InstagramUser(
                pk=str(user.pk),
                username=user.username,
                full_name=user.full_name,
                profile_pic_url=getattr(user, "profile_pic_url_hd", None)
                or getattr(user, "profile_pic_url", None),
                is_private=getattr(user, "is_private", False),
            )
        except Exception as e:
            logger.error("Failed to lookup user {}: {}", username, e)
            raise

    async def fetch_user_media(
        self,
        username_or_id: str,
        count: int = 12,
        max_id: Optional[str] = None,
    ) -> tuple[list[InstagramMedia], Optional[str]]:
        await self._ensure_session()

        user_id = username_or_id
        if not username_or_id.isdigit():
            user = await self.lookup_user(username_or_id)
            user_id = user.pk

        try:
            medias = self._client.user_medias(user_id, amount=count)
            media_list = []
            for media in medias:
                parsed = self._parse_media_item(media)
                if parsed:
                    media_list.append(parsed)
            return media_list, None
        except Exception as e:
            logger.error("Failed to fetch user media for {}: {}", username_or_id, e)
            raise

    async def fetch_user_posts(self, username: str, posts_limit: int = 10) -> list[dict]:
        all_media = []
        max_id = None
        while len(all_media) < posts_limit:
            batch, max_id = await self.fetch_user_media(
                username, count=min(12, posts_limit - len(all_media)), max_id=max_id
            )
            all_media.extend(batch)
            if not max_id:
                break
        return [
            {
                "shortcode": m.shortcode,
                "caption": m.caption,
                "image_url": m.image_url,
                "post_url": m.post_url,
                "taken_at": m.taken_at,
                "media_type": m.media_type,
                "raw_json": m.raw_json,
            }
            for m in all_media[:posts_limit]
        ]

    def _parse_media_item(self, media) -> Optional[InstagramMedia]:
        try:
            shortcode = getattr(media, "code", None) or getattr(media, "shortcode", None)
            if not shortcode:
                return None

            taken_at = getattr(media, "taken_at", None)
            if taken_at and taken_at.tzinfo is None:
                taken_at = taken_at.replace(tzinfo=timezone.utc)

            media_type = getattr(media, "media_type", 1)
            media_type_map = {1: "image", 2: "video", 8: "carousel"}
            media_type_str = media_type_map.get(media_type, "image") if isinstance(media_type, int) else str(media_type)

            image_url = None
            image_versions2 = getattr(media, "image_versions2", None)
            if image_versions2:
                candidates = getattr(image_versions2, "candidates", [])
                if candidates:
                    sorted_candidates = sorted(candidates, key=lambda c: getattr(c, "width", 0), reverse=True)
                    if sorted_candidates:
                        image_url = getattr(sorted_candidates[0], "url", None)
            if not image_url:
                image_url = getattr(media, "thumbnail_url", None) or getattr(media, "display_url", None)

            caption = getattr(media, "caption_text", None) or getattr(media, "caption", None)
            if hasattr(caption, "text"):
                caption = caption.text

            pk = getattr(media, "pk", None) or getattr(media, "id", None)

            raw = {
                "pk": str(pk) if pk is not None else None,
                "media_type": media_type,
                "code": shortcode,
            }

            return InstagramMedia(
                shortcode=shortcode,
                caption=caption,
                image_url=image_url,
                post_url=f"https://www.instagram.com/p/{shortcode}/",
                taken_at=taken_at,
                media_type=media_type_str,
                raw_json=raw,
            )
        except Exception as e:
            logger.warning("Failed to parse media item: {}", e)
            return None

    async def close(self) -> None:
        try:
            self._client.logout()
        except Exception:
            pass


_instance: Optional[InstagramClient] = None


async def get_client() -> InstagramClient:
    global _instance
    if _instance is None:
        _instance = InstagramClient()
    await _instance._ensure_session()
    return _instance


async def close_client() -> None:
    global _instance
    if _instance:
        await _instance.close()
        _instance = None


# Alias for compatibility
get_instagram_client = get_client
close_instagram_client = close_client
