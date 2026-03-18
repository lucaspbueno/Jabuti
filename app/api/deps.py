"""Dependências injetáveis nas rotas FastAPI."""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.system_health_service import SystemHealthService


def get_system_health_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SystemHealthService:
    return SystemHealthService(settings)
