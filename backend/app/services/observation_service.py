from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import CaptureSession
from app.repositories.observations import (
    ObservationRepository,
    observation_detail,
    observation_summary,
)
from app.schemas.observation import (
    ObservationDetail,
    ObservationListResponse,
)
from app.schemas.analyze import AnalyzeResponse
from app.services.analysis_service import AnalysisService
from app.services.image_storage import ImageStorage, ImageStorageError


class ObservationNotFoundError(LookupError):
    pass


class ObservationPersistenceError(RuntimeError):
    pass


class ObservationService:
    def __init__(
        self,
        session: Session,
        analysis_service: AnalysisService,
        image_storage: ImageStorage,
    ) -> None:
        self.session = session
        self.repository = ObservationRepository(session)
        self.analysis_service = analysis_service
        self.image_storage = image_storage

    def create(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        content_type: str | None,
        title: str | None,
        location: str | None,
        source_type: str | None = "upload",
        source_device_id: str | None = None,
        source_device_name: str | None = None,
        captured_at: datetime | None = None,
        session_id: str | None = None,
    ) -> ObservationDetail:
        title = self._optional_text(title, "title")
        location = self._optional_text(location, "location")
        analysis = self.analysis_service.analyze(
            image_bytes=image_bytes,
            filename=filename,
            content_type=content_type,
        )
        detail, _ = self.persist_analyzed(
            image_bytes=image_bytes,
            content_type=content_type or "",
            analysis=analysis,
            title=title,
            location=location,
            source_type=source_type,
            source_device_id=source_device_id,
            source_device_name=source_device_name,
            captured_at=captured_at,
            session_id=session_id,
            commit=True,
        )
        return detail

    def persist_analyzed(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
        analysis: AnalyzeResponse,
        title: str | None,
        location: str | None,
        source_type: str | None,
        source_device_id: str | None,
        source_device_name: str | None,
        captured_at: datetime | None,
        session_id: str | None,
        commit: bool,
    ) -> tuple[ObservationDetail, str]:
        title = self._optional_text(title, "title")
        location = self._optional_text(location, "location")
        if session_id and self.session.get(CaptureSession, session_id) is None:
            raise ValueError("session_id does not reference an existing capture session")
        mime_type = content_type
        image_path = self.image_storage.save(image_bytes, mime_type)
        try:
            model = self.repository.create(
                observation_id=str(uuid4()),
                title=title,
                location=location,
                created_at=datetime.now(timezone.utc),
                image_path=image_path,
                mime_type=mime_type,
                analysis=analysis,
                source_type=self._optional_text(source_type, "source_type", 50),
                source_device_id=self._optional_text(source_device_id, "source_device_id", 255),
                source_device_name=self._optional_text(source_device_name, "source_device_name", 255),
                captured_at=captured_at,
                session_id=session_id,
            )
            if commit:
                self.session.commit()
        except Exception as exc:
            self.session.rollback()
            self.image_storage.delete(image_path)
            if isinstance(exc, ValueError):
                raise
            raise ObservationPersistenceError(
                f"Unable to persist scene observation: {exc}"
            ) from exc
        return observation_detail(model), image_path

    def list(
        self,
        *,
        limit: int,
        offset: int,
        label: str | None,
        query: str | None,
        session_id: str | None = None,
    ) -> ObservationListResponse:
        items, total = self.repository.list(
            limit=limit,
            offset=offset,
            label=self._clean_query(label),
            query=self._clean_query(query),
            session_id=self._clean_query(session_id),
        )
        return ObservationListResponse(
            items=[observation_summary(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    def detail(self, observation_id: str) -> ObservationDetail:
        model = self.repository.get(observation_id)
        if model is None:
            raise ObservationNotFoundError("Scene observation was not found")
        return observation_detail(model)

    def image(self, observation_id: str) -> tuple[Path, str]:
        model = self.repository.get(observation_id)
        if model is None:
            raise ObservationNotFoundError("Scene observation was not found")
        path = self.image_storage.existing_path(model.image_path)
        if path is None:
            raise ObservationNotFoundError("Stored scene image was not found")
        return path, model.mime_type

    def delete(self, observation_id: str) -> None:
        model = self.repository.get(observation_id)
        if model is None:
            raise ObservationNotFoundError("Scene observation was not found")
        staged_delete = self.image_storage.stage_delete(model.image_path)
        try:
            self.repository.delete(model)
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            try:
                self.image_storage.restore_delete(staged_delete)
            except OSError:
                pass
            raise ObservationPersistenceError(
                f"Unable to delete scene observation: {exc}"
            ) from exc
        try:
            self.image_storage.finalize_delete(staged_delete)
        except OSError as exc:
            raise ImageStorageError(
                "Observation rows were deleted, but final image cleanup failed"
            ) from exc

    @staticmethod
    def _optional_text(value: str | None, field: str, maximum: int = 200) -> str | None:
        if value is None or not value.strip():
            return None
        cleaned = value.strip()
        if len(cleaned) > maximum:
            raise ValueError(f"{field} cannot exceed {maximum} characters")
        return cleaned

    @staticmethod
    def _clean_query(value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None
