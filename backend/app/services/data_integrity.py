from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.models import CaptureSession, Observation, ObservedObject, ObservedRelation
from app.services.dashboard_service import DashboardService
from app.services.image_storage import ImageStorage, ImageStorageError


@dataclass(frozen=True, slots=True)
class IntegrityCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class IntegrityReport:
    ok: bool
    checks: list[IntegrityCheck]

    def to_dict(self) -> dict[str, object]:
        return {"ok": self.ok, "checks": [asdict(item) for item in self.checks]}


class DataIntegrityValidator:
    def __init__(self, session: Session, storage: ImageStorage) -> None:
        self.session = session
        self.storage = storage

    def run(self) -> IntegrityReport:
        observations = list(self.session.scalars(select(Observation)).unique())
        sessions = list(self.session.scalars(select(CaptureSession)).unique())
        checks = [
            self._count_fields(observations),
            self._relation_references(observations),
            self._orphans(),
            self._image_rows(observations),
            self._stored_images(observations),
            self._session_references(observations, sessions),
            self._sort_order(observations),
            self._demo_markers(observations, sessions),
            self._export_paths(),
        ]
        return IntegrityReport(ok=all(item.passed for item in checks), checks=checks)

    @staticmethod
    def _result(name: str, failures: list[str], success: str) -> IntegrityCheck:
        return IntegrityCheck(name, not failures, success if not failures else "; ".join(failures[:5]))

    def _count_fields(self, rows: list[Observation]) -> IntegrityCheck:
        failures = [
            row.id
            for row in rows
            if row.object_count != len(row.objects) or row.relation_count != len(row.relations)
        ]
        return self._result("count_fields", failures, f"{len(rows)} observations match child counts")

    def _relation_references(self, rows: list[Observation]) -> IntegrityCheck:
        failures: list[str] = []
        for row in rows:
            object_ids = {item.id for item in row.objects}
            for relation in row.relations:
                if (
                    relation.subject_id not in object_ids
                    or relation.object_id not in object_ids
                    or relation.subject_id == relation.object_id
                ):
                    failures.append(f"{row.id}:{relation.id}")
        return self._result("relation_references", failures, "all relation endpoints are local and non-self")

    def _orphans(self) -> IntegrityCheck:
        queries = {
            "objects": "SELECT COUNT(*) FROM observed_objects o LEFT JOIN observations p ON p.id=o.observation_id WHERE p.id IS NULL",
            "relations": "SELECT COUNT(*) FROM observed_relations r LEFT JOIN observations p ON p.id=r.observation_id WHERE p.id IS NULL",
            "sessions": "SELECT COUNT(*) FROM observations o LEFT JOIN capture_sessions s ON s.id=o.session_id WHERE o.session_id IS NOT NULL AND s.id IS NULL",
        }
        failures = [name for name, query in queries.items() if int(self.session.scalar(text(query)) or 0)]
        return self._result("orphan_rows", failures, "no orphan objects, relations, or session references")

    def _image_rows(self, rows: list[Observation]) -> IntegrityCheck:
        failures: list[str] = []
        for row in rows:
            try:
                if self.storage.existing_path(row.image_path) is None:
                    failures.append(row.id)
            except ImageStorageError:
                failures.append(row.id)
        return self._result("observation_images", failures, "every observation image exists inside storage")

    def _stored_images(self, rows: list[Observation]) -> IntegrityCheck:
        expected = {Path(row.image_path).name for row in rows}
        actual = {
            item.name
            for item in self.storage.root.glob("*")
            if item.is_file() and not item.name.startswith(".")
        } if self.storage.root.exists() else set()
        failures = sorted(actual - expected)
        return self._result("unreferenced_images", failures, "no stored image is missing an observation row")

    def _session_references(
        self, rows: list[Observation], sessions: list[CaptureSession]
    ) -> IntegrityCheck:
        session_ids = {item.id for item in sessions}
        failures = [row.id for row in rows if row.session_id and row.session_id not in session_ids]
        return self._result("session_references", failures, "all observation session references are valid")

    def _sort_order(self, rows: list[Observation]) -> IntegrityCheck:
        failures = []
        for row in rows:
            order = [item.sort_order for item in row.objects]
            if order != list(range(len(order))):
                failures.append(row.id)
        return self._result("object_sort_order", failures, "object sort order is stable and unique")

    def _demo_markers(
        self, rows: list[Observation], sessions: list[CaptureSession]
    ) -> IntegrityCheck:
        session_demo = {item.id: item.is_demo for item in sessions}
        failures = [
            row.id
            for row in rows
            if (row.engine == "demo-seed") != row.is_demo
            or (row.session_id and row.is_demo != session_demo.get(row.session_id, row.is_demo))
        ]
        return self._result("demo_markers", failures, "demo markers are internally consistent")

    def _export_paths(self) -> IntegrityCheck:
        payload = DashboardService(self.session).export().model_dump_json()
        failures = []
        if str(self.storage.root) in payload or "image_path" in payload:
            failures.append("export exposes storage details")
        return self._result("export_paths", failures, "export contains no storage path fields")
