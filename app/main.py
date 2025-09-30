from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Base, User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecDev Course App", version="0.1.0")


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize FastAPI HTTPException into our error envelope
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


@app.post("/users")
async def create_user(
    name: str, email: str, password: str, db: Session = Depends(get_db)
):
    user = (
        db.query(User).filter(or_(User.username == name, User.email == email)).first()
    )
    if user:
        raise ApiError(
            code="existing user", message="Такой пользователь уже есть", status=400
        )
    user = User(username=name, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ApiError(
            code="non existing user", message="Такого пользователя нет", status=404
        )
    return user


@app.delete("/users/{user_id}")
async def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ApiError(
            code="non existing user", message="Такого пользователя нет", status=404
        )
    db.delete(user)
    db.commit()
    return user


@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    db: Session = Depends(get_db),
    name: str = None,
    email: str = None,
    password: str = None,
):
    user = (
        db.query(User).filter(or_(User.email == email, User.username == name)).first()
    )
    if user:
        raise ApiError(
            code="existing user", message="Такой пользователь уже есть", status=400
        )
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise ApiError(
            code="non existing user", message="Такого пользователя нет", status=404
        )

    if name is not None:
        user_db.username = name
    if email is not None:
        user_db.email = email
    if password is not None:
        user_db.password = password

    db.commit()
    db.refresh(user_db)
    return user_db


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


# Example minimal entity (for tests/demo)
_DB = {"items": []}


@app.post("/items", include_in_schema=False)
def create_item(name: str):
    if not name or len(name) > 100:
        raise ApiError(
            code="validation_error", message="name must be 1..100 chars", status=422
        )
    item = {"id": len(_DB["items"]) + 1, "name": name}
    _DB["items"].append(item)
    return item


@app.get("/items/{item_id}", include_in_schema=False)
def get_item(item_id: int):
    for it in _DB["items"]:
        if it["id"] == item_id:
            return it
    raise ApiError(code="not_found", message="item not found", status=404)
