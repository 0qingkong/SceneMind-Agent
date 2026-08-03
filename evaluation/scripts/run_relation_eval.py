from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from evaluation.scripts.common import ROOT, file_hash, read_csv, write_json


def run(annotations: Path, output: Path, analyzer_mode: str = "mock") -> dict[str, object]:
    rows = read_csv(annotations)
    if analyzer_mode == "yolo":
        payload = {
            "module": "relation", "status": "not_run", "analyzer_mode": "yolo",
            "reason": "No licensed local YOLO image/result set is configured; Mock/manual judgments are not mixed into YOLO metrics.",
            "reviewed_predictions": 0, "precision_by_predicate": {}, "macro_precision": None,
            "overall_precision": None, "ambiguity_rate": None,
            "annotation_sha256": file_hash(annotations), "rows": [],
        }
        write_json(output, payload)
        return payload
    per_predicate: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        per_predicate[row["predicate"]].append(row["manual_correct"].casefold() == "true")
    precision = {name: sum(values) / len(values) for name, values in sorted(per_predicate.items())}
    payload = {
        "module": "relation",
        "analyzer_mode": analyzer_mode,
        "status": "complete" if rows else "not_run",
        "reviewed_predictions": len(rows),
        "metric_scope": "precision over reviewed predicted relations; recall not measured",
        "precision_by_predicate": precision,
        "macro_precision": sum(precision.values()) / len(precision) if precision else None,
        "overall_precision": sum(value for values in per_predicate.values() for value in values) / len(rows) if rows else None,
        "ambiguity_rate": sum(row["ambiguous"].casefold() == "true" for row in rows) / len(rows) if rows else None,
        "judgment_counts": {
            "correct": sum(row["manual_correct"].casefold() == "true" for row in rows),
            "incorrect": sum(row["manual_correct"].casefold() == "false" for row in rows),
            "ambiguous": sum(row["ambiguous"].casefold() == "true" for row in rows),
        },
        "annotation_sha256": file_hash(annotations),
        "rows": rows,
    }
    write_json(output, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, default=ROOT / "evaluation/manifests/relation_annotations.example.csv")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--analyzer-mode", choices=["mock", "yolo"], default="mock")
    args = parser.parse_args()
    payload = run(args.annotations, args.output, args.analyzer_mode)
    print(f"relation: {payload['status']} ({payload['reviewed_predictions']} reviewed predictions)")


if __name__ == "__main__":
    main()
