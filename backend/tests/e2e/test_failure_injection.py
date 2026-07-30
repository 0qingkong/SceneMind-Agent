from __future__ import annotations

import base64
from io import BytesIO
from time import perf_counter

import pytest

from app.dependencies import get_analysis_service, get_image_storage
from app.services.analysis_service import AnalysisService
from app.services.analyzers import AnalyzerError
from app.services.image_storage import ImageStorageError
from app.services.spatial import SpatialReasoner

from .conftest import DeterministicSystemAnalyzer, image_file


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        ({}, 422),
        ({"file": ("empty.jpg", BytesIO(), "image/jpeg")}, 400),
        ({"file": ("bad.txt", BytesIO(b"text"), "text/plain")}, 415),
        ({"file": ("bad.jpg", BytesIO(b"not-an-image"), "image/jpeg")}, 400),
        ({"file": ("bad.png", BytesIO(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl2nWQAAAAASUVORK5CYII=")), "image/png")}, 400),
    ],
)
def test_invalid_inputs_leave_no_rows_or_files(system_harness, files, expected) -> None:
    response = system_harness.client.post("/api/v1/observations", files=files)
    assert response.status_code == expected
    assert "traceback" not in response.text.casefold()
    assert system_harness.client.get("/api/v1/observations").json()["total"] == 0
    assert not system_harness.storage.root.exists() or not list(system_harness.storage.root.iterdir())


def test_invalid_json_pagination_and_session_interval(system_harness) -> None:
    client = system_harness.client
    malformed = client.post(
        "/api/v1/agent/query",
        content=b"{bad",
        headers={"content-type": "application/json"},
    )
    assert malformed.status_code == 422
    assert client.get("/api/v1/observations?limit=0").status_code == 422
    assert client.get("/api/v1/observations?offset=-1").status_code == 422
    assert client.post(
        "/api/v1/capture-sessions",
        json={"source_type": "browser_camera", "sample_interval_seconds": 1},
    ).status_code == 422


def test_analyzer_failure_has_no_mock_fallback_or_partial_data(system_harness) -> None:
    class FailingAnalyzer(DeterministicSystemAnalyzer):
        engine = "failing-test-analyzer"

        def analyze(self, **_: object):
            raise AnalyzerError("controlled inference failure")

    system_harness.client.app.dependency_overrides[get_analysis_service] = lambda: AnalysisService(
        FailingAnalyzer(), SpatialReasoner()
    )
    response = system_harness.client.post(
        "/api/v1/observations",
        files={"file": ("desk.jpg", image_file(), "image/jpeg")},
    )
    assert response.status_code == 503
    assert "controlled inference failure" in response.json()["detail"]
    assert system_harness.client.get("/api/v1/observations").json()["total"] == 0
    assert not system_harness.storage.root.exists() or not list(system_harness.storage.root.iterdir())


def test_storage_failure_is_explicit_and_creates_no_row(system_harness) -> None:
    class FailingStorage:
        def save(self, *_: object, **__: object) -> str:
            raise ImageStorageError("controlled storage failure")

    system_harness.client.app.dependency_overrides[get_image_storage] = lambda: FailingStorage()
    response = system_harness.client.post(
        "/api/v1/observations",
        files={"file": ("desk.jpg", image_file(), "image/jpeg")},
    )
    assert response.status_code == 500
    assert "controlled storage failure" in response.json()["detail"]
    assert str(system_harness.root) not in response.text
    assert system_harness.client.get("/api/v1/observations").json()["total"] == 0


def test_stopped_session_rejects_samples_and_delete_is_documented(system_harness) -> None:
    client = system_harness.client
    created = client.post(
        "/api/v1/capture-sessions",
        json={"source_type": "browser_camera", "sample_interval_seconds": 5},
    )
    session_id = created.json()["id"]
    assert client.delete(f"/api/v1/capture-sessions/{session_id}").status_code == 409
    assert client.post(f"/api/v1/capture-sessions/{session_id}/stop").status_code == 200
    assert client.post(f"/api/v1/capture-sessions/{session_id}/stop").status_code == 200
    rejected = client.post(
        f"/api/v1/capture-sessions/{session_id}/samples",
        files={"file": ("frame.jpg", image_file(), "image/jpeg")},
    )
    assert rejected.status_code == 409
    assert client.delete(f"/api/v1/capture-sessions/{session_id}").status_code == 204
    assert client.delete(f"/api/v1/capture-sessions/{session_id}").status_code == 404


def test_deterministic_api_latency_stays_within_broad_regression_budget(system_harness) -> None:
    client = system_harness.client
    calls = {
        "health": lambda: client.get("/api/v1/health"),
        "readiness": lambda: client.get("/api/v1/ready"),
        "observation_list": lambda: client.get("/api/v1/observations"),
        "last_seen": lambda: client.get("/api/v1/memory/last-seen?q=missing"),
        "agent_query": lambda: client.post("/api/v1/agent/query", json={"query": "Where is the missing cup?"}),
        "insights": lambda: client.get("/api/v1/insights"),
    }
    timings: dict[str, float] = {}
    for name, call in calls.items():
        started = perf_counter()
        response = call()
        timings[name] = perf_counter() - started
        assert response.status_code in {200, 404}, (name, response.text)
    assert all(seconds < 10 for seconds in timings.values()), timings
