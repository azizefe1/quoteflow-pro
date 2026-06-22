import uuid
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def register_and_login(email: str) -> str:
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Test12345",
            "full_name": "Product User",
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


def create_company(token: str, name: str = "Product API Company") -> dict:
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


def decimal_from_json(value: object) -> Decimal:
    return Decimal(str(value))


def test_create_product_for_company():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    response = client.post(
        f"/api/companies/{company['id']}/products",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "sku": "GEN-001",
            "name": "Industrial Generator",
            "description": "Diesel generator for industrial use",
            "unit": "piece",
            "unit_price": "125000.00",
            "currency": "try",
            "tax_rate": "20.00",
            "stock_quantity": "5.00",
        },
    )

    assert response.status_code == 201

    product = response.json()

    assert product["company_id"] == company["id"]
    assert product["sku"] == "GEN-001"
    assert product["name"] == "Industrial Generator"
    assert product["currency"] == "TRY"
    assert decimal_from_json(product["unit_price"]) == Decimal("125000.00")
    assert product["is_active"] is True


def test_duplicate_product_sku_fails_in_same_company():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    create_product(token, company["id"], sku="DUP-001", name="First Product")

    response = client.post(
        f"/api/companies/{company['id']}/products",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "sku": "DUP-001",
            "name": "Second Product",
            "unit_price": "200.00",
        },
    )

    assert response.status_code == 409


def test_list_products_for_company():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    create_product(token, company["id"], sku="GEN-001", name="Industrial Generator")
    create_product(token, company["id"], sku="CMP-001", name="Air Compressor")

    response = client.get(
        f"/api/companies/{company['id']}/products",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 2
    assert payload["limit"] == 20
    assert payload["offset"] == 0

    product_names = {product["name"] for product in payload["items"]}

    assert "Industrial Generator" in product_names
    assert "Air Compressor" in product_names


def test_search_products():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    create_product(token, company["id"], sku="GEN-001", name="Industrial Generator")
    create_product(token, company["id"], sku="CMP-001", name="Air Compressor")

    response = client.get(
        f"/api/companies/{company['id']}/products?search=compressor",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "Air Compressor"


def test_paginate_products():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    create_product(token, company["id"], sku="P-001", name="Product 1")
    create_product(token, company["id"], sku="P-002", name="Product 2")
    create_product(token, company["id"], sku="P-003", name="Product 3")

    response = client.get(
        f"/api/companies/{company['id']}/products?limit=2&offset=1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 3
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    assert len(payload["items"]) == 2


def test_get_product_detail():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    product = create_product(token, company["id"])

    response = client.get(
        f"/api/companies/{company['id']}/products/{product['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    product_detail = response.json()

    assert product_detail["id"] == product["id"]
    assert product_detail["company_id"] == company["id"]
    assert product_detail["name"] == "Industrial Generator"


def test_update_product():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    product = create_product(token, company["id"])

    response = client.patch(
        f"/api/companies/{company['id']}/products/{product['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Updated Generator",
            "unit_price": "130000.00",
            "stock_quantity": "8.00",
        },
    )

    assert response.status_code == 200

    updated_product = response.json()

    assert updated_product["id"] == product["id"]
    assert updated_product["name"] == "Updated Generator"
    assert decimal_from_json(updated_product["unit_price"]) == Decimal("130000.00")
    assert decimal_from_json(updated_product["stock_quantity"]) == Decimal("8.00")


def test_deactivate_product_and_include_inactive():
    token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    product = create_product(token, company["id"])

    delete_response = client.delete(
        f"/api/companies/{company['id']}/products/{product['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    list_response = client.get(
        f"/api/companies/{company['id']}/products",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0

    include_inactive_response = client.get(
        f"/api/companies/{company['id']}/products?include_inactive=true",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert include_inactive_response.status_code == 200
    assert include_inactive_response.json()["total"] == 1
    assert include_inactive_response.json()["items"][0]["is_active"] is False


def test_non_member_cannot_access_company_products():
    owner_token = register_and_login(f"product-owner-{uuid.uuid4()}@example.com")
    outsider_token = register_and_login(f"product-outsider-{uuid.uuid4()}@example.com")

    company = create_company(owner_token)
    product = create_product(owner_token, company["id"])

    list_response = client.get(
        f"/api/companies/{company['id']}/products",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    detail_response = client.get(
        f"/api/companies/{company['id']}/products/{product['id']}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    update_response = client.patch(
        f"/api/companies/{company['id']}/products/{product['id']}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
        json={
            "name": "Unauthorized Update",
        },
    )

    delete_response = client.delete(
        f"/api/companies/{company['id']}/products/{product['id']}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    assert list_response.status_code == 404
    assert detail_response.status_code == 404
    assert update_response.status_code == 404
    assert delete_response.status_code == 404
