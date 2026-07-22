# SceneMind Architecture

## System overview

SceneMind is a local-first competition MVP with a Vue 3 frontend and a FastAPI backend. SQLite stores structured observation metadata; original images use UUID filenames under a configured storage root. The API never returns filesystem paths.

```text
Vue /analyze ──multipart──> AnalysisService ──> SceneAnalyzer (YOLO or explicit Mock)
                                  │
                                  └──> SpatialReasoner (deterministic 2D geometry)
                                            │
Vue /memory <──JSON/image── ObservationService ──> SQLite + image storage
                                            │
Vue /agent  <──evidence──── AgentExecutor ──> MemoryService / repository
                         planner -> tools -> formatter
```

## Backend boundaries

- `services/analyzers`: lazy YOLO and explicit Mock implementations behind `SceneAnalyzer`.
- `AnalysisService`: upload size, MIME, decode and dimension validation; runs detection and spatial reasoning once.
- `services/spatial`: normalized-box geometry only. It does not infer depth or physical distance.
- `ObservationService`: transaction-aware save, read and delete behavior.
- `MemoryService`: newest-first category retrieval with stable repeated-object numbering.
- `agent`: deterministic intent plan, read-only structured tools, grounded formatter and response schemas. It is not open-domain chat.
- `DemoDataService`: optional generated sample observations marked by `engine=demo-seed`; fixed IDs make seeding idempotent.

## Data model

An `Observation` owns `ObservedObject` and `ObservedRelation` rows with delete cascades. Object and relation IDs are scoped to one observation. Bounding boxes stay normalized as `[x1, y1, x2, y2]`. Image paths stored in SQLite are relative to `SCENE_STORAGE_DIR`.

The API derives `is_demo` from the trusted engine marker rather than requiring a schema migration. Demo reset selects only that marker and leaves all real-engine rows untouched.

## Agent grounding

```text
query
  -> AgentPlanner: one supported intent + bounded arguments
  -> AgentTools: existing memory/repository calls, structured data only
  -> AgentExecutor: tool trace + evidence cards
  -> formatter: answer constrained to returned evidence
```

Supported intents are `last_seen`, `history`, `recent_observations`, `observation_detail`, `object_count`, `help`, and `unknown`. Category retrieval cannot prove cross-image identity. Returned 2D relations cannot prove real depth or distance; relevant responses carry these limitations explicitly.

## Reliability properties

- Invalid size, MIME or undecodable images fail before inference.
- Real analyzer failures return `503`; Mock output is never a silent fallback.
- DB sessions are context-managed and closed after requests.
- Failed observation writes remove newly saved images.
- Delete stages the image, commits the DB delete, then finalizes file cleanup.
- Storage path resolution rejects traversal and API schemas omit absolute paths.
- Tests use fake inference and temporary databases/storage; real YOLO has a separate manual smoke procedure.
