# Final judge Q&A

## 1. How is this different from an ordinary YOLO demo?

YOLO is one replaceable analyzer. SceneMind normalizes detections, derives inspectable 2D relations, saves timestamped Observations, retrieves Last-Seen/History results, and lets a bounded Agent cite the exact stored evidence. The product value is the evidence-backed spatial-memory loop, not a detector canvas alone.

## 2. Why not use one multimodal model for everything?

The competition build favors deterministic, observable components. Detection, relation rules, persistence and Agent tools can be tested separately and fail explicitly. A future multimodal model could add hypotheses, but it would not replace evidence IDs, provenance or supported-query boundaries.

## 3. Can the system prove that two detected cups are the same cup?

No. Current retrieval matches object categories across observations. “The cup was last seen” means the newest matching cup evidence; it does not establish physical-instance identity.

## 4. How reliable are the spatial relations?

They are deterministic image-plane rules over normalized boxes. Day 15 manually reviewed 12 predicted relations: 11 were correct, giving 91.67% overall precision; one ambiguous `near` prediction was counted wrong. This small review does not measure recall, depth or physical distance.

## 5. Why SQLite?

SQLite gives the local competition demo transactions, restart persistence, simple backup/reset and inspectable queries with no external service. Its single-node scope is deliberate; a multi-user deployment would need user isolation, migration and managed storage work.

## 6. Is the AI-glasses integration real?

No. `AI Glasses Simulator / 未来设备交互预览` is a browser simulator that exercises the capture-source boundary. No vendor SDK or physical glasses telemetry is integrated.

## 7. How is privacy handled?

Camera access is user-initiated, audio is disabled, an active-camera indicator remains visible, local observations can be exported or deleted, and Demo/Mock/Simulator states are labeled. Authentication, cloud encryption and automatic face blurring are not implemented and are not claimed.

## 8. How is continuous capture controlled?

It is a foreground, low-frequency, sequential session: one frame is processed at a time, with observable saved/skipped/error decisions and explicit start/stop. It is not an autonomous background surveillance service.

## 9. What does the Agent actually do?

It classifies a bounded set of supported questions, validates parameters, calls deterministic Memory tools and returns structured text with Observation evidence IDs. It is not open-domain chat and does not invent evidence when a supported query has no result.

## 10. What are the main evaluation results?

The committed Day 15 synthetic baseline records Memory 10/10, Agent 17/18 (94.44%), relations 11/12 reviewed correct (91.67% overall precision), sessions 6/6 and Mock processing 6/6. The formal real-YOLO benchmark is `not_run` because no licensed local real-scene set was approved.

## 11. What fails in low light or occlusion?

Real detector confidence and boxes can degrade, small objects can be missed, and derived relations inherit those box errors. The UI exposes confidences and evidence. Profile C is a recovery path, not proof that real-scene detection succeeded.

## 12. How can this scale after the competition?

Preserve the analyzer, capture-source and repository contracts while adding approved device adapters, user-scoped storage, encrypted deployment, explicit tracking hypotheses and separately evaluated depth/VLM evidence. Those are roadmap items, not current features.

## 13. Why keep inverse relations in the API but collapse them in the UI?

Directed pairs make programmatic queries unambiguous. The UI collapses reciprocal presentation to reduce noise while preserving symmetric `near`/`overlaps` and containment `inside`/`contains` semantics.

## 14. What happens when real YOLO fails?

The API returns an observable error and never silently substitutes Mock output. An operator may intentionally switch to the labeled Profile C emergency path.
