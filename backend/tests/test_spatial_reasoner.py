import math

import pytest

from app.core.config import Settings
from app.schemas.analyze import DetectedObject
from app.services.spatial import SpatialReasoner


def make_object(
    object_id: str,
    bbox: list[float],
    confidence: float = 0.9,
) -> DetectedObject:
    return DetectedObject(
        id=object_id,
        label=object_id,
        display_name=object_id,
        confidence=confidence,
        bbox=bbox,
    )


def relation_tuples(reasoner: SpatialReasoner, objects: list[DetectedObject]):
    return {
        (item.subject_id, item.predicate, item.object_id)
        for item in reasoner.reason(objects)
    }


def test_empty_and_single_object_have_no_relations() -> None:
    reasoner = SpatialReasoner()
    assert reasoner.reason([]) == []
    assert reasoner.reason([make_object("a", [0.1, 0.1, 0.2, 0.2])]) == []


def test_clear_left_right_inverse_pair_without_self_relations() -> None:
    objects = [
        make_object("left", [0.05, 0.4, 0.15, 0.6]),
        make_object("right", [0.75, 0.4, 0.85, 0.6]),
    ]
    tuples = relation_tuples(SpatialReasoner(), objects)
    assert ("left", "left_of", "right") in tuples
    assert ("right", "right_of", "left") in tuples
    assert all(subject != object_ for subject, _, object_ in tuples)


def test_clear_above_below_inverse_pair() -> None:
    objects = [
        make_object("top", [0.4, 0.05, 0.6, 0.15]),
        make_object("bottom", [0.4, 0.75, 0.6, 0.85]),
    ]
    tuples = relation_tuples(SpatialReasoner(), objects)
    assert ("top", "above", "bottom") in tuples
    assert ("bottom", "below", "top") in tuples


def test_near_threshold_is_inclusive_and_outside_is_excluded() -> None:
    first = make_object("a", [0.05, 0.45, 0.15, 0.55])
    boundary = make_object("b", [0.30, 0.45, 0.40, 0.55])
    outside = make_object("c", [0.301, 0.45, 0.401, 0.55])
    reasoner = SpatialReasoner(near_threshold=0.25)
    boundary_relations = reasoner.reason([first, boundary])
    outside_relations = reasoner.reason([first, outside])
    near = next(item for item in boundary_relations if item.predicate == "near")
    assert near.score == 0
    assert not any(item.predicate == "near" for item in outside_relations)


def test_overlap_relation_is_symmetric_once_and_uses_stable_id_order() -> None:
    objects = [
        make_object("z", [0.1, 0.1, 0.4, 0.4]),
        make_object("a", [0.3, 0.3, 0.6, 0.6]),
    ]
    overlaps = [
        item for item in SpatialReasoner().reason(objects) if item.predicate == "overlaps"
    ]
    assert len(overlaps) == 1
    assert (overlaps[0].subject_id, overlaps[0].object_id) == ("a", "z")
    assert overlaps[0].evidence.iou == pytest.approx(0.058824, abs=1e-6)


def test_containment_inverse_pair_suppresses_overlap() -> None:
    objects = [
        make_object("outer", [0.1, 0.1, 0.6, 0.6]),
        make_object("inner", [0.2, 0.2, 0.3, 0.3]),
    ]
    relations = SpatialReasoner().reason(objects)
    tuples = {(item.subject_id, item.predicate, item.object_id) for item in relations}
    assert ("inner", "inside", "outer") in tuples
    assert ("outer", "contains", "inner") in tuples
    assert not any(item.predicate == "overlaps" for item in relations)


def test_nearly_aligned_centers_do_not_create_axis_relations() -> None:
    objects = [
        make_object("a", [0.30, 0.30, 0.40, 0.40]),
        make_object("b", [0.34, 0.31, 0.44, 0.41]),
    ]
    relations = SpatialReasoner().reason(objects)
    axis_predicates = {"left_of", "right_of", "above", "below"}
    assert not any(item.predicate in axis_predicates for item in relations)


def test_output_is_unique_deterministic_sorted_capped_and_references_valid() -> None:
    objects = [
        make_object("c", [0.75, 0.75, 0.9, 0.9], 0.7),
        make_object("a", [0.05, 0.05, 0.2, 0.2], 0.9),
        make_object("b", [0.35, 0.35, 0.5, 0.5], 0.8),
    ]
    before = [item.model_dump() for item in objects]
    full = SpatialReasoner(max_relations=80).reason(objects)
    repeated = SpatialReasoner(max_relations=80).reason(objects)
    capped = SpatialReasoner(max_relations=2).reason(objects)
    tuples = [(item.subject_id, item.predicate, item.object_id) for item in full]
    valid_ids = {item.id for item in objects}

    assert [item.model_dump() for item in full] == [item.model_dump() for item in repeated]
    assert len(tuples) == len(set(tuples))
    assert [item.model_dump(exclude={"id"}) for item in capped] == [
        item.model_dump(exclude={"id"}) for item in full[:2]
    ]
    assert all(
        item.subject_id in valid_ids and item.object_id in valid_ids for item in full
    )
    assert all(math.isfinite(item.score) and 0 <= item.score <= 1 for item in full)
    assert [item.score for item in full] == sorted(
        (item.score for item in full), reverse=True
    )
    assert [item.model_dump() for item in objects] == before


def test_score_can_reach_one_and_never_exceeds_bounds() -> None:
    identical = [
        make_object("a", [0.1, 0.1, 0.4, 0.4], 1),
        make_object("b", [0.1, 0.1, 0.4, 0.4], 1),
    ]
    scores = [item.score for item in SpatialReasoner().reason(identical)]
    assert 1 in scores
    assert all(0 <= score <= 1 for score in scores)


def test_disabled_reasoning_returns_empty_list() -> None:
    objects = [
        make_object("a", [0.1, 0.1, 0.2, 0.2]),
        make_object("b", [0.7, 0.7, 0.8, 0.8]),
    ]
    assert SpatialReasoner(enabled=False).reason(objects) == []


def test_spatial_settings_parse_and_validate() -> None:
    settings = Settings.from_env(
        {
            "SPATIAL_ENABLED": "off",
            "SPATIAL_NEAR_THRESHOLD": "0.4",
            "SPATIAL_MAX_RELATIONS": "12",
        }
    )
    assert settings.spatial_enabled is False
    assert settings.spatial_near_threshold == 0.4
    assert settings.spatial_max_relations == 12
    with pytest.raises(ValueError, match="SPATIAL_NEAR_THRESHOLD"):
        Settings(spatial_near_threshold=0)
    with pytest.raises(ValueError, match="SPATIAL_ENABLED"):
        Settings.from_env({"SPATIAL_ENABLED": "sometimes"})
