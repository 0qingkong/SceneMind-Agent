from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.agent.formatter import CATEGORY_LIMITATION, SPATIAL_LIMITATION
from app.agent.planner import AgentPlanner
from app.core.config import Settings
from app.db import Database
from app.dependencies import get_analysis_service, get_db_session, get_image_storage, get_settings
from app.main import app
from app.schemas.analyze import DetectedObject
from app.services.analysis_service import AnalysisService
from app.services.analyzers import AnalysisResult
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner


class AgentFixtureAnalyzer:
    engine = "fake-agent-detector"
    model_name = "fake"
    is_loaded = True
    device = "cpu"

    def analyze(self, **_: object) -> AnalysisResult:
        return AnalysisResult(
            scene_summary="检测到杯子、人物、椅子和电脑。",
            objects=[
                DetectedObject(id="cup-1", label="cup", display_name="杯子", confidence=0.95, bbox=[0.05, 0.3, 0.18, 0.6]),
                DetectedObject(id="person-1", label="person", display_name="人", confidence=0.94, bbox=[0.25, 0.1, 0.48, 0.85]),
                DetectedObject(id="chair-1", label="chair", display_name="椅子", confidence=0.91, bbox=[0.24, 0.55, 0.51, 0.94]),
                DetectedObject(id="laptop-1", label="laptop", display_name="笔记本电脑", confidence=0.93, bbox=[0.65, 0.35, 0.9, 0.62]),
            ],
        )


def image_stream() -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", (320, 240), "white").save(stream, "JPEG")
    stream.seek(0)
    return stream


@pytest.fixture
def agent_client(tmp_path: Path):
    database = Database(f"sqlite:///{tmp_path / 'agent.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    settings = Settings(agent_default_limit=3, agent_max_limit=5)

    def sessions():
        yield from database.sessions()

    app.dependency_overrides[get_db_session] = sessions
    app.dependency_overrides[get_image_storage] = lambda: storage
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_analysis_service] = lambda: AnalysisService(
        AgentFixtureAnalyzer(), SpatialReasoner()
    )
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    database.engine.dispose()


def save(client: TestClient, title: str, location: str = "图书馆") -> dict:
    response = client.post(
        "/api/v1/observations",
        files={"file": ("scene.jpg", image_stream(), "image/jpeg")},
        data={"title": title, "location": location},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.parametrize(
    ("query", "intent", "limit"),
    [
        ("我的杯子最后出现在哪里？", "last_seen", 1),
        ("最近在哪些场景里见过人物？", "history", 3),
        ("展示最近两条场景记忆", "recent_observations", 2),
        ("图书馆那条记录里有什么？", "observation_detail", 1),
        ("一共检测到多少把椅子？", "object_count", 3),
        ("在图书馆一共检测到多少个人？", "object_count", 3),
        ("help", "help", 3),
        ("今天天气怎么样？", "unknown", 3),
        ("Where was my mug last seen?", "last_seen", 1),
    ],
)
def test_deterministic_intent_planning(query: str, intent: str, limit: int) -> None:
    plan = AgentPlanner(default_limit=3, max_limit=5).plan(query)
    assert plan.intent == intent
    assert plan.limit == limit


def test_planner_clamps_requested_limits() -> None:
    plan = AgentPlanner(default_limit=3, max_limit=5).plan("展示最近99条场景记忆")
    assert plan.intent == "recent_observations"
    assert plan.limit == 5


def test_agent_api_answers_are_grounded_and_limited(agent_client: TestClient) -> None:
    created = save(agent_client, "图书馆阅读区")
    response = agent_client.post("/api/v1/agent/query", json={"query": "我的杯子最后出现在哪里？"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "last_seen"
    assert payload["evidence"][0]["observation_id"] == created["id"]
    assert payload["evidence"][0]["image_url"] == created["image_url"]
    assert payload["evidence"][0]["detail_url"] == created["detail_url"]
    assert payload["evidence"][0]["matched_objects"] == ["杯子"]
    assert CATEGORY_LIMITATION in payload["limitations"]
    assert SPATIAL_LIMITATION in payload["limitations"]
    assert payload["tool_steps"][0]["tool"] == "memory_last_seen"


def test_history_detail_count_limits_and_no_match(agent_client: TestClient) -> None:
    save(agent_client, "图书馆旧记录")
    save(agent_client, "图书馆新记录")

    history = agent_client.post("/api/v1/agent/query", json={"query": "最近在哪些场景里见过电脑？"}).json()
    assert history["intent"] == "history"
    assert len(history["evidence"]) == 2

    detail = agent_client.post("/api/v1/agent/query", json={"query": "图书馆那条记录里有什么？"}).json()
    assert detail["intent"] == "observation_detail"
    assert detail["evidence"][0]["title"] == "图书馆新记录"
    assert "人物" in detail["answer"]

    count = agent_client.post("/api/v1/agent/query", json={"query": "一共检测到多少把椅子？"}).json()
    assert count["intent"] == "object_count"
    assert count["tool_steps"][0]["result_count"] == 2
    assert "2" in count["answer"]

    scoped_count = agent_client.post("/api/v1/agent/query", json={"query": "在图书馆一共检测到多少个人？"}).json()
    assert scoped_count["tool_steps"][0]["arguments"]["location"] == "图书馆"
    assert scoped_count["tool_steps"][0]["result_count"] == 2

    no_match = agent_client.post("/api/v1/agent/query", json={"query": "我的手机最后出现在哪里？"}).json()
    assert no_match["intent"] == "last_seen"
    assert no_match["evidence"] == []
    assert no_match["tool_steps"][0]["status"] == "no_match"

    unknown = agent_client.post("/api/v1/agent/query", json={"query": "写一首诗"}).json()
    assert unknown["intent"] == "unknown"
    assert unknown["evidence"] == []


def test_agent_request_validation(agent_client: TestClient) -> None:
    response = agent_client.post("/api/v1/agent/query", json={"query": ""})
    assert response.status_code == 422
