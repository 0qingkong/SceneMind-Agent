from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.db import Database
from app.dependencies import get_analysis_service, get_db_session, get_image_storage
from app.main import app
from app.schemas.analyze import DetectedObject
from app.services.analysis_service import AnalysisService
from app.services.analyzers import AnalysisResult, AnalyzerError
from app.services.image_storage import ImageStorage, ImageStorageError
from app.services.observation_service import ObservationService
from app.services.spatial import SpatialReasoner


class ObservationAnalyzer:
    engine = "fake-memory-detector"
    model_name = "fake"
    is_loaded = True
    device = "cpu"

    def analyze(self, **_: object) -> AnalysisResult:
        return AnalysisResult(
            scene_summary="检测到 2 个人物。",
            objects=[
                DetectedObject(
                    id="object-1",
                    label="person",
                    display_name="人",
                    confidence=0.95,
                    bbox=[0.1, 0.2, 0.3, 0.8],
                ),
                DetectedObject(
                    id="object-2",
                    label="person",
                    display_name="人",
                    confidence=0.91,
                    bbox=[0.6, 0.2, 0.8, 0.8],
                ),
            ],
        )


def test_image() -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", (320, 240), "white").save(stream, "JPEG")
    stream.seek(0)
    return stream


@pytest.fixture
def observation_client(tmp_path: Path):
    database = Database(f"sqlite:///{tmp_path / 'test.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    analysis = AnalysisService(ObservationAnalyzer(), SpatialReasoner())

    def sessions():
        yield from database.sessions()

    app.dependency_overrides[get_db_session] = sessions
    app.dependency_overrides[get_image_storage] = lambda: storage
    app.dependency_overrides[get_analysis_service] = lambda: analysis
    yield TestClient(app), storage, database
    app.dependency_overrides.clear()
    database.engine.dispose()


def create_observation(client: TestClient, title: str = "会议室"):
    return client.post(
        "/api/v1/observations",
        files={"file": ("people.jpg", test_image(), "image/jpeg")},
        data={"title": title, "location": "上海办公室"},
    )


def test_create_retrieve_list_and_delete_observation(observation_client) -> None:
    client, storage, _ = observation_client
    created = create_observation(client)
    assert created.status_code == 201
    payload = created.json()
    observation_id = payload["id"]
    assert payload["object_count"] == 2
    assert [item["sort_order"] for item in payload["objects"]] == [0, 1]
    assert payload["relations"]
    assert payload["created_at"].endswith(("Z", "+00:00"))
    assert payload["image_url"] == f"/api/v1/observations/{observation_id}/image"
    assert str(storage.root) not in str(payload)
    assert all(
        relation["subject_id"] in {"object-1", "object-2"}
        and relation["object_id"] in {"object-1", "object-2"}
        for relation in payload["relations"]
    )

    detail = client.get(f"/api/v1/observations/{observation_id}")
    assert detail.status_code == 200
    assert detail.json()["objects"] == payload["objects"]
    listing = client.get("/api/v1/observations?label=PERSON&q=人")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    image = client.get(f"/api/v1/observations/{observation_id}/image")
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/jpeg"
    saved_images = list(storage.root.glob("*.jpg"))
    assert len(saved_images) == 1
    assert saved_images[0].stem.isalnum() and len(saved_images[0].stem) == 32

    saved_images[0].unlink()
    assert client.get(f"/api/v1/observations/{observation_id}/image").status_code == 404

    assert client.delete(f"/api/v1/observations/{observation_id}").status_code == 204
    assert client.get(f"/api/v1/observations/{observation_id}").status_code == 404
    assert not list(storage.root.glob("*.jpg"))


def test_newest_first_pagination_and_free_text(observation_client) -> None:
    client, _, _ = observation_client
    first = create_observation(client, "第一个场景").json()
    second = create_observation(client, "第二个场景").json()
    page = client.get("/api/v1/observations?limit=1&offset=0").json()
    assert page["total"] == 2
    assert page["items"][0]["id"] == second["id"]
    assert client.get("/api/v1/observations?q=第一个").json()["items"][0]["id"] == first["id"]
    assert client.get("/api/v1/observations?q=上海").json()["total"] == 2


def test_invalid_image_and_analyzer_failure_leave_no_rows_or_images(
    observation_client,
) -> None:
    client, storage, database = observation_client
    invalid = client.post(
        "/api/v1/observations",
        files={"file": ("bad.jpg", BytesIO(b"bad"), "image/jpeg")},
    )
    assert invalid.status_code == 400

    class FailingAnalyzer(ObservationAnalyzer):
        def analyze(self, **_: object) -> AnalysisResult:
            raise AnalyzerError("detector unavailable")

    app.dependency_overrides[get_analysis_service] = lambda: AnalysisService(
        FailingAnalyzer(), SpatialReasoner()
    )
    failed = create_observation(client)
    assert failed.status_code == 503
    assert client.get("/api/v1/observations").json()["total"] == 0
    assert not storage.root.exists() or not list(storage.root.iterdir())
    database.engine.dispose()


def test_storage_rejects_path_traversal(tmp_path: Path) -> None:
    storage = ImageStorage(tmp_path / "images")
    with pytest.raises(ImageStorageError):
        storage.resolve("../outside.jpg")


def test_persistence_failure_cleans_saved_image(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'failure.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    analysis = AnalysisService(ObservationAnalyzer(), SpatialReasoner())
    with database.session_factory() as session:
        service = ObservationService(session, analysis, storage)

        def fail_create(**_: object):
            raise RuntimeError("database write failed")

        service.repository.create = fail_create  # type: ignore[method-assign]
        with pytest.raises(Exception, match="Unable to persist"):
            service.create(
                image_bytes=test_image().getvalue(),
                filename="people.jpg",
                content_type="image/jpeg",
                title=None,
                location=None,
            )
    assert storage.root.exists()
    assert not list(storage.root.iterdir())
    database.engine.dispose()
