import math

import pytest

from app.services.spatial.geometry import (
    box_area,
    box_center,
    box_height,
    box_width,
    containment_ratio,
    horizontal_overlap_ratio,
    iou,
    normalized_center_distance,
    validate_bbox,
    vertical_overlap_ratio,
)


def test_area_dimensions_and_center() -> None:
    bbox = [0.1, 0.2, 0.5, 0.8]
    assert box_width(bbox) == pytest.approx(0.4)
    assert box_height(bbox) == pytest.approx(0.6)
    assert box_area(bbox) == pytest.approx(0.24)
    assert box_center(bbox) == pytest.approx((0.3, 0.5))


def test_iou_disjoint_partial_and_identical() -> None:
    first = [0.0, 0.0, 0.4, 0.4]
    assert iou(first, [0.6, 0.6, 0.9, 0.9]) == 0
    assert iou(first, [0.2, 0.2, 0.6, 0.6]) == pytest.approx(1 / 7)
    assert iou(first, first) == 1


def test_containment_distance_and_axis_overlap() -> None:
    inner = [0.2, 0.2, 0.4, 0.4]
    outer = [0.1, 0.1, 0.6, 0.6]
    assert containment_ratio(inner, outer) == 1
    assert containment_ratio(outer, inner) == pytest.approx(0.16)
    assert normalized_center_distance(inner, outer) == pytest.approx(math.sqrt(0.005))
    assert horizontal_overlap_ratio(inner, outer) == 1
    assert vertical_overlap_ratio(inner, outer) == 1


@pytest.mark.parametrize(
    "bbox",
    (
        [0.1, 0.2, 0.3],
        [0.2, 0.2, 0.2, 0.4],
        [0.2, 0.4, 0.3, 0.3],
        [-0.1, 0.1, 0.2, 0.2],
        [0.1, 0.1, 1.1, 0.2],
        [0.1, 0.1, math.inf, 0.2],
        [0.1, math.nan, 0.2, 0.3],
    ),
)
def test_rejects_invalid_or_non_finite_boxes(bbox: list[float]) -> None:
    with pytest.raises(ValueError):
        validate_bbox(bbox)
