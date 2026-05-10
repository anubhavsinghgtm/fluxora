from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.exceptions import SchemaFetchException

logger = logging.getLogger(__name__)

def get_schema_info(db: Session):
    sql = text("""
        select table_name, column_name, data_type
        from information_schema.columns
        where table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    try:
        result = db.execute(sql).mappings().fetchall()
        return [dict(row) for row in result]
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