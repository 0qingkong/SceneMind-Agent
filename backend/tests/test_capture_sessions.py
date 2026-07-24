from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from app.core.config import Settings
from app.db import Database
from app.schemas.analyze import DetectedObject
from app.schemas.capture import CaptureSessionCreate
from app.services.analysis_service import AnalysisService
from app.services.analyzers import AnalysisResult
from app.services.capture_session_service import (
    CaptureSampleInProgressError,
    CaptureSessionService,
    CaptureSessionStateError,
    _sample_lock,
)
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner


class MutableCaptureAnalyzer:
    engine = "fake-capture"
    model_name = "fake"
    is_loaded = True
    device = "cpu"

    def __init__(self) -> None:
        self.labels = ["person"]

    def analyze(self, **_: object) -> AnalysisResult:
        display = {"person": "人", "cup": "杯子", "chair": "椅子"}
        return AnalysisResult(
            scene_summary=f"检测到 {len(self.labels)} 个物体。",
            objects=[
                DetectedObject(
                    id=f"object-{index}",
                    label=label,
                    display_name=display[label],
                    confidence=0.9,
                    bbox=[0.05 + index * 0.25, 0.2, 0.22 + index * 0.25, 0.75],
                )
                for index, label in enumerate(self.labels)
            ],
        )


def image_bytes() -> bytes:
    stream = BytesIO()
    Image.new("RGB", (320, 240), "white").save(stream, "JPEG")
    return stream.getvalue()


def make_service(database: Database, storage: ImageStorage, analyzer: MutableCaptureAnalyzer):
    session = database.session_factory()
    settings = Settings(
        capture_min_interval_seconds=3,
        capture_default_interval_seconds=5,
        capture_max_interval_seconds=60,
        capture_min_save_gap_seconds=15,
        capture_object_count_delta=2,
    )
    return session, CaptureSessionService(
        session,
        AnalysisService(analyzer, SpatialReasoner()),
        storage,
        settings,
    )


def sample(service: CaptureSessionService, session_id: str, force: bool = False):
    return service.sample(
        session_id,
        image_bytes=image_bytes(),
        filename="capture.jpg",
        content_type="image/jpeg",
        force_save=force,
        captured_at=None,
        source_device_id="camera-1",
        source_device_name="Test Camera",
    )


def test_session_policy_counters_target_and_restart_persistence(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'capture.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    analyzer = MutableCaptureAnalyzer()
    db_session, service = make_service(database, storage, analyzer)
    created = service.create(
        CaptureSessionCreate(
            title="桌面观察",
            location="实验室",
            source_type="browser_camera",
            device_name="Test Camera",
            sample_interval_seconds=5,
            target_query="杯子",
        )
    )

    first = sample(service, created.id)
    assert first.saved is True and first.reason == "first_valid_sample"
    second = sample(service, created.id)
    assert second.saved is False and second.reason == "no_meaningful_change"

    analyzer.labels = ["person", "cup"]
    target = sample(service, created.id)
    assert target.saved is True
    assert target.reason == "target_first_appearance"
    assert target.target_found is True
    assert target.session.sampled_frames == 3
    assert target.session.analyzed_frames == 3
    assert target.session.saved_observations == 2
    assert len(list(storage.root.glob("*.jpg"))) == 2

    with pytest.raises(CaptureSessionStateError):
        service.delete(created.id)
    stopped = service.stop(created.id)
    assert stopped.status == "stopped" and stopped.ended_at is not None
    db_session.close()

    restarted_session, restarted = make_service(database, storage, analyzer)
    persisted = restarted.detail(created.id)
    assert persisted.status == "stopped"
    assert persisted.saved_observations == 2
    assert len(persisted.recent_observations) == 2
    with pytest.raises(CaptureSessionStateError):
        sample(restarted, created.id)
    restarted.delete(created.id)
    assert restarted.observations.list(limit=20, offset=0, label=None, query=None).total == 2
    assert all(item.session_id is None for item in restarted.observations.list(limit=20, offset=0, label=None, query=None).items)
    restarted_session.close()
    database.engine.dispose()


def test_manual_mode_force_save_and_duplicate_sample_guard(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'manual.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    analyzer = MutableCaptureAnalyzer()
    db_session, service = make_service(database, storage, analyzer)
    created = service.create(
        CaptureSessionCreate(
            source_type="browser_camera",
            sample_interval_seconds=5,
            auto_save_mode="manual",
        )
    )
    automatic = sample(service, created.id)
    assert automatic.saved is False and automatic.reason == "manual_mode"
    forced = sample(service, created.id, force=True)
    assert forced.saved is True and forced.reason == "force_save"

    lock = _sample_lock(created.id)
    lock.acquire()
    try:
        with pytest.raises(CaptureSampleInProgressError):
            sample(service, created.id)
    finally:
        lock.release()
    service.stop(created.id)
    db_session.close()
    database.engine.dispose()


def test_session_interval_validation(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'interval.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    db_session, service = make_service(database, storage, MutableCaptureAnalyzer())
    with pytest.raises(ValueError, match="between 3 and 60"):
        service.create(CaptureSessionCreate(source_type="browser_camera", sample_interval_seconds=2))
    db_session.close()
    database.engine.dispose()
