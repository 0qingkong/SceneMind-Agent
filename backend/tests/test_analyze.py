from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.dependencies import get_analyzer
from app.main import app
from app.schemas.analyze import DetectedObject
from app.services.analyzers import AnalysisResult, AnalyzerError

client = TestClient(app)


class FakeAnalyzer:
    engine = "fake-detector"
    model_name = "fake-model"
    is_loaded = True
    device = "cpu"

    def analyze(self, **_: object) -> AnalysisResult:
        return AnalysisResult(
            scene_summary="检测到 1 个物体：椅子 1 个。",
            objects=[
                DetectedObject(
                    id="object-1",
                    label="chair",
                    display_name="椅子",
                    confidence=0.88,
                    bbox=[0.1, 0.2, 0.5, 0.8],
                )
            ],
        )


@pytest.fixture(autouse=True)
def override_analyzer() -> None:
    app.dependency_overrides[get_analyzer] = FakeAnalyzer
    yield
    app.dependency_overrides.clear()


def create_test_image(width: int = 640, height: int = 480) -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", (width, height), "white").save(stream, format="JPEG")
    stream.seek(0)
    return stream


def test_analyze_rejects_text_file() -> None:
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("test.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 415


def test_analyze_rejects_fake_image() -> None:
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("fake.jpg", BytesIO(b"not-an-image"), "image/jpeg")},
    )
    assert response.status_code == 400


def test_analyze_returns_dimensions_and_boxes() -> None:
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("scene.jpg", create_test_image(), "image/jpeg")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["engine"] == "fake-detector"
    assert payload["image_width"] == 640
    assert payload["image_height"] == 480
    assert payload["objects"][0]["bbox"] == [0.1, 0.2, 0.5, 0.8]


def test_analyze_reports_analyzer_failure() -> None:
    class FailingAnalyzer(FakeAnalyzer):
        def analyze(self, **_: object) -> AnalysisResult:
            raise AnalyzerError("real detector unavailable")

    app.dependency_overrides[get_analyzer] = FailingAnalyzer
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("scene.jpg", create_test_image(), "image/jpeg")},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "real detector unavailable"
