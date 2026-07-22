from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import Settings
from app.db import Database
from app.dependencies import (
    get_analysis_service,
    get_db_session,
    get_image_storage,
    get_settings,
)
from app.main import app
from app.schemas.analyze import DetectedObject
from app.services.analysis_service import AnalysisService
from app.services.analyzers import AnalysisResult
from app.services.image_storage import ImageStorage
from app.services.object_names import build_object_name_map
from app.services.spatial import SpatialReasoner


class QueryAnalyzer:
    engine = "fake-query-detector"
    model_name = "fake"
    is_loaded = True
    device = "cpu"

    def __init__(self, label: str = "cup", display_name: str = "杯子") -> None:
        self.label = label
        self.display_name = display_name

    def analyze(self, **_: object) -> AnalysisResult:
        return AnalysisResult(
            scene_summary=f"检测到 {self.display_name} 和瓶子。",
            objects=[
                DetectedObject(
                    id="object-1",
                    label=self.label,
                    display_name=self.display_name,
                    confidence=0.92,
                    bbox=[0.1, 0.3, 0.25, 0.6],
                ),
                DetectedObject(
                    id="object-2",
                    label="bottle",
                    display_name="瓶子",
                    confidence=0.88,
                    bbox=[0.32, 0.3, 0.45, 0.6],
                ),
                DetectedObject(
                    id="object-3",
                    label="book",
                    display_name="书本",
                    confidence=0.82,
                    bbox=[0.75, 0.65, 0.9, 0.8],
                ),
            ],
        )


def image_stream() -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", (320, 240), "white").save(stream, "JPEG")
    stream.seek(0)
    return stream


@pytest.fixture
def memory_client(tmp_path: Path):
    database = Database(f"sqlite:///{tmp_path / 'memory.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    settings = Settings(memory_relation_context_limit=2)

    def sessions():
        yield from database.sessions()

    app.dependency_overrides[get_db_session] = sessions
    app.dependency_overrides[get_image_storage] = lambda: storage
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_analysis_service] = lambda: AnalysisService(
        QueryAnalyzer(), SpatialReasoner()
    )
    yield TestClient(app)
    app.dependency_overrides.clear()
    database.engine.dispose()


def save(client: TestClient, title: str):
    response = client.post(
        "/api/v1/observations",
        files={"file": ("scene.jpg", image_stream(), "image/jpeg")},
        data={"title": title},
    )
    assert response.status_code == 201
    return response.json()


def test_english_chinese_partial_and_case_insensitive_search(memory_client) -> None:
    save(memory_client, "杯子场景")
    assert memory_client.get("/api/v1/memory/last-seen?q=CUP").status_code == 200
    assert memory_client.get("/api/v1/memory/last-seen?q=杯子").status_code == 200
    assert memory_client.get("/api/v1/memory/last-seen?q=up").status_code == 200


def test_last_seen_and_history_are_newest_first_and_paginated(memory_client) -> None:
    first = save(memory_client, "旧场景")
    second = save(memory_client, "新场景")
    latest = memory_client.get("/api/v1/memory/last-seen?q=cup").json()
    assert latest["result"]["observation"]["id"] == second["id"]
    history = memory_client.get("/api/v1/memory/history?q=cup&limit=1&offset=0").json()
    assert history["total"] == 2
    assert history["items"][0]["observation"]["id"] == second["id"]
    older = memory_client.get("/api/v1/memory/history?q=cup&limit=1&offset=1").json()
    assert older["items"][0]["observation"]["id"] == first["id"]


def test_no_match_behavior_and_relation_context(memory_client) -> None:
    save(memory_client, "桌面")
    assert memory_client.get("/api/v1/memory/last-seen?q=umbrella").status_code == 404
    assert memory_client.get("/api/v1/memory/history?q=umbrella").json()["items"] == []
    result = memory_client.get("/api/v1/memory/last-seen?q=cup").json()["result"]
    matched_ids = set(result["matched_object_ids"])
    assert matched_ids == {"object-1"}
    assert len(result["relations"]) <= 2
    assert all(
        relation["subject_id"] in matched_ids or relation["object_id"] in matched_ids
        for relation in result["relations"]
    )
    semantic_keys = {
        (
            relation["subject_id"],
            relation["object_id"],
        )
        for relation in result["relations"]
    }
    assert len(semantic_keys) == len(result["relations"])


def test_person_alias_and_stable_duplicate_numbering(memory_client) -> None:
    app.dependency_overrides[get_analysis_service] = lambda: AnalysisService(
        QueryAnalyzer("person", "人"), SpatialReasoner()
    )
    save(memory_client, "人物场景")
    response = memory_client.get("/api/v1/memory/last-seen?q=人物")
    assert response.status_code == 200
    assert response.json()["result"]["matched_names"] == ["人物"]

    class Item:
        def __init__(self, object_id: str, sort_order: int) -> None:
            self.id = object_id
            self.label = "person"
            self.display_name = "人"
            self.sort_order = sort_order

    names = build_object_name_map([Item("second", 1), Item("first", 0)])
    assert names == {"first": "人物 1", "second": "人物 2"}
