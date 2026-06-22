import uuid

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.services.quote_status import (
    InvalidQuoteStatusError,
    InvalidQuoteStatusTransitionError,
    validate_quote_status_transition,
)


client = TestClient(app)


def register_and_login(email: str) -> str:
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Test12345",
            "full_name": "Quote Status User",
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


def create_company(token: str, name: str = "Quote Status Company") -> dict:
    response = client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": name,
            "industry": "Machinery",
        },
    )

    assert response.status_code == 201

    return response.json()["company"]


def create_customer(token: str, company_id: str) -> dict:
    response = client.post(
        f"/api/companies/{company_id}/customers",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "ABC Industrial Ltd.",
            "contact_name": "Ahmet Yilmaz",
            "email": "contact@abcindustrial.com",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_quote(token: str, company_id: str, customer_id: str) -> dict:
    response = client.post(
        f"/api/companies/{company_id}/quotes",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "customer_id": customer_id,
            "quote_number": f"Q-{uuid.uuid4()}",
            "title": "Status Quote",
            "currency": "TRY",
            "items": [
                {
                    "description": "Service Item",
                    "quantity": "1.00",
                    "unit": "service",
                    "unit_price": "1000.00",
                    "tax_rate": "20.00",
                },
            ],
        },
    )

    assert response.status_code == 201

    return response.json()


def test_validate_quote_status_transition_allows_valid_flow():
    assert validate_quote_status_transition("draft", "sent") == "sent"
    assert validate_quote_status_transition("sent", "accepted") == "accepted"
    assert validate_quote_status_transition("sent", "rejected") == "rejected"
    assert validate_quote_status_transition("sent", "expired") == "expired"


def test_validate_quote_status_transition_rejects_invalid_status():
    with pytest.raises(InvalidQuoteStatusError):
        validate_quote_status_transition("draft", "unknown")


def test_validate_quote_status_transition_rejects_invalid_flow():
    with pytest.raises(InvalidQuoteStatusTransitionError):
        validate_quote_status_transition("accepted", "sent")


def test_update_quote_status_from_draft_to_sent():
    token = register_and_login(f"quote-status-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    quote = create_quote(token, company["id"], customer["id"])

    response = client.patch(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "sent",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "sent"


def test_update_quote_status_from_sent_to_accepted():
    token = register_and_login(f"quote-status-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    quote = create_quote(token, company["id"], customer["id"])

    sent_response = client.patch(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "sent",
        },
    )

    assert sent_response.status_code == 200

    accepted_response = client.patch(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "accepted",
        },
    )

    assert accepted_response.status_code == 200
    assert accepted_response.json()["status"] == "accepted"


def test_invalid_quote_status_transition_fails():
    token = register_and_login(f"quote-status-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    quote = create_quote(token, company["id"], customer["id"])

    sent_response = client.patch(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "sent",
        },
    )

    assert sent_response.status_code == 200

    accepted_response = client.patch(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "accepted",
        },
    )

    assert accepted_response.status_code == 200

    invalid_response = client.patch(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "sent",
        },
    )

    assert invalid_response.status_code == 400


def test_non_member_cannot_update_quote_status():
    owner_token = register_and_login(f"quote-status-owner-{uuid.uuid4()}@example.com")
    outsider_token = register_and_login(f"quote-status-outsider-{uuid.uuid4()}@example.com")

    company = create_company(owner_token)
    customer = create_customer(owner_token, company["id"])
    quote = create_quote(owner_token, company["id"], customer["id"])

    response = client.patch(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/status",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
        json={
            "status": "sent",
        },
    )

    assert response.status_code == 404
