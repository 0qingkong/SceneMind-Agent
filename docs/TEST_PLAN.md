# SceneMind Day 14 Test Plan

## Objective

Prove that the competition MVP works end to end, reports controlled failures clearly, recovers only owned processes, and preserves user data. Day 14 adds test infrastructure and narrowly scoped fixes only; it adds no product capability.

## Test layers

1. **Backend unit/service:** existing pytest plus deterministic validation, persistence, session, readiness, and integrity checks.
2. **API integration:** the real FastAPI app with temporary SQLite/storage, fake analyzer, real spatial reasoner, and dependency overrides.
3. **Browser E2E:** Playwright with headless Edge, fixed 1280x900 viewport, Profile C/Mock, synthetic permitted image, and no camera request.
4. **Manual acceptance:** Profile A camera/YOLO, Profile B permitted image/YOLO, and trusted-HTTPS phone checks remain human-operated.

## Isolation

- Every automated run uses a timestamp/PID identifier under ignored `.runtime/test-results/`.
- Databases, storage, fixtures, logs, traces, and screenshots are run-local.
- Tests bind lifespan resources through `app.state`, so startup cannot touch the production singleton database.
- Real `.env`, `backend/data`, user uploads, YOLO weights, and physical cameras are excluded.
- Owned test processes are tracked by exact PID and cleaned in `finally` blocks.

## Coverage matrix

| Area | Deterministic checks |
| --- | --- |
| API lifecycle | health/readiness, analyze/save/list/detail/image, retrieval, Agent, session save/skip/stop, stats, insights, export, delete/404/cleanup |
| Input failures | missing, empty, MIME mismatch, corrupt image/checksum, malformed JSON, pagination, interval |
| Service failures | analyzer exception without Mock fallback, storage failure, rollback coverage |
| Session failures | active delete, repeated stop, sample after stop, duplicate delete |
| Process failures | occupied port, stale PID, exact owned-process stop, no-op cleanup |
| Data integrity | counts, relation endpoints, orphan rows, image references, sessions, ordering, demo markers, path-free export |
| Browser | analysis/detail, memory, Agent trace/evidence, sessions, devices/glasses/insights/system, empty states |
| Privacy/security | no absolute paths, no camera automation, simulator disclaimer, controlled error bodies |

## Performance sanity

Deterministic health, readiness, observation list, last-seen, Agent, and insights calls must each remain below `TEST_API_TIMEOUT_SECONDS` (default 10 seconds). This is a broad regression guard, not a benchmark; real YOLO is excluded.

## Acceptance criteria

- Backend, frontend build/capture tests, lifecycle, six browser flows, failure injection, integrity, and Profile C pass.
- No listener, PID file, user database change, or non-ignored artifact remains.
- No P0/P1 defect remains open.
- Hardware tests are reported as `not run` when unavailable.

## Manual tests and exclusions

Profile A, Profile B, and phone HTTPS/camera acceptance require explicit hardware and image permission. Distributed guarantees, formal load tests, real-time video, real glasses SDKs, and model-accuracy claims are outside Day 14.
