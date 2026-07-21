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


@dataclass(frozen=True, slots=True)
class Settings:
    analyzer_mode: str = "yolo"
    yolo_model: str = "yolo26n.pt"
    yolo_conf: float = 0.30
    yolo_imgsz: int = 640
    yolo_max_det: int = 30
    yolo_device: str = "auto"

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
        )
