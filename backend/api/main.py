from fastapi import FastAPI

from api.routes import chat, health, memory

app = FastAPI(title="MatchMind API", version="1.0.0")

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
