from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from time import perf_counter

from PIL import Image

from evaluation.scripts.common import ROOT, environment, file_hash, latency_summary, read_jsonl, write_json
from app.core.config import Settings
from app.services.analysis_service import AnalysisService
from app.services.analyzers import create_analyzer
from app.services.spatial import SpatialReasoner


def run(mode: str, manifest: Path, output: Path) -> dict[str, object]:
    rows = read_jsonl(manifest)
    settings = Settings(analyzer_mode=mode)
    analyzer = create_analyzer(settings)
    service = AnalysisService(analyzer, SpatialReasoner.from_settings(settings))
    results = []
    for index, row in enumerate(rows):
        asset_path = row.get("asset_path")
        if mode == "yolo" and not asset_path:
            continue
        if asset_path:
            image_bytes = (ROOT / asset_path).read_bytes()
            filename = Path(asset_path).name
        else:
            stream = BytesIO()
            Image.new("RGB", (640, 480), (230 - index * 10, 235, 240)).save(stream, "PNG")
            image_bytes, filename = stream.getvalue(), f"synthetic-{index}.png"
        started = perf_counter()
        try:
            result = service.analyze(image_bytes=image_bytes, filename=filename, content_type="image/png")
            results.append({"sample_id": row["sample_id"], "success": True, "detections": len(result.objects), "labels": sorted({item.label for item in result.objects}), "latency_ms": round((perf_counter() - started) * 1000, 3), "error": None})
        except Exception as exc:
            results.append({"sample_id": row["sample_id"], "success": False, "detections": 0, "labels": [], "latency_ms": round((perf_counter() - started) * 1000, 3), "error": type(exc).__name__})
    success = [item for item in results if item["success"]]
    payload = {
        "module": "detection",
        "status": "complete" if results else "not_run",
        "analyzer_mode": mode,
        "ground_truth": "none",
        "invalid_metrics": ["mAP", "recall", "F1"],
        "sample_count": len(results),
        "processing_success_rate": len(success) / len(results) if results else None,
        "non_empty_rate": sum(item["detections"] > 0 for item in results) / len(results) if results else None,
        "average_detections": sum(item["detections"] for item in results) / len(results) if results else None,
        "category_coverage": sorted({label for item in success for label in item["labels"]}),
        "latency": latency_summary(item["latency_ms"] for item in results),
        "manifest_sha256": file_hash(manifest),
        "environment": environment(mode, analyzer.model_name),
        "results": results,
    }
    write_json(output, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyzer-mode", choices=["mock", "yolo"], default="mock")
    parser.add_argument("--manifest", type=Path, default=ROOT / "evaluation/manifests/scenes.example.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(args.analyzer_mode, args.manifest, args.output)
    print(f"detection: {payload['status']} ({payload['sample_count']} samples)")


if __name__ == "__main__":
    main()
