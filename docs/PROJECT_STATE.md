# SceneMind Agent — Project State

Last updated: 2026-08-03

## Deadline

Competition submission deadline: 2026-08-08.

## Completed

### Day 15 - Formal reproducible evaluation

- One-command, JSON-capable detection/relation/memory/Agent/session harness
- Licensed/synthetic asset manifest policy and validation
- Actual manual relation judgments and deterministic query/sequence cases
- P50/P95 summaries, environment/config/hash capture and generated reports
- Nine visible failure/limitation cases; Mock and YOLO results separated
- Actual Mock report: memory 10/10, Agent 17/18, session 6/6; real YOLO not run

### Day 14 - End-to-end resilience validation

- Isolated FastAPI lifespan and complete multi-endpoint API lifecycle
- Six deterministic Playwright Profile C flows without camera access
- Controlled input, analyzer, storage, session, port, PID, and process failures
- JSON-capable data-integrity validator and PowerShell entry points
- Corrupt-image HTTP 400 handling and reliable managed-process cleanup
- Actual report with Profile A/B/phone explicitly marked `not run`

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

### Day 7 + Day 8 — Grounded Agent and competition package

- Deterministic memory-agent intents, read-only tools and evidence cards
- Explicit Demo Mode, evaluation tooling and competition documentation

### Day 9–12 — Multi-device capture and continuous spatial observation

- Typed browser capture sources and Live Lens
- Persistent low-frequency capture sessions
- Device statistics, AI Glasses Simulator, insights and privacy preferences

## Current milestone

### Day 15 — Formal quantitative evaluation

- Reproducible runtime reports and manual annotations are complete for the permitted synthetic set.
- Real YOLO evaluation is explicitly `not_run` because no licensed local real-image set was available in this environment.

## Next milestones

- Collect and annotate a lawful 40–60 image real-scene set.
- Rehearse Profile A/B and phone camera with target hardware and trusted HTTPS.
- Fix the documented physical-distance Agent misroute with a focused regression before changing the reported baseline.

## Product constraints

Do not add before the competition MVP is stable:

- AI-glasses hardware integration
- continuous video ingestion
- complex authentication
- social features
- custom large-model training
- distributed infrastructure
