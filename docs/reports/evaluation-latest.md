# SceneMind Reviewed Evaluation Baseline

Reviewed: 2026-08-03. The reproducible runtime output remains under ignored `.runtime/evaluation/<run-id>`; this committed pointer records the evidence accepted for release.

| Capability | Result |
| --- | --- |
| Mock processing | 6 / 6 success; 3.0 detections/image |
| Relations | 11 / 12 correct; 91.67% overall precision |
| Memory | 10 / 10 exact; ordering/evidence/restart persistence 100% |
| Agent | 17 / 18 intent, parameter, tool and evidence matches; 94.44% |
| Sessions | 6 / 6 decisions; 4 / 6 saved |
| Real YOLO | `not_run` because no licensed local real-image set was available |

This small synthetic baseline does not provide detector mAP, recall or F1. Read [EVALUATION.md](../EVALUATION.md) for methodology, latency, environment, failure cases and reproduction commands.
