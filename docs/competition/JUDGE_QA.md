# Judge Q&A

## 1. How is this different from a normal YOLO project?

YOLO is one replaceable analyzer. SceneMind adds explainable 2D relations, transactional scene persistence, Last-Seen/History retrieval, continuous-observation policies and a bounded Agent that returns original evidence. The differentiator is the closed loop, not a custom detector.

## 2. Why not call one multimodal large model?

The competition questions are narrow and evidence-sensitive. Deterministic tools reduce network dependency, latency and hallucination risk and expose exactly which stored records produced an answer. A future planner could change while keeping the same read-only tools and evidence contract.

## 3. Can SceneMind confirm this is the same cup in two photos?

No. Current retrieval matches detector categories and aliases. It can say the newest Observation contained a cup-like category; it cannot establish physical-instance identity across images. That would require additional embedding/tracking evidence and a different claim.

## 4. Are the 2D spatial relations reliable?

They are deterministic and inspectable for the configured image-plane rules, but boxes can be ambiguous. Day 15 reviewed 12 predictions: 11 were correct, 91.67% overall precision; one ambiguous `near` case was counted wrong. These relations do not establish true depth, support or metric distance.

## 5. Why SQLite rather than a graph/vector database?

The MVP stores modest structured snapshots and executes newest-first category queries on one workstation. SQLite is inspectable, transactional and easy to back up. Repository/service boundaries allow future storage replacement. A graph/vector database would not solve the current lack of physical-instance identity evidence.

## 6. Are AI glasses really connected?

No. The current product contains **AI Glasses Simulator / 未来设备交互预览** in the browser. It validates a capture interaction and adapter boundary, not a vendor SDK or real hardware link. Android XR/vendor/custom adapters are future work.

## 7. Why is continuous observation not frame-by-frame inference?

SceneMind targets durable memory, not video analytics. A foreground awaited loop samples at low frequency; a per-session lock prevents overlap; meaningful-change rules avoid storing every unchanged scene. This reduces compute/storage and makes every save/skip reason explainable.

## 8. How do you handle privacy?

Permission is user-triggered, the active-camera indicator cannot be disabled, audio is always off, only still frames are submitted, and tracks are released on leave/error. Data is local by default and export excludes image bytes/server paths. Authentication, encryption, face blur, automatic retention and production cloud isolation are not implemented.

## 9. How would this extend to real devices?

A new device implements the existing CaptureSource lifecycle and emits image evidence plus source metadata. It must add device permission/privacy behavior and tests. The current backend Observation/Agent contracts need not depend on a vendor SDK, but no future adapter is claimed as already integrated.

## 10. How were Day 15 metrics obtained?

Committed synthetic manifests and manual relation annotations drive isolated detection, relation, memory, Agent and session runners. The reviewed baseline is Memory 10/10, Agent 17/18, relations 11/12, sessions 6/6 and Mock processing 6/6. Runtime reports record environment and hashes. Real YOLO stayed `not_run` because no licensed local real-scene set was available.

## 11. What is the biggest observed failure?

One question requesting centimetre distance was routed to object count and returned four unsupported evidence IDs. It lowered Agent unsupported handling to 66.67% and overall matching to 17/18. The release documents it instead of rewriting the baseline after evaluation.

## 12. What happens if the model fails during the demo?

Real mode returns an explicit `503`; it never silently changes to Mock. The operator states the failure and switches to visibly disclosed Profile C, whose deterministic evidence demonstrates orchestration, memory and Agent behavior only. PID/log/readiness/smoke tools support recovery.

## 13. Is the real YOLO detector tested at all?

The implementation and manual smoke procedure exist, and earlier project work manually verified real image detection. The Day 15 formal environment did not contain a permitted local dataset with box ground truth, so the release truthfully records real-YOLO evaluation as `not_run` and makes no mAP/recall/F1 claim.

## 14. How do you know answers are grounded?

The deterministic planner selects a bounded read-only tool. The response schema includes the tool/arguments/status, evidence Observation IDs, image/detail URLs and limitations. The formatter is built from returned structured results. Day 15 compares expected intent, parameters, tool and evidence IDs.

## 15. Can Demo reset delete user data?

The reset command requires explicit confirmation and selects durable Demo markers, including the exact legacy demo engine. Idempotent seeds skip colliding IDs rather than overwrite them. Unmarked real/user Observations are outside reset selection; automated tests verify this boundary.

## 16. Is this production ready?

It is competition-demo ready for a single local workstation after the specified validation. It is not a production multi-user/cloud service: authentication, authorization, encryption, scalable storage, monitoring and deployment hardening remain future work.
