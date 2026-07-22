from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.memory import RelationContext

AgentIntent = Literal[
    "last_seen",
    "history",
    "recent_observations",
    "observation_detail",
    "object_count",
    "help",
    "unknown",
]


class AgentQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)


class AgentPlan(BaseModel):
    intent: AgentIntent
    object_query: str | None = None
    observation_ref: str | None = None
    location: str | None = None
    limit: int = Field(default=3, ge=1, le=100)


class ToolStep(BaseModel):
    tool: str
    arguments: dict[str, str | int | None] = Field(default_factory=dict)
    status: Literal["success", "no_match", "skipped"]
    result_count: int = Field(default=0, ge=0)


class EvidenceCard(BaseModel):
    observation_id: str
    title: str | None
    location: str | None
    timestamp: datetime
    image_url: str
    detail_url: str
    matched_objects: list[str] = Field(default_factory=list)
    relation_context: list[RelationContext] = Field(default_factory=list)
    is_demo: bool = False


class AgentQueryResponse(BaseModel):
    query: str
    intent: AgentIntent
    answer: str
    tool_steps: list[ToolStep] = Field(default_factory=list)
    evidence: list[EvidenceCard] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ObjectCountResult(BaseModel):
    query: str | None
    location: str | None
    count: int = Field(ge=0)
    matches: list[EvidenceCard] = Field(default_factory=list)
