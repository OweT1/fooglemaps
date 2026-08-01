import json
from typing import Optional

from loguru import logger

from utils import get_async_openrouter_client

EXTRACTION_PROMPT = """You are a food location extractor for Singapore. Given an Instagram caption, extract details about the food place being mentioned.

Return ONLY valid JSON with these fields:
- "place_name": the name of the eatery, hawker stall, restaurant, cafe, or food place (or null if none mentioned)
- "address": any location descriptor (street, mall, neighbourhood, area) mentioned (or null if none)
- "cuisine": array of cuisine types or specific food items mentioned (e.g. ["Chinese", "Laksa", "Seafood", "Hawker"]), empty array if none

If the caption is not about food or doesn't mention a place, set place_name to null.

Caption: {caption}"""


async def extract_from_caption(caption: str) -> dict:
    client = get_async_openrouter_client()
    try:
        resp = await client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": "You extract food place info from Instagram captions. Return only valid JSON."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(caption=caption[:2000])},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=300,
        )
        text = resp.choices[0].message.content
        data = json.loads(text)
        logger.debug("Extracted from caption: {}", data)
        return data
    except Exception as e:
        logger.error("LLM extraction failed: {}", e)
        return {"place_name": None, "address": None, "cuisine": []}
