# SceneMind Technical Report

## Abstract

SceneMind is a local-first, evidence-backed spatial-memory agent for permitted multi-device visual capture. It combines real YOLO object detection, deterministic two-dimensional relation reasoning, persistent scene observations, foreground sequential sampling and a bounded tool-calling Agent. The competition MVP emphasizes a reliable closed loop and transparent limits: category retrieval does not establish physical-instance identity, image-plane relations do not establish depth, and the browser AI Glasses Simulator is not real hardware. Day 14 validates deterministic orchestration and failure recovery; Day 15 records a small synthetic baseline without claiming detector accuracy that was not measured.

The competition demo and its speaker notes use one canonical sequence: problem, permitted multi-device visual capture, object detection, explainable 2D relations, persistent scene memory, grounded Agent query, evidence trace-back, continuous observation, the explicitly labeled AI Glasses Simulator, and measured evaluation/privacy boundaries. Exact actions, time boxes and Profile B/C recovery steps are maintained in [FINAL_DEMO_SCRIPT](../demo/FINAL_DEMO_SCRIPT.md).

## 1. Background and problem definition

**Implemented product scope.** Existing detectors answer what appears in one image but do not by themselves provide durable “where and when was it last seen?” evidence. SceneMind defines the unit of memory as an Observation containing an original image, detected objects, directed image-plane relations, optional location/source and timestamp. Later retrieval returns that evidence rather than an unsupported textual guess.

## 2. User needs and product goals

The primary flow is: see a scene, understand objects and 2D relations, form memory, then retrieve it through natural language with source evidence. The release targets mobile-oriented operation, visible capture state, quick local recovery and honest competition presentation. It intentionally excludes social features, account systems, custom model training and broad cloud infrastructure.

## 3. Overall system architecture

**Implemented.** A Vue 3/TypeScript frontend calls a FastAPI `/api/v1` backend. Services isolate analyzer, spatial reasoning, Observation persistence, memory retrieval, Agent execution, capture sessions and dashboard aggregation. SQLAlchemy/SQLite stores structured metadata; original images use UUID filenames in local filesystem storage. Schemas never expose absolute paths. Detailed Mermaid diagrams are in [ARCHITECTURE](../ARCHITECTURE.md).

## 4. Multi-device capture layer

**Implemented:** user-selected image upload, browser camera still capture and a shared `CaptureSource` lifecycle. Browser permission is user-triggered, constraints always disable audio, one source owns at most one stream, and disconnect/error/unmount stops every track. Canvas capture bounds image width and compresses the frame before upload.

**Demonstration simulation:** `GlassesSimulatorSource` previews a glasses-like browser interaction. It stays labeled “AI Glasses Simulator / 未来设备交互预览” and does not report real hardware telemetry.

**Future:** Android XR, vendor Wearable SDK and custom hardware adapters may implement the same lifecycle after device-specific permission, privacy and reliability testing.

## 5. Visual detection layer

**Implemented.** `SceneAnalyzer` separates explicit Mock and lazy reusable Ultralytics YOLO implementations. Configuration controls model, confidence, image size, maximum detections and device. Returned boxes are clamped normalized `[x1,y1,x2,y2]` values with labels, localized display names and confidence. Upload validation rejects oversized, unsupported or undecodable files before inference. A YOLO failure returns `503`; Mock is never selected silently.

**Measured boundary.** Day 15 Mock processing succeeded on 6 / 6 synthetic cases with 3.0 detections/image. Real YOLO accuracy and latency are `not_run` because the evaluation environment lacked a licensed local real-scene set and box ground truth. No mAP, recall or F1 is claimed.

## 6. Two-dimensional spatial relation reasoning

**Implemented.** A deterministic reasoner consumes normalized boxes and emits directed `left_of/right_of`, `above/below`, `near`, `overlaps`, `inside/contains`. Evidence includes center distance, intersection-over-union or containment ratio. Scores combine the lower object confidence with geometry strength. Thresholds and output cap are configurable, and Mock/YOLO use the same reasoner.

The API retains inverse directions for completeness. The frontend collapses reciprocal presentation and keeps near, overlap and containment semantics. These predicates describe an image plane only; they cannot prove support, depth ordering or metric distance.

Day 15 manually reviewed 12 predicted relations: 11 / 12 correct, 91.67% overall precision and 85.71% macro precision. The single ambiguous `near` example was retained as incorrect rather than removed.

## 7. Scene memory model

**Implemented.** `Observation` owns object and relation snapshots. SQLite contains metadata and relative image paths; a storage service writes the original image. Creation runs analysis once and then persists a coherent snapshot. Transaction failure removes a new image. Deletion stages the image, commits relational deletion and then finalizes cleanup, with explicit error behavior.

Last-Seen and History search detector categories and selected Chinese/English aliases in newest-first order. Stable repeated-object ordinals are local presentation metadata. Day 15 Memory achieved 10 / 10 exact expected Observation IDs with 100% ordering, evidence availability and restart persistence.

## 8. Continuous observation and change policy

**Implemented.** A persistent CaptureSession records state, interval, target query, save mode, counters, last error and timing. The frontend uses one awaited foreground loop; the backend locks a session so samples cannot overlap. Each successful sample runs inference once. `manual`, `meaningful-change` and `every-analyzed-sample` modes record exact save/skip reasons.

Meaningful change includes first valid evidence, label multiset changes, significant object-count change, target first appearance, minimum save gap or a forced save. Day 15 produced 6 / 6 correct decisions and saved 4 / 6 frames. The design does not stream video/audio or promise background capture.

## 9. Agent Planner and tool calling

**Implemented.** A deterministic planner maps questions to last seen, history, recent observations, Observation detail, object count, help or unknown. Tools are read-only wrappers over existing services. The executor returns a tool trace, evidence cards and limitations; the formatter may describe only returned data. Unsupported or no-match paths do not invent evidence.

Day 15 matched intent, parameters, tool and evidence on 17 / 18 questions (94.44%). One physical-distance question was misrouted to object count and returned unsupported evidence; this remains documented rather than changing the baseline. The Agent is not open-domain chat and does not use an external large model.

## 10. Frontend product design

**Implemented.** A layered token system defines color, typography, 8px spacing, radii, controls, breakpoints, focus and safe areas. Desktop exposes eight primary destinations; mobile limits bottom navigation to Home, Lens, Memory, Agent and Me. Me groups sessions, devices, insights, privacy and system status.

Home explains the loop and boundaries within the first screen. Analyze shows engine/confidence/latency/relations. Memory provides filters and safe-image fallbacks. Agent prioritizes evidence. Camera and simulator states are always explicit. Loading, empty, success, warning, error, retry, disabled, focus-visible and reduced-motion behavior are covered across core flows.

## 11. Engineering and demo safeguards

**Implemented.** Setup/start/stop scripts support Profile A/B/C. Profile C seeds deterministic Demo Observations/sessions idempotently; scoped reset deletes only durable Demo markers. Managed startup writes PID identity metadata and logs. Stop verifies role, process name and start time before terminating only the managed tree. `/health` is liveness; `/ready` probes database and writable image storage without model activation.

The competition recovery package includes extended smoke, controlled failure tests, relational/filesystem integrity checks, offline inventory and copyable UI recovery commands.

## 12. Testing and reliability

**Implemented evidence.** pytest covers services/routes, isolated lifespan, transaction behavior and validation. Node capture tests validate source lifecycle and privacy constraints. Playwright exercises six core Profile C flows and four UI viewports without camera permission. Failure scripts cover invalid input, analyzer/storage/session/port/PID/process faults. The integrity validator checks relational invariants, image references in both directions, ordering, demo markers and export path safety.

Day 14 automation is deterministic Mock/fake inference. Profile A/B, physical phone HTTPS, true camera behavior and real glasses are manual/not-run scopes, not implied by browser tests.

## 13. Formal evaluation results

Day 15 uses committed synthetic manifests, relation annotations, deterministic memory/Agent cases and session sequences. Actual baseline:

| Module | Result |
| --- | --- |
| Mock processing | 6 / 6 success, 100% non-empty, 3.0 detections/image |
| Relations | 11 / 12 correct, 91.67% overall precision |
| Memory | 10 / 10 exact, all supporting integrity measures 100% |
| Agent | 17 / 18 matches, 94.44% |
| Sessions | 6 / 6 decisions, 4 / 6 saved |
| Real YOLO | `not_run` |

The report records latency distributions and environment separately. Small strata are evidence cases, not population estimates. See [EVALUATION](../EVALUATION.md).

## 14. Privacy and security

**Implemented:** permission explanation, non-disableable camera indicator, no audio, still-frame transfer, deterministic stream release, local storage, path-safe image access, path-free export, specific deletion and scoped Demo reset.

**Not implemented:** authentication, tenant isolation, application-managed encryption, face blur, consent ledger, automatic retention deletion, cloud synchronization or secure-erasure guarantees. A detector may label `person` but performs no identity recognition. Deployment beyond localhost requires a trusted HTTPS/access-control layer outside the current application.

## 15. Known limitations

- Category search cannot confirm the same cup/person across images.
- Two-dimensional relations can be ambiguous and do not provide depth or centimetres.
- The real detector lacks a committed licensed real-scene benchmark with box annotations.
- Browser background scheduling, camera enumeration and Wake Lock are best-effort.
- SQLite/local images target a single process and single workstation.
- The physical-distance Agent misroute remains a documented evaluation failure.
- The glasses experience is simulated, not vendor hardware integration.

## 16. Future work

**Near-term validation:** collect a lawful 40-60 real-image set, annotate boxes/relations, separate cold/warm YOLO latency, rehearse target phone via trusted HTTPS, and fix the unsupported distance-intent route with a new baseline version.

**Later product work:** visual embeddings or explicit tracking for identity hypotheses, depth/VLM evidence with new predicates, authentication and user-scoped retention, encrypted/object storage deployment, and tested Android XR/vendor/custom adapters. These plans must not be used as current experiment results.

## 17. Conclusion

SceneMind demonstrates that object detection becomes more useful when connected to explainable relations, durable scene evidence and bounded retrieval. Its main engineering contribution is a credible local product loop with explicit recovery and claim boundaries. The release package favors reproducibility and source evidence over broad unsupported capability claims.
