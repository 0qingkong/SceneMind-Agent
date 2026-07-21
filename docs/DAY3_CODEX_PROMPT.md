# Day 3 Codex Prompt — Real YOLO Detection

Copy the entire prompt below into Codex while the local SceneMind Agent repository is open.

---

You are implementing Day 3 of SceneMind Agent.

First read:

- `AGENTS.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISIONS.md`
- the current backend analyzer implementation
- the current API schema
- the frontend bbox rendering implementation

Do not start editing until you have inspected the repository and summarized the current architecture.

## Goal

Replace the fixed Mock object detections with real Ultralytics YOLO object detection while preserving the current frontend contract.

Use the current Ultralytics nano detection model:

```text
yolo26n.pt
```

The implementation must work on Windows and support CPU. Use CUDA automatically when PyTorch reports it is available.

## Branch

Create and work on:

```text
feature/day3-real-yolo
```

If there are uncommitted changes, stop and report them before changing files.

## Functional requirements

1. Add a `YoloSceneAnalyzer` implementation that conforms to the existing `SceneAnalyzer` protocol.
2. Load the YOLO model lazily and reuse the same model instance across requests.
3. Accept image bytes directly; do not require permanent uploaded files.
4. Run object detection with configurable:
   - model name
   - confidence threshold
   - image size
   - maximum detections
   - device
5. Read configuration from environment variables with safe defaults:
   - `ANALYZER_MODE=yolo`
   - `YOLO_MODEL=yolo26n.pt`
   - `YOLO_CONF=0.30`
   - `YOLO_IMGSZ=640`
   - `YOLO_MAX_DET=30`
   - `YOLO_DEVICE=auto`
6. Convert pixel boxes to normalized `[x1, y1, x2, y2]`.
7. Clamp all normalized coordinates to `[0, 1]`.
8. Skip invalid or zero-area boxes.
9. Sort detections by confidence descending.
10. Return the existing `DetectedObject` schema.
11. Add Chinese display names for common indoor COCO classes, including at least:
    - person
    - chair
    - couch
    - bed
    - dining table
    - laptop
    - keyboard
    - mouse
    - cell phone
    - book
    - backpack
    - handbag
    - bottle
    - cup
    - bowl
    - clock
    - tv
12. Unknown classes should use their English class name as `display_name`.
13. Generate a concise truthful scene summary from detected class counts without calling an LLM.
14. If no objects are detected, return an empty object list and an explicit summary.
15. Do not silently fall back to Mock when YOLO mode fails.
16. Keep Mock mode available through `ANALYZER_MODE=mock`.
17. Unsupported analyzer modes must fail clearly at application startup or first use.
18. Update `/api/v1/health` so it reports:
    - configured analyzer mode
    - model name
    - whether the model has been loaded
    - device after model initialization, when known
19. Do not load the model merely to answer the health endpoint.
20. The first inference may download model weights. Do not commit weights.

## Structure

Prefer focused modules such as:

```text
backend/app/core/config.py
backend/app/services/analyzers/factory.py
backend/app/services/analyzers/yolo.py
backend/app/services/label_map.py
```

Keep route handlers thin.

## Dependencies and repository hygiene

1. Add Ultralytics to `backend/requirements.txt`.
2. Install a compatible version in the existing virtual environment.
3. After successful installation, pin the exact installed Ultralytics version.
4. Do not manually pin a different Torch build unless required.
5. Add these patterns to `.gitignore` if absent:

```text
*.pt
backend/models/
runs/
```

6. Update `.env.example` with the new configuration.
7. Update README with:
   - real detector setup
   - first-run weight download note
   - CPU/GPU behavior
   - configuration variables
8. Update `docs/PROJECT_STATE.md` only after the milestone passes checks.

## Tests

Tests must not download model weights.

Add unit tests for:

- analyzer factory selecting mock/yolo
- unsupported analyzer mode
- pixel-to-normalized bbox conversion
- coordinate clamping
- invalid zero-area box rejection
- Chinese label mapping
- scene summary generation
- route behavior using a fake analyzer or dependency override

Keep existing tests passing.

Optionally add a manually invoked smoke-test script that runs a real YOLO inference, but do not include it in normal automated tests.

## Acceptance criteria

All must pass:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
```

```powershell
cd frontend
npm run build
```

Then manually:

1. Start the backend.
2. Open `/api/v1/health`.
3. Upload a real indoor image from the frontend.
4. Confirm detected labels and boxes correspond to actual objects.
5. Confirm the response engine identifies the real model.
6. Confirm no `.pt` weight is staged by Git.

## Scope restrictions

Do not implement yet:

- spatial relations
- database persistence
- object tracking
- VLM calls
- Agent framework
- login
- UI redesign
- Docker
- deployment

## Final handoff

Return exactly:

1. Architecture inspection
2. Summary
3. Files changed
4. Configuration added
5. Commands run
6. Test/build results
7. Manual inference result
8. Known limitations
9. Git status
10. Recommended commit message

Do not claim completion if real inference was not manually verified.
