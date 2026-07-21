from app.core.config import Settings
from app.services.analyzers.base import SceneAnalyzer
from app.services.analyzers.mock import MockSceneAnalyzer
from app.services.analyzers.yolo import YoloSceneAnalyzer


def create_analyzer(settings: Settings) -> SceneAnalyzer:
    if settings.analyzer_mode == "mock":
        return MockSceneAnalyzer()
    if settings.analyzer_mode == "yolo":
        return YoloSceneAnalyzer(settings)
    raise ValueError(
        f"Unsupported ANALYZER_MODE {settings.analyzer_mode!r}; expected 'yolo' or 'mock'"
    )
