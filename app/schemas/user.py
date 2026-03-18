"""Schemas Pydantic da feature de usuário."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.constants import UserConstraints


class UserBase(BaseModel):
    """Campos compartilhados da entidade de usuário."""

    name: str = Field(
        min_length=UserConstraints.NAME_MIN_LENGTH,
        max_length=UserConstraints.NAME_MAX_LENGTH,
    )
    email: EmailStr


class UserCreate(UserBase):
    """Payload para criação de usuário."""

    password: str = Field(
        min_length=UserConstraints.PASSWORD_MIN_LENGTH,
        max_length=UserConstraints.PASSWORD_MAX_LENGTH,
    )


class UserUpdate(BaseModel):
    """Payload para atualização parcial de usuário."""

    name: str | None = Field(
        default=None,
        min_length=UserConstraints.NAME_MIN_LENGTH,
        max_length=UserConstraints.NAME_MAX_LENGTH,
    )
    email: EmailStr | None = None
    password: str | None = Field(
        default=None,
        min_length=UserConstraints.PASSWORD_MIN_LENGTH,
        max_length=UserConstraints.PASSWORD_MAX_LENGTH,
    )
    active: bool | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> UserUpdate:
        fields = (self.name, self.email, self.password, self.active)

        if all(field is None for field in fields):
            raise ValueError("Pelo menos um campo deve ser informado para atualização.")

        return self

class UserResponse(BaseModel):
    """Resposta pública da entidade de usuário."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    active: bool
    created_at: datetime
    updated_at: datetime
