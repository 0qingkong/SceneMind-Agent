from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analyze import router as analyze_router
from app.api.routes.health import router as health_router

app = FastAPI(
    title="SceneMind Agent API",
    version="0.3.0",
    description="SceneMind Agent 多模态空间记忆服务。",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(analyze_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "SceneMind Agent API",
        "version": "0.3.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
