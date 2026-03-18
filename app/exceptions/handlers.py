"""Handlers globais de exceções da aplicação."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic_core import ErrorDetails
from starlette.exceptions import HTTPException

from app.exceptions.base import AppError
from app.schemas.error import ErrorContent, ErrorResponse


RequestExceptionHandler = Callable[[Request, Exception], Awaitable[JSONResponse]]


def _build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetails] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorContent(
            code=code,
            message=message,
            details=details,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
    )


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """Traduz exceções da aplicação em resposta HTTP padronizada."""

    return _build_error_response(
        status_code=exc.status_code,
        code=exc.error_code,
        message=exc.message,
    )


async def validation_error_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Padroniza erros de validação de entrada."""

    return _build_error_response(
        status_code=422,
        code="validation_error",
        message="Erro de validação na requisição.",
        details=list( exc.errors()),
    )


async def http_exception_handler(
    _: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Padroniza exceções HTTP geradas pelo FastAPI/Starlette."""

    return _build_error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
    )


async def unexpected_exception_handler(_: Request, __: Exception) -> JSONResponse:
    """Evita expor detalhes internos em erros inesperados."""

    return _build_error_response(
        status_code=500,
        code="internal_server_error",
        message="Ocorreu um erro interno na aplicação.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos os handlers globais da aplicação."""

    app.add_exception_handler(
        AppError,
        cast(RequestExceptionHandler, app_error_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(RequestExceptionHandler, validation_error_handler),
    )
    app.add_exception_handler(
        HTTPException,
        cast(RequestExceptionHandler, http_exception_handler),
    )
    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )
