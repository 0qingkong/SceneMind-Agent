from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.analyze import RelationPredicate
from app.schemas.observation import ObservationSummary


class RelationContext(BaseModel):
    relation_id: str
    subject_id: str
    subject_name: str
    predicate: RelationPredicate
    object_id: str
    object_name: str
    score: float = Field(ge=0, le=1)


class MemoryMatch(BaseModel):
    observation: ObservationSummary
    matched_object_ids: list[str]
    matched_names: list[str]
    relations: list[RelationContext]


class LastSeenResponse(BaseModel):
    query: str
    matched_labels: list[str]
    result: MemoryMatch


class HistoryResponse(BaseModel):
    query: str
    items: list[MemoryMatch]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)
