"""Rotas CRUD da feature de usuário."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import UserDependencies
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(UserDependencies.get_service)],
) -> UserResponse:
    return await service.create_user(payload)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(UserDependencies.get_service)],
) -> UserResponse:
    return await service.get_user_by_id(user_id)


@router.get("", response_model=UserListResponse)
async def list_users(
    service: Annotated[UserService, Depends(UserDependencies.get_service)],
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> UserListResponse:
    return await service.list_users(limit=limit, offset=offset)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(UserDependencies.get_service)],
) -> UserResponse:
    return await service.update_user(user_id, payload)


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(UserDependencies.get_service)],
) -> UserResponse:
    return await service.delete_user(user_id)
