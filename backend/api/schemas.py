from typing import Any, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str
    language_hint: Optional[str] = None


class TraceStep(BaseModel):
    agent: str
    tool: str
    query: str
    duration_ms: int
    score: Optional[float] = None


class TraceInfo(BaseModel):
    agents_fired: list[str]
    total_ms: int
    steps: list[TraceStep]


class ResponsePayload(BaseModel):
    type: str
    data: Any
    text: str


class ChatResponse(BaseModel):
    response: ResponsePayload
    trace: TraceInfo
    session_id: str
