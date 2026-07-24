from pathlib import Path

from app.core.config import Settings
from app.db import Database
from app.schemas.capture import CaptureSessionCreate
from app.services.analysis_service import AnalysisService
from app.services.capture_session_service import CaptureSessionService
from app.services.dashboard_service import DashboardService
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner
from test_capture_sessions import MutableCaptureAnalyzer, image_bytes


def test_dashboard_empty_state(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'empty.db'}")
    database.create_tables()
    with database.session_factory() as session:
        service = DashboardService(session)
        insights = service.insights()
        assert insights.total_observations == 0
        assert insights.total_sessions == 0
        assert insights.session_save_efficiency == 0
        assert insights.top_objects == []
        assert len(insights.daily_activity) == 30
        stats = service.device_stats()
        assert stats.memory_count == 0 and stats.sources == []
    database.engine.dispose()


def test_device_stats_insights_and_export_use_persisted_data(tmp_path: Path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'dashboard.db'}")
    database.create_tables()
    storage = ImageStorage(tmp_path / "images")
    analyzer = MutableCaptureAnalyzer()
    settings = Settings()
    with database.session_factory() as session:
        capture = CaptureSessionService(
            session,
            AnalysisService(analyzer, SpatialReasoner()),
            storage,
            settings,
        )
        created = capture.create(
            CaptureSessionCreate(
                title="统计会话",
                source_type="browser_camera",
                device_name="Dashboard Camera",
                sample_interval_seconds=5,
            )
        )
        result = capture.sample(
            created.id,
            image_bytes=image_bytes(),
            filename="capture.jpg",
            content_type="image/jpeg",
            force_save=False,
            captured_at=None,
            source_device_id="dashboard-camera",
            source_device_name="Dashboard Camera",
        )
        assert result.saved

        dashboard = DashboardService(session)
        stats = dashboard.device_stats()
        assert stats.memory_count == 1
        assert stats.session_count == 1
        assert stats.active_session_count == 1
        assert any(item.source_type == "browser_camera" for item in stats.sources)

        insights = dashboard.insights()
        assert insights.total_observations == 1
        assert insights.sampled_frames == 1
        assert insights.analyzed_frames == 1
        assert insights.saved_frames == 1
        assert insights.session_save_efficiency == 1
        assert insights.top_objects[0].label == "人"

        exported = dashboard.export()
        assert len(exported.observations) == 1
        assert len(exported.capture_sessions) == 1
        payload = exported.model_dump_json()
        assert str(tmp_path) not in payload
        assert "image_path" not in payload
    database.engine.dispose()
