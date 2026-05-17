from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re


# ── Схеми для реєстрації ──


class UserCreate(BaseModel):
    """Схема запиту на реєстрацію нового користувача."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=150)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Перевірка складності пароля."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль має містити хоча б одну велику літеру")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль має містити хоча б одну малу літеру")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль має містити хоча б одну цифру")
        return v


class UserResponse(BaseModel):
    """Схема відповіді (без пароля)."""

    id: int
    username: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Схеми для входу ──


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str
    roles: list[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str

    model_config = {"from_attributes": True}
