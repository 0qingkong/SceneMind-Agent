from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from app.core.config import Settings
from app.dependencies import get_observation_service, get_settings
from app.schemas.observation import ObservationDetail, ObservationListResponse
from app.services.analysis_service import ImageValidationError
from app.services.analyzers import AnalyzerError
from app.services.image_storage import ImageStorageError
from app.services.observation_service import (
    ObservationNotFoundError,
    ObservationPersistenceError,
    ObservationService,
)

router = APIRouter(prefix="/observations", tags=["observations"])


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, ImageValidationError):
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    if isinstance(exc, ObservationNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, AnalyzerError):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(exc, (ImageStorageError, ObservationPersistenceError)):
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    raise exc


@router.post("", response_model=ObservationDetail, status_code=201)
async def create_observation(
    service: Annotated[ObservationService, Depends(get_observation_service)],
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    location: str | None = Form(default=None),
) -> ObservationDetail:
    content = await file.read()
    try:
        return await run_in_threadpool(
            service.create,
            image_bytes=content,
            filename=file.filename or "unnamed-image",
            content_type=file.content_type,
            title=title,
            location=location,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get("", response_model=ObservationListResponse)
def list_observations(
    service: Annotated[ObservationService, Depends(get_observation_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    limit: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
    label: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> ObservationListResponse:
    resolved_limit = limit or settings.observation_default_limit
    if resolved_limit > settings.observation_max_limit:
        raise HTTPException(
            status_code=422,
            detail=f"limit cannot exceed {settings.observation_max_limit}",
        )
    return service.list(
        limit=resolved_limit,
        offset=offset,
        label=label,
        query=q,
    )


@router.get("/{observation_id}", response_model=ObservationDetail)
def get_observation(
    observation_id: str,
    service: Annotated[ObservationService, Depends(get_observation_service)],
) -> ObservationDetail:
    try:
        return service.detail(observation_id)
    except ObservationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{observation_id}/image", response_class=FileResponse)
def get_observation_image(
    observation_id: str,
    service: Annotated[ObservationService, Depends(get_observation_service)],
) -> FileResponse:
    try:
        path, mime_type = service.image(observation_id)
    except (ObservationNotFoundError, ImageStorageError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type=mime_type)


@router.delete("/{observation_id}", status_code=204)
def delete_observation(
    observation_id: str,
    service: Annotated[ObservationService, Depends(get_observation_service)],
) -> Response:
    try:
        service.delete(observation_id)
    except Exception as exc:
        _raise_http_error(exc)
    return Response(status_code=204)
