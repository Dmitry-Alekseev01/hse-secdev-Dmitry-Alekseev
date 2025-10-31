import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    username: str | None = Field(
        None, min_length=2, max_length=50, pattern="^[a-zA-Zа-яА-ЯёЁ0-9_ ]+$"
    )
    email: EmailStr | None = None


class UserCreate(BaseModel):
    username: str = Field(
        ..., min_length=2, max_length=50, pattern="^[a-zA-Zа-яА-ЯёЁ0-9_ ]+$"
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    username: str | None = Field(
        None, min_length=2, max_length=50, pattern="^[a-zA-Zа-яА-ЯёЁ0-9_ ]+$"
    )
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
