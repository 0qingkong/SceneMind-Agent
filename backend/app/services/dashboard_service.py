from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import CaptureSession, Observation, ObservedObject
from app.repositories.observations import observation_detail
from app.schemas.dashboard import (
    DailyActivity,
    DataExportResponse,
    DeviceSourceStat,
    DeviceStatsResponse,
    InsightsResponse,
    RankedCount,
)
from app.services.capture_session_service import session_summary


def _utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def device_stats(self) -> DeviceStatsResponse:
        memory_count = self._count(Observation)
        session_count = self._count(CaptureSession)
        active_count = self.session.scalar(
            select(func.count()).select_from(CaptureSession).where(CaptureSession.status == "active")
        ) or 0
        merged: dict[tuple[str, str | None], dict[str, object]] = {}
        observation_rows = self.session.execute(
            select(
                func.coalesce(Observation.source_type, "upload"),
                Observation.source_device_name,
                func.count(Observation.id),
                func.max(func.coalesce(Observation.captured_at, Observation.created_at)),
            ).group_by(func.coalesce(Observation.source_type, "upload"), Observation.source_device_name)
        ).all()
        for source_type, device_name, count, latest in observation_rows:
            merged[(source_type, device_name)] = {
                "observation_count": int(count),
                "session_count": 0,
                "latest_activity": _utc(latest),
            }
        session_rows = self.session.execute(
            select(
                CaptureSession.source_type,
                CaptureSession.device_name,
                func.count(CaptureSession.id),
                func.max(CaptureSession.started_at),
            ).group_by(CaptureSession.source_type, CaptureSession.device_name)
        ).all()
        for source_type, device_name, count, latest in session_rows:
            entry = merged.setdefault(
                (source_type, device_name),
                {"observation_count": 0, "session_count": 0, "latest_activity": None},
            )
            entry["session_count"] = int(count)
            previous = entry["latest_activity"]
            latest_utc = _utc(latest)
            if latest_utc and (previous is None or latest_utc > previous):  # type: ignore[operator]
                entry["latest_activity"] = latest_utc
        sources = [
            DeviceSourceStat(
                source_type=source_type,
                device_name=device_name,
                observation_count=int(values["observation_count"]),
                session_count=int(values["session_count"]),
                latest_activity=values["latest_activity"],  # type: ignore[arg-type]
            )
            for (source_type, device_name), values in sorted(merged.items(), key=lambda item: item[0][0])
        ]
        return DeviceStatsResponse(
            memory_count=memory_count,
            session_count=session_count,
            active_session_count=active_count,
            sources=sources,
        )

    def insights(self) -> InsightsResponse:
        now = datetime.now(timezone.utc)
        total_observations = self._count(Observation)
        observations_7 = self._observations_since(now - timedelta(days=7))
        observations_30 = self._observations_since(now - timedelta(days=30))
        total_sessions = self._count(CaptureSession)
        active_sessions = self.session.scalar(
            select(func.count()).select_from(CaptureSession).where(CaptureSession.status == "active")
        ) or 0
        totals = self.session.execute(
            select(
                func.coalesce(func.sum(CaptureSession.sampled_frames), 0),
                func.coalesce(func.sum(CaptureSession.analyzed_frames), 0),
                func.coalesce(func.sum(CaptureSession.saved_observations), 0),
            )
        ).one()
        sampled, analyzed, saved = map(int, totals)
        averages = self.session.execute(
            select(
                func.coalesce(func.avg(Observation.object_count), 0),
                func.coalesce(func.avg(Observation.relation_count), 0),
            )
        ).one()
        recent = list(
            self.session.scalars(
                select(CaptureSession)
                .options(selectinload(CaptureSession.observations))
                .order_by(CaptureSession.started_at.desc())
                .limit(5)
            )
        )
        return InsightsResponse(
            total_observations=total_observations,
            observations_7_days=observations_7,
            observations_30_days=observations_30,
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            sampled_frames=sampled,
            analyzed_frames=analyzed,
            saved_frames=saved,
            average_objects=round(float(averages[0]), 2),
            average_relations=round(float(averages[1]), 2),
            session_save_efficiency=round(saved / analyzed, 4) if analyzed else 0,
            top_objects=self._ranked(
                select(ObservedObject.display_name, func.count(ObservedObject.row_id))
                .group_by(ObservedObject.display_name)
                .order_by(func.count(ObservedObject.row_id).desc())
            ),
            top_locations=self._ranked(
                select(Observation.location, func.count(Observation.id))
                .where(Observation.location.is_not(None), Observation.location != "")
                .group_by(Observation.location)
                .order_by(func.count(Observation.id).desc())
            ),
            top_sources=self._ranked(
                select(func.coalesce(Observation.source_type, "upload"), func.count(Observation.id))
                .group_by(func.coalesce(Observation.source_type, "upload"))
                .order_by(func.count(Observation.id).desc())
            ),
            top_devices=self._ranked(
                select(Observation.source_device_name, func.count(Observation.id))
                .where(Observation.source_device_name.is_not(None), Observation.source_device_name != "")
                .group_by(Observation.source_device_name)
                .order_by(func.count(Observation.id).desc())
            ),
            daily_activity=self._daily_activity(now.date() - timedelta(days=29)),
            recent_sessions=[session_summary(item) for item in recent],
        )

    def export(self) -> DataExportResponse:
        observations = list(
            self.session.scalars(
                select(Observation)
                .options(selectinload(Observation.objects), selectinload(Observation.relations))
                .order_by(Observation.created_at.desc())
            )
        )
        sessions = list(
            self.session.scalars(
                select(CaptureSession)
                .options(selectinload(CaptureSession.observations))
                .order_by(CaptureSession.started_at.desc())
            )
        )
        return DataExportResponse(
            exported_at=datetime.now(timezone.utc),
            observations=[observation_detail(item) for item in observations],
            capture_sessions=[session_summary(item) for item in sessions],
            note="JSON metadata export; stored image bytes are not embedded.",
        )

    def _count(self, model: type[Observation] | type[CaptureSession]) -> int:
        return self.session.scalar(select(func.count()).select_from(model)) or 0

    def _observations_since(self, threshold: datetime) -> int:
        return self.session.scalar(
            select(func.count()).select_from(Observation).where(Observation.created_at >= threshold)
        ) or 0

    def _ranked(self, statement: object) -> list[RankedCount]:
        rows = self.session.execute(statement.limit(8)).all()  # type: ignore[union-attr]
        return [RankedCount(label=str(label), count=int(count)) for label, count in rows]

    def _daily_activity(self, start: date) -> list[DailyActivity]:
        rows = self.session.execute(
            select(func.date(Observation.created_at), func.count(Observation.id))
            .where(Observation.created_at >= datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc))
            .group_by(func.date(Observation.created_at))
            .order_by(func.date(Observation.created_at))
        ).all()
        counts = {str(day): int(count) for day, count in rows}
        return [
            DailyActivity(date=(start + timedelta(days=index)).isoformat(), count=counts.get((start + timedelta(days=index)).isoformat(), 0))
            for index in range(30)
        ]
