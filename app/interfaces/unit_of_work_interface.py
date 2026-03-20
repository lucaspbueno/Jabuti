"""Contrato da unidade de trabalho."""

from typing import Protocol


class UnitOfWorkInterface(Protocol):
    """Contrato mínimo esperado para confirmar transações."""

    async def commit(self) -> None: ...
