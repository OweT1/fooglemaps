import asyncio
import json
from datetime import datetime

from loguru import logger
from pydantic import BaseModel

from commons.llm import get_async_openrouter_client
from commons.llm import OPENROUTER_EXTRACTION_MODELS

EXTRACTION_PROMPT = """You are a deals extractor for Singapore Instagram captions. Given a caption, extract the promotion/deal being advertised.

Return ONLY valid JSON with these fields:
- "title": short promotional headline (e.g. "15% off weekday lunch")
- "venue_name": the eatery/stall/restaurant/cafe where the deal is available (required if the caption advertises a deal)
- "address": any location descriptor (street, mall, neighbourhood, area) mentioned
- "discount_text": the discount as written in the caption (e.g. "Buy 1 Get 1 Free")
- "pct_off": integer 0-100 for a straight percentage discount if stated, otherwise null (BOGO and other non-percentage offers must be null)
- "valid_from": deal start date in ISO-8601 (YYYY-MM-DD) if stated, otherwise null
- "valid_until": deal end date in ISO-8601 (YYYY-MM-DD) if stated, otherwise null
- "terms": any conditions (minimum spend, time windows, exclusions) mentioned
- "description": 1-2 sentence summary of the deal

Rules:
- If the caption is not advertising a deal/promotion, set venue_name to null.
- Prefer explicit dates stating the deal's validity; for "while stocks last" or no end date stated, keep valid_until null.

Caption: {caption}"""

SYSTEM_PROMPT = (
    "You extract food deals from Instagram captions. Return only valid JSON."
)

# Each model gets this many attempts (with backoff) before moving to the next.
RETRIES_PER_MODEL = 3
# Simple exponential backoff between attempts (2s, 4s, 8s, ... capped).
BACKOFF_BASE_SECONDS = 2.0
BACKOFF_MAX_SECONDS = 16.0


class ExtractedDeal(BaseModel):
    title: str | None = None
    venue_name: str | None = None
    address: str | None = None
    discount_text: str | None = None
    pct_off: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    terms: str | None = None
    description: str | None = None


_EMPTY_RESULT: dict = {}


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


async def extract_deal_from_caption(caption: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(caption=caption[:2000])

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
                    "Backing off {}s before retry {}/{} with {}",
                    delay,
                    attempt + 1,
                    RETRIES_PER_MODEL,
                    model,
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
                data = ExtractedDeal.model_validate(
                    _parse_json(resp.choices[0].message.content)
                ).model_dump()
                _clamp(data)
                logger.debug("Extracted deal with {}: {}", model, data)
                return data
            except Exception as e:
                logger.warning(
                    "Deal LLM extraction with {} failed (attempt {}/{}, model {}/{}): {}",
                    model,
                    attempt + 1,
                    RETRIES_PER_MODEL,
                    model_index,
                    total_models,
                    e,
                )

    logger.error(
        "Deal LLM extraction failed for all {} models ({} attempts each), returning empty result",
        total_models,
        RETRIES_PER_MODEL,
    )
    return dict(_EMPTY_RESULT)


def _clamp(data: dict) -> None:
    for key in ("title", "venue_name", "discount_text"):
        value = data.get(key)
        if isinstance(value, str) and len(value) > 500:
            data[key] = value[:500]
    pct_off = data.get("pct_off")
    if pct_off is not None:
        try:
            data["pct_off"] = max(0, min(100, int(pct_off)))
        except (TypeError, ValueError):
            data["pct_off"] = None