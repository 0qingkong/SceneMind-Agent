from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.agent import router as agent_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.health import router as health_router
from app.api.routes.memory import router as memory_router
from app.api.routes.observations import router as observations_router
from app.dependencies import database, image_storage, settings
from app.services.demo_data import DemoDataService


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.create_tables()
    if settings.demo_mode:
        with database.session_factory() as session:
            DemoDataService(session, image_storage).seed()
    yield

app = FastAPI(
    title="SceneMind Agent API",
    version="0.8.0",
    description="SceneMind Agent 多模态空间记忆服务。",
    lifespan=lifespan,
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
app.include_router(observations_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "SceneMind Agent API",
        "version": "0.8.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
