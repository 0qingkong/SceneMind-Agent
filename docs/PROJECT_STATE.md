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

### Day 3 — Real YOLO object detector

- Ultralytics `yolo26n.pt` real object detection
- Lazy, reusable model loading with automatic CPU/CUDA device selection
- Configurable model, confidence, image size, maximum detections, and device
- Normalized and clamped evidence bounding boxes
- Chinese labels for common indoor COCO classes
- Truthful count-based scene summaries and explicit failure behavior
- Analyzer factory with retained Mock mode
- Health reporting for mode, model, load state, and initialized device
- Unit, route, production-build, and real indoor-image inference verification

## Current milestone

### Day 4 — Spatial-relation engine

Derive simple spatial relations from detected-object bounding boxes while preserving evidence traceability.

## Next milestones

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
