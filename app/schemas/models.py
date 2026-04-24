from pydantic import BaseModel
from typing import Any


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    query_used: str | None = None
    raw_data: Any | None = None
