from google import genai
from google.genai import types
from functools import lru_cache

from app.core.config import get_settings



@lru_cache
def get_llm_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def get_generation_config() -> types.GenerateContentConfig:
    settings = get_settings()
    return types.GenerateContentConfig(
        temperature=settings.GEMINI_TEMPERATURE,
        max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )