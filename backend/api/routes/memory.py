import hashlib

from fastapi import APIRouter, Depends

from agents.memory_agent import get_fan_profile
from api.db import get_db

router = APIRouter()


@router.get("/memory/{session_id}")
def get_memory(session_id: str, db=Depends(get_db)):
    fan_id = hashlib.sha256(session_id.encode()).hexdigest()[:16]
    profile = get_fan_profile(db, fan_id)
    return profile or {}
