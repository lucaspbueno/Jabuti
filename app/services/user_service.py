"""Service da feature de usuário."""

import uuid

from app.exceptions import UserEmailAlreadyExistsError, UserNotFoundError
from app.models import User
from app.repositories import UserRepository
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate


class UserService:
    """Orquestra regras de negócio da feature de usuário."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponse:
        user = await self._get_existing_user(user_id)

        return self._to_response(user)

    async def list_users(self, *, limit: int, offset: int) -> UserListResponse:
        users = await self._repository.list_users(limit=limit, offset=offset)
        total = await self._repository.count()

        return UserListResponse(
            items=[self._to_response(user) for user in users],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def create_user(self, payload: UserCreate) -> UserResponse:
        email = str(payload.email)

        await self._ensure_email_is_available(email)

        user = await self._repository.create(
            name=payload.name,
            email=email,
            password=payload.password,
        )

        return self._to_response(user)

    async def update_user(
        self,
        user_id: uuid.UUID,
        payload: UserUpdate,
    ) -> UserResponse:
        user = await self._get_existing_user(user_id)
        email = str(payload.email) if payload.email is not None else None

        if email:
            await self._ensure_email_is_available_for_update(email, user_id)

        updated_user = await self._repository.update(
            user,
            name=payload.name,
            email=email,
            password=payload.password,
            active=payload.active,
        )

        return self._to_response(updated_user)

    async def delete_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self._get_existing_user(user_id)
        deleted_user = await self._repository.delete(user)

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
