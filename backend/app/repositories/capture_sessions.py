from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import CaptureSession


class CaptureSessionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, model: CaptureSession) -> CaptureSession:
        self.session.add(model)
        self.session.flush()
        return model

    def get(self, session_id: str) -> CaptureSession | None:
        return self.session.scalar(
            select(CaptureSession)
            .where(CaptureSession.id == session_id)
            .options(selectinload(CaptureSession.observations))
        )

    def list(self, *, limit: int = 100, offset: int = 0) -> tuple[list[CaptureSession], int]:
        total = self.session.scalar(select(func.count()).select_from(CaptureSession)) or 0
        items = list(
            self.session.scalars(
                select(CaptureSession)
                .options(selectinload(CaptureSession.observations))
                .order_by(CaptureSession.started_at.desc(), CaptureSession.id.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        return items, total

    def active_count(self) -> int:
        return self.session.scalar(
            select(func.count()).select_from(CaptureSession).where(CaptureSession.status == "active")
        ) or 0

    def delete(self, model: CaptureSession) -> None:
        self.session.delete(model)
