from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Observation, ObservedObject, ObservedRelation
from app.schemas.analyze import AnalyzeResponse, DetectedRelation, RelationEvidence
from app.schemas.observation import (
    ObservationDetail,
    ObservationSummary,
    ObservedObjectRead,
)


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def observation_summary(model: Observation) -> ObservationSummary:
    labels = list(dict.fromkeys(item.display_name for item in model.objects))
    return ObservationSummary(
        id=model.id,
        title=model.title,
        location=model.location,
        created_at=_utc(model.created_at),
        image_url=f"/api/v1/observations/{model.id}/image",
        detail_url=f"/memory/{model.id}",
        engine=model.engine,
        summary=model.summary,
        object_count=model.object_count,
        relation_count=model.relation_count,
        labels=labels,
        is_demo=model.engine == "demo-seed",
        source_type=model.source_type,
        source_device_id=model.source_device_id,
        source_device_name=model.source_device_name,
        captured_at=_utc(model.captured_at) if model.captured_at else None,
        session_id=model.session_id,
    )


def observation_detail(model: Observation) -> ObservationDetail:
    objects = [
        ObservedObjectRead(
            id=item.id,
            sort_order=item.sort_order,
            label=item.label,
            display_name=item.display_name,
            confidence=item.confidence,
            bbox=[item.bbox_x1, item.bbox_y1, item.bbox_x2, item.bbox_y2],
        )
        for item in sorted(model.objects, key=lambda item: item.sort_order)
    ]
    relations = [
        DetectedRelation(
            id=item.id,
            subject_id=item.subject_id,
            predicate=item.predicate,
            object_id=item.object_id,
            score=item.score,
            evidence=RelationEvidence(
                method="geometry",
                center_distance=item.center_distance,
                iou=item.iou,
                containment_ratio=item.containment_ratio,
            ),
        )
        for item in sorted(
            model.relations,
            key=lambda item: (-item.score, item.predicate, item.subject_id, item.object_id),
        )
    ]
    summary = observation_summary(model)
    return ObservationDetail(
        **summary.model_dump(),
        original_filename=model.original_filename,
        mime_type=model.mime_type,
        image_width=model.image_width,
        image_height=model.image_height,
        objects=objects,
        relations=relations,
    )


class ObservationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        observation_id: str,
        title: str | None,
        location: str | None,
        created_at: datetime,
        image_path: str,
        mime_type: str,
        analysis: AnalyzeResponse,
        source_type: str | None = None,
        source_device_id: str | None = None,
        source_device_name: str | None = None,
        captured_at: datetime | None = None,
        session_id: str | None = None,
    ) -> Observation:
        object_ids = {item.id for item in analysis.objects}
        if len(object_ids) != len(analysis.objects):
            raise ValueError("Detected object IDs must be unique inside an observation")
        if any(
            relation.subject_id not in object_ids or relation.object_id not in object_ids
            for relation in analysis.relations
        ):
            raise ValueError("Relations must reference objects in the same observation")

        model = Observation(
            id=observation_id,
            title=title,
            location=location,
            created_at=created_at,
            image_path=image_path,
            original_filename=analysis.filename,
            mime_type=mime_type,
            image_width=analysis.image_width,
            image_height=analysis.image_height,
            engine=analysis.engine,
            summary=analysis.scene_summary,
            object_count=len(analysis.objects),
            relation_count=len(analysis.relations),
            source_type=source_type,
            source_device_id=source_device_id,
            source_device_name=source_device_name,
            captured_at=captured_at,
            session_id=session_id,
            objects=[
                ObservedObject(
                    id=item.id,
                    sort_order=index,
                    label=item.label,
                    display_name=item.display_name,
                    confidence=item.confidence,
                    bbox_x1=item.bbox[0],
                    bbox_y1=item.bbox[1],
                    bbox_x2=item.bbox[2],
                    bbox_y2=item.bbox[3],
                )
                for index, item in enumerate(analysis.objects)
            ],
            relations=[
                ObservedRelation(
                    id=item.id,
                    subject_id=item.subject_id,
                    predicate=item.predicate,
                    object_id=item.object_id,
                    score=item.score,
                    method=item.evidence.method,
                    center_distance=item.evidence.center_distance,
                    iou=item.evidence.iou,
                    containment_ratio=item.evidence.containment_ratio,
                )
                for item in analysis.relations
            ],
        )
        self.session.add(model)
        self.session.flush()
        return model

    def get(self, observation_id: str) -> Observation | None:
        statement = (
            select(Observation)
            .where(Observation.id == observation_id)
            .options(
                selectinload(Observation.objects),
                selectinload(Observation.relations),
            )
        )
        return self.session.scalar(statement)

    def list(
        self,
        *,
        limit: int,
        offset: int,
        label: str | None = None,
        query: str | None = None,
        session_id: str | None = None,
    ) -> tuple[list[Observation], int]:
        statement = select(Observation)
        if label:
            label_value = label.casefold()
            statement = statement.where(
                Observation.objects.any(func.lower(ObservedObject.label) == label_value)
            )
        if query:
            pattern = f"%{query.casefold()}%"
            statement = statement.where(
                or_(
                    func.lower(func.coalesce(Observation.title, "")).like(pattern),
                    func.lower(func.coalesce(Observation.location, "")).like(pattern),
                    func.lower(Observation.summary).like(pattern),
                    Observation.objects.any(
                        or_(
                            func.lower(ObservedObject.label).like(pattern),
                            func.lower(ObservedObject.display_name).like(pattern),
                        )
                    ),
                )
            )
        if session_id:
            statement = statement.where(Observation.session_id == session_id)
        total = self.session.scalar(
            select(func.count()).select_from(statement.order_by(None).subquery())
        ) or 0
        items = list(
            self.session.scalars(
                statement.options(
                    selectinload(Observation.objects),
                    selectinload(Observation.relations),
                )
                .order_by(Observation.created_at.desc(), Observation.id.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        return items, total

    def matching(
        self,
        *,
        terms: Sequence[str],
        limit: int,
        offset: int,
        location: str | None = None,
    ) -> tuple[list[Observation], int]:
        object_conditions = []
        for term in terms:
            pattern = f"%{term.casefold()}%"
            object_conditions.extend(
                (
                    func.lower(ObservedObject.label).like(pattern),
                    func.lower(ObservedObject.display_name).like(pattern),
                )
            )
        statement = select(Observation).where(
            Observation.objects.any(or_(*object_conditions))
        )
        if location:
            statement = statement.where(
                func.lower(func.coalesce(Observation.location, "")).like(
                    f"%{location.casefold()}%"
                )
            )
        total = self.session.scalar(
            select(func.count()).select_from(statement.subquery())
        ) or 0
        items = list(
            self.session.scalars(
                statement.options(
                    selectinload(Observation.objects),
                    selectinload(Observation.relations),
                )
                .order_by(Observation.created_at.desc(), Observation.id.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        return items, total

    def find_reference(self, reference: str) -> Observation | None:
        cleaned = reference.strip()
        if not cleaned:
            return None
        exact = self.get(cleaned)
        if exact is not None:
            return exact
        pattern = f"%{cleaned.casefold()}%"
        statement = (
            select(Observation)
            .where(
                or_(
                    func.lower(func.coalesce(Observation.title, "")).like(pattern),
                    func.lower(func.coalesce(Observation.location, "")).like(pattern),
                )
            )
            .options(
                selectinload(Observation.objects),
                selectinload(Observation.relations),
            )
            .order_by(Observation.created_at.desc(), Observation.id.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def count_objects(
        self,
        *,
        terms: Sequence[str] | None = None,
        location: str | None = None,
    ) -> int:
        statement = select(func.count(ObservedObject.row_id)).join(Observation)
        if terms:
            conditions = []
            for term in terms:
                pattern = f"%{term.casefold()}%"
                conditions.extend(
                    (
                        func.lower(ObservedObject.label).like(pattern),
                        func.lower(ObservedObject.display_name).like(pattern),
                    )
                )
            statement = statement.where(or_(*conditions))
        if location:
            statement = statement.where(
                func.lower(func.coalesce(Observation.location, "")).like(
                    f"%{location.casefold()}%"
                )
            )
        return self.session.scalar(statement) or 0

    def demo_observations(self) -> list[Observation]:
        return list(
            self.session.scalars(
                select(Observation)
                .where(Observation.engine == "demo-seed")
                .options(
                    selectinload(Observation.objects),
                    selectinload(Observation.relations),
                )
                .order_by(Observation.created_at.desc(), Observation.id.desc())
            )
        )

    def delete(self, model: Observation) -> None:
        self.session.delete(model)
