import logging
from google.api_core import exceptions as google_exceptions
from google.genai import types


from app.core.config import get_settings
from app.core.exceptions import LLMQuotaExceededException, LLMException
from app.llm.client import get_llm_client, get_generation_config
from app.llm.prompt import build_insights_prompt


logger = logging.getLogger(__name__)


def generate_insights(query: str, results: list[dict]) -> str:
    """
    Takes the user's original question and the DB results,
    returns a plain English insight string.

    Args:
        query:   The user's original natural language question.
        results: The list of dicts returned from the DB query.

    Returns:
        A plain English insight string.

    Raises:
        LLMQuotaExceededException: Gemini quota hit.
        LLMException:              Any other LLM failure.
    """
    # if no results — no point calling the LLM
    if not results:
        return "No data found for this query."

    settings = get_settings()
    client   = get_llm_client()

    # insights need a slightly different config —
    # higher temperature for more natural language
    
    config = types.GenerateContentConfig(
        temperature=0.4,        # slightly higher than SQL — we want natural prose
        max_output_tokens=500,  # insights are short
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # disable thinking
    )

    prompt = build_insights_prompt(query=query, results=results)

    logger.debug("Generating insights for query: %s", query)

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
        logger.info("Raw insight response: '%s'", response.text)
        logger.info("Finish reason: %s", response.candidates[0].finish_reason)
        insight = response.text.strip() if response.text else "Could not generate insight."
        logger.debug("Generated insight: %s", insight)
        return insight

    except google_exceptions.ResourceExhausted as e:
        logger.error("Gemini quota exhausted during insight generation: %s", e)
        raise LLMQuotaExceededException("LLM quota exhausted.") from e

    except Exception as e:
        logger.error("Insight generation failed: %s", e)
        raise LLMException(f"Insight generation failed: {e}") from e