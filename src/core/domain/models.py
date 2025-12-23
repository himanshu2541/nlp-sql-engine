from pydantic import BaseModel
from typing import List, Any


class SQLQuery(BaseModel):
    query: str
    explanation: str = ""


class QueryResult(BaseModel):
    columns: List[str]
    rows: List[List[Any]]


class NLQuery(BaseModel):
    question: str
    context: str = ""


class PipelineResult(BaseModel):
    sql_query: SQLQuery
    result: QueryResult