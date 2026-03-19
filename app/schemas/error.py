"""Schemas de resposta de erro da aplicação."""

from pydantic import BaseModel
from pydantic_core import ErrorDetails


class ErrorContent(BaseModel):
    """Conteúdo padronizado de erro."""

    code: str
    message: str
    details: list[ErrorDetails] | None = None


class ErrorResponse(BaseModel):
    """Envelope padrão de erro da API."""

    error: ErrorContent
