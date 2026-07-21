from app.schemas.analyze import DetectedObject
from app.services.analyzers.base import AnalysisResult


class MockSceneAnalyzer:
    engine = "mock-v0.2"
    model_name = None

    @property
    def is_loaded(self) -> bool:
        return False

    @property
    def device(self) -> None:
        return None

    def analyze(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        image_width: int,
        image_height: int,
    ) -> AnalysisResult:
        objects = [
            DetectedObject(
                id="object-1",
                label="desk",
                display_name="书桌",
                confidence=0.94,
                bbox=[0.07, 0.48, 0.94, 0.94],
            ),
            DetectedObject(
                id="object-2",
                label="laptop",
                display_name="笔记本电脑",
                confidence=0.91,
                bbox=[0.28, 0.30, 0.69, 0.62],
            ),
            DetectedObject(
                id="object-3",
                label="cup",
                display_name="杯子",
                confidence=0.87,
                bbox=[0.72, 0.36, 0.86, 0.68],
            ),
        ]
        return AnalysisResult(
            scene_summary="当前为 Mock 分析：返回 3 个固定示例物体，不代表真实检测结果。",
            objects=objects,
        )
