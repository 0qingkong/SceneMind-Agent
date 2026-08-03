# SceneMind Competition Summary

## Positioning

**SceneMind：面向多设备视觉采集的证据化空间记忆智能体。**

SceneMind 不是单纯的 YOLO 识别页面，而是将视觉感知、可解释二维空间关系、连续场景记忆和基于工具调用的自然语言检索组合成完整产品闭环。

```text
多设备视觉采集 -> 目标检测 -> 二维空间关系 -> 场景记忆
-> Last-Seen / History -> 证据化 Agent
```

## Implemented evidence loop

1. Real YOLO mode detects multiple object categories and normalized boxes.
2. Deterministic image-plane geometry derives explainable directed relations.
3. One transaction saves image, objects, relations, location, source and timestamp.
4. Memory retrieves newest category matches and ordered history.
5. A bounded Agent calls read-only tools and returns original-image evidence.
6. Upload, browser camera stills and an explicitly labeled glasses simulator share a capture contract.
7. Foreground low-frequency sessions explain why each analyzed sample was saved or skipped.

## Day 14 reliability evidence

The deterministic suite covers an isolated API lifecycle, six Profile C browser flows, controlled failures, and database/filesystem integrity. Real YOLO, Profile A/B, physical phone camera and real glasses were not part of that automated run. See [TEST_REPORT](TEST_REPORT.md).

## Day 15 measured baseline

| Capability | Measured result |
| --- | --- |
| Memory | 10 / 10 exact ID; ordering, evidence and restart persistence 100% |
| Agent | 17 / 18 intent, parameter, tool and evidence matches; 94.44% |
| Relations | 11 / 12 reviewed predictions correct; 91.67% overall precision |
| Sessions | 6 / 6 exact save/skip decisions; 4 / 6 saved |
| Mock processing | 6 / 6 success; 3.0 detections per image |
| Real YOLO evaluation | `not_run` because no licensed local real-image set was available |

The six-scene synthetic set is small. There is no bounding-box ground truth, so SceneMind does not claim detector mAP, recall or F1. Full method, latency and failure details are in [EVALUATION](EVALUATION.md).

## Credibility boundaries

- Real inference errors are explicit; Mock is never a silent fallback.
- Repeated labels receive stable ordinals only in presentation.
- Directed inverse relations remain in the API; the UI collapses reciprocal duplication.
- Category retrieval does not identify the same physical instance across images.
- Two-dimensional relations do not establish depth, support or metric distance.
- AI Glasses Simulator is a browser interaction preview, not connected hardware.
- Encryption, face blur, account authentication, retention automation and production cloud isolation are not implemented.

## Competition recovery

Profiles A and B demonstrate real YOLO when hardware, permissions and licensed inputs are ready. Profile C is a deterministic, visibly disclosed Mock fallback with idempotent generated evidence. Managed PID/log tooling, readiness checks, smoke tests, safe reset and offline preparation reduce demo recovery time without overstating capability.

Supporting materials: [pitch deck](competition/PITCH_DECK.md), [technical report](competition/TECHNICAL_REPORT.md), [demo scripts](competition/DEMO_SCRIPT.md), [judge Q&A](competition/JUDGE_QA.md), and [claims ledger](competition/CLAIMS_LEDGER.md).
