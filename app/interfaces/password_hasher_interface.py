"""Contrato de hashing de senha."""

from typing import Protocol


class PasswordHasherInterface(Protocol):
    """Contrato mínimo esperado para hash de senha."""

    def hash_password(self, plain_password: str) -> str: ...
