from pydantic import BaseModel, Field
from typing import List, Dict, Any


class NaturalQueryResponse(BaseModel):
    status: str = Field(examples=["success"])
    data: List[Dict[str, Any]] = Field(description="The results of the generated SQL query")
    insight: str = Field(description="Plain English summary of the query results.")
    count: int = Field(description="The number of rows returned by the SQL query")
    sql: str = Field(description="The generated SQL query.")
    explanation: str = Field(description="One sentence explanation of what the SQL query does.")