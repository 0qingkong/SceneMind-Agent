# SceneMind Agent — Project State

Last updated: 2026-07-22

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

### Day 4 — Spatial-relation engine

- Deterministic 2D geometry helpers and relation reasoner
- Evidence-backed left/right, above/below, near, overlap, and containment relations
- Shared Mock/YOLO reasoning path
- Configurable thresholds, deterministic scores, sorting, and output cap
- Responsive frontend relation presentation

### Day 5 + Day 6 — Persistent scene memory and retrieval

- SQLite observation, object and relation snapshots
- UUID-based filesystem image storage with transactional cleanup
- Memory timeline, detail, delete, last-seen and paginated history
- Stable repeated-object numbering and label-based retrieval limitations

## Current milestone

### Day 7 + Day 8 — Grounded Agent and competition package

Implementation is ready for user verification: deterministic agent intents and tools, evidence-first `/agent`, explicit limitations, demo seeding/reset, evaluation/report tooling, fake-inference end-to-end smoke coverage, product polish, and competition documentation.

## Next milestones

- Run required backend/frontend checks and manual real-YOLO acceptance.
- Record real-image evaluation results without claiming unmeasured metrics.
- Merge the Day 7/8 feature branch and rehearse the competition demo.

## Product constraints

Do not add before the competition MVP is stable:

- AI-glasses hardware integration
- continuous video ingestion
- complex authentication
- social features
- custom large-model training
- distributed infrastructure
