import asyncio
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import httpx
from httpx_curl_cffi import AsyncCurlTransport
from loguru import logger

INSTAGRAM_BASE = "https://www.instagram.com"
INSTAGRAM_API = "https://www.instagram.com/api/v1"
WEB_APP_ID = "936619743392459"


@dataclass
class InstagramMedia:
    shortcode: str
    caption: Optional[str]
    image_url: Optional[str]
    post_url: str
    taken_at: Optional[datetime]
    media_type: str
    raw_json: dict


@dataclass
class InstagramUser:
    pk: str
    username: str
    full_name: Optional[str]
    profile_pic_url: Optional[str]
    is_private: bool


class InstagramClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=INSTAGRAM_BASE,
            transport=AsyncCurlTransport(impersonate="chrome"),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "*/*",
                "Origin": INSTAGRAM_BASE,
                "Referer": f"{INSTAGRAM_BASE}/",
            },
            follow_redirects=True,
        )
        self._loaded = False
        self._logged_in = False
        self._lsd: Optional[str] = None

    @property
    def _csrf(self) -> Optional[str]:
        return self.client.cookies.get("csrftoken", domain=".instagram.com")

    async def _ensure_session(self):
        if self._loaded:
            return

        session_cookie = os.getenv("INSTAGRAM_SESSION_COOKIE")
        if session_cookie:
            self.client.cookies.set(
                "sessionid",
                session_cookie,
                domain=".instagram.com",
            )
            self._logged_in = True
            resp = await self.client.get("/")
            resp.raise_for_status()
            logger.debug("Primed session, csrf: {}", self._csrf)
            self._loaded = True
            logger.info("Using provided Instagram session cookie")
            return

        username = os.getenv("INSTAGRAM_USERNAME")
        password = os.getenv("INSTAGRAM_PASSWORD")
        await self._login(username, password)
        self._loaded = True

    async def _fetch_csrf_token(self):
        resp = await self.client.get("/accounts/login/")
        resp.raise_for_status()
        logger.debug("Fetched CSRF token: {}", self._csrf)
        match = re.search(r'"lsd"\s*:\s*"([^"]+)"', resp.text)
        if match:
            self._lsd = match.group(1)
            logger.debug("Extracted lsd token: {}", self._lsd)

    async def _login(self, username: str, password: str):
        await self._fetch_csrf_token()
        timestamp = int(time.time() * 1000)
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        data = {
            "enc_password": enc_password,
            "username": username,
            "queryParams": "{}",
            "optIntoOneTap": "false",
            "stopDeletionNonce": "",
            "trustedDeviceRecords": "{}",
            "lsd": self._lsd or "",
        }
        headers = {
            "X-CSRFToken": self._csrf or "",
            "X-Instagram-AJAX": "1",
            "X-IG-App-ID": WEB_APP_ID,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"{INSTAGRAM_BASE}/accounts/login/",
        }
        resp = await self.client.post(
            f"{INSTAGRAM_API}/web/accounts/login/ajax/",
            data=data,
            headers=headers,
        )
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            logger.error(
                "Login returned non-JSON response (status={} content-type={}): {}",
                resp.status_code,
                content_type,
                resp.text[:500],
            )
            raise RuntimeError(
                f"Instagram login returned non-JSON response (status={resp.status_code}). "
                "The account may still be flagged or blocked — approve in a browser."
            )
        body = resp.json()
        logger.debug("Login response body: {}", body)
        if body.get("authenticated"):
            self._logged_in = True
            logger.info("Instagram login successful as @{}", username)
        elif body.get("two_factor_required"):
            logger.error("Instagram 2FA required — not supported yet")
            raise RuntimeError("Instagram 2FA required — log in manually in a browser")
        elif (
            body.get("checkpoint_url")
            and (
                body.get("checkpoint_required")
                or body.get("message") == "checkpoint_required"
                or body.get("error_type") == "AuthPlatformLoginChallengeException"
            )
        ):
            logger.error(
                "Instagram checkpoint required — open {} in a browser to approve this device/login",
                body.get("checkpoint_url"),
            )
            raise RuntimeError(
                "Instagram checkpoint required — approve the login at "
                f"{INSTAGRAM_BASE}{body['checkpoint_url']}"
            )
        elif body.get("message"):
            logger.error("Instagram login failed: {}", body.get("message"))
            raise RuntimeError(f"Instagram login failed: {body.get('message')}")
        else:
            logger.error("Instagram login failed: {}", body)
            raise RuntimeError(f"Instagram login failed: {body}")

    async def _api_request(self, method: str, path: str, **kwargs) -> dict:
        headers = kwargs.pop("headers", {})
        headers.setdefault("X-IG-App-ID", WEB_APP_ID)
        if self._csrf:
            headers.setdefault("X-CSRFToken", self._csrf)
        headers.setdefault("Referer", f"{INSTAGRAM_BASE}/")

        for attempt in range(3):
            try:
                resp = await self.client.request(
                    method,
                    f"{INSTAGRAM_API}{path}",
                    headers=headers,
                    **kwargs,
                )
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 60))
                    logger.warning("Rate limited. Retrying after {}s", retry_after)
                    await asyncio.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                logger.error("Instagram API error {}: body={}", e.response.status_code, e.response.text)
                if e.response.status_code == 429 and attempt < 2:
                    retry_after = int(e.response.headers.get("Retry-After", 60))
                    logger.warning("Rate limited. Retrying after {}s", retry_after)
                    await asyncio.sleep(retry_after)
                    continue
                raise
        raise RuntimeError(f"API request failed after 3 retries: {path}")

    async def lookup_user(self, username: str) -> InstagramUser:
        await self._ensure_session()
        logger.debug("Looking for username: {}", username)
        data = await self._api_request("GET", f"/users/web_profile_info/?username={username}")
        logger.debug("Received user data for username: {}", username)
        user_data = data["data"]["user"]
        return InstagramUser(
            pk=user_data["id"],
            username=user_data["username"],
            full_name=user_data.get("full_name"),
            profile_pic_url=user_data.get("profile_pic_url_hd") or user_data.get("profile_pic_url"),
            is_private=user_data.get("is_private", False),
        )

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

        params = {"count": count}
        if max_id:
            params["max_id"] = max_id

        body = await self._api_request(
            "GET",
            f"/feed/user/{user_id}/",
            params=params,
        )

        items = body.get("items", [])
        media_list = []
        for item in items:
            parsed = self._parse_media_item(item)
            if parsed:
                media_list.append(parsed)

        next_cursor = body.get("next_max_id") if body.get("more_available") else None
        return media_list, next_cursor

    async def fetch_user_posts(self, username: str, posts_limit: int = 10) -> list[dict]:
        all_media = []
        max_id = None
        while len(all_media) < posts_limit:
            batch, max_id = await self.fetch_user_media(username, count=min(12, posts_limit - len(all_media)), max_id=max_id)
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

    def _parse_media_item(self, item: dict) -> Optional[InstagramMedia]:
        try:
            shortcode = item.get("shortcode") or item.get("code")
            if not shortcode:
                return None

            taken_at_ts = item.get("taken_at_timestamp") or item.get("taken_at")
            taken_at = datetime.fromtimestamp(taken_at_ts, tz=timezone.utc) if taken_at_ts else None

            typename = item.get("__typename", "")
            if typename:
                media_type_map = {"GraphImage": "image", "GraphVideo": "video", "GraphSidecar": "carousel"}
                media_type = media_type_map.get(typename, "image")
                media_type_val = {"image": 1, "video": 2, "carousel": 8}.get(media_type, 1)
            else:
                media_type_val = item.get("media_type", 1)
                type_map = {1: "image", 2: "video", 8: "carousel"}
                media_type = type_map.get(media_type_val, "image")

            image_url = None
            if item.get("image_versions2"):
                candidates = item["image_versions2"].get("candidates", [])
                if candidates:
                    sorted_candidates = sorted(candidates, key=lambda c: c.get("width", 0), reverse=True)
                    image_url = sorted_candidates[0].get("url")
            if not image_url and item.get("display_url"):
                image_url = item["display_url"]
            if not image_url and item.get("display_src"):
                image_url = item["display_src"]
            if not image_url and item.get("carousel_media"):
                first = item["carousel_media"][0]
                if first.get("image_versions2"):
                    candidates = first["image_versions2"].get("candidates", [])
                    if candidates:
                        sorted_candidates = sorted(candidates, key=lambda c: c.get("width", 0), reverse=True)
                        image_url = sorted_candidates[0].get("url")
            if not image_url and item.get("edge_sidecar_to_children"):
                edges = item["edge_sidecar_to_children"].get("edges", [])
                if edges:
                    node = edges[0].get("node", {})
                    if node.get("display_url"):
                        image_url = node["display_url"]

            caption = None
            if item.get("caption"):
                caption = item["caption"].get("text")
            if not caption and item.get("edge_media_to_caption"):
                edges = item["edge_media_to_caption"].get("edges", [])
                if edges:
                    caption = edges[0].get("node", {}).get("text")

            pk = item.get("pk") or item.get("id")
            comment_count = item.get("comment_count")
            if comment_count is None and item.get("edge_media_to_comment"):
                comment_count = item["edge_media_to_comment"].get("count")
            like_count = item.get("like_count")
            if like_count is None and item.get("edge_media_preview_like"):
                like_count = item["edge_media_preview_like"].get("count")

            raw = {
                "pk": pk,
                "media_type": media_type_val,
                "comment_count": comment_count,
                "like_count": like_count,
                "has_location": item.get("location") is not None,
                "location": item.get("location"),
                "lat": item.get("lat"),
                "lng": item.get("lng"),
            }

            return InstagramMedia(
                shortcode=shortcode,
                caption=caption,
                image_url=image_url,
                post_url=f"https://www.instagram.com/p/{shortcode}/",
                taken_at=taken_at,
                media_type=media_type,
                raw_json=raw,
            )
        except Exception as e:
            logger.warning("Failed to parse media item: {} (pk={})", e, item.get("pk") or item.get("id"))
            return None

    async def close(self):
        await self.client.aclose()


_instance: Optional[InstagramClient] = None


async def get_client() -> InstagramClient:
    global _instance
    if _instance is None:
        _instance = InstagramClient()
    await _instance._ensure_session()
    return _instance


async def close_client():
    global _instance
    if _instance:
        await _instance.close()
        _instance = None
