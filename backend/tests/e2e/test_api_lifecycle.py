from __future__ import annotations

from .conftest import image_file


def _assert_no_absolute_paths(value: object, root: str) -> None:
    serialized = str(value)
    assert root not in serialized
    assert "image_path" not in serialized


def test_complete_api_lifecycle(system_harness) -> None:
    client = system_harness.client

    assert client.get("/api/v1/health").status_code == 200
    ready = client.get("/api/v1/ready")
    assert ready.status_code == 200 and ready.json()["status"] == "ready"

    analyzed = client.post(
        "/api/v1/analyze",
        files={"image": ("desk.jpg", image_file(), "image/jpeg")},
    )
    assert analyzed.status_code == 200
    assert analyzed.json()["engine"] == "fake-system-detector"

    first = client.post(
        "/api/v1/observations",
        files={"file": ("desk.jpg", image_file(), "image/jpeg")},
        data={"title": "Earlier desk", "location": "Lab"},
    )
    second = client.post(
        "/api/v1/observations",
        files={"file": ("desk.jpg", image_file("ivory"), "image/jpeg")},
        data={"title": "Latest desk", "location": "Studio"},
    )
    assert first.status_code == second.status_code == 201
    first_id, second_id = first.json()["id"], second.json()["id"]

    listing = client.get("/api/v1/observations?limit=10")
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()["items"][:2]] == [second_id, first_id]
    detail = client.get(f"/api/v1/observations/{second_id}")
    assert detail.status_code == 200
    object_ids = {item["id"] for item in detail.json()["objects"]}
    assert all(
        relation["subject_id"] in object_ids and relation["object_id"] in object_ids
        for relation in detail.json()["relations"]
    )
    image = client.get(f"/api/v1/observations/{second_id}/image")
    assert image.status_code == 200 and image.content

    last_seen = client.get("/api/v1/memory/last-seen?q=cup")
    assert last_seen.status_code == 200
    assert last_seen.json()["result"]["observation"]["id"] == second_id
    history = client.get("/api/v1/memory/history?q=cup")
    assert [item["observation"]["id"] for item in history.json()["items"][:2]] == [second_id, first_id]
    agent = client.post("/api/v1/agent/query", json={"query": "Where was my cup last seen?"})
    assert agent.status_code == 200
    assert agent.json()["evidence"][0]["observation_id"] == second_id

    session = client.post(
        "/api/v1/capture-sessions",
        json={
            "title": "Lifecycle session",
            "source_type": "browser_camera",
            "sample_interval_seconds": 5,
            "auto_save_mode": "meaningful-change",
        },
    )
    assert session.status_code == 201
    session_id = session.json()["id"]
    saved = client.post(
        f"/api/v1/capture-sessions/{session_id}/samples",
        files={"file": ("frame-1.jpg", image_file(), "image/jpeg")},
    )
    assert saved.status_code == 200
    assert saved.json()["saved"] is True
    sample_observation_id = saved.json()["observation_id"]
    skipped = client.post(
        f"/api/v1/capture-sessions/{session_id}/samples",
        files={"file": ("frame-2.jpg", image_file(), "image/jpeg")},
    )
    assert skipped.status_code == 200
    assert skipped.json()["saved"] is False
    stopped = client.post(f"/api/v1/capture-sessions/{session_id}/stop")
    assert stopped.status_code == 200 and stopped.json()["status"] == "stopped"
    session_detail = client.get(f"/api/v1/capture-sessions/{session_id}")
    assert session_detail.status_code == 200
    assert session_detail.json()["sampled_frames"] == 2
    assert session_detail.json()["saved_observations"] == 1

    assert client.get("/api/v1/devices/stats").status_code == 200
    assert client.get("/api/v1/insights").json()["total_observations"] == 3
    exported = client.get("/api/v1/privacy/export")
    assert exported.status_code == 200
    _assert_no_absolute_paths(exported.json(), str(system_harness.root))

    assert client.delete(f"/api/v1/observations/{sample_observation_id}").status_code == 204
    assert client.delete(f"/api/v1/capture-sessions/{session_id}").status_code == 204
    assert client.delete(f"/api/v1/observations/{first_id}").status_code == 204
    assert client.delete(f"/api/v1/observations/{second_id}").status_code == 204
    assert client.get(f"/api/v1/observations/{second_id}").status_code == 404
    assert client.get(f"/api/v1/observations/{second_id}/image").status_code == 404
    assert client.get(f"/api/v1/capture-sessions/{session_id}").status_code == 404
    assert not list(system_harness.storage.root.glob("*"))
