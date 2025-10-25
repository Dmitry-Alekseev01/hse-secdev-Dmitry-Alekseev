import re

from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import engine, get_db
from .errors import RFC7807Error, setup_exception_handlers
from .models import Base, User
from .security_headers import SecurityHeadersMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecDev Course App", version="0.1.0")
app.add_middleware(SecurityHeadersMiddleware)
setup_exception_handlers(app)


class UserCreate(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=50, pattern="^[a-zA-Zа-яА-ЯёЁ0-9_ ]+$"
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
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
    name: str | None = Field(
        None, min_length=2, max_length=50, pattern="^[a-zA-Zа-яА-ЯёЁ0-9_ ]+$"
    )
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
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


@app.get("/users")
async def get_users(request: Request, db: Session = Depends(get_db)):
    return db.query(User).all()


@app.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(or_(User.username == user_data.name, User.email == user_data.email))
        .first()
    )
    if user:
        raise RFC7807Error(
            status=400, title="existing user", detail="Такой пользователь уже есть"
        )
    user = User(
        username=user_data.name, email=user_data.email, password=user_data.password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise RFC7807Error(
            status=404, title="non existing user", detail="Такого пользователя нет"
        )
    return user


@app.delete("/users/{user_id}")
async def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise RFC7807Error(
            status=404, title="non existing user", detail="Такого пользователя нет"
        )
    db.delete(user)
    db.commit()
    return user


@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    if user_data.email or user_data.name:
        user = (
            db.query(User)
            .filter(or_(User.email == user_data.email, User.username == user_data.name))
            .first()
        )
        if user:
            raise RFC7807Error(
                status=400, title="existing user", detail="Такой пользователь уже есть"
            )

    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise RFC7807Error(
            status=404, title="non existing user", detail="Такого пользователя нет"
        )

    if user_data.name is not None:
        user_db.username = user_data.name
    if user_data.email is not None:
        user_db.email = user_data.email
    if user_data.password is not None:
        user_db.password = user_data.password

    db.commit()
    db.refresh(user_db)
    return user_db


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}
