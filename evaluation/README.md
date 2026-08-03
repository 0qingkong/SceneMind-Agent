# Reproducible evaluation harness

This directory contains source-controlled manifests, annotations and runners. Generated results stay under ignored `.runtime/evaluation/<run-id>`.

Run all deterministic modules from the repository root:

```powershell
.\scripts\run-evaluation.ps1 -Module all -AnalyzerMode mock
```

Use `-Module detection|relation|memory|agent|session`, `-AnalyzerMode mock|yolo`, and `-Json` for a machine-readable summary. Invalid manifests return non-zero.

## Asset policy

Only team-owned, explicitly permitted, synthetic, or suitably licensed public assets may be referenced. Committed manifests use relative paths or external asset keys; never add usernames, absolute paths, private identifiable photographs, model weights or runtime output. To evaluate local real images, add permitted relative `asset_path` entries in a local manifest and do not commit the images unless publication is authorized.

## Metric boundaries

- Mock results validate deterministic plumbing and must not be mixed with YOLO metrics.
- Detection mAP/recall/F1 require reviewed bbox ground truth, which is absent.
- Reviewed predicted relations support precision only unless valid relations are exhaustively annotated.
- P50/P95 values include sample count; cold and warm YOLO timings must be reported separately.

See [formal methodology](../docs/EVALUATION.md), [limitations](../docs/LIMITATIONS.md), and the CSV/JSONL templates in `templates/`.
