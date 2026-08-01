import httpx
from loguru import logger
from typing import Optional

from core import settings


async def geocode_location(location_name: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
    api_key = settings.google_maps_api_key
    if not api_key:
        logger.warning("GOOGLE_MAPS_API_KEY not set, skipping geocoding")
        return None, None, None

    params = {
        "address": location_name,
        "key": api_key,
        "region": "sg",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params=params,
                timeout=10,
            )
            data = resp.json()
        except Exception as e:
            logger.error("Geocoding request failed for '{}': {}", location_name, e)
            return None, None, None

    if data.get("status") != "OK" or not data.get("results"):
        logger.warning("Geocoding returned no results for '{}': {}", location_name, data.get("status"))
        return None, None, None

    result = data["results"][0]
    lat = result["geometry"]["location"]["lat"]
    lng = result["geometry"]["location"]["lng"]
    address = result.get("formatted_address")
    logger.debug("Geocoded '{}' -> ({}, {}): {}", location_name, lat, lng, address)
    return lat, lng, address
