# Claims Ledger

Use this table during slides, demo and Q&A. “Implemented” means present in current code; “simulated” must always be disclosed; “measured” includes exact Day 15 evidence; “future” must not be phrased as current capability.

| Claim | Status | Evidence | Allowed use | Prohibited wording |
| --- | --- | --- | --- | --- |
| Real YOLO object detection mode exists | Implemented; Day 15 real evaluation `not_run` | `YoloSceneAnalyzer`, analyze route, manual smoke procedure | “SceneMind supports explicit real YOLO mode” | “Our detector has proven production accuracy” |
| Mock analyzer | Implemented explicit fallback | analyzer factory, Profile C banner/tests | “Profile C deterministically demonstrates orchestration” | “Mock boxes are real detections” |
| Two-dimensional spatial relations | Implemented and measured | reasoner, 11 / 12 review, 91.67% precision | “Explainable image-plane geometry” | “Understands true depth/physical distance” |
| Directed inverse relations | Implemented API | response schema/reasoner tests | “API preserves left/right and other directed evidence” | “UI shows every inverse duplicate” |
| Near/overlap/inside/contains | Implemented | reasoner/tests/relation review | Use exact predicate semantics with 2D caveat | “Near means physically close” |
| Scene persistence | Implemented | SQLite models, image storage, API lifecycle | “Persists local Observation snapshots and images” | “Cloud-synced durable storage” |
| Last-Seen | Implemented and measured | MemoryService, 10 / 10 Memory | “Newest matching category evidence” | “Tracks the same physical object” |
| History | Implemented and measured | memory history API and ordering cases | “Newest-first category history” | “Complete real-world movement history” |
| Agent tool calling | Implemented and measured | planner/tools/executor, 17 / 18 | “Bounded deterministic read-only tool use” | “Open-domain autonomous multimodal Agent” |
| Browser camera | Implemented; hardware acceptance separate | BrowserCameraSource/capture tests | “User-triggered still capture with audio off” | “Reliable background video collection” |
| Continuous observation | Implemented foreground sampling; measured | session service, 6 / 6 decisions | “Low-frequency foreground sampling with explainable save policy” | “Always-on background recording” |
| AI Glasses Simulator | Simulated | simulator view/source/disclaimer | “Future device interaction preview in browser” | “Connected to real AI glasses” |
| Android XR/vendor/custom adapters | Future | adapter design only | “Architecture provides a future extension boundary” | “Already integrated hardware SDKs” |
| Profile C Demo evidence | Implemented generated Mock | deterministic seed/reset/tests | “Visibly marked emergency evidence demo” | “Real YOLO or field data” |
| Memory metric | Measured small synthetic set | Day 15 report: 10 / 10 | State sample count and integrity measures | Generalize to arbitrary datasets |
| Agent metric | Measured small synthetic set | Day 15 report: 17 / 18, 94.44% | State failed distance case | “No hallucinations” or “100% Agent” |
| Relation metric | Measured reviewed predictions | 11 / 12, 91.67% overall precision | Call it precision on 12 predictions | Call it recall/mAP or population accuracy |
| Session metric | Measured deterministic sequences | 6 / 6 decisions, 4 / 6 saved | State exact sequence count | Claim production camera reliability |
| Mock processing metric | Measured deterministic fixtures | 6 / 6, 3.0 detections/image | Orchestration/latency context only | Detector accuracy |
| Privacy: no audio and visible indicator | Implemented | capture constraints/UI tests | Exact behavior statement | “Fully privacy compliant” |
| Metadata export | Implemented | `/privacy/export` | “Exports JSON metadata without image bytes/server paths” | “Complete backup” |
| Encryption, face blur, retention, auth, cloud isolation | Future/not implemented | privacy UI/docs | Explicitly say not implemented | Present as active safeguards |
| No face recognition | Current boundary | no identity model/API | “SceneMind does not identify people” | “Person detection guarantees anonymity” |
| Day 14 browser reliability | Measured Profile C automation | TEST_REPORT, six flows | “Deterministic browser flows passed” | “Physical camera/phone/real YOLO passed” |

When in doubt, use the narrower statement and point to the original evidence. See [EVALUATION](../EVALUATION.md) and [PRIVACY](../PRIVACY.md).
