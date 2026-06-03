from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.routes import chat, health, memory
from api.telemetry import setup_phoenix


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_phoenix()
    yield


app = FastAPI(title="MatchMind API", version="1.0.0", lifespan=lifespan)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
