import logging
import re
from google.api_core import exceptions as google_exceptions
from sqlalchemy.orm import Session
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)


from app.core.config import get_settings
from app.core.exceptions import (
    InvalidSQLGeneratedException,
    LLMQuotaExceededException,
    LLMException,
)
from app.db.operations import get_schema_info, format_schema_for_prompt
from app.llm.client import get_llm_client, get_generation_config
from app.llm.prompt import build_sql_prompt

logger = logging.getLogger(__name__)

_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def _parse_llm_response(raw_response: str) -> tuple[str, str]:
    """
    Parses the raw LLM response to extract the SQL query and explanation.
    Expects the format:
    SQL: <the sql query>
    Explanation: <the explanation>

    Returns:
        A tuple of (sql, explanation)
    """
    sql_match = re.search(r"SQL:\s*(.+)\s*Explanation:|$", raw_response, re.IGNORECASE | re.DOTALL)
    explanation_match = re.search(r"Explanation:\s*(.+)", raw_response, re.IGNORECASE | re.DOTALL)

    sql = sql_match.group(1).strip() if sql_match else ""
    explanation = explanation_match.group(1).strip() if explanation_match else ""

    return sql, explanation



def _extract_sql(raw_response: str) -> str:
    cleaned = re.sub(r"```(?:sql)?|```", "", raw_response).strip()
    return cleaned


def _validate_sql(sql: str) -> bool:
    if sql.upper() == "INVALID":
        return False
    stripped = sql.strip().upper()
    if not stripped.startswith("SELECT"):
        return False
    if _FORBIDDEN_KEYWORDS.search(sql):
        logger.warning("Forbidden keyword detected in generated SQL: %s", sql)
        return False
    return True


def _call_llm(prompt: str) -> str:
    settings = get_settings()
    client = get_llm_client()
    config = get_generation_config()

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
        return response.text or ""
    except google_exceptions.ResourceExhausted as e:
        logger.error("Gemini quota exhausted: %s", e)
        raise LLMQuotaExceededException("LLM quota exhausted.") from e
    except Exception as e:
        logger.error("Gemini call failed: %s", e)
        raise LLMException(f"LLM call failed: {e}") from e

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((LLMException)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)

def _call_llm_with_retry(prompt: str) -> None:
    return _call_llm(prompt)

def generate_sql_from_english(query: str, db: Session) -> tuple[str, str]:
    """
    Generates a SQL query from an English question.
    """
    schema_rows = get_schema_info(db)
    schema_str = format_schema_for_prompt(schema_rows)
    prompt = build_sql_prompt(query=query, schema=schema_str)

    raw_sql = _call_llm_with_retry(prompt)  # Call the LLM with retry logic
    logger.debug("Raw SQL response from LLM: %s", raw_sql)  # Log the raw response at debug level

    sql, explanation = _parse_llm_response(raw_sql)
    sql = _extract_sql(sql)

    if not _validate_sql(sql):
        raise InvalidSQLGeneratedException(
            f"Could not generate a valid SELECT query for: '{query}'"
        )

    ## attempt 2
    logger.warning("Attempting to generate SQL again due to invalid output.")
    correction_prompt = build_sql_prompt(
        query=f"IMPORTANT: Return ONLY a SELECT query. Do not use reserved words as aliases. {query}",
        schema=schema_str,
    )
    raw_sql = _call_llm_with_retry(correction_prompt)  # Call the LLM with the correction prompt
    logger.debug("Raw SQL response from LLM (second attempt): %s", raw_sql)  # Log the raw response at debug level

    sql, explanation = _parse_llm_response(raw_sql)
    sql = _extract_sql(sql)

    if _validate_sql(sql):
        return sql, explanation

    logger.error("Failed to generate valid SQL after correction attempt for query: %s", query)
    raise InvalidSQLGeneratedException(
        f"Could not generate a valid SELECT query for: '{query}'"
    )