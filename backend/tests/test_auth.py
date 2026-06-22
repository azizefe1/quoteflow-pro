import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.services.security import hash_password, verify_password


client = TestClient(app)


def test_register_login_and_get_current_user():
    unique_email = f"user-{uuid.uuid4()}@example.com"

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": unique_email,
            "password": "Test12345",
            "full_name": "Test User",
        },
    )

    assert register_response.status_code == 201

    registered_user = register_response.json()

    assert registered_user["email"] == unique_email
    assert registered_user["full_name"] == "Test User"
    assert registered_user["is_active"] is True

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": unique_email,
            "password": "Test12345",
        },
    )

    assert login_response.status_code == 200

    token_payload = login_response.json()

    assert token_payload["token_type"] == "bearer"
    assert token_payload["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token_payload['access_token']}",
        },
    )

    assert me_response.status_code == 200

    current_user = me_response.json()

    assert current_user["email"] == unique_email
    assert current_user["full_name"] == "Test User"


def test_register_normalizes_email_and_full_name():
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "  USER@Example.COM  ",
            "password": "Test12345",
            "full_name": "  Test User  ",
        },
    )

    assert register_response.status_code == 201

    registered_user = register_response.json()

    assert registered_user["email"] == "user@example.com"
    assert registered_user["full_name"] == "Test User"


def test_register_duplicate_email_fails():
    payload = {
        "email": "duplicate@example.com",
        "password": "Test12345",
        "full_name": "Duplicate User",
    }

    first_response = client.post("/api/auth/register", json=payload)
    second_response = client.post("/api/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_with_wrong_password_fails():
    unique_email = f"user-{uuid.uuid4()}@example.com"

    client.post(
        "/api/auth/register",
        json={
            "email": unique_email,
            "password": "Test12345",
            "full_name": "Test User",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": unique_email,
            "password": "WrongPassword123",
        },
    )

    assert login_response.status_code == 401


def test_get_me_without_token_fails():
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_get_me_with_invalid_token_fails():
    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_password_hash_verify_round_trip():
    password = "StrongPassword123"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("WrongPassword123", password_hash) is False
