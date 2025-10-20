# from fastapi import Depends, FastAPI, Request
# from fastapi.responses import JSONResponse
# from sqlalchemy import or_
# from sqlalchemy.orm import Session

# from .database import engine, get_db
# from .models import Base, User
# from .errors import RFC7807Error, setup_exception_handlers


# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="SecDev Course App", version="0.1.0")

# setup_exception_handlers(app)

# class ApiError(Exception):
#     def __init__(self, code: str, message: str, status: int = 400):
#         self.code = code
#         self.message = message
#         self.status = status

# @app.get("/users")
# async def get_users(request: Request, db: Session = Depends(get_db)):
#     return db.query(User).all()

# @app.post("/users")
# async def create_user(
#     request: Request,
#     name: str,
#     email: str,
#     password: str,
#     db: Session = Depends(get_db)
# ):
#     print(f"Received: name={name}, email={email}, password={password}")
#     user = (
#         db.query(User).filter(or_(User.username == name, User.email == email)).first()
#     )
#     if user:
#         raise RFC7807Error(
#             status=400,
#             title="existing user",
#             detail="Такой пользователь уже есть"
#         )
#     user = User(username=name, email=email, password=password)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user

# @app.get("/users/{user_id}")
# async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise RFC7807Error(
#             status=404,
#             title="non existing user",
#             detail="Такого пользователя нет"
#         )
#     return user

# @app.delete("/users/{user_id}")
# async def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise RFC7807Error(
#             status=404,
#             title="non existing user",
#             detail="Такого пользователя нет"
#         )
#     db.delete(user)
#     db.commit()
#     return user

# @app.put("/users/{user_id}")
# async def update_user(
#     user_id: int,
#     db: Session = Depends(get_db),
#     name: str = None,
#     email: str = None,
#     password: str = None,
# ):
#     if email or name:
#         user = db.query(User).filter(or_(User.email == email, User.username == name)).first()
#         if user:
#             raise RFC7807Error(
#                 status=400,
#                 title="existing user",
#                 detail="Такой пользователь уже есть"
#             )

#     user_db = db.query(User).filter(User.id == user_id).first()
#     if not user_db:
#         raise RFC7807Error(
#             status=404,
#             title="non existing user",
#             detail="Такого пользователя нет"
#         )

#     if name is not None:
#         user_db.username = name
#     if email is not None:
#         user_db.email = email
#     if password is not None:
#         user_db.password = password

#     db.commit()
#     db.refresh(user_db)
#     return user_db

# @app.get("/health", include_in_schema=False)
# def health():
#     return {"status": "ok"}


from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import engine, get_db
from .errors import RFC7807Error, setup_exception_handlers
from .models import Base, User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecDev Course App", version="0.1.0")

setup_exception_handlers(app)


# Добавьте Pydantic модели
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: str = None
    email: str = None
    password: str = None


@app.get("/users")
async def get_users(request: Request, db: Session = Depends(get_db)):
    return db.query(User).all()


@app.post("/users")
async def create_user(
    user_data: UserCreate, db: Session = Depends(get_db)  # Используем Pydantic модель
):
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
    user_data: UserUpdate,  # Используем Pydantic модель
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
