import uuid
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def decimal_from_json(value: object) -> Decimal:
    return Decimal(str(value))


def register_and_login(email: str) -> str:
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Test12345",
            "full_name": "Quote User",
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


def create_company(token: str, name: str = "Quote API Company") -> dict:
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


def create_customer(token: str, company_id: str, name: str = "ABC Industrial Ltd.") -> dict:
    response = client.post(
        f"/api/companies/{company_id}/customers",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": name,
            "contact_name": "Ahmet Yilmaz",
            "email": "contact@abcindustrial.com",
            "phone": "+90 555 111 22 33",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_product(
    token: str,
    company_id: str,
    sku: str = "GEN-001",
    name: str = "Industrial Generator",
) -> dict:
    response = client.post(
        f"/api/companies/{company_id}/products",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "sku": sku,
            "name": name,
            "description": "Diesel generator for industrial use",
            "unit": "piece",
            "unit_price": "125000.00",
            "currency": "TRY",
            "tax_rate": "20.00",
            "stock_quantity": "5.00",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_quote(
    token: str,
    company_id: str,
    customer_id: str,
    product_id: str,
    quote_number: str = "Q-2026-0001",
) -> dict:
    response = client.post(
        f"/api/companies/{company_id}/quotes",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "customer_id": customer_id,
            "quote_number": quote_number,
            "title": "Industrial Generator Quote",
            "valid_until": "2026-12-31",
            "currency": "TRY",
            "notes": "Delivery included.",
            "items": [
                {
                    "product_id": product_id,
                    "description": "Industrial Generator",
                    "quantity": "2.00",
                    "unit": "piece",
                    "unit_price": "125000.00",
                    "tax_rate": "20.00",
                    "sort_order": 1,
                },
                {
                    "description": "Installation Service",
                    "quantity": "1.00",
                    "unit": "service",
                    "unit_price": "10000.00",
                    "tax_rate": "20.00",
                    "sort_order": 2,
                },
            ],
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_quote_with_calculated_totals():
    token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    product = create_product(token, company["id"])

    response = client.post(
        f"/api/companies/{company['id']}/quotes",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "customer_id": customer["id"],
            "quote_number": "Q-2026-0001",
            "title": "Industrial Generator Quote",
            "valid_until": "2026-12-31",
            "currency": "try",
            "notes": "Delivery included.",
            "items": [
                {
                    "product_id": product["id"],
                    "description": "Industrial Generator",
                    "quantity": "2.00",
                    "unit": "piece",
                    "unit_price": "125000.00",
                    "tax_rate": "20.00",
                    "sort_order": 1,
                },
                {
                    "description": "Installation Service",
                    "quantity": "1.00",
                    "unit": "service",
                    "unit_price": "10000.00",
                    "tax_rate": "20.00",
                    "sort_order": 2,
                },
            ],
        },
    )

    assert response.status_code == 201

    quote = response.json()

    assert quote["company_id"] == company["id"]
    assert quote["customer_id"] == customer["id"]
    assert quote["quote_number"] == "Q-2026-0001"
    assert quote["title"] == "Industrial Generator Quote"
    assert quote["status"] == "draft"
    assert quote["currency"] == "TRY"

    assert decimal_from_json(quote["subtotal_amount"]) == Decimal("260000.00")
    assert decimal_from_json(quote["tax_amount"]) == Decimal("52000.00")
    assert decimal_from_json(quote["total_amount"]) == Decimal("312000.00")

    assert len(quote["items"]) == 2
    assert quote["items"][0]["description"] == "Industrial Generator"
    assert decimal_from_json(quote["items"][0]["subtotal_amount"]) == Decimal("250000.00")
    assert decimal_from_json(quote["items"][0]["tax_amount"]) == Decimal("50000.00")
    assert decimal_from_json(quote["items"][0]["total_amount"]) == Decimal("300000.00")


def test_list_quotes_for_company():
    token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    product = create_product(token, company["id"])

    create_quote(
        token=token,
        company_id=company["id"],
        customer_id=customer["id"],
        product_id=product["id"],
        quote_number="Q-2026-0001",
    )
    create_quote(
        token=token,
        company_id=company["id"],
        customer_id=customer["id"],
        product_id=product["id"],
        quote_number="Q-2026-0002",
    )

    response = client.get(
        f"/api/companies/{company['id']}/quotes",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 2
    assert payload["limit"] == 20
    assert payload["offset"] == 0

    quote_numbers = {quote["quote_number"] for quote in payload["items"]}

    assert "Q-2026-0001" in quote_numbers
    assert "Q-2026-0002" in quote_numbers


def test_get_quote_detail():
    token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    product = create_product(token, company["id"])
    quote = create_quote(token, company["id"], customer["id"], product["id"])

    response = client.get(
        f"/api/companies/{company['id']}/quotes/{quote['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    quote_detail = response.json()

    assert quote_detail["id"] == quote["id"]
    assert quote_detail["quote_number"] == "Q-2026-0001"
    assert len(quote_detail["items"]) == 2


def test_duplicate_quote_number_fails_in_same_company():
    token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])
    product = create_product(token, company["id"])

    create_quote(
        token=token,
        company_id=company["id"],
        customer_id=customer["id"],
        product_id=product["id"],
        quote_number="Q-DUP-001",
    )

    response = client.post(
        f"/api/companies/{company['id']}/quotes",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "customer_id": customer["id"],
            "quote_number": "Q-DUP-001",
            "title": "Duplicate Quote",
            "currency": "TRY",
            "items": [
                {
                    "description": "Duplicate Item",
                    "quantity": "1.00",
                    "unit": "piece",
                    "unit_price": "100.00",
                    "tax_rate": "20.00",
                },
            ],
        },
    )

    assert response.status_code == 409


def test_quote_requires_customer_from_same_company():
    first_token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")
    second_token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")

    first_company = create_company(first_token, "First Quote Company")
    second_company = create_company(second_token, "Second Quote Company")

    customer_from_second_company = create_customer(second_token, second_company["id"])
    product_from_first_company = create_product(first_token, first_company["id"])

    response = client.post(
        f"/api/companies/{first_company['id']}/quotes",
        headers={
            "Authorization": f"Bearer {first_token}",
        },
        json={
            "customer_id": customer_from_second_company["id"],
            "quote_number": "Q-CROSS-001",
            "title": "Invalid Customer Quote",
            "currency": "TRY",
            "items": [
                {
                    "product_id": product_from_first_company["id"],
                    "description": "Industrial Generator",
                    "quantity": "1.00",
                    "unit": "piece",
                    "unit_price": "125000.00",
                    "tax_rate": "20.00",
                },
            ],
        },
    )

    assert response.status_code == 404


def test_quote_requires_product_from_same_company():
    first_token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")
    second_token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")

    first_company = create_company(first_token, "First Product Company")
    second_company = create_company(second_token, "Second Product Company")

    customer_from_first_company = create_customer(first_token, first_company["id"])
    product_from_second_company = create_product(second_token, second_company["id"])

    response = client.post(
        f"/api/companies/{first_company['id']}/quotes",
        headers={
            "Authorization": f"Bearer {first_token}",
        },
        json={
            "customer_id": customer_from_first_company["id"],
            "quote_number": "Q-CROSS-002",
            "title": "Invalid Product Quote",
            "currency": "TRY",
            "items": [
                {
                    "product_id": product_from_second_company["id"],
                    "description": "External Product",
                    "quantity": "1.00",
                    "unit": "piece",
                    "unit_price": "100.00",
                    "tax_rate": "20.00",
                },
            ],
        },
    )

    assert response.status_code == 404


def test_non_member_cannot_access_company_quotes():
    owner_token = register_and_login(f"quote-owner-{uuid.uuid4()}@example.com")
    outsider_token = register_and_login(f"quote-outsider-{uuid.uuid4()}@example.com")

    company = create_company(owner_token)
    customer = create_customer(owner_token, company["id"])
    product = create_product(owner_token, company["id"])
    quote = create_quote(owner_token, company["id"], customer["id"], product["id"])

    list_response = client.get(
        f"/api/companies/{company['id']}/quotes",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    detail_response = client.get(
        f"/api/companies/{company['id']}/quotes/{quote['id']}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    create_response = client.post(
        f"/api/companies/{company['id']}/quotes",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
        json={
            "customer_id": customer["id"],
            "quote_number": "Q-OUTSIDER-001",
            "title": "Outsider Quote",
            "currency": "TRY",
            "items": [
                {
                    "description": "Unauthorized Item",
                    "quantity": "1.00",
                    "unit": "piece",
                    "unit_price": "100.00",
                    "tax_rate": "20.00",
                },
            ],
        },
    )

    assert list_response.status_code == 404
    assert detail_response.status_code == 404
    assert create_response.status_code == 404
