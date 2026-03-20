"""Contrato do serviço de cache."""

from typing import Protocol


class CacheServiceInterface(Protocol):
    """Contrato mínimo esperado para operações de cache."""

    async def get_json(self, key: str) -> dict[str, object] | None: ...

    async def set_json(
        self,
        key: str,
        value: dict[str, object],
        *,
        ttl_seconds: int | None = None,
    ) -> None: ...

    async def delete(self, key: str) -> int: ...

    async def delete_by_prefix(self, prefix: str) -> int: ...
