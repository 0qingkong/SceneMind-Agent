from dataclasses import dataclass
from typing import Protocol

from app.schemas.analyze import DetectedObject


@dataclass(slots=True)
class AnalysisResult:
    scene_summary: str
    objects: list[DetectedObject]


class SceneAnalyzer(Protocol):
    engine: str

    def analyze(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        image_width: int,
        image_height: int,
    ) -> AnalysisResult:
        ...
