import os

from loguru import logger
from openai import AsyncOpenAI

def get_async_openrouter_client() -> AsyncOpenAI:
  api_key = os.getenv("OPENROUTER_API_KEY")
  if not api_key:
      logger.warning("OPENROUTER_API_KEY not set, skipping LLM extraction")
      raise ValueError("OPENROUTER_API_KEY not set.")

  client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
  return client