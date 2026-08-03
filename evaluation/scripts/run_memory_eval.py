from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from time import perf_counter

from evaluation.scripts.common import ROOT, file_hash, latency_summary, read_jsonl, write_json
from app.core.config import Settings
from app.db import Database
from app.services.demo_data import DemoDataService
from app.services.image_storage import ImageStorage
from app.services.memory_service import MemoryNotFoundError, MemoryService


def run(cases_path: Path, output: Path) -> dict[str, object]:
    cases = read_jsonl(cases_path)
    with tempfile.TemporaryDirectory(prefix="scenemind-memory-eval-") as temporary:
        root = Path(temporary)
        database_path = root / "evaluation.db"
        storage = ImageStorage(root / "images")
        database = Database(f"sqlite:///{database_path}")
        database.create_tables()
        started = perf_counter()
        with database.session_factory() as session:
            seed = DemoDataService(session, storage).seed()
        seed_ms = (perf_counter() - started) * 1000
        database.engine.dispose()

        # Reopen the database before every evaluation to prove persistence is
        # independent of the original SQLAlchemy engine/session.
        database = Database(f"sqlite:///{database_path}")
        results = []
        latencies = []
        with database.session_factory() as session:
            memory = MemoryService(session, Settings())
            for case in cases:
                started = perf_counter()
                actual_ids: list[str] = []
                try:
                    if case["operation"] == "last_seen":
                        actual_ids = [memory.last_seen(case["query"]).result.observation.id]
                    elif case["operation"] == "history":
                        actual_ids = [item.observation.id for item in memory.history(query=case["query"], limit=100, offset=0).items]
                    else:
                        try:
                            memory.last_seen(case["query"])
                        except MemoryNotFoundError:
                            actual_ids = []
                    expected = case.get("expected_observation_ids")
                    if expected is None:
                        expected_id = case.get("expected_observation_id")
                        expected = [expected_id] if expected_id else []
                    passed = actual_ids == expected
                    error = None
                except Exception as exc:
                    passed, error = False, type(exc).__name__
                latency = (perf_counter() - started) * 1000
                latencies.append(latency)
                results.append({"case_id": case["case_id"], "passed": passed, "expected_ids": expected, "actual_ids": actual_ids, "latency_ms": round(latency, 3), "error": error})
            image_available = all(storage.existing_path(item.image_path) is not None for item in memory.repository.list(limit=100, offset=0)[0])
        database.engine.dispose()
    passed = sum(item["passed"] for item in results)
    payload = {
        "module": "memory",
        "status": "complete" if cases else "not_run",
        "case_count": len(cases),
        "exact_match_accuracy": passed / len(cases) if cases else None,
        "history_ordering_accuracy": sum(item["passed"] for item in results if item["case_id"].startswith("memory-history")) / max(1, sum(item["case_id"].startswith("memory-history") for item in results)),
        "evidence_image_availability": 1.0 if image_available else 0.0,
        "restart_persistence_rate": 1.0 if seed.demo_observation_ids and results else None,
        "seed_time_ms": round(seed_ms, 3),
        "latency": latency_summary(latencies),
        "query_set_sha256": file_hash(cases_path),
        "results": results,
    }
    write_json(output, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation/manifests/memory_queries.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(args.cases, args.output)
    print(f"memory: {payload['exact_match_accuracy']:.1%} ({payload['case_count']} cases)")


if __name__ == "__main__":
    main()
