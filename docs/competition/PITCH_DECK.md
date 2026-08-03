# SceneMind Pitch Deck Source

Project title: **SceneMind：面向多设备视觉采集的证据化空间记忆智能体**. Target total speaking time: 5 minutes. Every measured number below comes from [Day 15 evaluation](../EVALUATION.md); real YOLO evaluation remains `not_run`.

## Page 1 - SceneMind

**Conclusion:** Turn permitted visual scenes into searchable memory with original evidence.

- Multi-device still-image capture
- Explainable two-dimensional relations
- Persistent Last-Seen / History memory
- Tool-grounded natural-language retrieval

**Visual:** hero UI plus closed-loop arrow. **Asset:** `01-home.png`. **Time:** 20s. **Speaker note:** Lead with the memory problem, not the detector. **Source:** README positioning and implemented routes.

## Page 2 - The missing “where and when”

**Conclusion:** Recognition answers what is visible now; users also need when, where and proof later.

- People remember seeing an item but forget its last context.
- A detector result disappears unless it becomes durable evidence.
- A useful answer must link back to the source image.
- Trust requires admitting identity and depth limits.

**Visual:** “current detection” versus “retrievable memory” comparison. **Asset:** `04-memory.png`. **Time:** 20s. **Speaker note:** Use a cup or notebook scenario without claiming instance identity. **Source:** product workflow and limitations.

## Page 3 - Four-step product loop

**Conclusion:** SceneMind connects perception, relation reasoning, memory and evidence retrieval.

- See: upload or capture a still frame.
- Understand: detect categories and derive 2D relations.
- Remember: save image, objects, relations, source, location and time.
- Retrieve: Agent calls Last-Seen/History tools and returns evidence.

**Visual:** four numbered cards. **Asset:** `01-home.png`. **Time:** 25s. **Speaker note:** Emphasize one consistent data contract. **Source:** [architecture](../ARCHITECTURE.md).

## Page 4 - Multi-source capture

**Conclusion:** One capture boundary supports today's browser and tomorrow's adapters.

- Implemented upload source for licensed local images.
- Implemented browser camera with explicit permission and `audio: false`.
- Implemented browser AI Glasses Simulator with visible disclosure.
- Android XR/vendor SDK/custom hardware are future adapters.

**Visual:** three implemented source cards plus dashed future adapters. **Asset:** `02-live-lens.png`, `07-devices.png`. **Time:** 25s. **Speaker note:** Never describe simulator as hardware. **Source:** [device adapters](../DEVICE_ADAPTERS.md).

## Page 5 - Detection plus explainable geometry

**Conclusion:** Real YOLO provides object evidence; deterministic geometry adds inspectable image-plane relations.

- Real mode returns normalized bounding boxes and confidence.
- Analyzer failures return `503`, never silent Mock.
- Directed left/right, above/below, near, overlap and containment stay in the API.
- UI collapses reciprocal duplicates but preserves semantic relations.

**Visual:** analysis screenshot with annotated boxes and relation list. **Asset:** `03-analysis.png`. **Time:** 30s. **Speaker note:** Scores are detection confidence times geometry strength, not learned relation probability. **Source:** analyze schema and spatial reasoner.

## Page 6 - Durable scene memory

**Conclusion:** Each saved scene is a queryable, evidence-backed Observation.

- SQLite stores metadata, objects, relations and source/session context.
- UUID-named original images remain in local filesystem storage.
- Last-Seen and History return newest category matches.
- Stable ordinals disambiguate repeated labels in one scene.

**Visual:** Observation card connected to objects, relations and image. **Asset:** `04-memory.png`, `06-session.png`. **Time:** 25s. **Speaker note:** Category matching is not physical-instance tracking. **Source:** [architecture](../ARCHITECTURE.md) and [API](../API.md).

## Page 7 - Evidence-first Agent

**Conclusion:** The Agent is a bounded retrieval interface, not open-domain chat.

- Deterministic intent planner chooses one supported query type.
- Read-only tools reuse Memory/Observation services.
- Answers are constrained to structured tool results.
- UI prioritizes image evidence, limitations and a collapsed trace.

**Visual:** answer -> tool -> evidence -> boundary flow. **Asset:** `05-agent.png`. **Time:** 30s. **Speaker note:** Show a Last-Seen answer and open its image. **Source:** Agent schemas/executor and Day 15 Agent manifest.

## Page 8 - Continuous observation without video streaming

**Conclusion:** Low-frequency foreground sampling records meaningful scene changes with explainable decisions.

- One awaited loop prevents overlapping frontend captures.
- Backend locks each session and runs one inference per sample.
- Manual, meaningful-change and every-analyzed-sample modes are explicit.
- Save/skip reasons and sampled/analyzed/saved counters are persisted.

**Visual:** session state timeline. **Asset:** `06-session.png`. **Time:** 25s. **Speaker note:** No continuous audio/video and no guaranteed background capture. **Source:** CaptureSession service and architecture state diagram.

## Page 9 - AI glasses path, honestly framed

**Conclusion:** The current simulator validates interaction and adapter boundaries, not commercial hardware connectivity.

- “AI Glasses Simulator” and “未来设备交互预览” remain visible.
- Current input is a browser simulation.
- CaptureSource keeps backend contracts hardware-neutral.
- Future Android XR/vendor/custom adapters require separate integration and testing.

**Visual:** simulator screenshot with disclosure highlighted. **Asset:** `08-glasses-simulator.png`. **Time:** 20s. **Speaker note:** Say the exact limitation before discussing roadmap. **Source:** [device adapters](../DEVICE_ADAPTERS.md).

## Page 10 - Reliability and measured evidence

**Conclusion:** Deterministic tests prove the product loop; small-sample evaluation exposes both success and failure.

- Day 14: isolated API lifecycle, six core browser flows, controlled failures and integrity checks.
- Memory: 10 / 10 exact; ordering/evidence/restart persistence 100%.
- Agent: 17 / 18 matches, 94.44%.
- Relations: 11 / 12 reviewed correct, 91.67% overall precision.
- Sessions: 6 / 6 decisions; Mock processing: 6 / 6.

**Visual:** compact scorecard plus “Real YOLO: not_run” badge. **Asset:** `11-evaluation.png`. **Time:** 35s. **Speaker note:** The set is synthetic and small; no detector mAP/recall/F1 claim. **Source:** [EVALUATION](../EVALUATION.md), [TEST_REPORT](../TEST_REPORT.md).

## Page 11 - Privacy and trustworthy limits

**Conclusion:** Visible capture state and narrow claims are product features.

- Camera purpose before permission; active indicator cannot be disabled.
- No audio; still frames only; local SQLite/image storage.
- Export excludes image bytes and server paths.
- No face recognition, identity tracking, encryption, face blur, cloud sync or authentication.
- Two-dimensional relations do not prove depth or physical distance.

**Visual:** implemented versus not implemented two-column boundary. **Asset:** `10-privacy-system.png`. **Time:** 30s. **Speaker note:** Do not imply local storage alone guarantees privacy. **Source:** [PRIVACY](../PRIVACY.md), [LIMITATIONS](../LIMITATIONS.md).

## Page 12 - From reliable demo to real-world validation

**Conclusion:** SceneMind has a complete evidence loop and a clear path to stronger real-device proof.

- Current: local product loop, deterministic recovery, Profile A/B/C.
- Next: lawful 40-60 real-scene dataset and bounding-box annotation.
- Next: target-phone HTTPS rehearsal and real YOLO cold/warm evaluation.
- Future: authenticated deployment, privacy controls and tested hardware adapters.

**Visual:** now / next / future roadmap. **Asset:** `09-insights.png` plus architecture graphic. **Time:** 20s. **Speaker note:** Close on evidence-backed memory, not speculative hardware. **Source:** [PROJECT_STATE](../PROJECT_STATE.md) and [ROADMAP](../ROADMAP.md).
