import pytest

from app.core.config import Settings
from app.services.analyzers.factory import create_analyzer
from app.services.analyzers.mock import MockSceneAnalyzer
from app.services.analyzers.yolo import YoloSceneAnalyzer


def test_factory_selects_mock() -> None:
    analyzer = create_analyzer(Settings(analyzer_mode="mock"))
    assert isinstance(analyzer, MockSceneAnalyzer)


def test_factory_selects_lazy_yolo() -> None:
    analyzer = create_analyzer(Settings(analyzer_mode="yolo"))
    assert isinstance(analyzer, YoloSceneAnalyzer)
    assert analyzer.model_name == "yolo26n.pt"
    assert analyzer.is_loaded is False


def test_factory_rejects_unsupported_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported ANALYZER_MODE"):
        create_analyzer(Settings(analyzer_mode="unknown"))
