# Competition Demo Scripts

## Operator preflight

Run `scripts/check-system.ps1`, start the chosen Profile with `-NoBrowser`, run `scripts/smoke-demo.ps1 -Extended`, then open Home. Keep Profile C ready as the disclosed deterministic fallback. Never switch from failed YOLO to Mock without telling judges.

Profile routing:

- **A:** camera + real YOLO; preferred only after target camera/HTTPS/model rehearsal.
- **B:** licensed local image + real YOLO; fallback when camera/HTTPS is unreliable.
- **C:** generated evidence + explicit Mock; fallback when real model/input is unavailable.

## 90-second sprint

| Time | Profile | Operator action | Spoken line | Expected UI | Failure switch |
| ---: | --- | --- | --- | --- | --- |
| 0-12s | A/B/C | Show Home hero and loop | “SceneMind turns permitted visual scenes into searchable spatial memory with original evidence.” | Hero, four-step loop, profile banner | If app unavailable, open static deck pages 1 and 3 |
| 12-30s | A: Live; B: Analyze; C: seeded Analyze | Capture/select one frame and analyze | “Detection is only step one; the same result also gets explainable image-plane relations.” | Boxes, object list, engine and 2D boundary | A camera failure -> B; YOLO failure -> disclose C |
| 30-44s | Same | Save or open seeded memory | “The image, objects, relations, place and time become one Observation.” | Saved state, evidence card | Open pre-seeded Profile C memory |
| 44-66s | Same | Ask “我的杯子最后出现在哪里？” | “The Agent selects a read-only Last-Seen tool and can only answer from stored evidence.” | Answer, evidence card, limitations | Use prepared Profile C question |
| 66-78s | Same | Open original evidence | “The answer links back to the source image rather than relying on a text-only claim.” | Observation image/detail | Show formal Agent screenshot |
| 78-90s | C-compatible | Flash simulator disclosure and evaluation card | “The glasses view is explicitly a simulator; measured baselines are 10/10 Memory, 17/18 Agent and 11/12 relations.” | Simulator label/evaluation summary | Use deck pages 9-10 |

## 3-minute standard path

| Time | Profile | Operator action | Spoken line | Expected UI | Failure switch |
| ---: | --- | --- | --- | --- | --- |
| 0-20s | A/B/C | Home | “SceneMind is an evidence-backed spatial-memory Agent for multi-device visual capture.” | Value, loop, sources | Static page 1 |
| 20-45s | A | Open Live, explain purpose, connect | “Permission is user-triggered, audio is always off, and the capture indicator cannot be hidden.” | Purpose notice, active indicator | Permission/HTTPS failure -> B |
| 20-45s | B/C | Open Analyze and select approved/generated image | “When camera conditions are unsuitable we use an approved local image; C is visibly Mock.” | Preview and profile disclosure | Use seeded C evidence |
| 45-75s | A/B/C | Analyze | “Real mode uses YOLO; failures are explicit. Deterministic geometry adds directed 2D relations.” | Engine, boxes, objects, filtered relations | YOLO error -> disclose C, never imply real result |
| 75-95s | Same | Save/open memory | “One coherent Observation persists the original evidence and structured graph.” | Success plus memory card | Open latest seeded memory |
| 95-125s | Same | Open session list/detail | “Foreground low-frequency sessions save first evidence or meaningful changes and record every reason.” | Session status/counters/timeline | Show Profile C seeded session |
| 125-155s | Same | Ask Agent and open evidence | “The planner calls a bounded read-only tool; category matching is not instance identity.” | Answer, trace, evidence, limit | Use prepared screenshot/question |
| 155-180s | A/B/C | Simulator then Insights/Privacy | “The glasses interaction is simulated. SQL aggregates are real persisted data, and unimplemented privacy controls are labeled as planned.” | Exact simulator notice, metrics, boundaries | Use deck pages 9-11 |

## 5-minute complete path

| Time | Profile | Operator action | Spoken line | Expected UI | Failure switch |
| ---: | --- | --- | --- | --- | --- |
| 0-25s | A/B/C | Home positioning | “The problem is not seeing an object once; it is retrieving when and where it was seen with proof.” | Hero and evidence-first card | Deck pages 1-2 |
| 25-50s | A/B/C | Scroll loop and sources | “Capture, detect and relate, persist, then retrieve through a grounded Agent.” | Four-step loop and source cards | Deck page 3 |
| 50-80s | A | Live purpose and connect | “SceneMind requests camera only after this click, with no audio.” | Indicator, device selector, frame controls | Camera/HTTPS failure -> B |
| 50-80s | B/C | Analyze source | “This local image is licensed for demonstration; Profile C is generated Mock evidence.” | Preview and banner | Seed/restart C |
| 80-125s | A/B/C | Analyze and inspect filters | “YOLO boxes stay normalized. Relation scores expose geometry evidence; reciprocal display is collapsed but the API remains directed.” | Objects, latency, confidence, top relations | Open reviewed screenshot |
| 125-155s | Same | Save and enter Memory | “SQLite stores metadata and a local image path; the API never reveals the server path.” | Memory total, filters, recent evidence | Use seeded Memory |
| 155-195s | Same | Show session timeline | “One inference occurs per sample. Meaningful-change avoids saving every unchanged frame.” | Sample/analyze/save counts and reasons | Open seeded session |
| 195-235s | Same | Agent query, trace and image | “This is not open-domain chat: planner, read-only tool, evidence, answer and limits stay inspectable.” | Answer/evidence/trace | Use prepared query or screenshot |
| 235-260s | C-compatible | Devices and simulator | “Upload and browser camera are implemented. The AI glasses view is a browser simulator; real SDK adapters are future work.” | Source groups and exact disclaimer | Deck pages 4 and 9 |
| 260-285s | A/B/C | Insights, Privacy, System | “Statistics come from persisted data. Readiness checks storage without activating YOLO. Encryption and face blur are not implemented.” | Aggregates, privacy boundary, ready state | Deck page 11 |
| 285-300s | A/B/C | Evaluation summary | “The small deterministic baseline is Memory 10/10, Agent 17/18, relations 11/12, sessions 6/6; real YOLO benchmark is not run.” | Scorecard | Deck page 10 |

## Failure narration

- **Camera fails:** “The secure-context/device path is unavailable, so I am switching to Profile B with an approved local image; the detector remains real YOLO.”
- **YOLO fails:** “The real analyzer is unavailable and returned an explicit error. I am switching to disclosed Profile C to demonstrate orchestration and evidence retrieval, not detector accuracy.”
- **Frontend fails:** run `scripts/stop-demo.ps1`, start Profile C, extended smoke, reopen; use deck during recovery.
- **Evidence image fails:** state that the link is unavailable, show the friendly missing-evidence state, then use another seeded Observation; do not conceal the error.
- **Agent unsupported question:** show the boundary response and use a prepared Last-Seen question.

After rehearsal/demo, run `scripts/stop-demo.ps1`. Use `scripts/reset-demo.ps1 -ConfirmReset` only when the scoped removal is intended, and verify unmarked user evidence remains.
