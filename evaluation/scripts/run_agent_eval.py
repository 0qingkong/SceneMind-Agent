from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from time import perf_counter

from evaluation.scripts.common import ROOT, file_hash, latency_summary, read_jsonl, write_json
from app.agent.executor import AgentExecutor
from app.agent.planner import AgentPlanner
from app.agent.tools import AgentTools
from app.core.config import Settings
from app.db import Database
from app.services.demo_data import DemoDataService
from app.services.image_storage import ImageStorage
from app.services.memory_service import MemoryService


TOOL_NAMES = {
    "memory_last_seen": "memory.last_seen",
    "memory_history": "memory.history",
    "list_recent_observations": "observations.list",
    "count_objects": "memory.count_objects",
    "none": None,
}


def hallucination_count(actual_ids: list[str], expected_ids: list[str]) -> int:
    """Count evidence IDs returned without support in the annotated case."""
    return len(set(actual_ids) - set(expected_ids))


def run(cases_path: Path, output: Path) -> dict[str, object]:
    cases = read_jsonl(cases_path)
    with tempfile.TemporaryDirectory(prefix="scenemind-agent-eval-") as temporary:
        root = Path(temporary)
        database = Database(f"sqlite:///{root / 'agent.db'}")
        database.create_tables()
        storage = ImageStorage(root / "images")
        settings = Settings()
        results, latencies = [], []
        with database.session_factory() as session:
            DemoDataService(session, storage).seed()
            executor = AgentExecutor(AgentPlanner(), AgentTools(MemoryService(session, settings), settings))
            for case in cases:
                started = perf_counter()
                response = executor.execute(case["query"])
                latency = (perf_counter() - started) * 1000
                latencies.append(latency)
                actual_tool = TOOL_NAMES.get(response.tool_steps[0].tool) if response.tool_steps else None
                actual_parameters = response.tool_steps[0].arguments if response.tool_steps else {}
                actual_ids = [item.observation_id for item in response.evidence]
                expected_ids = case["expected_evidence_ids"]
                intent_ok = response.intent == case["expected_intent"]
                tool_ok = actual_tool == case.get("expected_tool")
                parameters_ok = actual_parameters == case.get("expected_parameters", {})
                evidence_ok = actual_ids == expected_ids
                hallucinations = hallucination_count(actual_ids, expected_ids)
                results.append({
                    "case_id": case["case_id"], "intent_ok": intent_ok, "tool_ok": tool_ok,
                    "parameters_ok": parameters_ok, "evidence_ok": evidence_ok,
                    "expected_intent": case["expected_intent"],
                    "actual_intent": response.intent, "expected_tool": case.get("expected_tool"),
                    "actual_tool": actual_tool, "expected_parameters": case.get("expected_parameters", {}),
                    "actual_parameters": actual_parameters, "expected_answer_type": case["expected_answer_type"],
                    "expected_evidence_ids": expected_ids,
                    "actual_evidence_ids": actual_ids, "hallucinations": hallucinations,
                    "latency_ms": round(latency, 3),
                })
        database.engine.dispose()
    count = len(results)
    payload = {
        "module": "agent", "status": "complete" if count else "not_run", "case_count": count,
        "intent_accuracy": sum(item["intent_ok"] for item in results) / count if count else None,
        "parameter_extraction_accuracy": sum(item["parameters_ok"] for item in results) / count if count else None,
        "tool_selection_accuracy": sum(item["tool_ok"] for item in results) / count if count else None,
        "evidence_grounding_accuracy": sum(item["evidence_ok"] for item in results) / count if count else None,
        "no_result_handling_accuracy": _subset_accuracy(results, "no_result"),
        "unsupported_query_handling_accuracy": _subset_accuracy(results, "limitation"),
        "hallucination_count": sum(item["hallucinations"] for item in results),
        "latency": latency_summary(latencies), "query_set_sha256": file_hash(cases_path), "results": results,
    }
    write_json(output, payload)
    return payload


def _subset_accuracy(results: list[dict[str, object]], answer_type: str) -> float | None:
    subset = [item for item in results if item["expected_answer_type"] == answer_type]
    if not subset:
        return None
    return sum(
        bool(item["intent_ok"]) and bool(item["tool_ok"]) and bool(item["evidence_ok"])
        for item in subset
    ) / len(subset)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation/manifests/agent_queries.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(args.cases, args.output)
    print(f"agent: intent={payload['intent_accuracy']:.1%}, evidence={payload['evidence_grounding_accuracy']:.1%}")


if __name__ == "__main__":
    main()
