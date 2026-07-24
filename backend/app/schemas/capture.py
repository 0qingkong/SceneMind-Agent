from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.analyze import AnalyzeResponse
from app.schemas.observation import ObservationSummary

CaptureStatus = Literal["active", "stopped", "failed"]
AutoSaveMode = Literal["manual", "meaningful-change", "every-analyzed-sample"]


class CaptureSessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    source_type: str = Field(default="browser_camera", min_length=1, max_length=50)
    device_name: str | None = Field(default=None, max_length=255)
    sample_interval_seconds: int | None = None
    target_query: str | None = Field(default=None, max_length=200)
    auto_save_mode: AutoSaveMode = "meaningful-change"


class CaptureSessionSummary(BaseModel):
    id: str
    title: str | None
    location: str | None
    source_type: str
    device_name: str | None
    status: CaptureStatus
    started_at: datetime
    ended_at: datetime | None
    sample_interval_seconds: int
    sampled_frames: int = Field(ge=0)
    analyzed_frames: int = Field(ge=0)
    saved_observations: int = Field(ge=0)
    target_query: str | None
    target_seen: bool
    last_error: str | None
    auto_save_mode: AutoSaveMode
    last_sampled_at: datetime | None
    last_saved_at: datetime | None


class CaptureSessionDetail(CaptureSessionSummary):
    recent_observations: list[ObservationSummary] = Field(default_factory=list)


class CaptureSessionListResponse(BaseModel):
    items: list[CaptureSessionSummary]
    total: int = Field(ge=0)


class CaptureSampleResponse(BaseModel):
    session: CaptureSessionSummary
    saved: bool
    reason: str
    observation_id: str | None
    target_found: bool
    analysis: AnalyzeResponse
