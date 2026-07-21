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
