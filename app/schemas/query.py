from pydantic import BaseModel, Field
from typing import List, Dict, Any


class NaturalQueryResponse(BaseModel):
    status: str = Field(examples=["success"])
    data: List[Dict[str, Any]] = Field(description="The results of the generated SQL query")
    count: int = Field(description="The number of rows returned by the SQL query")