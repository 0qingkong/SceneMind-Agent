# SceneMind Agent — Agent Engineering Guide

This file defines the rules for any coding agent working in this repository.

## Product goal

SceneMind Agent is a mobile-oriented multimodal spatial-memory product.

Competition MVP flow:

1. Upload a scene image.
2. Detect multiple objects with evidence-backed bounding boxes.
3. Derive simple spatial relations.
4. Save scene, object, relation, and timestamp observations.
5. Answer where an object was last seen with image evidence.

The August 8 competition build must prioritize a reliable demonstration over broad scope.

## Current architecture

- Frontend: Vue 3 + TypeScript + Vite + Vue Router
- Backend: FastAPI + Pydantic
- Current analyzer abstraction:
  - `SceneAnalyzer`
  - `MockSceneAnalyzer`
- API prefix: `/api/v1`
- Analysis endpoint: `POST /api/v1/analyze`
- Bounding boxes use normalized coordinates:
  - `[x1, y1, x2, y2]`
  - every value must be clamped to `[0, 1]`

## Engineering rules

1. Inspect the repository before editing.
2. Preserve existing API contracts unless the task explicitly requires a versioned change.
3. Do not rewrite working modules without a concrete reason.
4. Keep `main` runnable.
5. Work on a `feature/*` branch.
6. Never commit:
   - `.env`
   - API keys
   - model weights
   - `.venv`
   - `node_modules`
   - generated `runs/`
   - user-uploaded images
7. Add or update tests for changed backend behavior.
8. Run all relevant checks before declaring completion.
9. Do not hide failures by silently returning Mock results.
10. Prefer explicit configuration and observable error messages.
11. Keep changes focused on one milestone.
12. Update `docs/PROJECT_STATE.md` after each completed milestone.

## Required checks

Backend:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
```

Frontend:

```powershell
cd frontend
npm run build
```

## Required handoff format

At the end of every task, report:

1. Summary
2. Files changed
3. Architecture decisions
4. Commands run
5. Test/build results
6. Known limitations
7. Suggested next task
8. Git branch
9. Commit SHA, when committed

Do not say only “done”.
