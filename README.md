# AI Analytics Assistant

A FastAPI-based web application that converts plain English questions into SQL queries and executes them against a PostgreSQL database.

## What It Does

- Runs a FastAPI server with REST endpoints
- Accepts natural language questions (e.g., "Show me the top 5 customers by order amount")
- Uses Google's Gemini LLM to automatically translate English into SQL `SELECT` queries
- Executes the generated SQL safely against PostgreSQL
- Returns the database results as JSON

## Main Endpoint

```
GET /api/v1/natural-query?q=your+question
```

**Example:**
```
GET /api/v1/natural-query?q=Show me the top 5 customers by total order amount
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {"customer_id": 1, "total_amount": 5000},
    {"customer_id": 2, "total_amount": 4500},
    ...
  ],
  "count": 5
}
```

## Project Structure

### API Layer
- `app/main.py` — FastAPI app initialization, error handlers, health check

### Routes
- `app/api/v1/routes/query.py` — Public `/natural-query` endpoint

### Services
- `app/services/query_service.py` — Orchestrates SQL generation and execution
- `app/llm/sql_generator.py` — Calls LLM, cleans output, validates SQL
- `app/llm/prompt.py` — Defines the prompt template for the model
- `app/llm/client.py` — LLM client initialization

### Database
- `app/db/session.py` — SQLAlchemy session and connection pooling
- `app/db/operations.py` — Schema inspection and formatting
- `app/core/config.py` — Configuration and environment settings

### Error Handling
- `app/core/exceptions.py` — Custom exceptions (quota, invalid SQL, DB errors, etc.)

## How It Works

1. User sends a natural language question to `/api/v1/natural-query?q=...`
2. The app fetches the database schema (table names, column names)
3. A prompt is built combining the schema and the user's question
4. Gemini LLM is called to generate SQL
5. The response is cleaned (Markdown removed, validated)
6. The SQL is executed against PostgreSQL
7. Results are returned to the user

## Key Features

- **Natural Language Interface** — No SQL knowledge required
- **Safety** — Only `SELECT` queries allowed, forbidden keywords filtered
- **Error Handling** — Graceful handling of LLM quota, invalid SQL, and DB errors
- **Schema Awareness** — Automatically uses the database schema for better SQL generation
- **Logging** — Debug and info logs for troubleshooting

## Setup

### Requirements
- Python 3.9+
- PostgreSQL database
- Google Gemini API key

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://user:password@localhost/dbname
APP_ENV=development
LOG_LEVEL=INFO
GEMINI_MODEL=gemini-2.5-flash
```

### Run the Server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Health Check

```
GET http://localhost:8000/health
```

## Error Codes

| Status | Error | Meaning |
|--------|-------|---------|
| 400 | `DatabaseQueryException` | SQL execution failed |
| 422 | `InvalidSQLGeneratedException` | Generated SQL was invalid or unsafe |
| 429 | `LLMQuotaExceededException` | Gemini API quota exhausted |
| 502 | `LLMException` | LLM call failed |
| 500 | `SchemaFetchException` | Could not fetch database schema |

## Why Use This?

- **Speed** — Ask questions instead of writing SQL
- **Accessibility** — No expertise in SQL needed
- **Automation** — Great for dashboards, analytics, self-service BI
- **Safety** — Restricted to SELECT queries only

## Limitations

- Only supports `SELECT` queries
- Requires accurate database schema
- LLM may struggle with complex, multi-table questions
- Subject to Gemini API rate limits and costs

---

**Built with FastAPI, SQLAlchemy, PostgreSQL, and Google Gemini**
