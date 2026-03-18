"""Exceções de domínio e mapeamento HTTP."""

from app.exceptions.user import (
    UserDomainError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)

__all__ = [
    "UserDomainError",
    "UserEmailAlreadyExistsError",
    "UserNotFoundError",
]
