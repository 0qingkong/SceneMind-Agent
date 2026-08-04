# SceneMind Final Demo Script

Release target: `0.9.0-rc1`. Canonical story: **problem → multi-device visual capture → object detection → explainable 2D relations → persistent scene memory → grounded Agent query → evidence trace-back → continuous observation → AI Glasses Simulator → evaluation and privacy boundaries**.

## Profile decision

| Profile | Input and analyzer | Recording role | Required disclosure |
| --- | --- | --- | --- |
| Profile A | Browser camera + real YOLO | Live hardware path after target-device rehearsal | Camera/HTTPS/hardware result must be stated |
| Profile B | Approved local image + real YOLO | Deterministic real-analyzer recording path | Image ownership and model identity must be recorded |
| Profile C | Generated Demo evidence + explicit Mock | Complete emergency path and automated screenshot baseline | Mock proves orchestration, not YOLO accuracy |

Never change from YOLO to Mock silently. Profile B currently requires human-supplied, approved images listed in [DEMO_ASSET_MANIFEST](DEMO_ASSET_MANIFEST.md).

## Canonical 3-5 minute flow

| # | Route | Precondition | Click/action | Expected visible result | Narration | Max | Fallback |
| ---: | --- | --- | --- | --- | --- | ---: | --- |
| 1 | `/` | Selected Profile is running and smoke passed | Show hero and four-step loop | Value proposition, sources, profile banner | “SceneMind turns permitted visual scenes into searchable memory with original evidence.” | 20s | Use approved Home screenshot |
| 2 | `/live` or `/analyze` | A: trusted camera; B: approved image; C: generated fixture | A: explain permission then connect; B/C: select image | Camera purpose or image preview; no audio request | “One capture contract supports upload, browser stills, and a clearly labeled simulator.” | 25s | A → B; B model/input failure → disclosed C |
| 3 | `/analyze` | A/B real YOLO available, or C visibly Mock | Analyze once | Engine, boxes, object count, confidence, latency | “Detection is one component; failures stay explicit instead of becoming fake Mock results.” | 25s | Open prepared Profile C analysis |
| 4 | `/analyze` | Analysis result visible | Filter/expand relations | Chinese 2D relations and geometry disclaimer | “Relations are deterministic image-plane geometry, not depth or centimetres.” | 20s | Use `03-analysis.png` |
| 5 | `/analyze` | Title/location prepared | Choose save action once | Success message and persistent Observation | “The source image, objects, relations, place and time become one coherent memory.” | 20s | Open seeded Memory; do not double-click |
| 6 | `/memory` | At least one Observation exists | Search `杯子`; open newest card | Total, filters, newest evidence and repeated-label ordinals | “Last-Seen and History retrieve category evidence; they do not prove the same physical cup.” | 25s | Use Profile C seeded desk evidence |
| 7 | `/agent` | Cup evidence exists | Ask `我的杯子最后出现在哪里？` | Supported intent, answer, evidence card, limitations | “The Agent selects a bounded read-only tool and answers only from stored records.” | 30s | Use prepared question/screenshot |
| 8 | `/memory/{id}` | Agent evidence link is valid | Open cited observation | Original image, metadata, objects and relations | “Every answer can trace back to the original visual evidence.” | 20s | Open seeded Observation ID `...0101` |
| 9 | `/sessions/{id}` | Seeded or rehearsed session exists | Open timeline | Status, sample/analyze/save counts and reasons | “Foreground low-frequency observation saves meaningful changes instead of streaming video.” | 25s | Use Demo session ID `...0201` |
| 10 | `/devices`, `/glasses` | Browser frontend available | Show device center, then simulator disclosure; do not request camera during automated capture | Capture-source status, `AI Glasses Simulator` and hardware disclaimer | “The source abstraction is implemented; this glasses view is a browser preview, not connected eyewear.” | 20s | Use approved device/simulator screenshots |
| 11 | `/insights`, `/privacy`, `/system` | Persisted data and ready backend | Show aggregates, camera indicator rule and readiness | SQL-derived counts, planned controls, version/profile | “Statistics come from stored data; the camera indicator cannot be disabled; unimplemented protections stay labeled.” | 25s | Use approved status screenshots |
| 12 | `/` evaluation section | Day 15 source report available | End on scorecard | Memory 10/10; Agent 17/18; relations 11/12; sessions 6/6; real YOLO `not_run` | “The measured set is small and deterministic; it is evidence, not a universal accuracy claim.” | 25s | Use pitch slide 10 |

## Claims that must remain explicit

- Category retrieval is not cross-image physical-instance identity.
- Bounding-box relations are two-dimensional and do not prove depth, support, or metric distance.
- The Agent is deterministic and bounded, not open-domain autonomous chat.
- Browser continuous observation is foreground, low-frequency still capture without audio.
- AI Glasses Simulator is not commercial glasses hardware or a vendor SDK.
- Encryption, face blur, authentication, cloud sync, and retention automation are not implemented.
- Day 15 did not run a licensed real-YOLO benchmark and provides no mAP/recall/F1.

## Recovery phrases

- **Camera:** “The target camera/secure-context path is unavailable, so I am switching to approved Profile B without changing the real analyzer.”
- **YOLO/input:** “Real inference is unavailable and returned an explicit error. I am switching to disclosed Profile C to demonstrate orchestration, memory, and evidence—not detector accuracy.”
- **Frontend:** speak from the storyboard while running `stop-demo.ps1`, Profile C startup, and extended smoke.
- **Agent no match:** show the truthful no-result state, then use the prepared cup query.
- **Evidence unavailable:** show the friendly missing-image state and select a second seeded Observation; do not hide the failure.

## Close

“SceneMind is not just a YOLO page. It joins inspectable perception, durable spatial memory, continuous observation, and evidence-grounded retrieval in one testable local product loop.”
