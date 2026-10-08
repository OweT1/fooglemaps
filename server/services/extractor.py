import asyncio
import json

from loguru import logger

from utils import get_async_openrouter_client
from utils.llm import OPENROUTER_EXTRACTION_MODELS

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

SYSTEM_PROMPT = (
    "You extract food place info from Instagram captions. Return only valid JSON."
)

# Each model gets this many attempts (with backoff) before moving to the next.
RETRIES_PER_MODEL = 3
# Simple exponential backoff between attempts (2s, 4s, 8s, ... capped).
BACKOFF_BASE_SECONDS = 2.0
BACKOFF_MAX_SECONDS = 16.0

_EMPTY_RESULT: dict = {"place_name": None, "address": None, "cuisine": []}


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


def _parse_json(text: str | None) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty LLM response")

    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped[:3].lower() == "json":
            stripped = stripped[3:].lstrip("\n")

    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        # Reasoning models sometimes wrap the object in prose; retry on the
        # outermost braces before giving up on this attempt.
        start, end = stripped.find("{"), stripped.rfind("}")
        if start == -1 or end <= start:
            raise ValueError(f"Unparseable LLM response: {stripped[:150]!r}")
        try:
            data = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as e:
            raise ValueError(f"Unparseable LLM response: {stripped[:150]!r}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object, got {type(data).__name__}")
    return data


async def extract_from_caption(caption: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(
        caption=caption[:2000],
        cuisines=", ".join(CUISINES),
        max_cuisines=MAX_CUISINES_PER_PLACE,
    )

    try:
        client = get_async_openrouter_client()
    except ValueError:
        return dict(_EMPTY_RESULT)

    total_models = len(OPENROUTER_EXTRACTION_MODELS)
    for model_index, model in enumerate(OPENROUTER_EXTRACTION_MODELS, start=1):
        for attempt in range(RETRIES_PER_MODEL):
            if attempt:
                delay = min(BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)), BACKOFF_MAX_SECONDS)
                logger.debug(
                    "Backing off {}s before retry {}/{} with {}", delay, attempt + 1, RETRIES_PER_MODEL, model
                )
                await asyncio.sleep(delay)

            try:
                resp = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    # Reasoning tokens count toward max_tokens, so leave headroom.
                    max_tokens=4000,
                    extra_body={"reasoning": {"enabled": True}},
                )
                # The free tier intermittently returns choices=None upstream.
                if not resp.choices:
                    raise ValueError("LLM returned no choices")
                data = _parse_json(resp.choices[0].message.content)
                data["cuisine"] = _normalise_cuisines(data.get("cuisine"))
                data.setdefault("place_name", None)
                data.setdefault("address", None)
                logger.debug("Extracted from caption with {}: {}", model, data)
                return data
            except Exception as e:
                logger.warning(
                    "LLM extraction with {} failed (attempt {}/{}, model {}/{}): {}",
                    model,
                    attempt + 1,
                    RETRIES_PER_MODEL,
                    model_index,
                    total_models,
                    e,
                )

    logger.error(
        "LLM extraction failed for all {} models ({} attempts each), returning empty result",
        total_models,
        RETRIES_PER_MODEL,
    )
    return dict(_EMPTY_RESULT)
