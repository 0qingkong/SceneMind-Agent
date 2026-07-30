from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.agent import router as agent_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.capture_sessions import router as capture_sessions_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.memory import router as memory_router
from app.api.routes.observations import router as observations_router
from app.dependencies import database, image_storage, settings
from app.core.version import APP_VERSION
from app.services.demo_data import DemoDataService


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Tests can bind isolated lifecycle resources through app.state without
    # mutating the production dependency singletons or the user's database.
    active_database = getattr(application.state, "database", database)
    active_storage = getattr(application.state, "image_storage", image_storage)
    active_settings = getattr(application.state, "settings", settings)
    active_database.create_tables()
    if active_settings.demo_mode:
        with active_database.session_factory() as session:
            DemoDataService(session, active_storage).seed()
    yield

app = FastAPI(
    title="SceneMind Agent API",
    version=APP_VERSION,
    description="SceneMind Agent 多模态空间记忆服务。",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(analyze_router, prefix="/api/v1")
app.include_router(observations_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(capture_sessions_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "SceneMind Agent API",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "ready": "/api/v1/ready",
    }
