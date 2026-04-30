from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.query import NaturalQueryResponse
from app.services.query_service import get_query_results

router = APIRouter()


@router.get(
    "/natural-query",
    response_model=NaturalQueryResponse,
    summary="Convert natural language to SQL and return results",
    response_description="The generated SQL query and matching database rows.",
)
async def natural_query(
    q: str = Query(..., min_length=3, description="Your question in plain English."),
    db: Session = Depends(get_db),
) -> NaturalQueryResponse:
    """
    Accepts a plain English question, converts it to SQL via an LLM,
    executes it against the database, and returns the results.

    **Example**: `?q=Show me the top 5 customers by total order amount`
    """
    data = get_query_results(q, db)
    return NaturalQueryResponse(
        status="success",
        data=data,
        count=len(data),
    )