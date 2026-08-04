# API Reference

Base URL: `http://127.0.0.1:8000/api/v1`. Interactive OpenAPI documentation is available at `/docs`. Examples use synthetic identifiers and contain no private data or local filesystem paths.

## Common behavior

- JSON errors use FastAPI's `{"detail":"message"}` shape.
- Uploads accept permitted JPG, PNG and WebP images within configured size/dimension limits.
- Bounding boxes are normalized `[x1, y1, x2, y2]` and relation scores are `[0, 1]`.
- Typical errors: `400/413/415/422` invalid input, `404` missing record, `409` invalid session state, `500` persistence failure, `503` analyzer/readiness failure.
- The API has no authentication in this local competition MVP; do not expose it to an untrusted network.

## Liveness and readiness

### `GET /health`

Returns process liveness and lightweight analyzer configuration without loading YOLO.

```json
{"status":"ok","service":"scenemind-agent-api","version":"0.9.0-rc1","analyzer_mode":"mock","model_loaded":false,"demo_mode":true,"demo_profile":"C"}
```

### `GET /ready`

Checks database access and writable image storage, plus reports analyzer, spatial, demo and active-session state. Returns `200` when ready or `503` when a required storage dependency is unavailable.

```json
{"status":"ready","database_reachable":true,"storage_writable":true,"analyzer_mode":"mock","spatial_reasoner_enabled":true,"active_session_count":0}
```

Readiness intentionally does not initialize or run the model.

## Analyze

### `POST /analyze`

Multipart request with required `file`; does not persist the result.

```powershell
Invoke-RestMethod -Method Post -Form @{ file = Get-Item .\sample.jpg } `
  http://127.0.0.1:8000/api/v1/analyze
```

```json
{
  "trace_id":"analysis-example",
  "engine":"yolo:yolo26n.pt",
  "filename":"sample.jpg",
  "image_width":1280,
  "image_height":720,
  "scene_summary":"检测到 2 个物体。",
  "objects":[{"id":"obj-1","label":"cup","display_name":"杯子","confidence":0.91,"bbox":[0.2,0.3,0.4,0.7]}],
  "relations":[],
  "latency_ms":58.4
}
```

This endpoint does not identify the same physical instance across images. YOLO failure returns `503`; it never silently emits Mock data.

## Observations and images

### `POST /observations`

Persists one multipart image plus optional `title`, `location`, `source_type`, `source_device_id`, `source_device_name`, `captured_at` and `session_id`. Returns `201 ObservationDetail` containing object and relation snapshots.

```powershell
Invoke-RestMethod -Method Post -Form @{
  file = Get-Item .\sample.jpg
  title = "演示桌面"
  location = "展台"
  source_type = "upload"
} http://127.0.0.1:8000/api/v1/observations
```

### `GET /observations`

Query parameters: `limit`, `offset`, `label`, `q`, `session_id`. Returns newest-first `{items,total,limit,offset}`. `limit` above the configured maximum returns `422`.

### `GET /observations/{observation_id}`

Returns one detail including metadata, objects and directed relations. Missing ID returns `404`.

### `GET /observations/{observation_id}/image`

Streams the stored original image with its media type. It never exposes the storage path. Missing or invalid evidence returns `404`.

### `DELETE /observations/{observation_id}`

Returns `204` after deleting the Observation, child rows and image through staged transactional cleanup. This is permanent and should be confirmed in the UI.

## Memory retrieval

### `GET /memory/last-seen?q=cup`

Returns the newest Observation containing a matching detector category/display alias.

```json
{"query":"cup","matched_labels":["cup"],"result":{"matched_object_ids":["obj-1"],"matched_names":["杯子"],"relations":[],"observation":{"id":"observation-example","image_url":"/api/v1/observations/observation-example/image"}}}
```

No match returns `404`.

### `GET /memory/history?q=cup&limit=20&offset=0`

Returns newest-first `{query,items,total,limit,offset}`. No match returns an empty list. Matching is label/category retrieval, not cross-image identity tracking.

## Agent

### `POST /agent/query`

```json
{"query":"我的杯子最后出现在哪里？"}
```

```json
{
  "query":"我的杯子最后出现在哪里？",
  "intent":"last_seen",
  "answer":"最近一次匹配到杯子是在展台。",
  "tool_steps":[{"tool":"memory.last_seen","arguments":{"query":"杯子"},"status":"success","result_count":1}],
  "evidence":[{"observation_id":"observation-example","location":"展台","image_url":"/api/v1/observations/observation-example/image","detail_url":"/api/v1/observations/observation-example","matched_objects":["杯子"],"relation_context":[],"is_demo":false}],
  "limitations":["类别匹配不等于确认同一现实物体。"]
}
```

The deterministic Agent supports last seen, history, recent observations, observation detail, object count, help and unknown intents. Empty/overlong input returns `422`. It is not open-domain chat and does not estimate physical distance.

## Capture sessions

### `POST /capture-sessions`

```json
{"title":"展台观察","location":"展台","source_type":"browser_camera","sample_interval_seconds":5,"target_query":"cup","auto_save_mode":"meaningful-change"}
```

Returns `201 CaptureSessionDetail`. Modes are `manual`, `meaningful-change`, and `every-analyzed-sample`; interval constraints come from environment settings.

### `GET /capture-sessions` and `GET /capture-sessions/{session_id}`

Return session counters, state, timestamps, save mode, last error and recent evidence. Missing ID returns `404`.

### `POST /capture-sessions/{session_id}/samples`

Multipart fields: required `file`; optional `force_save`, `captured_at`, `source_device_id`, `source_device_name`.

```json
{"saved":true,"reason":"first-valid-sample","observation_id":"observation-example","target_found":true,"session":{"status":"active"},"analysis":{"engine":"mock-v0.2"}}
```

A stopped/failed session or overlapping sample returns `409`; image errors follow Analyze behavior.

### `POST /capture-sessions/{session_id}/stop`

Moves an active session to `stopped` and returns its detail. Invalid state returns `409`.

### `DELETE /capture-sessions/{session_id}`

Deletes a stopped session and detaches its observations so memory evidence remains. Returns `204`; deleting an active session is rejected.

## Devices and insights

### `GET /devices/stats`

Returns memory/session counts and persisted source/device aggregates. Browser device enumeration is ephemeral frontend state and is not reported as permanent online status.

### `GET /insights`

Returns real SQL aggregates: observation/session counts, sampled/analyzed/saved frames, averages, save efficiency, ranked objects/locations/sources/devices, daily activity and recent sessions. Empty data stays an explicit empty state instead of a fabricated percentage.

## Privacy export and deletion

### `GET /privacy/export`

Returns timestamped JSON metadata for observations and sessions. Image bytes and server paths are excluded.

```json
{"exported_at":"2026-08-03T12:00:00Z","observations":[],"capture_sessions":[],"note":"Image bytes are not included."}
```

The API does not provide one unscoped “delete everything” endpoint. Use `DELETE /observations/{id}` and `DELETE /capture-sessions/{id}` for user-directed deletion. The operator-only `scripts/reset-demo.ps1 -ConfirmReset` removes only marked Demo evidence. Retention automation, encryption and account-scoped deletion are not implemented.

## Further contracts

Source schemas are under `backend/app/schemas` and `backend/app/agent/schemas.py`. See [architecture](ARCHITECTURE.md), [privacy](PRIVACY.md), and [deployment](DEPLOYMENT.md) for trust and operational boundaries.
