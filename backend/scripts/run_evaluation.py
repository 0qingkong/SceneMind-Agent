from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agent.planner import AgentPlanner


def _manual_metric(cases: list[dict[str, Any]], field: str) -> dict[str, Any]:
    checked = [item for item in cases if item.get(field) is not None]
    if not checked:
        return {"status": "not_run", "checked": 0, "total": len(cases), "value": None}
    passed = sum(bool(item[field]) for item in checked)
    return {
        "status": "complete" if len(checked) == len(cases) else "partial",
        "checked": len(checked),
        "total": len(cases),
        "passed": passed,
        "value": passed / len(checked),
    }


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    planner = AgentPlanner()
    intent_cases = data.get("agent_intent_cases", [])
    intent_results = []
    for item in intent_cases:
        actual = planner.plan(item["query"]).intent
        intent_results.append({**item, "actual": actual, "passed": actual == item["expected"]})
    intent_passed = sum(item["passed"] for item in intent_results)

    detection_cases = data.get("detection_cases", [])
    measured_latency = [
        float(item["latency_ms"])
        for item in detection_cases
        if item.get("latency_ms") is not None
    ]
    detection = _manual_metric(detection_cases, "success")
    detection["average_latency_ms"] = (
        sum(measured_latency) / len(measured_latency) if measured_latency else None
    )

    grounding_cases = data.get("grounding_checks", [])
    measured_hallucinations = [
        int(item["hallucinations"])
        for item in grounding_cases
        if item.get("hallucinations") is not None
    ]
    hallucination_metric = {
        "status": "complete" if measured_hallucinations and len(measured_hallucinations) == len(grounding_cases) else ("partial" if measured_hallucinations else "not_run"),
        "checked": len(measured_hallucinations),
        "total": len(grounding_cases),
        "count": sum(measured_hallucinations) if measured_hallucinations else None,
        "expected": 0,
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "detection_success_and_latency": detection,
            "spatial_relation_precision": _manual_metric(data.get("spatial_relation_checks", []), "correct"),
            "save_restart_delete_consistency": _manual_metric(data.get("persistence_checks", []), "passed"),
            "last_seen_history_correctness": _manual_metric(data.get("memory_checks", []), "passed"),
            "agent_intent_accuracy": {
                "status": "complete" if intent_cases else "not_run",
                "checked": len(intent_cases),
                "passed": intent_passed,
                "value": intent_passed / len(intent_cases) if intent_cases else None,
            },
            "evidence_grounding_success": _manual_metric(grounding_cases, "passed"),
            "hallucination_count": hallucination_metric,
        },
        "agent_intent_results": intent_results,
        "source_cases": data,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SceneMind Evaluation Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "Unmeasured metrics remain `not_run`; they are not treated as passing results.",
        "",
        "| Metric | Status | Result |",
        "| --- | --- | --- |",
    ]
    for name, metric in report["metrics"].items():
        value = metric.get("value")
        if value is not None:
            result = f"{value * 100:.1f}%"
        elif metric.get("count") is not None:
            result = str(metric["count"])
        else:
            result = "not measured"
        lines.append(f"| {name} | {metric['status']} | {result} |")
    lines.extend(("", "## Agent intent cases", ""))
    for item in report["agent_intent_results"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['query']}` → `{item['actual']}` (expected `{item['expected']}`)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate evidence-based SceneMind evaluation reports.")
    parser.add_argument("--cases", type=Path, default=Path("evaluation/cases.json"))
    parser.add_argument("--json-output", type=Path, default=Path("../docs/reports/evaluation-latest.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("../docs/reports/evaluation-latest.md"))
    args = parser.parse_args()

    data = json.loads(args.cases.read_text(encoding="utf-8"))
    report = evaluate(data)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {args.json_output} and {args.markdown_output}")


if __name__ == "__main__":
    main()
