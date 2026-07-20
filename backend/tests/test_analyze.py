from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


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
    assert payload["engine"] == "mock-v0.2"
    assert payload["image_width"] == 640
    assert payload["image_height"] == 480
    assert len(payload["objects"]) == 3
