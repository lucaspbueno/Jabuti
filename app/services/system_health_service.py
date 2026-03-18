"""Serviço de status / healthcheck da aplicação (sem dependência de banco ou cache)."""

from app.core.config import Settings
from app.schemas.health import HealthStatusResponse


class SystemHealthService:
    """Expõe o estado de saúde reportado pela API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_status(self) -> HealthStatusResponse:
        """Retorna snapshot de saúde baseado apenas em configuração."""
        return HealthStatusResponse(
            status="healthy",
            app_name=self._settings.app_name,
            environment=self._settings.environment,
        )
