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
- Always use meaningful table aliases that are NOT PostgreSQL reserved words.
  Use abbreviations like: cust, prod, ord, items, dlv — never use: do, as, in, is, on, to, by, at.
- Always qualify column names with table alias when joining multiple tables.
- Use double quotes around column or table names only if they contain special characters.


Natural language query: {query}
""".strip()


def build_sql_prompt(query: str, schema: str) -> str:
    return ENGLISH_TO_SQL_PROMPT.format(schema=schema, query=query)