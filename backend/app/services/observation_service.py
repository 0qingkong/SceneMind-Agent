from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories.observations import (
    ObservationRepository,
    observation_detail,
    observation_summary,
)
from app.schemas.observation import (
    ObservationDetail,
    ObservationListResponse,
)
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
    ) -> ObservationDetail:
        title = self._optional_text(title, "title")
        location = self._optional_text(location, "location")
        analysis = self.analysis_service.analyze(
            image_bytes=image_bytes,
            filename=filename,
            content_type=content_type,
        )
        mime_type = content_type or ""
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
            )
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            self.image_storage.delete(image_path)
            if isinstance(exc, ValueError):
                raise
            raise ObservationPersistenceError(
                f"Unable to persist scene observation: {exc}"
            ) from exc
        return observation_detail(model)

    def list(
        self,
        *,
        limit: int,
        offset: int,
        label: str | None,
        query: str | None,
    ) -> ObservationListResponse:
        items, total = self.repository.list(
            limit=limit,
            offset=offset,
            label=self._clean_query(label),
            query=self._clean_query(query),
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
    def _optional_text(value: str | None, field: str) -> str | None:
        if value is None or not value.strip():
            return None
        cleaned = value.strip()
        if len(cleaned) > 200:
            raise ValueError(f"{field} cannot exceed 200 characters")
        return cleaned

    @staticmethod
    def _clean_query(value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None
