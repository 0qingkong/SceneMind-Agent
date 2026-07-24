from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import Settings
from app.db import Database
from app.dependencies import get_analysis_service, get_db_session, get_image_storage, get_settings
from app.main import app
from app.services.analysis_service import AnalysisService
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner
from test_capture_sessions import MutableCaptureAnalyzer


def image_stream() -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", (320, 240), "white").save(stream, "JPEG")
    stream.seek(0)
    return stream


def test_capture_session_api_lifecycle(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'api.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    analyzer = MutableCaptureAnalyzer()
    settings = Settings()

    def sessions():
        yield from database.sessions()

    app.dependency_overrides[get_db_session] = sessions
    app.dependency_overrides[get_image_storage] = lambda: storage
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_analysis_service] = lambda: AnalysisService(
        analyzer, SpatialReasoner()
    )
    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/capture-sessions",
                json={
                    "title": "API capture",
                    "source_type": "browser_camera",
                    "sample_interval_seconds": 5,
                    "target_query": "cup",
                    "auto_save_mode": "meaningful-change",
                },
            )
            assert created.status_code == 201
            session_id = created.json()["id"]

            sampled = client.post(
                f"/api/v1/capture-sessions/{session_id}/samples",
                files={"file": ("frame.jpg", image_stream(), "image/jpeg")},
                data={"force_save": "false", "source_device_name": "API Camera"},
            )
            assert sampled.status_code == 200
            assert sampled.json()["saved"] is True
            assert sampled.json()["observation_id"]

            assert client.get("/api/v1/capture-sessions").json()["total"] == 1
            detail = client.get(f"/api/v1/capture-sessions/{session_id}")
            assert detail.json()["recent_observations"][0]["source_device_name"] == "API Camera"

            assert client.delete(f"/api/v1/capture-sessions/{session_id}").status_code == 409
            assert client.post(f"/api/v1/capture-sessions/{session_id}/stop").status_code == 200
            assert client.delete(f"/api/v1/capture-sessions/{session_id}").status_code == 204
            assert client.get(f"/api/v1/capture-sessions/{session_id}").status_code == 404
    finally:
        app.dependency_overrides.clear()
        database.engine.dispose()
