"""Rota de healthcheck."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_system_health_service
from app.schemas.health import HealthStatusResponse
from app.services.system_health_service import SystemHealthService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatusResponse)
async def health(
    service: Annotated[SystemHealthService, Depends(get_system_health_service)],
) -> HealthStatusResponse:
    return await service.get_status()
