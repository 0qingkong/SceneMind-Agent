from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from app.dependencies import get_capture_session_service
from app.schemas.capture import (
    CaptureSampleResponse,
    CaptureSessionCreate,
    CaptureSessionDetail,
    CaptureSessionListResponse,
)
from app.services.analysis_service import ImageValidationError
from app.services.analyzers import AnalyzerError
from app.services.capture_session_service import (
    CaptureSampleInProgressError,
    CaptureSessionNotFoundError,
    CaptureSessionService,
    CaptureSessionStateError,
)

router = APIRouter(prefix="/capture-sessions", tags=["capture-sessions"])


def _http_error(exc: Exception) -> None:
    if isinstance(exc, CaptureSessionNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, (CaptureSessionStateError, CaptureSampleInProgressError)):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if isinstance(exc, ImageValidationError):
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    if isinstance(exc, AnalyzerError):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise exc


@router.post("", response_model=CaptureSessionDetail, status_code=201)
def create_session(
    request: CaptureSessionCreate,
    service: Annotated[CaptureSessionService, Depends(get_capture_session_service)],
) -> CaptureSessionDetail:
    try:
        return service.create(request)
    except Exception as exc:
        _http_error(exc)
        raise


@router.get("", response_model=CaptureSessionListResponse)
def list_sessions(
    service: Annotated[CaptureSessionService, Depends(get_capture_session_service)],
) -> CaptureSessionListResponse:
    return service.list()


@router.get("/{session_id}", response_model=CaptureSessionDetail)
def get_session(
    session_id: str,
    service: Annotated[CaptureSessionService, Depends(get_capture_session_service)],
) -> CaptureSessionDetail:
    try:
        return service.detail(session_id)
    except Exception as exc:
        _http_error(exc)
        raise


@router.post("/{session_id}/samples", response_model=CaptureSampleResponse)
async def create_sample(
    session_id: str,
    service: Annotated[CaptureSessionService, Depends(get_capture_session_service)],
    file: UploadFile = File(...),
    force_save: bool = Form(default=False),
    captured_at: datetime | None = Form(default=None),
    source_device_id: str | None = Form(default=None),
    source_device_name: str | None = Form(default=None),
) -> CaptureSampleResponse:
    content = await file.read()
    try:
        return await run_in_threadpool(
            service.sample,
            session_id,
            image_bytes=content,
            filename=file.filename or "capture.jpg",
            content_type=file.content_type,
            force_save=force_save,
            captured_at=captured_at,
            source_device_id=source_device_id,
            source_device_name=source_device_name,
        )
    except Exception as exc:
        _http_error(exc)
        raise


@router.post("/{session_id}/stop", response_model=CaptureSessionDetail)
def stop_session(
    session_id: str,
    service: Annotated[CaptureSessionService, Depends(get_capture_session_service)],
) -> CaptureSessionDetail:
    try:
        return service.stop(session_id)
    except Exception as exc:
        _http_error(exc)
        raise


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    service: Annotated[CaptureSessionService, Depends(get_capture_session_service)],
) -> Response:
    try:
        service.delete(session_id)
    except Exception as exc:
        _http_error(exc)
    return Response(status_code=204)
