from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.schemas.analyze import DetectedObject
from app.services.analyzers.yolo import (
    YoloSceneAnalyzer,
    build_scene_summary,
    normalize_bbox,
    result_to_objects,
)
from app.services.label_map import get_display_name


def make_object(display_name: str) -> DetectedObject:
    return DetectedObject(
        id="object-test",
        label="test",
        display_name=display_name,
        confidence=0.9,
        bbox=[0.1, 0.1, 0.2, 0.2],
    )


def test_normalizes_pixel_bbox() -> None:
    assert normalize_bbox(
        [64, 48, 320, 240], image_width=640, image_height=480
    ) == [0.1, 0.1, 0.5, 0.5]


def test_clamps_normalized_coordinates() -> None:
    assert normalize_bbox(
        [-10, -20, 700, 500], image_width=640, image_height=480
    ) == [0.0, 0.0, 1.0, 1.0]


@pytest.mark.parametrize(
    "bbox",
    ([10, 10, 10, 20], [10, 10, 20, 10], [700, 10, 800, 20]),
)
def test_rejects_zero_area_bbox(bbox: list[float]) -> None:
    assert normalize_bbox(bbox, image_width=640, image_height=480) is None


def test_chinese_label_mapping_and_english_fallback() -> None:
    assert get_display_name("chair") == "椅子"
    assert get_display_name("cell phone") == "手机"
    assert get_display_name("tv") == "电视"
    assert get_display_name("umbrella") == "umbrella"


def test_builds_truthful_scene_summary() -> None:
    objects = [make_object("椅子"), make_object("椅子"), make_object("杯子")]
    assert build_scene_summary(objects) == "检测到 3 个物体：椅子 2 个、杯子 1 个。"
    assert build_scene_summary([]) == "未检测到符合置信度阈值的物体。"


def test_converts_sorts_and_filters_model_results() -> None:
    result = SimpleNamespace(
        names={0: "chair", 1: "umbrella"},
        boxes=SimpleNamespace(
            xyxy=[[10, 10, 50, 50], [20, 20, 80, 80], [5, 5, 5, 10]],
            conf=[0.60, 0.95, 0.99],
            cls=[0, 1, 0],
        ),
    )
    objects = result_to_objects(result, image_width=100, image_height=100)
    assert [item.confidence for item in objects] == [0.95, 0.6]
    assert [item.display_name for item in objects] == ["umbrella", "椅子"]
    assert objects[0].bbox == [0.2, 0.2, 0.8, 0.8]


def test_lazy_model_is_reused(monkeypatch: pytest.MonkeyPatch) -> None:
    analyzer = YoloSceneAnalyzer(Settings())
    fake_model = object()
    initialization_count = 0

    def initialize() -> tuple[object, str, str]:
        nonlocal initialization_count
        initialization_count += 1
        return fake_model, "cpu", "cpu"

    monkeypatch.setattr(analyzer, "_initialize_model", initialize)
    assert analyzer._get_model() is fake_model
    assert analyzer._get_model() is fake_model
    assert initialization_count == 1
    assert analyzer.is_loaded is True
    assert analyzer.device == "cpu"
