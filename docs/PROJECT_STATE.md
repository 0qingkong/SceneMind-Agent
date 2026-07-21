# SceneMind Agent — Project State

Last updated: 2026-07-21

## Deadline

Competition submission deadline: 2026-08-08.

## Completed

### Day 1 — Runnable skeleton

- Vue 3 + TypeScript + Vite frontend
- FastAPI backend
- Image upload and preview
- Frontend/backend communication
- Mock analysis response
- Initial tests and GitHub repository

### Day 2 — Product shell and bbox visualization

- Vue Router
- Home, analysis, and memory routes
- Unified analysis response schema
- Normalized bounding-box overlay
- Analyzer service abstraction
- Image validation and real image dimensions
- Backend tests
- Frontend production build check

## Current milestone

### Day 3 — Real object detector

Replace `MockSceneAnalyzer` with a real Ultralytics YOLO detector while preserving the frontend API contract.

## Next milestones

- Day 4: spatial-relation engine
- Day 5: scene persistence
- Day 6: object history and last-seen query
- Day 7: agent tool orchestration
- Day 8+: evaluation, UX polish, deployment, submission materials

## Product constraints

Do not add before the competition MVP is stable:

- AI-glasses hardware integration
- continuous video ingestion
- complex authentication
- social features
- custom large-model training
- distributed infrastructure
