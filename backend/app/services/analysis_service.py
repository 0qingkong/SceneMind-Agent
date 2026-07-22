from __future__ import annotations

from io import BytesIO
from time import perf_counter
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from app.schemas.analyze import AnalyzeResponse
from app.services.analyzers import SceneAnalyzer
from app.services.spatial import SpatialReasoner

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


class ImageValidationError(ValueError):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


class AnalysisService:
    def __init__(
        self,
        analyzer: SceneAnalyzer,
        spatial_reasoner: SpatialReasoner,
    ) -> None:
        self.analyzer = analyzer
        self.spatial_reasoner = spatial_reasoner

    def analyze(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        content_type: str | None,
    ) -> AnalyzeResponse:
        started_at = perf_counter()
        image_width, image_height = self.validate_image(image_bytes, content_type)
        analysis = self.analyzer.analyze(
            image_bytes=image_bytes,
            filename=filename,
            image_width=image_width,
            image_height=image_height,
        )
        relations = self.spatial_reasoner.reason(analysis.objects)
        return AnalyzeResponse(
            trace_id=str(uuid4()),
            engine=self.analyzer.engine,
            filename=filename,
            image_width=image_width,
            image_height=image_height,
            scene_summary=analysis.scene_summary,
            objects=analysis.objects,
            relations=relations,
            latency_ms=round((perf_counter() - started_at) * 1000, 2),
        )

    @staticmethod
    def validate_image(
        image_bytes: bytes,
        content_type: str | None,
    ) -> tuple[int, int]:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ImageValidationError(415, "仅支持 JPG、PNG 和 WebP 图片。")
        if not image_bytes:
            raise ImageValidationError(400, "上传文件为空。")
        if len(image_bytes) > MAX_FILE_SIZE:
            raise ImageValidationError(413, "图片不能超过 10 MB。")
        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image.verify()
            with Image.open(BytesIO(image_bytes)) as image:
                width, height = image.size
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ImageValidationError(
                400, "文件内容不是有效图片或图片已经损坏。"
            ) from exc
        if width <= 0 or height <= 0:
            raise ImageValidationError(400, "无法读取图片尺寸。")
        return width, height
