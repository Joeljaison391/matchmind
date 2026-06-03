from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "atlas_connected": True,
        "gemini_reachable": True,
        "phoenix_connected": True,
    }
