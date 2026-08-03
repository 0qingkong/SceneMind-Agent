from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import Settings
from app.db import Database
from app.dependencies import (
    get_analysis_service,
    get_analyzer,
    get_db_session,
    get_image_storage,
    get_settings,
)
from app.main import app
from app.schemas.analyze import DetectedObject
from app.services.analysis_service import AnalysisService
from app.services.analyzers import AnalysisResult
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner


class DeterministicSystemAnalyzer:
    engine = "fake-system-detector"
    model_name = "fake-system"
    is_loaded = True
    device = "cpu"

    def __init__(self) -> None:
        self.labels = ["cup", "laptop"]

    def analyze(self, **_: object) -> AnalysisResult:
        boxes = {
            "cup": [0.08, 0.35, 0.22, 0.65],
            "laptop": [0.45, 0.24, 0.88, 0.68],
            "book": [0.25, 0.55, 0.42, 0.78],
        }
        names = {"cup": "cup", "laptop": "laptop", "book": "book"}
        return AnalysisResult(
            scene_summary=f"Detected {len(self.labels)} objects.",
            objects=[
                DetectedObject(
                    id=f"{label}-{index}",
                    label=label,
                    display_name=names[label],
                    confidence=0.95 - index * 0.02,
                    bbox=boxes[label],
                )
                for index, label in enumerate(self.labels)
            ],
        )


def image_file(color: str = "white") -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", (640, 480), color).save(stream, "JPEG")
    stream.seek(0)
    return stream


@dataclass
class SystemHarness:
    client: TestClient
    database: Database
    storage: ImageStorage
    analyzer: DeterministicSystemAnalyzer
    root: Path


@pytest.fixture
def system_harness(tmp_path: Path):
    database = Database(f"sqlite:///{tmp_path / 'system.db'}")
    storage = ImageStorage(tmp_path / "images")
    settings = Settings(
        analyzer_mode="mock",
        demo_mode=False,
        database_url=database.url,
        scene_storage_dir=str(storage.root),
    )
    analyzer = DeterministicSystemAnalyzer()
    analysis = AnalysisService(analyzer, SpatialReasoner())

    def sessions():
        yield from database.sessions()

    app.state.database = database
    app.state.image_storage = storage
    app.state.settings = settings
    app.dependency_overrides[get_db_session] = sessions
    app.dependency_overrides[get_image_storage] = lambda: storage
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_analyzer] = lambda: analyzer
    app.dependency_overrides[get_analysis_service] = lambda: analysis
    try:
        with TestClient(app) as client:
            yield SystemHarness(client, database, storage, analyzer, tmp_path)
    finally:
        app.dependency_overrides.clear()
        for name in ("database", "image_storage", "settings"):
            if hasattr(app.state, name):
                delattr(app.state, name)
        database.engine.dispose()
