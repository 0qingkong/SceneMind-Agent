from pydantic import BaseModel, Field


class DetectedObject(BaseModel):
    id: str
    label: str
    display_name: str
    confidence: float = Field(ge=0, le=1)
    bbox: list[float] = Field(
        min_length=4,
        max_length=4,
        description="[x1, y1, x2, y2]，使用 0~1 归一化坐标。",
    )


class AnalyzeResponse(BaseModel):
    trace_id: str
    engine: str
    filename: str
    scene_summary: str
    objects: list[DetectedObject]
    latency_ms: float
