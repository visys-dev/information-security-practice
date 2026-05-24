from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re

from app.validators.sanitizer import contains_html, contains_sql_patterns, sanitize_text


# ── Схеми для реєстрації ──


class UserCreate(BaseModel):
    """Схема реєстрації з суворою валідацією."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Логін: 3-30 символів, лише латиниця, цифри, підкреслення",
    )
    email: EmailStr
    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        pattern=r"^\+?[0-9\s().-]+$",
        description="Телефон: цифри, пробіли, +, -, дужки",
    )
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if contains_sql_patterns(v):
            raise ValueError("Логін містить підозрілі SQL-патерни")
        return v

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

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if contains_sql_patterns(v):
            raise ValueError("Телефон містить підозрілі SQL-патерни")
        return v.strip()

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if contains_html(v):
            raise ValueError("Ім’я не може містити HTML-теги")
        if re.search(r"[<>&\"']", v):
            raise ValueError("Ім’я не може містити < > & \" '")
        if contains_sql_patterns(v):
            raise ValueError("Ім’я містить підозрілі SQL-патерни")
        return sanitize_text(v)


class UserResponse(BaseModel):
    """Схема відповіді (без пароля)."""

    id: int
    username: str
    email: str
    phone: str | None = None
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Схеми для входу ──


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_login_username(cls, v: str) -> str:
        if contains_sql_patterns(v):
            raise ValueError("Логін містить підозрілі SQL-патерни")
        return v


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
    refresh_token: str = Field(..., min_length=20, max_length=4096)


class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    phone: str | None = None
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if contains_html(v):
            raise ValueError("Коментар не може містити HTML-теги")
        return sanitize_text(v)


class CommentResponse(BaseModel):
    text: str
