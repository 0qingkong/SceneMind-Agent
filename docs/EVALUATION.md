# Evaluation Guide

SceneMind separates automated checks from manual real-image evaluation so unmeasured results are never reported as successes.

## Measures

| Measure | Evidence |
| --- | --- |
| Detection success and latency | Permitted real-image runs; record success and API `latency_ms` |
| Spatial-relation precision | Manually compare displayed relations with visible bounding-box geometry |
| Save/restart/delete consistency | Save, restart, retrieve, delete, then verify DB and image cleanup |
| Last-seen/history correctness | Known observations with controlled time order |
| Agent intent accuracy | Deterministic labeled cases in `backend/evaluation/cases.json` |
| Evidence-grounding success | Verify every factual answer points to a returned observation |
| Hallucination count | Count factual claims unsupported by returned evidence; target is zero |

## Generate reports

Manual fields default to `null`. Fill them only after performing the check, then run from `backend`:

```powershell
..\.venv\Scripts\python.exe scripts\run_evaluation.py
```

The script writes JSON and Markdown to `docs/reports/evaluation-latest.*`. Any untouched metric remains `not_run`; partial data is marked `partial`. The checked-in placeholder makes no benchmark claims.

## Automated smoke test

`tests/test_e2e_smoke.py` uses fake inference plus temporary SQLite/image storage and covers:

```text
health -> analyze -> save -> list -> last seen -> agent query -> detail -> delete
```

Run it alone with:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests\test_e2e_smoke.py -q
```

## Manual real-YOLO smoke test

1. Set `ANALYZER_MODE=yolo` and `DEMO_MODE=false`.
2. Start the backend and check `/api/v1/health`; mode must be `yolo`.
3. Upload a permitted real image through `/analyze` and confirm the response engine is YOLO, not Mock.
4. Confirm boxes match visible objects and record latency.
5. Save the same scene, restart the backend, and retrieve it from Memory.
6. Query an observed category through Memory and Agent; open the returned evidence.
7. Delete the observation and confirm its detail and image endpoints return `404`.
