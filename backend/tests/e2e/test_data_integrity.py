from __future__ import annotations

from app.db.models import ObservedRelation
from app.services.data_integrity import DataIntegrityValidator
from app.services.demo_data import DemoDataService


def test_seeded_isolated_database_passes_integrity(system_harness) -> None:
    with system_harness.database.session_factory() as session:
        DemoDataService(session, system_harness.storage).seed()
        report = DataIntegrityValidator(session, system_harness.storage).run()
    assert report.ok, report.to_dict()
    assert all(item.passed for item in report.checks)


def test_invalid_relation_and_orphan_image_are_reported(system_harness) -> None:
    with system_harness.database.session_factory() as session:
        DemoDataService(session, system_harness.storage).seed()
        relation = session.query(ObservedRelation).first()
        assert relation is not None
        relation.subject_id = "missing-object"
        session.commit()
        (system_harness.storage.root / "orphan.png").write_bytes(b"orphan")
        report = DataIntegrityValidator(session, system_harness.storage).run()
    failed = {item.name for item in report.checks if not item.passed}
    assert "relation_references" in failed
    assert "unreferenced_images" in failed
