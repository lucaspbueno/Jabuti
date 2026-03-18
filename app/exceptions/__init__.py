"""Exceções de domínio e mapeamento HTTP."""

from app.exceptions.base import AppError
from app.exceptions.handlers import register_exception_handlers
from app.exceptions.user import (
    UserDomainError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)

__all__ = [
    "AppError",
    "UserDomainError",
    "UserEmailAlreadyExistsError",
    "UserNotFoundError",
    "register_exception_handlers",
]
