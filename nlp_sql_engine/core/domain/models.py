from pydantic import BaseModel, Field, ConfigDict
from typing import List, Any, Iterator, Optional


class SQLQuery(BaseModel):
    query: str
    explanation: str = ""


class QueryResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    columns: List[str] = Field(default_factory=list)
    rows: Optional[Iterator[List[Any]]] = None


class NLQuery(BaseModel):
    question: str
    context: str = ""


class PipelineResult(BaseModel):
    sql_query: Optional[SQLQuery] = None
    result: Optional[QueryResult] = None

    error: Optional[str] = None
