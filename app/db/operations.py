from sqlalchemy.orm import Session
from sqlalchemy import text
import logging, time

from app.core.exceptions import SchemaFetchException
from app.core.config import get_settings

logger = logging.getLogger(__name__)


### Database schema fetching and formatting for LLM prompts
SCHEMA_CACHE_TTL = get_settings().SCHEMA_CACHE_TTL

_schema_cache: list[dict] | None = None
_schema_cache_timestamp: float | None = None


def invalidate_schema_cache():
    global _schema_cache, _schema_cache_timestamp
    _schema_cache = None
    _schema_cache_timestamp = None
    logger.debug("Schema cache invalidated")


def _is_cache_valid() -> bool:

    if _schema_cache is None or _schema_cache_timestamp is None:
        return False
    
    age = time.time() - _schema_cache_timestamp
    return age < SCHEMA_CACHE_TTL


def get_schema_info(db: Session):

    global _schema_cache, _schema_cache_timestamp

    if _is_cache_valid():
        logger.debug("Using cached schema info")
        return _schema_cache

    logger.debug("Fetching schema info from database")

    sql = text("""
        select table_name, column_name, data_type
        from information_schema.columns
        where table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    try:
        result = db.execute(sql).mappings().fetchall()
        rows = [dict(row) for row in result]

        _schema_cache = rows
        _schema_cache_timestamp = time.time()

        return _schema_cache

    except Exception as e:
        logger.error(f"Failed to fetch schema info %s:", e)
        raise SchemaFetchException("Failed to fetch schema info") from e




def format_schema_for_prompt(schema_rows: list[dict]) -> str:
    tables: dict[str, list[str]] = {}
    for row in schema_rows:
        table = row["table_name"]
        col = f"{row['column_name']}: {row['data_type']}"
        tables.setdefault(table, []).append(col)

    return "\n".join(
        f"{table}({', '.join(cols)})"
        for table, cols in tables.items()
    )