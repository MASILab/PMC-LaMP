from pydantic import BaseModel
from typing import List, Tuple


class QueryRequest(BaseModel):
    query: str


class AnswerResponse(BaseModel):
    query: str
    answer: str
    references: List[Tuple[str, str, float]]


class ErrorResponse(BaseModel):
    detail: str
