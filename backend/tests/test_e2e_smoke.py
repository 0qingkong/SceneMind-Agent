"""Fast end-to-end smoke path using fake inference and temporary storage."""

from io import BytesIO
from pathlib import Path

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


class SmokeAnalyzer:
    engine = "fake-smoke-detector"
    model_name = "fake-smoke"
    is_loaded = True
    device = "cpu"

    def analyze(self, **_: object) -> AnalysisResult:
        return AnalysisResult(
            scene_summary="检测到杯子和笔记本电脑。",
            objects=[
                DetectedObject(id="cup-1", label="cup", display_name="杯子", confidence=0.96, bbox=[0.08, 0.35, 0.22, 0.65]),
                DetectedObject(id="laptop-1", label="laptop", display_name="笔记本电脑", confidence=0.94, bbox=[0.45, 0.24, 0.88, 0.68]),
            ],
        )


def _image() -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", (640, 480), "white").save(stream, "JPEG")
    stream.seek(0)
    return stream


def test_complete_api_smoke_path(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'smoke.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    settings = Settings(analyzer_mode="mock", demo_mode=False)
    analyzer = SmokeAnalyzer()
    analysis = AnalysisService(analyzer, SpatialReasoner())

    def sessions():
        yield from database.sessions()

    app.dependency_overrides[get_db_session] = sessions
    app.dependency_overrides[get_image_storage] = lambda: storage
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_analyzer] = lambda: analyzer
    app.dependency_overrides[get_analysis_service] = lambda: analysis

    try:
        with TestClient(app) as client:
            assert client.get("/api/v1/health").status_code == 200

            analyzed = client.post(
                "/api/v1/analyze",
                files={"image": ("desk.jpg", _image(), "image/jpeg")},
            )
            assert analyzed.status_code == 200
            assert analyzed.json()["engine"] == "fake-smoke-detector"

            saved = client.post(
                "/api/v1/observations",
                files={"file": ("desk.jpg", _image(), "image/jpeg")},
                data={"title": "Smoke desk", "location": "Lab"},
            )
            assert saved.status_code == 201
            observation_id = saved.json()["id"]

            listing = client.get("/api/v1/observations")
            assert listing.status_code == 200
            assert listing.json()["total"] == 1

            last_seen = client.get("/api/v1/memory/last-seen?q=cup")
            assert last_seen.status_code == 200
            assert last_seen.json()["result"]["observation"]["id"] == observation_id

            agent = client.post(
                "/api/v1/agent/query",
                json={"query": "我的杯子最后出现在哪里？"},
            )
            assert agent.status_code == 200
            assert agent.json()["evidence"][0]["observation_id"] == observation_id

            detail = client.get(f"/api/v1/observations/{observation_id}")
            assert detail.status_code == 200

            assert client.delete(f"/api/v1/observations/{observation_id}").status_code == 204
            assert client.get(f"/api/v1/observations/{observation_id}").status_code == 404
            assert not list(storage.root.glob("*.jpg"))
    finally:
        app.dependency_overrides.clear()
        database.engine.dispose()
