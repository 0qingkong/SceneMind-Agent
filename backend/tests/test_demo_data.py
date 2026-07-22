from pathlib import Path
from datetime import datetime, timezone

from app.core.config import Settings
from app.db import Database
from app.db.models import Observation
from app.repositories.observations import ObservationRepository
from app.services.demo_data import DEMO_SCENES, DemoDataService
from app.services.image_storage import ImageStorage


def test_demo_seed_is_idempotent_visible_and_reset_is_scoped(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'demo.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")

    with database.session_factory() as session:
        real_path = storage.save(b"real-user-image", "image/png")
        real_id = DEMO_SCENES[0].observation_id
        session.add(
            Observation(
                id=real_id,
                title="真实用户记录",
                location="办公室",
                created_at=datetime.now(timezone.utc),
                image_path=real_path,
                original_filename="real.png",
                mime_type="image/png",
                image_width=1,
                image_height=1,
                engine="real-detector",
                summary="真实记录",
                object_count=0,
                relation_count=0,
            )
        )
        session.commit()
        service = DemoDataService(session, storage)
        assert service.seed() == len(DEMO_SCENES) - 1
        assert service.seed() == 0
        demo_rows = ObservationRepository(session).demo_observations()
        assert len(demo_rows) == len(DEMO_SCENES) - 1
        assert all(item.title and item.title.startswith("[演示]") for item in demo_rows)
        assert all(item.engine == "demo-seed" for item in demo_rows)
        assert service.reset() == len(DEMO_SCENES) - 1
        assert service.reset() == 0
        assert ObservationRepository(session).demo_observations() == []
        real_row = ObservationRepository(session).get(real_id)
        assert real_row is not None and real_row.title == "真实用户记录"
        assert storage.existing_path(real_path) is not None

    database.engine.dispose()


def test_demo_mode_configuration_defaults_off() -> None:
    assert Settings.from_env({}).demo_mode is False
    assert Settings.from_env({"DEMO_MODE": "true"}).demo_mode is True
