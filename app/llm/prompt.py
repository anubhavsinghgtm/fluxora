ENGLISH_TO_SQL_PROMPT = """
You are a PostgreSQL expert. Convert the natural language query below into a valid PostgreSQL SELECT statement.

Database schema:
{schema}

Rules:
- Return ONLY the raw SQL query. No markdown, no backticks, no explanation.
- The query MUST be a SELECT statement. Never generate INSERT, UPDATE, DELETE, DROP, or DDL.
- If the question cannot be answered with a SELECT query, return exactly: INVALID
- Use table and column names exactly as shown in the schema above.
- Use proper JOINs when data spans multiple tables.

Natural language query: {query}
""".strip()


def build_sql_prompt(query: str, schema: str) -> str:
    return ENGLISH_TO_SQL_PROMPT.format(schema=schema, query=query)