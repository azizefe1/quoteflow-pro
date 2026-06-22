import uuid

from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app
from app.models import User


Base.metadata.create_all(bind=engine)

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
