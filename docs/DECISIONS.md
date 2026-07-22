# Architecture Decision Log

## ADR-001 — Vue 3 mobile web frontend

Status: accepted

Reason: the existing stack is already functional, mobile-friendly, and sufficient for the competition. Rewriting in React would add schedule risk without improving the core AI capability.

## ADR-002 — FastAPI inference orchestration

Status: accepted

Reason: Python integrates directly with computer-vision and multimodal libraries, while FastAPI provides typed request/response contracts and interactive API documentation.

## ADR-003 — Normalized bounding boxes

Status: accepted

Decision: all API bounding boxes use `[x1, y1, x2, y2]` normalized to `[0, 1]`.

Reason: normalized coordinates decouple model pixels from responsive frontend display size.

## ADR-004 — Analyzer abstraction

Status: accepted

Decision: model implementations conform to the `SceneAnalyzer` protocol.

Reason: Mock, YOLO, open-vocabulary detection, and future remote inference can be swapped without rewriting the API or frontend.

## ADR-005 — Truthful failure behavior

Status: accepted

Decision: when real inference is enabled and unavailable, return an observable error rather than pretending Mock output is real.

Reason: silent fallback undermines evaluation credibility and makes bugs difficult to diagnose.

## ADR-006 — Deterministic 2D spatial heuristics

Status: accepted

Decision: Day 4 spatial relations are derived from normalized two-dimensional bounding-box geometry with deterministic thresholds and scores. The reasoner is shared by Mock and real analyzers and remains separate from object detection.

Reason: geometric rules are fast, reproducible, explainable, and require no additional heavyweight model. Their evidence can be inspected directly through center distance, IoU, or containment ratio.

Limit: image-plane geometry does not establish physical support, depth ordering, or metric distance. Relations such as `on`, `under`, `in_front_of`, and `behind` are excluded. Semantic or three-dimensional relations may be added later through a VLM or depth estimation while preserving the current evidence-backed contract.

## ADR-007 — SQLite metadata with filesystem image storage

Status: accepted

Decision: the competition MVP stores observation, object, and relation metadata in SQLite through SQLAlchemy 2.x, while image bytes remain in a UUID-named filesystem directory. Observation rows contain only relative image paths.

Reason: this is transactional enough for a single-machine demonstration, easy to inspect and back up, and avoids placing large binary payloads in the relational database. Repository, service, and storage boundaries allow PostgreSQL and object storage to replace local infrastructure later without changing API contracts.

## ADR-008 — Label-based memory retrieval

Status: accepted

Decision: last-seen and history queries match detector labels and display names with partial, case-insensitive English matching and selected Chinese aliases. Results return observation evidence and never claim cross-image object identity.

Reason: reliable identity tracking requires additional visual embeddings or tracking evidence. The MVP can truthfully answer where a class label was most recently detected using ordinary indexed relational queries; vector and graph databases are unnecessary at this stage.

## ADR-009 — Deterministic grounded memory agent

Status: accepted

Decision: natural-language memory questions are mapped to a closed set of intents by deterministic rules. Read-only tools wrap existing repositories and services, and the formatter may only describe returned structured results. Responses include tool traces, evidence cards and relevant limitation text.

Reason: the competition questions are narrow and testable. An open-domain model would add latency, network dependency and hallucination risk without improving grounded retrieval. The package boundary allows a future planner to change while preserving the same tools and evidence contract.

## ADR-010 — Explicit generated demo observations

Status: accepted

Decision: `DEMO_MODE` defaults off. When enabled, code-generated permitted scenes use fixed IDs, an `[演示]` title prefix and the `demo-seed` engine marker. Seeding skips every existing ID, and reset selects only the engine marker.

Reason: a reliable fallback should be reproducible and visibly distinct from real inference. Fixed IDs provide idempotence; engine-scoped reset prevents deletion of user data. No generated observation is represented as a real YOLO result.
