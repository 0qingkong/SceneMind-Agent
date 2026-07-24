from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_dashboard_service
from app.schemas.dashboard import DataExportResponse, DeviceStatsResponse, InsightsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["dashboard"])


@router.get("/devices/stats", response_model=DeviceStatsResponse)
def device_stats(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DeviceStatsResponse:
    return service.device_stats()


@router.get("/insights", response_model=InsightsResponse)
def insights(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> InsightsResponse:
    return service.insights()


@router.get("/privacy/export", response_model=DataExportResponse)
def export_data(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DataExportResponse:
    return service.export()
