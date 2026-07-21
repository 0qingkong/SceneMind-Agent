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

    def __post_init__(self) -> None:
        if not 0 <= self.yolo_conf <= 1:
            raise ValueError("YOLO_CONF must be between 0 and 1")
        if self.yolo_imgsz <= 0:
            raise ValueError("YOLO_IMGSZ must be greater than 0")
        if self.yolo_max_det <= 0:
            raise ValueError("YOLO_MAX_DET must be greater than 0")
        if not self.yolo_model.strip():
            raise ValueError("YOLO_MODEL must not be empty")
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

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if environ is None else environ
        return cls(
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
        )
