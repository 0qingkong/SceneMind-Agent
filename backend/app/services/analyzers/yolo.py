from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from io import BytesIO
from threading import Lock
from typing import Any

from PIL import Image

from app.core.config import Settings
from app.schemas.analyze import DetectedObject
from app.services.analyzers.base import AnalysisResult, AnalyzerError
from app.services.label_map import get_display_name


def normalize_bbox(
    pixel_bbox: Sequence[float],
    *,
    image_width: int,
    image_height: int,
) -> list[float] | None:
    """Normalize and clamp a pixel-space bbox, rejecting invalid areas."""

    if image_width <= 0 or image_height <= 0:
        raise ValueError("Image dimensions must be positive")
    if len(pixel_bbox) != 4:
        raise ValueError("A bounding box must contain exactly four coordinates")

    coordinates = [float(value) for value in pixel_bbox]
    if not all(math.isfinite(value) for value in coordinates):
        return None

    x1, y1, x2, y2 = coordinates
    normalized = [
        min(1.0, max(0.0, x1 / image_width)),
        min(1.0, max(0.0, y1 / image_height)),
        min(1.0, max(0.0, x2 / image_width)),
        min(1.0, max(0.0, y2 / image_height)),
    ]
    if normalized[2] <= normalized[0] or normalized[3] <= normalized[1]:
        return None
    return [round(value, 6) for value in normalized]


def build_scene_summary(objects: Sequence[DetectedObject]) -> str:
    if not objects:
        return "未检测到符合置信度阈值的物体。"

    counts = Counter(item.display_name for item in objects)
    details = "、".join(f"{name} {count} 个" for name, count in counts.items())
    return f"检测到 {len(objects)} 个物体：{details}。"


def _as_list(value: Any) -> list[Any]:
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "tolist"):
        value = value.tolist()
    return list(value)


def _resolve_class_name(names: Any, class_id: int) -> str:
    if isinstance(names, Mapping):
        return str(names.get(class_id, class_id))
    if isinstance(names, Sequence) and not isinstance(names, (str, bytes)):
        if 0 <= class_id < len(names):
            return str(names[class_id])
    return str(class_id)


def result_to_objects(
    result: Any,
    *,
    image_width: int,
    image_height: int,
) -> list[DetectedObject]:
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return []

    pixel_boxes = _as_list(boxes.xyxy)
    confidences = _as_list(boxes.conf)
    class_ids = _as_list(boxes.cls)
    names = getattr(result, "names", {})
    detections: list[tuple[float, str, str, list[float]]] = []

    for pixel_bbox, raw_confidence, raw_class_id in zip(
        pixel_boxes, confidences, class_ids, strict=False
    ):
        confidence = float(raw_confidence)
        if not math.isfinite(confidence):
            continue
        bbox = normalize_bbox(
            pixel_bbox,
            image_width=image_width,
            image_height=image_height,
        )
        if bbox is None:
            continue
        label = _resolve_class_name(names, int(raw_class_id))
        detections.append(
            (
                min(1.0, max(0.0, confidence)),
                label,
                get_display_name(label),
                bbox,
            )
        )

    detections.sort(key=lambda item: item[0], reverse=True)
    return [
        DetectedObject(
            id=f"object-{index}",
            label=label,
            display_name=display_name,
            confidence=round(confidence, 6),
            bbox=bbox,
        )
        for index, (confidence, label, display_name, bbox) in enumerate(
            detections, start=1
        )
    ]


class YoloSceneAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine = f"ultralytics:{settings.yolo_model}"
        self.model_name = settings.yolo_model
        self._model: Any | None = None
        self._predict_device: str | None = None
        self._device: str | None = None
        self._load_lock = Lock()

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def device(self) -> str | None:
        return self._device

    def _initialize_model(self) -> tuple[Any, str, str]:
        try:
            import torch
            from ultralytics import YOLO
        except (ImportError, OSError) as exc:
            raise AnalyzerError(
                f"YOLO dependencies could not be loaded: {exc}"
            ) from exc

        if self.settings.yolo_device == "auto":
            cuda_available = bool(torch.cuda.is_available())
            predict_device = "0" if cuda_available else "cpu"
            reported_device = "cuda:0" if cuda_available else "cpu"
        else:
            predict_device = self.settings.yolo_device
            reported_device = self.settings.yolo_device

        try:
            model = YOLO(self.model_name)
        except Exception as exc:
            raise AnalyzerError(
                f"Unable to load YOLO model {self.model_name!r}: {exc}"
            ) from exc
        return model, predict_device, reported_device

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        with self._load_lock:
            if self._model is None:
                model, predict_device, reported_device = self._initialize_model()
                self._model = model
                self._predict_device = predict_device
                self._device = reported_device
        return self._model

    def analyze(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        image_width: int,
        image_height: int,
    ) -> AnalysisResult:
        model = self._get_model()
        try:
            with Image.open(BytesIO(image_bytes)) as source_image:
                rgb_image = source_image.convert("RGB")
                results = model.predict(
                    source=rgb_image,
                    conf=self.settings.yolo_conf,
                    imgsz=self.settings.yolo_imgsz,
                    max_det=self.settings.yolo_max_det,
                    device=self._predict_device,
                    verbose=False,
                )
        except Exception as exc:
            raise AnalyzerError(f"YOLO inference failed for {filename!r}: {exc}") from exc

        result = results[0] if results else None
        objects = (
            result_to_objects(
                result,
                image_width=image_width,
                image_height=image_height,
            )
            if result is not None
            else []
        )
        return AnalysisResult(
            scene_summary=build_scene_summary(objects),
            objects=objects,
        )
