from fastapi import APIRouter, Depends

from api.db import get_db
from api.orchestrator import handle
from api.schemas import ChatRequest

router = APIRouter()


@router.post("/chat")
def chat(req: ChatRequest, db=Depends(get_db)):
    return handle(db, req.message, req.session_id, req.language_hint)
