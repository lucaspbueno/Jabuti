"""Testes dos schemas Pydantic da feature de usuário."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.constants import UserConstraints
from app.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate


def test_user_create_accepts_valid_payload() -> None:
    schema = UserCreate(
        name="Lucas",
        email="lucas@example.com",
        password="a" * UserConstraints.PASSWORD_MIN_LENGTH,
    )

    assert schema.name == "Lucas"
    assert schema.email == "lucas@example.com"


def test_user_create_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            name="Lucas",
            email="email-invalido",
            password="a" * UserConstraints.PASSWORD_MIN_LENGTH,
        )


def test_user_create_rejects_password_shorter_than_minimum() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            name="Lucas",
            email="lucas@example.com",
            password="a" * (UserConstraints.PASSWORD_MIN_LENGTH - 1),
        )


def test_user_update_accepts_partial_payload() -> None:
    schema = UserUpdate(name="Novo nome")

    assert schema.name == "Novo nome"
    assert schema.email is None
    assert schema.password is None
    assert schema.active is None


def test_user_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError):
        UserUpdate()


def test_user_response_reads_from_orm_object() -> None:
    now = datetime.now(UTC)
    user = User(
        id=uuid.uuid4(),
        name="Lucas",
        email="lucas@example.com",
        password="hashed-password",
        active=True,
        created_at=now,
        updated_at=now,
    )

    response = UserResponse.model_validate(user)

    assert response.id == user.id
    assert response.name == user.name
    assert response.email == user.email
    assert response.active is True
    assert response.created_at == now
    assert response.updated_at == now


def test_user_response_does_not_expose_password() -> None:
    assert "password" not in UserResponse.model_fields
