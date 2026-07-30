from datetime import datetime, timezone
from pathlib import Path

from app.agent.executor import AgentExecutor
from app.agent.planner import AgentPlanner
from app.agent.tools import AgentTools
from app.core.config import Settings
from app.db import Database
from app.db.models import CaptureSession, Observation
from app.repositories.observations import ObservationRepository
from app.services.dashboard_service import DashboardService
from app.services.demo_data import DEMO_SCENES, DEMO_SESSION_ID, DemoDataService
from app.services.image_storage import ImageStorage
from app.services.memory_service import MemoryService


def user_observation(storage: ImageStorage, observation_id: str) -> Observation:
    image_path = storage.save(b"real-user-image", "image/png")
    return Observation(
        id=observation_id,
        title="真实用户记录",
        location="办公室",
        created_at=datetime.now(timezone.utc),
        image_path=image_path,
        original_filename="real.png",
        mime_type="image/png",
        image_width=1,
        image_height=1,
        engine="real-detector",
        summary="真实记录",
        object_count=0,
        relation_count=0,
        is_demo=False,
    )


def test_demo_seed_is_idempotent_grounded_and_reset_is_scoped(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'demo.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    collision_id = DEMO_SCENES[0].observation_id
    user_id = "10000000-0000-4000-8000-000000000001"

    with database.session_factory() as session:
        collision = user_observation(storage, collision_id)
        user_row = user_observation(storage, user_id)
        collision_path = collision.image_path
        user_path = user_row.image_path
        session.add_all((collision, user_row))
        session.commit()

        service = DemoDataService(session, storage)
        first = service.seed()
        assert first.inserted_observations == len(DEMO_SCENES) - 1
        assert first.skipped_observations == 1
        assert first.inserted_sessions == 1
        second = service.seed()
        assert second.inserted_observations == 0
        assert second.skipped_observations == len(DEMO_SCENES)
        assert second.inserted_sessions == 0
        assert second.skipped_sessions == 1

        demo_rows = ObservationRepository(session).demo_observations()
        assert len(demo_rows) == len(DEMO_SCENES) - 1
        assert all(item.is_demo for item in demo_rows)
        assert all(item.title and item.title.startswith("[演示]") for item in demo_rows)
        assert all(item.engine == "demo-seed" for item in demo_rows)
        session_rows = sorted(
            (item for item in demo_rows if item.session_id == DEMO_SESSION_ID),
            key=lambda item: item.id,
        )
        assert [item.capture_reason for item in session_rows] == [
            "first_valid_sample",
            "label_multiset_changed",
        ]
        demo_session = session.get(CaptureSession, DEMO_SESSION_ID)
        assert demo_session is not None and demo_session.is_demo
        assert demo_session.saved_observations == 2

        memory = MemoryService(session, Settings())
        last_seen = memory.last_seen("杯子")
        assert last_seen.result.observation.is_demo is True
        assert last_seen.result.observation.id == DEMO_SCENES[-1].observation_id
        history = memory.history(query="杯子", limit=20, offset=0)
        assert history.total >= 2
        agent = AgentExecutor(AgentPlanner(), AgentTools(memory, Settings())).execute(
            "我的杯子最后出现在哪里？"
        )
        assert agent.evidence and agent.evidence[0].is_demo is True
        assert agent.evidence[0].observation_id == DEMO_SCENES[-1].observation_id

        dashboard = DashboardService(session)
        stats = dashboard.device_stats()
        insights = dashboard.insights()
        assert stats.session_count == 1
        assert any(item.source_type == "browser_camera" for item in stats.sources)
        assert insights.total_sessions == 1
        assert insights.total_observations == len(DEMO_SCENES) + 1

        demo_session.status = "active"
        demo_session.ended_at = None
        session.commit()
        reset = service.reset()
        assert reset.removed_observations == len(DEMO_SCENES) - 1
        assert reset.removed_sessions == 1
        assert reset.removed_files == len(DEMO_SCENES) - 1
        assert reset.stopped_active_sessions == 1
        repeated_reset = service.reset()
        assert repeated_reset.removed_observations == 0
        assert repeated_reset.removed_sessions == 0

        assert ObservationRepository(session).demo_observations() == []
        preserved_collision = ObservationRepository(session).get(collision_id)
        preserved_user = ObservationRepository(session).get(user_id)
        assert preserved_collision is not None and preserved_collision.title == "真实用户记录"
        assert preserved_user is not None and preserved_user.title == "真实用户记录"
        assert storage.existing_path(collision_path) is not None
        assert storage.existing_path(user_path) is not None
        assert len(list(storage.root.glob("*.png"))) == 2

    database.engine.dispose()


def test_demo_mode_configuration_defaults_off() -> None:
    assert Settings.from_env({}).demo_mode is False
    settings = Settings.from_env({"DEMO_MODE": "true", "DEMO_PROFILE": "C"})
    assert settings.demo_mode is True
    assert settings.demo_profile == "C"
