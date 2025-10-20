import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_endpoint():
    """Тест эндпоинта здоровья"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user_success(test_db):
    """Тест успешного создания пользователя"""
    response = client.post(
        "/users",
        json={  # Используем json вместо data
            "name": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert "username" in data
    assert "email" in data
    assert "id" in data
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_create_user_duplicate(test_db):
    """Тест создания дубликата пользователя"""
    response1 = client.post(
        "/users",
        json={"name": "user1", "email": "user1@example.com", "password": "pass1"},
    )
    assert response1.status_code == 200

    response2 = client.post(
        "/users",
        json={
            "name": "user2",
            "email": "user1@example.com",  # Дублирующий email
            "password": "pass2",
        },
    )

    assert response2.status_code == 400
    error_data = response2.json()
    assert error_data["title"] == "existing user"


def test_get_users_empty(test_db):
    """Тест получения пустого списка пользователей"""
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) == 0


def test_get_users_with_data(test_db):
    """Тест получения списка пользователей с данными"""
    client.post(
        "/users",
        json={"name": "user1", "email": "user1@example.com", "password": "pass1"},
    )
    client.post(
        "/users",
        json={"name": "user2", "email": "user2@example.com", "password": "pass2"},
    )

    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    usernames = [user["username"] for user in users]
    assert "user1" in usernames
    assert "user2" in usernames


def test_get_user_by_id_success(test_db):
    """Тест успешного получения пользователя по ID"""
    create_response = client.post(
        "/users",
        json={"name": "testuser", "email": "test@example.com", "password": "testpass"},
    )
    assert create_response.status_code == 200
    user_data = create_response.json()
    user_id = user_data["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id
    assert user["username"] == "testuser"


def test_get_user_by_id_not_found(test_db):
    """Тест получения несуществующего пользователя"""
    response = client.get("/users/999")
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["title"] == "non existing user"


def test_delete_user_success(test_db):
    """Тест успешного удаления пользователя"""
    create_response = client.post(
        "/users",
        json={"name": "todelete", "email": "delete@example.com", "password": "pass"},
    )
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]

    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404


def test_delete_user_not_found(test_db):
    """Тест удаления несуществующего пользователя"""
    response = client.delete("/users/999")
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["title"] == "non existing user"


def test_update_user_success(test_db):
    """Тест успешного обновления пользователя"""
    create_response = client.post(
        "/users",
        json={"name": "original", "email": "original@example.com", "password": "pass"},
    )
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]

    response = client.put(
        f"/users/{user_id}",
        json={"name": "updated", "email": "updated@example.com", "password": "newpass"},
    )

    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == "updated"
    assert updated_user["email"] == "updated@example.com"


def test_update_user_partial(test_db):
    """Тест частичного обновления пользователя"""
    create_response = client.post(
        "/users",
        json={"name": "partial", "email": "partial@example.com", "password": "pass"},
    )
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]

    response = client.put(f"/users/{user_id}", json={"name": "partial_updated"})

    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == "partial_updated"
    assert updated_user["email"] == "partial@example.com"  # осталось прежним


def test_update_user_duplicate_email(test_db):
    """Тест обновления с дублирующимся email"""
    client.post(
        "/users",
        json={"name": "user1", "email": "user1@example.com", "password": "pass1"},
    )
    create_response = client.post(
        "/users",
        json={"name": "user2", "email": "user2@example.com", "password": "pass2"},
    )
    user2_data = create_response.json()
    user2_id = user2_data["id"]

    response = client.put(f"/users/{user2_id}", json={"email": "user1@example.com"})

    assert response.status_code == 400
    error_data = response.json()
    assert error_data["title"] == "existing user"


def test_update_user_not_found(test_db):
    """Тест обновления несуществующего пользователя"""
    response = client.put("/users/999", json={"name": "updated"})
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["title"] == "non existing user"


def test_error_response_format(test_db):
    """Тест формата ошибки RFC7807"""
    response = client.get("/users/999")

    assert response.status_code == 404
    error_data = response.json()

    assert "type" in error_data
    assert "title" in error_data
    assert "status" in error_data
    assert "detail" in error_data
    assert "instance" in error_data
    assert "correlation_id" in error_data
