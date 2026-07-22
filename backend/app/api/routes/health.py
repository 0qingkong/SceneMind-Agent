from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.dependencies import get_analyzer, get_settings
from app.services.analyzers import SceneAnalyzer

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(
    settings: Annotated[Settings, Depends(get_settings)],
    analyzer: Annotated[SceneAnalyzer, Depends(get_analyzer)],
) -> dict[str, object]:
    return {
        "status": "ok",
        "service": "scenemind-agent-api",
        "version": "0.8.0",
        "analyzer": analyzer.engine,
        "analyzer_mode": settings.analyzer_mode,
        "model_name": analyzer.model_name,
        "model_loaded": analyzer.is_loaded,
        "device": analyzer.device,
        "demo_mode": settings.demo_mode,
        "timestamp": datetime.now(UTC).isoformat(),
    }
