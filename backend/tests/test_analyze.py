from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_rejects_text_file() -> None:
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("test.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 415


def test_analyze_returns_mock_result() -> None:
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("scene.jpg", BytesIO(b"fake-jpeg-content"), "image/jpeg")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["engine"] == "mock-day1"
    assert len(payload["objects"]) >= 1
