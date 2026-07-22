from typing import Literal

from pydantic import BaseModel, Field, FiniteFloat

RelationPredicate = Literal[
    "left_of",
    "right_of",
    "above",
    "below",
    "near",
    "overlaps",
    "inside",
    "contains",
]


class DetectedObject(BaseModel):
    id: str
    label: str
    display_name: str
    confidence: FiniteFloat = Field(ge=0, le=1)
    bbox: list[FiniteFloat] = Field(
        min_length=4,
        max_length=4,
        description="[x1, y1, x2, y2]，使用 0~1 归一化坐标。",
    )


class RelationEvidence(BaseModel):
    method: Literal["geometry"] = "geometry"
    center_distance: FiniteFloat | None = Field(default=None, ge=0)
    iou: FiniteFloat | None = Field(default=None, ge=0, le=1)
    containment_ratio: FiniteFloat | None = Field(default=None, ge=0, le=1)


class DetectedRelation(BaseModel):
    id: str
    subject_id: str
    predicate: RelationPredicate
    object_id: str
    score: FiniteFloat = Field(ge=0, le=1)
    evidence: RelationEvidence


class AnalyzeResponse(BaseModel):
    trace_id: str
    engine: str
    filename: str
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    scene_summary: str
    objects: list[DetectedObject]
    relations: list[DetectedRelation] = Field(default_factory=list)
    latency_ms: FiniteFloat = Field(ge=0)
