# Final public claims ledger

Release target: `0.9.0-rc1`. Every public sentence in README, pitch/report, demo narration, subtitles and release notes must stay within this table. The named owner must perform final human approval before publication.

| Public claim | Evidence file | Metric/source | Supported wording | Prohibited stronger wording | Approval owner |
|---|---|---|---|---|---|
| Real object detection path | `backend/app/analyzers/yolo_analyzer.py`, `docs/API.md` | Configured YOLO analyzer; failures remain visible | “Supports a local real-YOLO analyzer” | “Detector accuracy is proven” or silent Mock fallback | ML/demo owner |
| Structured Observation memory | `backend/app/services/memory_service.py`, `docs/EVALUATION.md` | Memory 10/10 on committed synthetic cases | “Persists timestamped scene, objects, relations and evidence” | “Recognizes every physical object forever” | Backend owner |
| Last-Seen and History | `docs/EVALUATION.md`, `docs/competition/TECHNICAL_REPORT.md` | 10/10 ordering/evidence/restart baseline | “Retrieves newest category evidence and history” | “Confirms this is the same physical cup” | Product owner |
| 2D spatial relations | `backend/app/services/spatial_reasoner.py`, `docs/reports/evaluation-latest.md` | 11/12 reviewed predictions; 91.67% overall precision | “Explainable image-plane geometry on a small reviewed set” | “Understands true depth, support or centimetres” | Evaluation owner |
| Agent evidence grounding | `backend/app/services/agent_service.py`, `docs/reports/evaluation-latest.md` | 17/18 intent/parameter/tool/evidence matches; 94.44% | “Bounded supported queries cite stored evidence” | “Open-domain assistant”, “no hallucinations”, or “100%” | Agent owner |
| Session processing | `docs/EVALUATION.md` | Sessions 6/6; Mock processing 6/6 | “Foreground sequential capture records saved/skipped/error outcomes” | “Fully autonomous background capture” | Frontend owner |
| Multi-device abstraction | `docs/DEVICE_ADAPTERS.md`, `frontend/src/capture` | Upload, browser camera and simulator sources implemented | “A shared capture-source abstraction” | “Every camera is integrated and continuously online” | Architecture owner |
| AI Glasses Simulator | `frontend/src/views/GlassesView.vue`, `docs/DEVICE_ADAPTERS.md` | Visible simulator disclaimer | “Browser future-device interaction preview” | “Connected to real glasses” or vendor SDK telemetry | Device owner |
| Privacy controls | `docs/PRIVACY.md`, `frontend/src/views/PrivacyView.vue` | Local settings, export/delete and visible camera state | “Local-first controls with explicit user capture” | “End-to-end cloud encryption”, “automatic face blur”, or compliance certification | Privacy owner |
| Deterministic Profile C | `docs/DEMO_RUNBOOK.md`, `backend/app/services/demo_data.py` | Code-generated seeded evidence | “Complete emergency demo path with labeled Mock data” | “Real detector result” or accuracy evidence | Demo owner |
| Day 15 evaluation scope | `docs/EVALUATION.md`, `docs/reports/evaluation-latest.md` | Small committed synthetic/reviewed datasets | “Regression and precision evidence for the stated cases” | Population accuracy, detector mAP/recall/F1 | Evaluation owner |
| Release-candidate status | `docs/release/RELEASE_NOTES_v0.9.0-rc1.md`, `VERSION` | Automated gate plus listed human gates | “Prepared release candidate” after gates pass | “Production certified”, “published”, or “hardware approved” | Release owner |

## Final consistency rule

If a source disagrees with this ledger or the Day 15 report, use the weaker wording and open a documentation defect. Automation can compare strings and metrics, but only the human owners can approve public context, images, hardware statements and final media.
