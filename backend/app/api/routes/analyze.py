from __future__ import annotations

from io import BytesIO
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.schemas.analyze import AnalyzeResponse
from app.services.analyzers import MockSceneAnalyzer

router = APIRouter(prefix="/analyze", tags=["analysis"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024
analyzer = MockSceneAnalyzer()


def read_image_size(content: bytes) -> tuple[int, int]:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
        with Image.open(BytesIO(content)) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail="文件内容不是有效图片或图片已经损坏。",
        ) from exc

    if width <= 0 or height <= 0:
        raise HTTPException(status_code=400, detail="无法读取图片尺寸。")

    return width, height


@router.post("", response_model=AnalyzeResponse)
async def analyze_scene(image: UploadFile = File(...)) -> AnalyzeResponse:
    started_at = perf_counter()

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="仅支持 JPG、PNG 和 WebP 图片。")

    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空。")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="图片不能超过 10 MB。")

    image_width, image_height = read_image_size(content)
    filename = image.filename or "unnamed-image"

    analysis = analyzer.analyze(
        image_bytes=content,
        filename=filename,
        image_width=image_width,
        image_height=image_height,
    )

    return AnalyzeResponse(
        trace_id=str(uuid4()),
        engine=analyzer.engine,
        filename=filename,
        image_width=image_width,
        image_height=image_height,
        scene_summary=analysis.scene_summary,
        objects=analysis.objects,
        latency_ms=round((perf_counter() - started_at) * 1000, 2),
    )
