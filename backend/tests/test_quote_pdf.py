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
            "full_name": "Quote PDF User",
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


def create_company(token: str) -> dict:
    response = client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "PDF Quote Company",
            "industry": "Machinery",
            "email": "info@example.com",
            "phone": "+90 555 000 00 00",
            "tax_number": "1234567890",
            "address": "Istanbul, Turkiye",
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
            "phone": "+90 555 111 22 33",
            "tax_number": "9876543210",
            "address": "Ankara, Turkiye",
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
            "quote_number": f"PDF-{uuid.uuid4()}",
            "title": "PDF Quote",
            "currency": "TRY",
            "notes": "This quote was generated for PDF export test.",
            "items": [
                {
                    "description": "Industrial Generator",
                    "quantity": "1.00",
                    "unit": "piece",
                    "unit_price": "125000.00",
                    "tax_rate": "20.00",
                },
                {
                    "description": "Installation Service",
                    "quantity": "1.00",
                    "unit": "service",
                    "unit_price": "10000.00",
                    "tax_rate": "20.00",
                },
            ],
        },
    )

    assert response.status_code == 201

    return response.json()


def test_download_quote_pdf():
    token = register_and_login(f"quote-pdf-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    quote = create_quote(token, company["id"], customer["id"])

    response = client.get(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/pdf",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 1000
    assert "attachment" in response.headers["content-disposition"]
    assert quote["quote_number"] in response.headers["content-disposition"]


def test_non_member_cannot_download_quote_pdf():
    owner_token = register_and_login(f"quote-pdf-owner-{uuid.uuid4()}@example.com")
    outsider_token = register_and_login(f"quote-pdf-outsider-{uuid.uuid4()}@example.com")

    company = create_company(owner_token)
    customer = create_customer(owner_token, company["id"])
    quote = create_quote(owner_token, company["id"], customer["id"])

    response = client.get(
        f"/api/companies/{company['id']}/quotes/{quote['id']}/pdf",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    assert response.status_code == 404
