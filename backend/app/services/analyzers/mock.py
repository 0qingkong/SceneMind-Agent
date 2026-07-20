from app.schemas.analyze import DetectedObject
from app.services.analyzers.base import AnalysisResult


class MockSceneAnalyzer:
    engine = "mock-v0.2"

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
                display_name="水杯",
                confidence=0.87,
                bbox=[0.72, 0.36, 0.86, 0.68],
            ),
        ]
        return AnalysisResult(
            scene_summary=(
                "当前为 Day 2 Mock 分析：系统已读取真实图片尺寸，"
                "并使用统一数据结构返回物体与归一化边界框。"
            ),
            objects=objects,
        )
