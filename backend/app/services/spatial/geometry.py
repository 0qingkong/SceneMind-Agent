from __future__ import annotations

import math
from collections.abc import Sequence

BBox = tuple[float, float, float, float]


def validate_bbox(bbox: Sequence[float]) -> BBox:
    if len(bbox) != 4:
        raise ValueError("A bounding box must contain exactly four coordinates")
    try:
        x1, y1, x2, y2 = (float(value) for value in bbox)
    except (TypeError, ValueError) as exc:
        raise ValueError("Bounding-box coordinates must be numbers") from exc
    if not all(math.isfinite(value) for value in (x1, y1, x2, y2)):
        raise ValueError("Bounding-box coordinates must be finite")
    if not all(0 <= value <= 1 for value in (x1, y1, x2, y2)):
        raise ValueError("Bounding-box coordinates must be normalized to [0, 1]")
    if x2 <= x1 or y2 <= y1:
        raise ValueError("Bounding boxes must have positive width and height")
    return x1, y1, x2, y2


def box_width(bbox: Sequence[float]) -> float:
    x1, _, x2, _ = validate_bbox(bbox)
    return x2 - x1


def box_height(bbox: Sequence[float]) -> float:
    _, y1, _, y2 = validate_bbox(bbox)
    return y2 - y1


def box_area(bbox: Sequence[float]) -> float:
    x1, y1, x2, y2 = validate_bbox(bbox)
    return (x2 - x1) * (y2 - y1)


def box_center(bbox: Sequence[float]) -> tuple[float, float]:
    x1, y1, x2, y2 = validate_bbox(bbox)
    return (x1 + x2) / 2, (y1 + y2) / 2


def intersection(first: Sequence[float], second: Sequence[float]) -> BBox | None:
    first_x1, first_y1, first_x2, first_y2 = validate_bbox(first)
    second_x1, second_y1, second_x2, second_y2 = validate_bbox(second)
    x1 = max(first_x1, second_x1)
    y1 = max(first_y1, second_y1)
    x2 = min(first_x2, second_x2)
    y2 = min(first_y2, second_y2)
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def intersection_area(first: Sequence[float], second: Sequence[float]) -> float:
    overlap = intersection(first, second)
    if overlap is None:
        return 0.0
    x1, y1, x2, y2 = overlap
    return (x2 - x1) * (y2 - y1)


def iou(first: Sequence[float], second: Sequence[float]) -> float:
    overlap_area = intersection_area(first, second)
    union_area = box_area(first) + box_area(second) - overlap_area
    return overlap_area / union_area if union_area > 0 else 0.0


def containment_ratio(
    candidate_inner: Sequence[float], candidate_outer: Sequence[float]
) -> float:
    return intersection_area(candidate_inner, candidate_outer) / box_area(candidate_inner)


def normalized_center_distance(
    first: Sequence[float], second: Sequence[float]
) -> float:
    first_x, first_y = box_center(first)
    second_x, second_y = box_center(second)
    return math.hypot(first_x - second_x, first_y - second_y)


def horizontal_overlap_ratio(
    first: Sequence[float], second: Sequence[float]
) -> float:
    first_x1, _, first_x2, _ = validate_bbox(first)
    second_x1, _, second_x2, _ = validate_bbox(second)
    overlap = max(0.0, min(first_x2, second_x2) - max(first_x1, second_x1))
    return overlap / min(first_x2 - first_x1, second_x2 - second_x1)


def vertical_overlap_ratio(
    first: Sequence[float], second: Sequence[float]
) -> float:
    _, first_y1, _, first_y2 = validate_bbox(first)
    _, second_y1, _, second_y2 = validate_bbox(second)
    overlap = max(0.0, min(first_y2, second_y2) - max(first_y1, second_y1))
    return overlap / min(first_y2 - first_y1, second_y2 - second_y1)
