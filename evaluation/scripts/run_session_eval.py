from __future__ import annotations

import argparse
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from evaluation.scripts.common import ROOT, file_hash, read_jsonl, write_json
from app.core.config import Settings
from app.db import Database
from app.schemas.analyze import DetectedObject
from app.schemas.capture import CaptureSessionCreate
from app.services.analysis_service import AnalysisService
from app.services.analyzers import AnalysisResult
from app.services.capture_session_service import CaptureSessionService
from app.services.image_storage import ImageStorage
from app.services.spatial import SpatialReasoner


class SequenceAnalyzer:
    engine, model_name, is_loaded, device = "fake-session-eval", "fake", True, "cpu"

    def __init__(self) -> None:
        self.labels: list[str] = []

    def analyze(self, **_: object) -> AnalysisResult:
        return AnalysisResult(
            scene_summary=f"Detected {len(self.labels)} objects",
            objects=[DetectedObject(id=f"{label}-{index}", label=label, display_name=label, confidence=0.9, bbox=[0.05 + index * 0.2, 0.2, 0.18 + index * 0.2, 0.7]) for index, label in enumerate(self.labels)],
        )


def _image() -> bytes:
    stream = BytesIO()
    Image.new("RGB", (320, 240), "white").save(stream, "JPEG")
    return stream.getvalue()


def run(cases_path: Path, output: Path) -> dict[str, object]:
    sequences = read_jsonl(cases_path)
    results = []
    with tempfile.TemporaryDirectory(prefix="scenemind-session-eval-") as temporary:
        root = Path(temporary)
        database = Database(f"sqlite:///{root / 'session.db'}")
        database.create_tables()
        storage = ImageStorage(root / "images")
        analyzer = SequenceAnalyzer()
        settings = Settings(capture_min_save_gap_seconds=3600)
        with database.session_factory() as session:
            service = CaptureSessionService(session, AnalysisService(analyzer, SpatialReasoner()), storage, settings)
            for sequence in sequences:
                created = service.create(CaptureSessionCreate(source_type="evaluation", sample_interval_seconds=5, target_query=sequence.get("target_query"), auto_save_mode=sequence["mode"]))
                for index, frame in enumerate(sequence["frames"]):
                    analyzer.labels = frame["labels"]
                    result = service.sample(created.id, image_bytes=_image(), filename=f"frame-{index}.jpg", content_type="image/jpeg", force_save=frame["force"], captured_at=None, source_device_id="evaluation", source_device_name="Evaluation Sequence")
                    results.append({"sequence_id": sequence["sequence_id"], "frame": index, "expected_saved": frame["expected_saved"], "actual_saved": result.saved, "expected_reason": frame["expected_reason"], "actual_reason": result.reason, "passed": result.saved == frame["expected_saved"] and result.reason == frame["expected_reason"]})
                service.stop(created.id)
        database.engine.dispose()
    count = len(results)
    saved = sum(item["actual_saved"] for item in results)
    payload = {
        "module": "session", "status": "complete" if count else "not_run", "frame_count": count,
        "decision_accuracy": sum(item["passed"] for item in results) / count if count else None,
        "sampled_to_saved_ratio": saved / count if count else None,
        "invalid_state_rejection": "covered_by_day14", "sequence_set_sha256": file_hash(cases_path), "results": results,
    }
    write_json(output, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation/manifests/session_sequences.example.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(args.cases, args.output)
    print(f"session: {payload['decision_accuracy']:.1%} ({payload['frame_count']} frames)")


if __name__ == "__main__":
    main()
