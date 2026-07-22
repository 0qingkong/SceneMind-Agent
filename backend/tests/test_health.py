from fastapi.testclient import TestClient

from app.core.config import Settings
from app.dependencies import get_analyzer, get_settings
from app.main import app
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
        assert payload["version"] == "0.8.0"
        assert payload["analyzer_mode"] == "yolo"
        assert payload["model_name"] == "yolo26n.pt"
        assert payload["model_loaded"] is False
        assert payload["device"] is None
        assert analyzer.is_loaded is False
    finally:
        app.dependency_overrides.clear()
