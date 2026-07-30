from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.version import APP_VERSION
from app.db.models import CaptureSession, Observation
from app.dependencies import (
    get_analyzer,
    get_db_session,
    get_image_storage,
    get_settings,
    get_spatial_reasoner,
)
from app.services.analyzers import SceneAnalyzer
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(
    settings: Annotated[Settings, Depends(get_settings)],
    analyzer: Annotated[SceneAnalyzer, Depends(get_analyzer)],
) -> dict[str, object]:
    return {
        "status": "ok",
        "service": "scenemind-agent-api",
        "version": APP_VERSION,
        "build": settings.app_build,
        "analyzer": analyzer.engine,
        "analyzer_mode": settings.analyzer_mode,
        "model_name": analyzer.model_name,
        "model_loaded": analyzer.is_loaded,
        "device": analyzer.device,
        "demo_mode": settings.demo_mode,
        "demo_profile": settings.demo_profile,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/ready")
def ready(
    settings: Annotated[Settings, Depends(get_settings)],
    analyzer: Annotated[SceneAnalyzer, Depends(get_analyzer)],
    reasoner: Annotated[SpatialReasoner, Depends(get_spatial_reasoner)],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[ImageStorage, Depends(get_image_storage)],
) -> JSONResponse:
    database_reachable = False
    demo_data_present = False
    active_session_count = 0
    try:
        session.execute(text("SELECT 1"))
        database_reachable = True
        demo_data_present = bool(
            session.scalar(
                select(func.count())
                .select_from(Observation)
                .where(or_(Observation.is_demo.is_(True), Observation.engine == "demo-seed"))
            )
        )
        active_session_count = int(
            session.scalar(
                select(func.count())
                .select_from(CaptureSession)
                .where(CaptureSession.status == "active")
            )
            or 0
        )
    except Exception:
        database_reachable = False

    try:
        storage_writable = storage.probe_writable()
    except Exception:
        storage_writable = False

    is_ready = database_reachable and storage_writable
    payload = {
        "status": "ready" if is_ready else "not_ready",
        "service": "scenemind-agent-api",
        "version": APP_VERSION,
        "build": settings.app_build,
        "database_reachable": database_reachable,
        "storage_writable": storage_writable,
        "analyzer_mode": settings.analyzer_mode,
        "model_configured": bool(analyzer.model_name),
        "model_name": analyzer.model_name,
        "model_loaded": analyzer.is_loaded,
        "device": analyzer.device,
        "spatial_reasoner_enabled": reasoner.enabled,
        "demo_mode": settings.demo_mode,
        "demo_profile": settings.demo_profile,
        "demo_data_present": demo_data_present,
        "active_session_count": active_session_count,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return JSONResponse(
        status_code=200 if is_ready else 503,
        content=jsonable_encoder(payload),
    )
