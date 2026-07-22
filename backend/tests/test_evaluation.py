from scripts.run_evaluation import evaluate, render_markdown


def test_evaluation_keeps_unmeasured_results_explicit() -> None:
    report = evaluate(
        {
            "agent_intent_cases": [
                {"query": "我的杯子最后出现在哪里？", "expected": "last_seen"}
            ],
            "detection_cases": [{"id": "real", "success": None, "latency_ms": None}],
            "spatial_relation_checks": [{"id": "spatial", "correct": None}],
            "persistence_checks": [{"id": "persistence", "passed": None}],
            "memory_checks": [{"id": "memory", "passed": None}],
            "grounding_checks": [
                {"id": "grounding", "passed": None, "hallucinations": None}
            ],
        }
    )
    metrics = report["metrics"]
    assert metrics["agent_intent_accuracy"]["value"] == 1
    assert metrics["detection_success_and_latency"]["status"] == "not_run"
    assert metrics["hallucination_count"]["count"] is None
    markdown = render_markdown(report)
    assert "not measured" in markdown
    assert "100.0%" in markdown
