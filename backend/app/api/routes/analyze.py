from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.analyze import AnalyzeResponse, DetectedObject

router = APIRouter(prefix="/analyze", tags=["analysis"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("", response_model=AnalyzeResponse)
async def analyze_scene(image: UploadFile = File(...)) -> AnalyzeResponse:
    started_at = perf_counter()

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="仅支持 JPG、PNG 和 WebP 图片。",
        )

    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空。")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="图片不能超过 10 MB。")

    # Day 1 使用 Mock 结果打通前后端。
    # Day 4 开始把这里替换为真实 DetectorService。
    objects = [
        DetectedObject(
            id="object-1",
            label="desk",
            display_name="书桌",
            confidence=0.94,
            bbox=[0.08, 0.46, 0.92, 0.93],
        ),
        DetectedObject(
            id="object-2",
            label="laptop",
            display_name="笔记本电脑",
            confidence=0.91,
            bbox=[0.30, 0.35, 0.67, 0.61],
        ),
        DetectedObject(
            id="object-3",
            label="cup",
            display_name="水杯",
            confidence=0.87,
            bbox=[0.72, 0.41, 0.83, 0.65],
        ),
    ]

    elapsed_ms = round((perf_counter() - started_at) * 1000, 2)

    return AnalyzeResponse(
        trace_id=str(uuid4()),
        engine="mock-day1",
        filename=image.filename or "unnamed-image",
        scene_summary="这是一个办公桌场景，桌面上有笔记本电脑和水杯。",
        objects=objects,
        latency_ms=elapsed_ms,
    )
