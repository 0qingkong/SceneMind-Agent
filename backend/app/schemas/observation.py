from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.analyze import DetectedObject, DetectedRelation


class ObservedObjectRead(DetectedObject):
    sort_order: int = Field(ge=0)


class ObservationSummary(BaseModel):
    id: str
    title: str | None
    location: str | None
    created_at: datetime
    image_url: str
    detail_url: str
    engine: str
    summary: str
    object_count: int = Field(ge=0)
    relation_count: int = Field(ge=0)
    labels: list[str] = Field(default_factory=list)
    is_demo: bool = False
    source_type: str | None = None
    source_device_id: str | None = None
    source_device_name: str | None = None
    captured_at: datetime | None = None
    session_id: str | None = None


class ObservationDetail(ObservationSummary):
    original_filename: str
    mime_type: str
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    objects: list[ObservedObjectRead]
    relations: list[DetectedRelation]


class ObservationListResponse(BaseModel):
    items: list[ObservationSummary]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)
