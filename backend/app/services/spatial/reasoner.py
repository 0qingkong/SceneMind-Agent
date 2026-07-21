from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from app.core.config import Settings
from app.schemas.analyze import (
    DetectedObject,
    DetectedRelation,
    RelationEvidence,
    RelationPredicate,
)
from app.services.spatial.geometry import (
    box_area,
    box_center,
    containment_ratio,
    iou,
    normalized_center_distance,
    validate_bbox,
)


def _rounded(value: float) -> float:
    rounded = round(min(1.0, max(0.0, value)), 6)
    return 0.0 if rounded == 0 else rounded


@dataclass(frozen=True, slots=True)
class _RelationCandidate:
    subject_id: str
    predicate: RelationPredicate
    object_id: str
    score: float
    evidence: RelationEvidence


class SpatialReasoner:
    """Infer explainable image-plane relations from normalized bounding boxes."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        near_threshold: float = 0.25,
        overlap_iou_threshold: float = 0.05,
        containment_threshold: float = 0.90,
        axis_separation_threshold: float = 0.08,
        max_relations: int = 80,
    ) -> None:
        self.enabled = enabled
        self.near_threshold = near_threshold
        self.overlap_iou_threshold = overlap_iou_threshold
        self.containment_threshold = containment_threshold
        self.axis_separation_threshold = axis_separation_threshold
        self.max_relations = max_relations

    @classmethod
    def from_settings(cls, settings: Settings) -> SpatialReasoner:
        return cls(
            enabled=settings.spatial_enabled,
            near_threshold=settings.spatial_near_threshold,
            overlap_iou_threshold=settings.spatial_overlap_iou_threshold,
            containment_threshold=settings.spatial_containment_threshold,
            axis_separation_threshold=settings.spatial_axis_separation_threshold,
            max_relations=settings.spatial_max_relations,
        )

    def reason(self, objects: Sequence[DetectedObject]) -> list[DetectedRelation]:
        if not self.enabled or len(objects) < 2:
            return []

        valid_objects: list[DetectedObject] = []
        for item in objects:
            try:
                validate_bbox(item.bbox)
            except ValueError:
                continue
            valid_objects.append(item)

        candidates: list[_RelationCandidate] = []
        seen: set[tuple[str, str, str]] = set()
        for first_index, first in enumerate(valid_objects):
            for second in valid_objects[first_index + 1 :]:
                if first.id != second.id:
                    self._reason_pair(first, second, candidates, seen)

        candidates.sort(
            key=lambda relation: (
                -relation.score,
                relation.predicate,
                relation.subject_id,
                relation.object_id,
            )
        )
        return [
            DetectedRelation(
                id=f"relation-{index}",
                subject_id=candidate.subject_id,
                predicate=candidate.predicate,
                object_id=candidate.object_id,
                score=candidate.score,
                evidence=candidate.evidence,
            )
            for index, candidate in enumerate(
                candidates[: self.max_relations], start=1
            )
        ]

    def _reason_pair(
        self,
        first: DetectedObject,
        second: DetectedObject,
        candidates: list[_RelationCandidate],
        seen: set[tuple[str, str, str]],
    ) -> None:
        first_area = box_area(first.bbox)
        second_area = box_area(second.bbox)
        first_in_second = containment_ratio(first.bbox, second.bbox)
        second_in_first = containment_ratio(second.bbox, first.bbox)
        confidence = min(first.confidence, second.confidence)
        contains_pair = False

        if first_area < second_area and first_in_second >= self.containment_threshold:
            contains_pair = True
            self._add_inverse_containment(
                first, second, first_in_second, confidence, candidates, seen
            )
        elif second_area < first_area and second_in_first >= self.containment_threshold:
            contains_pair = True
            self._add_inverse_containment(
                second, first, second_in_first, confidence, candidates, seen
            )

        pair_iou = iou(first.bbox, second.bbox)
        if not contains_pair and pair_iou >= self.overlap_iou_threshold:
            subject, object_ = sorted((first, second), key=lambda item: item.id)
            self._add(
                subject,
                "overlaps",
                object_,
                confidence * pair_iou,
                RelationEvidence(method="geometry", iou=_rounded(pair_iou)),
                candidates,
                seen,
            )

        center_distance = normalized_center_distance(first.bbox, second.bbox)
        rounded_distance = round(center_distance, 6)
        if center_distance <= self.near_threshold:
            subject, object_ = sorted((first, second), key=lambda item: item.id)
            near_strength = 1 - (center_distance / self.near_threshold)
            self._add(
                subject,
                "near",
                object_,
                confidence * near_strength,
                RelationEvidence(
                    method="geometry", center_distance=rounded_distance
                ),
                candidates,
                seen,
            )

        if contains_pair:
            return

        first_center_x, first_center_y = box_center(first.bbox)
        second_center_x, second_center_y = box_center(second.bbox)
        horizontal_separation = abs(first_center_x - second_center_x)
        vertical_separation = abs(first_center_y - second_center_y)
        axis_evidence = RelationEvidence(
            method="geometry", center_distance=rounded_distance
        )

        if horizontal_separation >= self.axis_separation_threshold:
            left, right = (
                (first, second)
                if first_center_x < second_center_x
                else (second, first)
            )
            axis_score = confidence * horizontal_separation
            self._add(
                left, "left_of", right, axis_score, axis_evidence, candidates, seen
            )
            self._add(
                right, "right_of", left, axis_score, axis_evidence, candidates, seen
            )

        if vertical_separation >= self.axis_separation_threshold:
            above, below = (
                (first, second)
                if first_center_y < second_center_y
                else (second, first)
            )
            axis_score = confidence * vertical_separation
            self._add(
                above, "above", below, axis_score, axis_evidence, candidates, seen
            )
            self._add(
                below, "below", above, axis_score, axis_evidence, candidates, seen
            )

    def _add_inverse_containment(
        self,
        inner: DetectedObject,
        outer: DetectedObject,
        ratio: float,
        confidence: float,
        candidates: list[_RelationCandidate],
        seen: set[tuple[str, str, str]],
    ) -> None:
        evidence = RelationEvidence(
            method="geometry", containment_ratio=_rounded(ratio)
        )
        score = confidence * ratio
        self._add(inner, "inside", outer, score, evidence, candidates, seen)
        self._add(outer, "contains", inner, score, evidence, candidates, seen)

    @staticmethod
    def _add(
        subject: DetectedObject,
        predicate: RelationPredicate,
        object_: DetectedObject,
        score: float,
        evidence: RelationEvidence,
        candidates: list[_RelationCandidate],
        seen: set[tuple[str, str, str]],
    ) -> None:
        key = (subject.id, predicate, object_.id)
        if subject.id == object_.id or key in seen or not math.isfinite(score):
            return
        seen.add(key)
        candidates.append(
            _RelationCandidate(
                subject_id=subject.id,
                predicate=predicate,
                object_id=object_.id,
                score=_rounded(score),
                evidence=evidence,
            )
        )
