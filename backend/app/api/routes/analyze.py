from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.dependencies import get_analysis_service
from app.schemas.analyze import AnalyzeResponse
from app.services.analysis_service import AnalysisService, ImageValidationError
from app.services.analyzers import AnalyzerError

router = APIRouter(prefix="/analyze", tags=["analysis"])

@router.post("", response_model=AnalyzeResponse)
async def analyze_scene(
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
    image: UploadFile = File(...),
) -> AnalyzeResponse:
    content = await image.read()
    filename = image.filename or "unnamed-image"
    try:
        return await run_in_threadpool(
            service.analyze,
            image_bytes=content,
            filename=filename,
            content_type=image.content_type,
        )
    except ImageValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except AnalyzerError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
