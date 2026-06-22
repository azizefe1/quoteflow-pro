import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def register_and_login(email: str) -> str:
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Test12345",
            "full_name": "Company Owner",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "Test12345",
        },
    )

    return login_response.json()["access_token"]


def test_create_company_workspace():
    token = register_and_login(f"owner-{uuid.uuid4()}@example.com")

    response = client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Example Machinery",
            "industry": "Machinery",
            "email": "info@example.com",
            "phone": "+90 555 000 00 00",
            "website": "https://example.com",
            "tax_number": "1234567890",
            "address": "Istanbul, Turkiye",
        },
    )

    assert response.status_code == 201

    payload = response.json()

    assert payload["role"] == "owner"
    assert payload["membership_id"]
    assert payload["company"]["name"] == "Example Machinery"
    assert payload["company"]["slug"] == "example-machinery"
    assert payload["company"]["industry"] == "Machinery"


def test_create_company_requires_authentication():
    response = client.post(
        "/api/companies",
        json={
            "name": "Unauthorized Company",
        },
    )

    assert response.status_code == 401


def test_list_my_company_workspaces():
    token = register_and_login(f"owner-{uuid.uuid4()}@example.com")

    client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "First Company",
            "industry": "Consulting",
        },
    )

    client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Second Company",
            "industry": "Manufacturing",
        },
    )

    response = client.get(
        "/api/companies/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    workspaces = response.json()

    assert len(workspaces) == 2
    assert workspaces[0]["role"] == "owner"
    assert workspaces[0]["company"]["name"] in ["First Company", "Second Company"]


def test_company_slug_is_unique():
    token = register_and_login(f"owner-{uuid.uuid4()}@example.com")

    first_response = client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Same Company",
        },
    )

    second_response = client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Same Company",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["company"]["slug"] == "same-company"
    assert second_response.json()["company"]["slug"] == "same-company-2"
