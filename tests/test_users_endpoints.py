def test_create_user_success(client):
    response = client.post(
        "/users", params={"name": "Misha", "email": "d@mail.ru", "password": "123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Misha"
    assert data["email"] == "d@mail.ru"
    assert data["password"] == "123"
    assert "id" in data


def test_create_existing_user(client, sample_user):
    response = client.post(
        "/users", params={"name": "Dima", "email": "d@mail.ru", "password": "123"}
    )
    assert response.status_code == 400
    assert "Такой пользователь уже есть" in response.json()["error"]["message"]


def test_get_users(client, sample_user):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "Dima"


def test_get_user_by_id_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "Пользователь не найден" in response.json()["error"]["message"]


def test_get_user_by_id_success(client, sample_user):
    response = client.get(f"/users/{sample_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_user.id
    assert data["username"] == "Dima"
    assert data["email"] == "dima@gmail.com"
    assert data["password"] == "123"


def test_delete_user_success(client, sample_user):
    response = client.delete(f"/users/{sample_user.id}")
    assert response.status_code == 200
    check = client.get(f"/users/{sample_user.id}")
    assert check.status_code == 404


def test_delete_user_fail(client):
    response = client.delete("/users/7898")
    assert response.status_code == 404


def test_update_user_success(client, sample_user):
    response = client.put(
        f"/users/{sample_user.id}",
        params={"name": "updatedDima", "email": "upd@gmail.com", "password": "newpass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updatedDima"
    assert data["email"] == "upd@gmail.com"
    assert data["password"] == "newpass"


def test_partial_user_update(client, sample_user):
    response = client.put(f"/users/{sample_user.id}", params={"name": "Daniil"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Daniil"
    assert data["email"] == "dima@gmail.com"
    assert data["password"] == "123"


def test_user_update_failure(client):
    response = client.put("/users/3838", params={"username": "kvdkmlvfkmlv"})
    assert response.status_code == 404
