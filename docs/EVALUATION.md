# SceneMind formal evaluation

Last reviewed: 2026-08-03. Each generated runtime report records the exact commit SHA used for that run.

## Goals and evidence rules

The evaluation asks how reliably each existing capability behaves, without adding product features. Mock runs measure deterministic orchestration and product logic only. They are never presented as YOLO accuracy. Unmeasured work remains `not_run`; failures stay in the generated report.

There is no complete bounding-box ground truth, so this project does **not** claim detection mAP, recall, or F1. Relation annotations review predicted relations and therefore support precision, not recall. Two-dimensional boxes do not establish depth or physical distance.

## Dataset and manifests

| Set | Actual size | Composition | Purpose |
| --- | ---: | --- | --- |
| Scenes | 6 | Synthetic desk, classroom, library, home, repeated people, low light | Harness processing and Mock latency |
| Relations | 12 predictions | 7 predicates, including inverse, overlap, near, inside and contains | Manual precision review |
| Memory | 10 queries | Last-seen, ordered history, Chinese/English aliases, no result | Isolated SQLite retrieval |
| Agent | 18 questions | Chinese/English, concise, polite, verbose, no-result and unsupported | Intent/tool/parameter/evidence grounding |
| Sessions | 2 sequences / 6 frames | Meaningful-change and manual modes | Save/skip policy |
| Failure gallery | 9 cases | Observed failures plus explicitly unmeasured risk | Competition limitations |

The committed scene entries use synthetic asset keys and contain no private photographs or absolute paths. This is below the recommended 40–60 real images, 150–300 relations, 30–50 memory queries and 50–70 Agent questions; results are preliminary and must not be generalized.

## Annotation methodology

Relations were reviewed against deterministic generated box geometry. Each row records subject, predicate, object, correctness, ambiguity and a reviewer note. The `near` case was deliberately retained as an incorrect, ambiguous prediction. Inverse `left/right` and `inside/contains` examples remain separate API judgments. The frontend may collapse reciprocal presentation, but evaluation does not remove directed API evidence.

Memory and Agent expected observation IDs come from fixed, idempotent Demo seed IDs in an isolated database. The memory runner disposes and reopens its SQLAlchemy engine before querying. Session frames use a deterministic analyzer and compare exact save/skip reasons.

## Metrics

- Detection without bbox ground truth: processing success, non-empty rate, detections/image, category coverage and end-to-end latency.
- Relations: precision per predicate, macro precision, overall precision and ambiguity rate.
- Memory: exact observation-ID match, history ordering, evidence-image availability and restart persistence.
- Agent: intent, parameters, tool, evidence IDs, no-result/unsupported handling and unsupported evidence count.
- Session: exact save/skip decision accuracy and sampled-to-saved ratio.
- Latency: `time.perf_counter()`, with count, min, P50, P95, max and mean. Cold and warm YOLO runs are not mixed because real YOLO was not run.

## Actual deterministic results

Run directory: ignored `.runtime/evaluation/20260803-150440-mock-44956`.

| Capability | Result |
| --- | --- |
| Mock processing | 6/6 images; 100% success; 100% non-empty; 3.0 detections/image |
| Mock analyze latency | P50 0.189 ms; P95 0.279 ms; n=6 |
| Relation review | 11/12 correct; 91.67% overall; 85.71% macro; 16.67% ambiguous |
| Memory | 10/10 exact; 100% ordering, evidence availability and restart persistence |
| Memory latency | P50 2.255 ms; P95 5.205 ms; n=10 |
| Agent | 17/18 intent, parameter, tool and evidence matches: 94.44% each |
| Agent no-result / unsupported | 100% / 66.67%; 4 unsupported evidence IDs in one failed distance query |
| Agent latency | P50 2.449 ms; P95 6.004 ms; n=18 |
| Session | 6/6 decisions; 4/6 saved; saved ratio 66.67% |

Per-predicate relation precision was 100% for `left_of`, `right_of`, `below`, `overlaps`, `inside` and `contains`; `near` was 0% on one ambiguous reviewed sample. These tiny strata are evidence cases, not stable population estimates.

## Environment

Windows AMD64, 32 logical CPUs, 31.6 GiB memory, Python 3.12.13 and Node v22.20.0. Mock mode had no model identifier. PyTorch, Ultralytics and CUDA probing returned unavailable in the restricted runner, so real YOLO results are `not_run`. Configured YOLO values were `yolo26n.pt`, confidence 0.30, image size 640, max detections 30 and device `auto`.

## Failure cases and limitations

Nine reviewed rows are in `evaluation/manifests/failure_cases.csv`. The most material observed defect is `agent-unsupported-03`: asking for centimetres was routed to object count and returned four evidence cards, producing four unsupported-evidence counts. Other rows record near/overlap ambiguity, local-only ordinals, same-class identity limits, missing real/bbox datasets, low-light uncertainty and untested hardware.

No open P0/P1 defect blocks deterministic evaluation. Real detector accuracy, cold/warm YOLO latency, physical phone camera and real glasses remain unmeasured.

## Reproduce

```powershell
.\scripts\run-evaluation.ps1 -Module all -AnalyzerMode mock
.\scripts\run-evaluation.ps1 -Module memory -Json
.\scripts\run-evaluation.ps1 -Module agent -Json
.\scripts\run-evaluation.ps1 -Module detection -AnalyzerMode yolo
.\scripts\run-evaluation.ps1 -Module relation -AnalyzerMode yolo
```

Generated reports are ignored under `.runtime/evaluation/<run-id>/`. A YOLO run needs a permitted local manifest with real `asset_path` entries; otherwise detection and relation are truthfully `not_run`.
