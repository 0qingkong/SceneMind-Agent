from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from evaluation.scripts.common import no_absolute_paths, write_json


def build(input_dir: Path) -> tuple[dict[str, object], str]:
    modules = {}
    for name in ("detection", "relation", "memory", "agent", "session"):
        path = input_dir / f"{name}-results.json"
        if path.exists():
            modules[name] = json.loads(path.read_text(encoding="utf-8"))
    failure_path = input_dir / "failures.csv"
    failures = []
    if failure_path.exists():
        with failure_path.open(encoding="utf-8-sig", newline="") as handle:
            failures = list(csv.DictReader(handle))
    summary = {
        "status": "complete" if modules else "not_run",
        "modules": {name: value.get("status") for name, value in modules.items()},
        "detection": {key: modules.get("detection", {}).get(key) for key in ("analyzer_mode", "sample_count", "processing_success_rate", "non_empty_rate", "average_detections")},
        "relation": {key: modules.get("relation", {}).get(key) for key in ("reviewed_predictions", "macro_precision", "overall_precision", "ambiguity_rate")},
        "memory": {key: modules.get("memory", {}).get(key) for key in ("case_count", "exact_match_accuracy", "history_ordering_accuracy", "restart_persistence_rate")},
        "agent": {key: modules.get("agent", {}).get(key) for key in ("case_count", "intent_accuracy", "parameter_extraction_accuracy", "tool_selection_accuracy", "evidence_grounding_accuracy", "no_result_handling_accuracy", "unsupported_query_handling_accuracy", "hallucination_count")},
        "session": {key: modules.get("session", {}).get(key) for key in ("frame_count", "decision_accuracy", "sampled_to_saved_ratio")},
        "failures": {"count": len(failures), "by_category": dict(sorted(Counter(item.get("category", "uncategorized") for item in failures).items()))},
    }
    lines = [
        "# SceneMind Evaluation Report", "", "This report is generated from result JSON; unmeasured values remain `not_run`/null.", "",
        "## Scope", "", "Mock results validate the harness and deterministic product logic. They are not YOLO model-accuracy claims. No bbox ground truth exists, so mAP, detection recall, and detection F1 are not reported.", "",
    ]
    for name, values in summary.items():
        if name in {"status", "modules"}:
            continue
        lines.extend((f"## {name.title()}", "", "```json", json.dumps(values, ensure_ascii=False, indent=2), "```", ""))
    if failures:
        lines.extend(("## Reviewed failure cases", "", "| Sample | Category | Impact |", "| --- | --- | --- |"))
        for item in failures:
            lines.append(f"| {item.get('sample_id', '')} | {item.get('category', '')} | {item.get('impact', '')} |")
        lines.append("")
    lines.extend(("## Real YOLO", "", "Status: `not_run` unless a licensed local-image manifest was supplied to a separate YOLO run.", "", "## Limitations", "", "- The committed scene set is synthetic and small.", "- Relation annotations cover predicted examples and support precision only, not recall.", "- Real camera, phone, and glasses hardware are not evaluated.", ""))
    markdown = "\n".join(lines)
    if not no_absolute_paths(summary) or not no_absolute_paths(markdown):
        raise ValueError("generated report contains an absolute local path")
    return summary, markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    args = parser.parse_args()
    summary, markdown = build(args.input_dir)
    write_json(args.input_dir / "summary.json", summary)
    (args.input_dir / "EVALUATION_REPORT.md").write_text(markdown, encoding="utf-8")
    print("report: complete")


if __name__ == "__main__":
    main()
