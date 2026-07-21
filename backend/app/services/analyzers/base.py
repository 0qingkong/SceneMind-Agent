from dataclasses import dataclass
from typing import Protocol

from app.schemas.analyze import DetectedObject


@dataclass(slots=True)
class AnalysisResult:
    scene_summary: str
    objects: list[DetectedObject]


class AnalyzerError(RuntimeError):
    """Raised when a configured analyzer cannot complete real inference."""


class SceneAnalyzer(Protocol):
    engine: str
    model_name: str | None

    @property
    def is_loaded(self) -> bool:
        ...

    @property
    def device(self) -> str | None:
        ...

    def analyze(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        image_width: int,
        image_height: int,
    ) -> AnalysisResult:
        ...
