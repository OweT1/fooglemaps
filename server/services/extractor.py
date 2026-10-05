import json
from typing import Optional

from loguru import logger

from utils import get_async_openrouter_client

from .cuisines import CUISINES, CUISINES_LOOKUP, MAX_CUISINES_PER_PLACE

EXTRACTION_PROMPT = """You are a food location extractor for Singapore. Given an Instagram caption, extract details about the food place being mentioned.

Return ONLY valid JSON with these fields:
- "place_name": the name of the eatery, hawker stall, restaurant, cafe, or food place (or null if none mentioned)
- "address": any location descriptor (street, mall, neighbourhood, area) mentioned (or null if none)
- "cuisine": array of at most {max_cuisines} cuisine types, chosen ONLY from the allowed list below. Pick the most specific options that apply. If the caption describes a dish (e.g. laksa, bak kut teh, chilli crab), choose the cuisine that best covers it (e.g. "Seafood", "Noodles"). Empty array if none apply.

Allowed cuisines (use these exact spellings, nothing else):
{cuisines}

If the caption is not about food or doesn't mention a place, set place_name to null.

Caption: {caption}"""


def _normalise_cuisines(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []

    matched: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        canonical = CUISINES_LOOKUP.get(item.strip().lower())
        if canonical and canonical not in matched:
            matched.append(canonical)

    if len(matched) > MAX_CUISINES_PER_PLACE:
        logger.warning(
            "LLM returned {} cuisines, capping at {}", len(matched), MAX_CUISINES_PER_PLACE
        )
        matched = matched[:MAX_CUISINES_PER_PLACE]
    return matched


async def extract_from_caption(caption: str) -> dict:
    client = get_async_openrouter_client()
    prompt = EXTRACTION_PROMPT.format(
        caption=caption[:2000],
        cuisines=", ".join(CUISINES),
        max_cuisines=MAX_CUISINES_PER_PLACE,
    )
    try:
        resp = await client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": "You extract food place info from Instagram captions. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=300,
        )
        text = resp.choices[0].message.content
        data = json.loads(text)
        data["cuisine"] = _normalise_cuisines(data.get("cuisine"))
        logger.debug("Extracted from caption: {}", data)
        return data
    except Exception as e:
        logger.error("LLM extraction failed: {}", e)
        return {"place_name": None, "address": None, "cuisine": []}
