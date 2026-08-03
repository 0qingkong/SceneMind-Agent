from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.scripts.build_report import build
from evaluation.scripts.common import latency_summary, no_absolute_paths, percentile
from evaluation.scripts.run_agent_eval import hallucination_count
from evaluation.scripts.run_relation_eval import run as run_relation
from evaluation.scripts.validate_manifest import validate_relations, validate_scenes


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_manifest_validation_accepts_committed_manifests() -> None:
    assert validate_scenes(ROOT / "evaluation/manifests/scenes.example.jsonl") == []
    assert validate_relations(ROOT / "evaluation/manifests/relation_annotations.example.csv") == []


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        ([{"sample_id": "same", "asset_key": "x", "license": "team-owned"}, {"sample_id": "same", "asset_key": "y", "license": "team-owned"}], "duplicate sample_id"),
        ([{"sample_id": "x", "asset_path": "evaluation/assets/missing.jpg", "license": "team-owned"}], "missing asset"),
        ([{"sample_id": "x", "asset_key": "x", "license": "private-unknown"}], "invalid permission/license"),
    ],
)
def test_manifest_rejects_invalid_inputs(tmp_path: Path, rows: list[dict[str, object]], expected: str) -> None:
    path = tmp_path / "scenes.jsonl"
    _write_jsonl(path, rows)
    assert any(expected in error for error in validate_scenes(path, require_assets=True))


def test_relation_parser_metrics_and_counts(tmp_path: Path) -> None:
    source = tmp_path / "relations.csv"
    fields = ["sample_id", "observation_id", "subject_label", "predicate", "object_label", "predicted", "manual_correct", "ambiguous", "reviewer_note"]
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([
            {"sample_id": "s", "observation_id": "o", "subject_label": "cup", "predicate": "left_of", "object_label": "book", "predicted": "true", "manual_correct": "true", "ambiguous": "false", "reviewer_note": "reviewed"},
            {"sample_id": "s", "observation_id": "o", "subject_label": "cup", "predicate": "near", "object_label": "book", "predicted": "true", "manual_correct": "false", "ambiguous": "true", "reviewer_note": "threshold"},
        ])
    assert validate_relations(source) == []
    result = run_relation(source, tmp_path / "result.json")
    assert result["overall_precision"] == 0.5
    assert result["judgment_counts"] == {"correct": 1, "incorrect": 1, "ambiguous": 1}


def test_relation_validator_rejects_self_relation(tmp_path: Path) -> None:
    source = tmp_path / "relations.csv"
    source.write_text("sample_id,observation_id,subject_label,predicate,object_label,predicted,manual_correct,ambiguous,reviewer_note\ns,o,cup,near,cup,true,true,false,bad\n", encoding="utf-8")
    assert any("self-relations" in error for error in validate_relations(source))


def test_percentiles_and_zero_sample_summary() -> None:
    assert percentile([1, 2, 3, 4], 0.5) == 2.5
    assert percentile([1, 2, 3, 4], 0.95) == pytest.approx(3.85)
    assert latency_summary([])["p95_ms"] is None


def test_hallucination_classification() -> None:
    assert hallucination_count(["known", "invented", "invented"], ["known"]) == 1


def test_report_uses_results_without_paths_or_mode_mixing(tmp_path: Path) -> None:
    (tmp_path / "detection-results.json").write_text(json.dumps({"status": "not_run", "analyzer_mode": "yolo", "sample_count": 0}), encoding="utf-8")
    (tmp_path / "agent-results.json").write_text(json.dumps({"status": "complete", "case_count": 1, "intent_accuracy": 1.0, "hallucination_count": 0}), encoding="utf-8")
    summary, markdown = build(tmp_path)
    assert summary["detection"] == {"analyzer_mode": "yolo", "sample_count": 0, "processing_success_rate": None, "non_empty_rate": None, "average_detections": None}
    assert "Mock results" in markdown and "mAP" in markdown
    assert no_absolute_paths(summary) and no_absolute_paths(markdown)
