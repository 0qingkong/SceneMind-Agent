from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


def _read_float(source: Mapping[str, str], name: str, default: float) -> float:
    raw_value = source.get(name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got {raw_value!r}") from exc


def _read_int(source: Mapping[str, str], name: str, default: int) -> int:
    raw_value = source.get(name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw_value!r}") from exc


def _read_bool(source: Mapping[str, str], name: str, default: bool) -> bool:
    raw_value = source.get(name)
    if raw_value is None or not raw_value.strip():
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(
        f"{name} must be one of true/false, 1/0, yes/no, or on/off, "
        f"got {raw_value!r}"
    )


@dataclass(frozen=True, slots=True)
class Settings:
    allowed_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")
    analyzer_mode: str = "yolo"
    yolo_model: str = "yolo26n.pt"
    yolo_conf: float = 0.30
    yolo_imgsz: int = 640
    yolo_max_det: int = 30
    yolo_device: str = "auto"
    spatial_enabled: bool = True
    spatial_near_threshold: float = 0.25
    spatial_overlap_iou_threshold: float = 0.05
    spatial_containment_threshold: float = 0.90
    spatial_axis_separation_threshold: float = 0.08
    spatial_max_relations: int = 80
    database_url: str = "sqlite:///./data/scenemind.db"
    scene_storage_dir: str = "./data/images"
    observation_default_limit: int = 20
    observation_max_limit: int = 100
    memory_history_default_limit: int = 20
    memory_history_max_limit: int = 100
    memory_relation_context_limit: int = 8
    agent_default_limit: int = 3
    agent_max_limit: int = 20
    demo_mode: bool = False
    capture_default_interval_seconds: int = 5
    capture_min_interval_seconds: int = 3
    capture_max_interval_seconds: int = 60
    capture_min_save_gap_seconds: int = 15
    capture_object_count_delta: int = 2
    capture_max_session_minutes: int = 60

    def __post_init__(self) -> None:
        if not 0 <= self.yolo_conf <= 1:
            raise ValueError("YOLO_CONF must be between 0 and 1")
        if self.yolo_imgsz <= 0:
            raise ValueError("YOLO_IMGSZ must be greater than 0")
        if self.yolo_max_det <= 0:
            raise ValueError("YOLO_MAX_DET must be greater than 0")
        if not self.yolo_model.strip():
            raise ValueError("YOLO_MODEL must not be empty")
        if not self.allowed_origins:
            raise ValueError("ALLOWED_ORIGINS must contain at least one origin")
        if not self.yolo_device.strip():
            raise ValueError("YOLO_DEVICE must not be empty")
        if not 0 < self.spatial_near_threshold <= 1:
            raise ValueError("SPATIAL_NEAR_THRESHOLD must be greater than 0 and at most 1")
        if not 0 <= self.spatial_overlap_iou_threshold <= 1:
            raise ValueError(
                "SPATIAL_OVERLAP_IOU_THRESHOLD must be between 0 and 1"
            )
        if not 0 < self.spatial_containment_threshold <= 1:
            raise ValueError(
                "SPATIAL_CONTAINMENT_THRESHOLD must be greater than 0 and at most 1"
            )
        if not 0 < self.spatial_axis_separation_threshold <= 1:
            raise ValueError(
                "SPATIAL_AXIS_SEPARATION_THRESHOLD must be greater than 0 and at most 1"
            )
        if self.spatial_max_relations <= 0:
            raise ValueError("SPATIAL_MAX_RELATIONS must be greater than 0")
        if not self.database_url.strip():
            raise ValueError("DATABASE_URL must not be empty")
        if not self.scene_storage_dir.strip():
            raise ValueError("SCENE_STORAGE_DIR must not be empty")
        limits = {
            "OBSERVATION_DEFAULT_LIMIT": self.observation_default_limit,
            "OBSERVATION_MAX_LIMIT": self.observation_max_limit,
            "MEMORY_HISTORY_DEFAULT_LIMIT": self.memory_history_default_limit,
            "MEMORY_HISTORY_MAX_LIMIT": self.memory_history_max_limit,
            "MEMORY_RELATION_CONTEXT_LIMIT": self.memory_relation_context_limit,
            "AGENT_DEFAULT_LIMIT": self.agent_default_limit,
            "AGENT_MAX_LIMIT": self.agent_max_limit,
            "CAPTURE_DEFAULT_INTERVAL_SECONDS": self.capture_default_interval_seconds,
            "CAPTURE_MIN_INTERVAL_SECONDS": self.capture_min_interval_seconds,
            "CAPTURE_MAX_INTERVAL_SECONDS": self.capture_max_interval_seconds,
            "CAPTURE_MIN_SAVE_GAP_SECONDS": self.capture_min_save_gap_seconds,
            "CAPTURE_OBJECT_COUNT_DELTA": self.capture_object_count_delta,
            "CAPTURE_MAX_SESSION_MINUTES": self.capture_max_session_minutes,
        }
        if any(value <= 0 for value in limits.values()):
            invalid = next(name for name, value in limits.items() if value <= 0)
            raise ValueError(f"{invalid} must be greater than 0")
        if self.observation_default_limit > self.observation_max_limit:
            raise ValueError(
                "OBSERVATION_DEFAULT_LIMIT must not exceed OBSERVATION_MAX_LIMIT"
            )
        if self.memory_history_default_limit > self.memory_history_max_limit:
            raise ValueError(
                "MEMORY_HISTORY_DEFAULT_LIMIT must not exceed MEMORY_HISTORY_MAX_LIMIT"
            )
        if self.agent_default_limit > self.agent_max_limit:
            raise ValueError("AGENT_DEFAULT_LIMIT must not exceed AGENT_MAX_LIMIT")
        if self.capture_min_interval_seconds > self.capture_max_interval_seconds:
            raise ValueError("CAPTURE_MIN_INTERVAL_SECONDS must not exceed CAPTURE_MAX_INTERVAL_SECONDS")
        if not self.capture_min_interval_seconds <= self.capture_default_interval_seconds <= self.capture_max_interval_seconds:
            raise ValueError("CAPTURE_DEFAULT_INTERVAL_SECONDS must be within the configured range")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if environ is None else environ
        return cls(
            allowed_origins=tuple(
                item.strip()
                for item in source.get(
                    "ALLOWED_ORIGINS",
                    "http://localhost:5173,http://127.0.0.1:5173",
                ).split(",")
                if item.strip()
            ),
            analyzer_mode=source.get("ANALYZER_MODE", "yolo").strip().lower() or "yolo",
            yolo_model=source.get("YOLO_MODEL", "yolo26n.pt").strip()
            or "yolo26n.pt",
            yolo_conf=_read_float(source, "YOLO_CONF", 0.30),
            yolo_imgsz=_read_int(source, "YOLO_IMGSZ", 640),
            yolo_max_det=_read_int(source, "YOLO_MAX_DET", 30),
            yolo_device=source.get("YOLO_DEVICE", "auto").strip().lower() or "auto",
            spatial_enabled=_read_bool(source, "SPATIAL_ENABLED", True),
            spatial_near_threshold=_read_float(
                source, "SPATIAL_NEAR_THRESHOLD", 0.25
            ),
            spatial_overlap_iou_threshold=_read_float(
                source, "SPATIAL_OVERLAP_IOU_THRESHOLD", 0.05
            ),
            spatial_containment_threshold=_read_float(
                source, "SPATIAL_CONTAINMENT_THRESHOLD", 0.90
            ),
            spatial_axis_separation_threshold=_read_float(
                source, "SPATIAL_AXIS_SEPARATION_THRESHOLD", 0.08
            ),
            spatial_max_relations=_read_int(
                source, "SPATIAL_MAX_RELATIONS", 80
            ),
            database_url=source.get(
                "DATABASE_URL", "sqlite:///./data/scenemind.db"
            ).strip(),
            scene_storage_dir=source.get(
                "SCENE_STORAGE_DIR", "./data/images"
            ).strip(),
            observation_default_limit=_read_int(
                source, "OBSERVATION_DEFAULT_LIMIT", 20
            ),
            observation_max_limit=_read_int(
                source, "OBSERVATION_MAX_LIMIT", 100
            ),
            memory_history_default_limit=_read_int(
                source, "MEMORY_HISTORY_DEFAULT_LIMIT", 20
            ),
            memory_history_max_limit=_read_int(
                source, "MEMORY_HISTORY_MAX_LIMIT", 100
            ),
            memory_relation_context_limit=_read_int(
                source, "MEMORY_RELATION_CONTEXT_LIMIT", 8
            ),
            agent_default_limit=_read_int(source, "AGENT_DEFAULT_LIMIT", 3),
            agent_max_limit=_read_int(source, "AGENT_MAX_LIMIT", 20),
            demo_mode=_read_bool(source, "DEMO_MODE", False),
            capture_default_interval_seconds=_read_int(source, "CAPTURE_DEFAULT_INTERVAL_SECONDS", 5),
            capture_min_interval_seconds=_read_int(source, "CAPTURE_MIN_INTERVAL_SECONDS", 3),
            capture_max_interval_seconds=_read_int(source, "CAPTURE_MAX_INTERVAL_SECONDS", 60),
            capture_min_save_gap_seconds=_read_int(source, "CAPTURE_MIN_SAVE_GAP_SECONDS", 15),
            capture_object_count_delta=_read_int(source, "CAPTURE_OBJECT_COUNT_DELTA", 2),
            capture_max_session_minutes=_read_int(source, "CAPTURE_MAX_SESSION_MINUTES", 60),
        )
