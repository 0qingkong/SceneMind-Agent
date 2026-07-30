import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.api.routes.health import ready
from app.db import Database
from app.dependencies import get_analyzer, get_settings
from app.main import app
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner
from app.services.analyzers.yolo import YoloSceneAnalyzer

client = TestClient(app)


def test_health() -> None:
    settings = Settings(analyzer_mode="yolo", yolo_model="yolo26n.pt")
    analyzer = YoloSceneAnalyzer(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_analyzer] = lambda: analyzer
    try:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["version"] == "0.13.0"
        assert payload["analyzer_mode"] == "yolo"
        assert payload["model_name"] == "yolo26n.pt"
        assert payload["model_loaded"] is False
        assert payload["device"] is None
        assert analyzer.is_loaded is False
    finally:
        app.dependency_overrides.clear()


def test_readiness_reports_dependencies_without_loading_yolo(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'ready.db'}")
    database.create_tables()
    settings = Settings(
        analyzer_mode="yolo",
        yolo_model="configured-model.pt",
        demo_mode=True,
        demo_profile="C",
    )
    analyzer = YoloSceneAnalyzer(settings)
    with database.session_factory() as session:
        response = ready(
            settings,
            analyzer,
            SpatialReasoner(),
            session,
            ImageStorage(tmp_path / "images"),
        )
    payload = json.loads(response.body)
    assert response.status_code == 200
    assert payload["status"] == "ready"
    assert payload["database_reachable"] is True
    assert payload["storage_writable"] is True
    assert payload["model_configured"] is True
    assert payload["model_loaded"] is False
    assert payload["demo_profile"] == "C"
    assert analyzer.is_loaded is False
    serialized = response.body.decode()
    assert str(tmp_path) not in serialized
    assert "database_url" not in serialized
    database.engine.dispose()


def test_readiness_failure_is_observable_and_does_not_expose_error() -> None:
    class FailingSession:
        def execute(self, *_: object) -> None:
            raise RuntimeError("secret database path C:/private/demo.db")

    class FailingStorage:
        def probe_writable(self) -> bool:
            raise OSError("secret storage path")

    settings = Settings(analyzer_mode="yolo")
    analyzer = YoloSceneAnalyzer(settings)
    response = ready(
        settings,
        analyzer,
        SpatialReasoner(),
        FailingSession(),  # type: ignore[arg-type]
        FailingStorage(),  # type: ignore[arg-type]
    )
    payload = json.loads(response.body)
    assert response.status_code == 503
    assert payload["status"] == "not_ready"
    assert payload["database_reachable"] is False
    assert payload["storage_writable"] is False
    assert "secret" not in response.body.decode()
    assert analyzer.is_loaded is False
