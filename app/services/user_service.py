"""Service da feature de usuário."""

import logging
import uuid

from app.cache import CacheKeys, CacheService
from app.db import UnitOfWork
from app.exceptions import UserEmailAlreadyExistsError, UserNotFoundError
from app.models import User
from app.repositories import UserRepository
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.security import PasswordHasher

logger = logging.getLogger(__name__)


class UserService:
    """Orquestra regras de negócio da feature de usuário."""

    def __init__(
        self,
        repository: UserRepository,
        unit_of_work: UnitOfWork,
        cache_service: CacheService,
        password_hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work
        self._cache_service = cache_service
        self._password_hasher = password_hasher

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponse:
        cached_response = await self._get_cached_user_detail(user_id)

        if cached_response is not None:
            return cached_response

        user = await self._get_existing_user(user_id)
        response = self._to_response(user)

        await self._set_user_detail_cache(response)

        return response

    async def list_users(self, *, limit: int, offset: int) -> UserListResponse:
        cached_response = await self._get_cached_user_list(limit=limit, offset=offset)
        if cached_response is not None:
            return cached_response

        users = await self._repository.list_users(limit=limit, offset=offset)
        total = await self._repository.count()

        response = UserListResponse(
            items=[self._to_response(user) for user in users],
            total=total,
            limit=limit,
            offset=offset,
        )
        await self._set_user_list_cache(response)

        return response

    async def create_user(self, payload: UserCreate) -> UserResponse:
        email = str(payload.email)
        hashed_password = self._password_hasher.hash_password(payload.password)

        await self._ensure_email_is_available(email)

        user = await self._repository.create(
            name=payload.name,
            email=email,
            password=hashed_password,
        )

        response = self._to_response(user)
        await self._unit_of_work.commit()
        await self._delete_user_list_cache()

        return response

    async def update_user(
        self,
        user_id: uuid.UUID,
        payload: UserUpdate,
    ) -> UserResponse:
        user = await self._get_existing_user(user_id)
        email = str(payload.email) if payload.email is not None else None
        password = payload.password

        if email:
            await self._ensure_email_is_available_for_update(email, user_id)

        if password:
            password = self._password_hasher.hash_password(password)

        updated_user = await self._repository.update(
            user,
            name=payload.name,
            email=email,
            password=password,
            active=payload.active,
        )
        await self._unit_of_work.commit()
        await self._delete_user_detail_cache(user_id)
        await self._delete_user_list_cache()

        return self._to_response(updated_user)

    async def delete_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self._get_existing_user(user_id)
        deleted_user = await self._repository.delete(user)

        await self._unit_of_work.commit()
        await self._delete_user_detail_cache(user_id)
        await self._delete_user_list_cache()

        return self._to_response(deleted_user)

    async def _get_existing_user(self, user_id: uuid.UUID) -> User:
        user = await self._repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError(user_id)

        return user

    async def _ensure_email_is_available(self, email: str) -> None:
        existing_user = await self._repository.get_by_email(email)

        if existing_user is not None:
            raise UserEmailAlreadyExistsError(email)

    async def _ensure_email_is_available_for_update(
        self,
        email: str,
        user_id: uuid.UUID,
    ) -> None:
        existing_user = await self._repository.get_by_email(email)

        if existing_user and existing_user.id != user_id:
            raise UserEmailAlreadyExistsError(email)

    @staticmethod
    def _to_response(user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def _get_cached_user_detail(self, user_id: uuid.UUID) -> UserResponse | None:
        payload = await self._cache_service.get_json(CacheKeys.user_detail(user_id))

        if payload is None:
            return None

        return UserResponse.model_validate(payload)

    async def _get_cached_user_list(self, *, limit: int, offset: int) -> UserListResponse | None:
        payload = await self._cache_service.get_json(CacheKeys.users_list(limit, offset))

        if payload is None:
            return None

        return UserListResponse.model_validate(payload)

    async def _set_user_detail_cache(self, response: UserResponse) -> None:
        key = CacheKeys.user_detail(response.id)
        payload = response.model_dump(mode="json")

        await self._cache_service.set_json(key, payload)

    async def _set_user_list_cache(self, response: UserListResponse) -> None:
        key = CacheKeys.users_list(response.limit, response.offset)
        payload = response.model_dump(mode="json")

        await self._cache_service.set_json(key, payload)

    async def _delete_user_detail_cache(self, user_id: uuid.UUID) -> None:
        try:
            await self._cache_service.delete(CacheKeys.user_detail(user_id))
        except Exception:
            logger.exception(
                "Falha ao invalidar cache de detalhe do usuário após commit.",
                extra={"user_id": str(user_id)},
            )

    async def _delete_user_list_cache(self) -> None:
        try:
            await self._cache_service.delete_by_prefix(CacheKeys.users_list_prefix())
        except Exception:
            logger.exception("Falha ao invalidar cache de listagem de usuários após commit.")
