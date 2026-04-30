import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.exceptions import DatabaseQueryException
from app.llm.sql_generator import generate_sql_from_english

logger = logging.getLogger(__name__)


def _execute_sql(sql: str, db: Session) -> list[dict]:
    try:
        result = db.execute(text(sql))
        return [dict(row) for row in result.mappings().fetchall()]
    except Exception as e:
        logger.error("Failed to execute SQL [%s]: %s", sql, e)
        raise DatabaseQueryException(f"Query execution failed: {e}") from e


def get_query_results(natural_query: str, db: Session) -> tuple[str, list[dict]]:
    sql = generate_sql_from_english(natural_query, db)
    logger.info("Executing generated SQL: %s", sql)
    results = _execute_sql(sql, db)
    return results