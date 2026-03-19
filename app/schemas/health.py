"""Schemas HTTP relacionados a healthcheck."""

from pydantic import BaseModel, Field


class HealthStatusResponse(BaseModel):
    """Resposta do endpoint de saúde da API."""

    status: str = Field(default="healthy", description="Estado geral da aplicação")
    app_name: str = Field(description="Nome configurado da aplicação")
    environment: str = Field(description="Ambiente de execução")
