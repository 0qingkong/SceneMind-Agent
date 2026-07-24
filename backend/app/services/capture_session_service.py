from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from threading import Lock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import CaptureSession
from app.repositories.capture_sessions import CaptureSessionRepository
from app.repositories.observations import observation_summary
from app.schemas.capture import (
    CaptureSampleResponse,
    CaptureSessionCreate,
    CaptureSessionDetail,
    CaptureSessionListResponse,
    CaptureSessionSummary,
)
from app.services.analysis_service import AnalysisService
from app.services.image_storage import ImageStorage
from app.services.memory_service import object_matches, search_terms
from app.services.observation_service import ObservationService


class CaptureSessionNotFoundError(LookupError):
    pass


class CaptureSessionStateError(RuntimeError):
    pass


class CaptureSampleInProgressError(RuntimeError):
    pass


_locks_guard = Lock()
_sample_locks: dict[str, Lock] = {}


def _sample_lock(session_id: str) -> Lock:
    with _locks_guard:
        return _sample_locks.setdefault(session_id, Lock())


def _utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def session_summary(model: CaptureSession) -> CaptureSessionSummary:
    return CaptureSessionSummary(
        id=model.id,
        title=model.title,
        location=model.location,
        source_type=model.source_type,
        device_name=model.device_name,
        status=model.status,
        started_at=_utc(model.started_at),
        ended_at=_utc(model.ended_at),
        sample_interval_seconds=model.sample_interval_seconds,
        sampled_frames=model.sampled_frames,
        analyzed_frames=model.analyzed_frames,
        saved_observations=model.saved_observations,
        target_query=model.target_query,
        target_seen=model.target_seen,
        last_error=model.last_error,
        auto_save_mode=model.auto_save_mode,
        last_sampled_at=_utc(model.last_sampled_at),
        last_saved_at=_utc(model.last_saved_at),
    )


class CaptureSessionService:
    def __init__(
        self,
        session: Session,
        analysis_service: AnalysisService,
        image_storage: ImageStorage,
        settings: Settings,
    ) -> None:
        self.session = session
        self.repository = CaptureSessionRepository(session)
        self.analysis_service = analysis_service
        self.image_storage = image_storage
        self.settings = settings
        self.observations = ObservationService(session, analysis_service, image_storage)

    def create(self, request: CaptureSessionCreate) -> CaptureSessionDetail:
        interval = request.sample_interval_seconds or self.settings.capture_default_interval_seconds
        if not self.settings.capture_min_interval_seconds <= interval <= self.settings.capture_max_interval_seconds:
            raise ValueError(
                f"sample_interval_seconds must be between {self.settings.capture_min_interval_seconds} and {self.settings.capture_max_interval_seconds}"
            )
        model = CaptureSession(
            id=str(uuid4()),
            title=self._clean(request.title),
            location=self._clean(request.location),
            source_type=request.source_type.strip(),
            device_name=self._clean(request.device_name),
            status="active",
            started_at=datetime.now(timezone.utc),
            ended_at=None,
            sample_interval_seconds=interval,
            sampled_frames=0,
            analyzed_frames=0,
            saved_observations=0,
            target_query=self._clean(request.target_query),
            last_error=None,
            auto_save_mode=request.auto_save_mode,
            last_labels_json="[]",
            target_seen=False,
        )
        self.repository.create(model)
        self.session.commit()
        return self._detail(model)

    def list(self) -> CaptureSessionListResponse:
        items, total = self.repository.list()
        return CaptureSessionListResponse(
            items=[session_summary(item) for item in items],
            total=total,
        )

    def detail(self, session_id: str) -> CaptureSessionDetail:
        return self._detail(self._get(session_id))

    def sample(
        self,
        session_id: str,
        *,
        image_bytes: bytes,
        filename: str,
        content_type: str | None,
        force_save: bool,
        captured_at: datetime | None,
        source_device_id: str | None,
        source_device_name: str | None,
    ) -> CaptureSampleResponse:
        lock = _sample_lock(session_id)
        if not lock.acquire(blocking=False):
            raise CaptureSampleInProgressError("A sample is already being analyzed for this session")
        try:
            return self._sample_locked(
                session_id,
                image_bytes=image_bytes,
                filename=filename,
                content_type=content_type,
                force_save=force_save,
                captured_at=captured_at,
                source_device_id=source_device_id,
                source_device_name=source_device_name,
            )
        finally:
            lock.release()

    def _sample_locked(
        self,
        session_id: str,
        **sample: object,
    ) -> CaptureSampleResponse:
        model = self._get(session_id)
        if model.status != "active":
            raise CaptureSessionStateError("Capture session is not active")
        now = datetime.now(timezone.utc)
        started_at = _utc(model.started_at) or now
        if now - started_at > timedelta(minutes=self.settings.capture_max_session_minutes):
            model.status = "stopped"
            model.ended_at = now
            model.last_error = "Maximum session duration reached"
            self.session.commit()
            raise CaptureSessionStateError("Maximum capture session duration reached")

        model.sampled_frames += 1
        model.last_sampled_at = now
        sample_device_name = self._clean(sample["source_device_name"])  # type: ignore[arg-type]
        if sample_device_name and not model.device_name:
            model.device_name = sample_device_name
        try:
            analysis = self.analysis_service.analyze(
                image_bytes=sample["image_bytes"],  # type: ignore[arg-type]
                filename=sample["filename"],  # type: ignore[arg-type]
                content_type=sample["content_type"],  # type: ignore[arg-type]
            )
        except Exception as exc:
            model.status = "failed"
            model.ended_at = now
            model.last_error = str(exc)[:500]
            self.session.commit()
            raise

        model.analyzed_frames += 1
        labels = sorted(item.label.casefold() for item in analysis.objects)
        previous_labels = json.loads(model.last_labels_json or "[]")
        target_found = self._target_found(model.target_query, analysis.objects)
        target_first = target_found and not model.target_seen
        if target_found:
            model.target_seen = True
        reason = self._save_reason(
            model,
            labels=labels,
            previous_labels=previous_labels,
            force_save=bool(sample["force_save"]),
            target_first=target_first,
            now=now,
        )
        should_save = reason not in {"manual_mode", "no_meaningful_change"}
        observation_id = None
        image_path = None
        try:
            if should_save:
                detail, image_path = self.observations.persist_analyzed(
                    image_bytes=sample["image_bytes"],  # type: ignore[arg-type]
                    content_type=str(sample["content_type"] or ""),
                    analysis=analysis,
                    title=model.title,
                    location=model.location,
                    source_type=model.source_type,
                    source_device_id=self._clean(sample["source_device_id"]),  # type: ignore[arg-type]
                    source_device_name=sample_device_name,
                    captured_at=sample["captured_at"] or now,  # type: ignore[arg-type]
                    session_id=model.id,
                    commit=False,
                )
                observation_id = detail.id
                model.saved_observations += 1
                model.last_saved_at = now
            model.last_labels_json = json.dumps(labels)
            model.last_error = None
            self.session.commit()
        except Exception:
            self.session.rollback()
            if image_path:
                self.image_storage.delete(image_path)
            raise
        return CaptureSampleResponse(
            session=session_summary(model),
            saved=should_save,
            reason=reason,
            observation_id=observation_id,
            target_found=target_found,
            analysis=analysis,
        )

    def stop(self, session_id: str) -> CaptureSessionDetail:
        model = self._get(session_id)
        if model.status == "active":
            model.status = "stopped"
            model.ended_at = datetime.now(timezone.utc)
            self.session.commit()
        return self._detail(model)

    def delete(self, session_id: str) -> None:
        model = self._get(session_id)
        if model.status == "active":
            raise CaptureSessionStateError("Stop the capture session before deleting it")
        for observation in model.observations:
            observation.session_id = None
        self.session.flush()
        self.repository.delete(model)
        self.session.commit()
        with _locks_guard:
            _sample_locks.pop(session_id, None)

    def _save_reason(
        self,
        model: CaptureSession,
        *,
        labels: list[str],
        previous_labels: list[str],
        force_save: bool,
        target_first: bool,
        now: datetime,
    ) -> str:
        if force_save:
            return "force_save"
        if model.auto_save_mode == "manual":
            return "manual_mode"
        if model.auto_save_mode == "every-analyzed-sample":
            return "every_analyzed_sample"
        if model.analyzed_frames == 1:
            return "first_valid_sample"
        if target_first:
            return "target_first_appearance"
        if Counter(labels) != Counter(previous_labels):
            if abs(len(labels) - len(previous_labels)) >= self.settings.capture_object_count_delta:
                return "object_count_delta"
            return "label_multiset_changed"
        last_saved_at = _utc(model.last_saved_at)
        if last_saved_at and (now - last_saved_at).total_seconds() >= self.settings.capture_min_save_gap_seconds:
            return "minimum_save_gap"
        return "no_meaningful_change"

    @staticmethod
    def _target_found(query: str | None, objects: list[object]) -> bool:
        if not query:
            return False
        terms = search_terms(query)
        return any(object_matches(item, terms) for item in objects)  # type: ignore[arg-type]

    def _get(self, session_id: str) -> CaptureSession:
        model = self.repository.get(session_id)
        if model is None:
            raise CaptureSessionNotFoundError("Capture session was not found")
        return model

    @staticmethod
    def _clean(value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None

    @staticmethod
    def _detail(model: CaptureSession) -> CaptureSessionDetail:
        observations = sorted(
            model.observations,
            key=lambda item: (item.created_at, item.id),
            reverse=True,
        )[:20]
        return CaptureSessionDetail(
            **session_summary(model).model_dump(),
            recent_observations=[observation_summary(item) for item in observations],
        )
