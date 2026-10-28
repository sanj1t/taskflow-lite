from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Smith",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient):
    payload = {
        "email": "bob@example.com",
        "full_name": "Bob Smith",
        "password": "securepassword123",
    }

    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_login_success(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "carol@example.com",
            "full_name": "Carol Smith",
            "password": "securepassword123",
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "carol@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


def test_login_invalid_password(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "dave@example.com",
            "full_name": "Dave Smith",
            "password": "securepassword123",
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "dave@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_me_requires_token(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_me_with_token(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "erin@example.com",
            "full_name": "Erin Smith",
            "password": "securepassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "erin@example.com", "password": "securepassword123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "erin@example.com"
