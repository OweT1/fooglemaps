from loguru import logger
from openai import AsyncOpenAI

from commons import settings

# Free Nemotron models on OpenRouter, tried in order when extraction fails.
OPENROUTER_EXTRACTION_MODELS: list[str] = [
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
]

# Reasoning models are slow; keep per-request timeout tighter than the OpenAI
# default (600s) so a stalled free model still fails over to the next one.
REQUEST_TIMEOUT_SECONDS = 90.0


def get_async_openrouter_client() -> AsyncOpenAI:
    api_key = settings.openrouter_api_key
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not set, skipping LLM extraction")
        raise ValueError("OPENROUTER_API_KEY not set.")

    # max_retries=0: the caller owns retry/failover timing via its backoff loop.
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=0,
    )
    return client
