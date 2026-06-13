from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.query import NaturalQueryResponse
from app.services.query_service import get_query_results

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

@router.get(
    "/natural-query",
    response_model=NaturalQueryResponse,
    summary="Convert natural language to SQL and return results",
    response_description="The generated SQL query and matching database rows.",
)
@limiter.limit("5/2hours") 
async def natural_query(
    request: Request,
    q: str = Query(..., min_length=3, description="Your question in plain English."),
    db: Session = Depends(get_db),
) -> NaturalQueryResponse:
    """
    Accepts a plain English question, converts it to SQL via an LLM,
    executes it against the database, and returns the results.

    **Example**: `?q=Show me the top 5 customers by total order amount`
    """
    sql, explanation, data, insights = get_query_results(q, db)
    return NaturalQueryResponse(
        status="success",
        data=data,
        count=len(data),
        insight=insights,
        explanation=explanation,
        sql=sql,
    )