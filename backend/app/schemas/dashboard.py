from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.capture import CaptureSessionSummary
from app.schemas.observation import ObservationDetail


class RankedCount(BaseModel):
    label: str
    count: int = Field(ge=0)


class DailyActivity(BaseModel):
    date: str
    count: int = Field(ge=0)


class DeviceSourceStat(BaseModel):
    source_type: str
    device_name: str | None
    observation_count: int = Field(ge=0)
    session_count: int = Field(ge=0)
    latest_activity: datetime | None


class DeviceStatsResponse(BaseModel):
    memory_count: int = Field(ge=0)
    session_count: int = Field(ge=0)
    active_session_count: int = Field(ge=0)
    sources: list[DeviceSourceStat]


class InsightsResponse(BaseModel):
    total_observations: int = Field(ge=0)
    observations_7_days: int = Field(ge=0)
    observations_30_days: int = Field(ge=0)
    total_sessions: int = Field(ge=0)
    active_sessions: int = Field(ge=0)
    sampled_frames: int = Field(ge=0)
    analyzed_frames: int = Field(ge=0)
    saved_frames: int = Field(ge=0)
    average_objects: float = Field(ge=0)
    average_relations: float = Field(ge=0)
    session_save_efficiency: float = Field(ge=0, le=1)
    top_objects: list[RankedCount]
    top_locations: list[RankedCount]
    top_sources: list[RankedCount]
    top_devices: list[RankedCount]
    daily_activity: list[DailyActivity]
    recent_sessions: list[CaptureSessionSummary]


class DataExportResponse(BaseModel):
    exported_at: datetime
    observations: list[ObservationDetail]
    capture_sessions: list[CaptureSessionSummary]
    note: str
