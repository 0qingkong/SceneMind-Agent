# SceneMind Agent — Competition Summary

## Problem

People often remember that an item was visible but not where or when they last saw it. SceneMind turns permitted scene photos into searchable, evidence-backed spatial memory.

## Demonstrated loop

1. Real YOLO detects multiple objects with normalized bounding boxes.
2. Deterministic geometry produces explainable 2D relations.
3. One observation saves the image, objects, relations, location and timestamp.
4. Memory retrieves last-seen and history results by category.
5. A focused natural-language Agent selects read-only tools and returns the original image evidence.
6. Browser cameras can contribute compressed still frames and persistent low-frequency observation sessions without recording audio or streaming video.

## Why it is credible

- Real inference errors are explicit; Mock is never a silent fallback.
- Repeated detections receive stable ordinal names.
- Reciprocal relations remain complete in the API while the UI removes duplicate pairs.
- Answers expose tool traces, evidence links and truthful limitations.
- Evaluation distinguishes measured, partial and not-run metrics.
- Demo data is generated, visibly marked, idempotent and independently removable.
- Device and insight pages use persisted source/session data, while browser connection state remains explicitly ephemeral.

## Deliberate limits

SceneMind does not perform face recognition, physical-instance tracking across images, metric depth estimation, open-domain chat, custom training or real commercial glasses integration. The browser glasses page is a labeled simulator. It does not capture audio or promise background execution, encryption, face blur, or cloud isolation. A category match is not proof that two pictures contain the same physical item. Image-plane relations are not physical distance or depth.

## Stack

Vue 3 + TypeScript + Vite; FastAPI + Pydantic; Ultralytics YOLO; deterministic geometry; SQLAlchemy + SQLite; local UUID-based image storage.

## Evaluation status

The repository includes unit/integration coverage, a fake-inference end-to-end smoke path, a manual real-YOLO procedure and a report generator. Consult `docs/reports/evaluation-latest.md`; the placeholder intentionally makes no unverified benchmark claim.
