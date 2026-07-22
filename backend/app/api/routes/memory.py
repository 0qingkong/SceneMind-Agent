from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import Settings
from app.dependencies import get_memory_service, get_settings
from app.schemas.memory import HistoryResponse, LastSeenResponse
from app.services.memory_service import MemoryNotFoundError, MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/last-seen", response_model=LastSeenResponse)
def last_seen(
    service: Annotated[MemoryService, Depends(get_memory_service)],
    q: str = Query(min_length=1),
) -> LastSeenResponse:
    try:
        return service.last_seen(q)
    except (MemoryNotFoundError, ValueError) as exc:
        status_code = 404 if isinstance(exc, MemoryNotFoundError) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.get("/history", response_model=HistoryResponse)
def history(
    service: Annotated[MemoryService, Depends(get_memory_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    q: str = Query(min_length=1),
    limit: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
) -> HistoryResponse:
    resolved_limit = limit or settings.memory_history_default_limit
    if resolved_limit > settings.memory_history_max_limit:
        raise HTTPException(
            status_code=422,
            detail=f"limit cannot exceed {settings.memory_history_max_limit}",
        )
    try:
        return service.history(
            query=q,
            limit=resolved_limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
