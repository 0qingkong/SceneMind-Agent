from __future__ import annotations

import argparse
from pathlib import Path

from evaluation.scripts.common import ROOT, environment, file_hash, write_json
from app.core.config import Settings


def capture(mode: str) -> dict[str, object]:
    settings = Settings(analyzer_mode=mode)
    payload = environment(mode, settings.yolo_model if mode == "yolo" else None)
    payload["config"] = {
        "confidence_threshold": settings.yolo_conf,
        "image_size": settings.yolo_imgsz,
        "max_detections": settings.yolo_max_det,
        "device_request": settings.yolo_device,
        "spatial_near_threshold": settings.spatial_near_threshold,
        "spatial_overlap_iou_threshold": settings.spatial_overlap_iou_threshold,
        "spatial_containment_threshold": settings.spatial_containment_threshold,
    }
    payload["manifest_hashes"] = {
        name: file_hash(ROOT / relative)
        for name, relative in {
            "scenes": "evaluation/manifests/scenes.example.jsonl",
            "relations": "evaluation/manifests/relation_annotations.example.csv",
            "memory": "evaluation/manifests/memory_queries.jsonl",
            "agent": "evaluation/manifests/agent_queries.jsonl",
            "sessions": "evaluation/manifests/session_sequences.example.jsonl",
        }.items()
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyzer-mode", choices=["mock", "yolo"], default="mock")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.output, capture(args.analyzer_mode))


if __name__ == "__main__":
    main()
