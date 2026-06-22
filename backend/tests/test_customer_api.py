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
            "full_name": "Customer User",
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


def create_company(token: str, name: str = "Customer API Company") -> dict:
    response = client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": name,
            "industry": "Manufacturing",
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
            "tax_number": "1234567890",
            "address": "Istanbul, Turkiye",
            "notes": "Priority customer",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_customer_for_company():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    response = client.post(
        f"/api/companies/{company['id']}/customers",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "ABC Industrial Ltd.",
            "contact_name": "Ahmet Yilmaz",
            "email": "contact@abcindustrial.com",
            "phone": "+90 555 111 22 33",
            "tax_number": "1234567890",
            "address": "Istanbul, Turkiye",
            "notes": "Priority customer",
        },
    )

    assert response.status_code == 201

    customer = response.json()

    assert customer["company_id"] == company["id"]
    assert customer["name"] == "ABC Industrial Ltd."
    assert customer["contact_name"] == "Ahmet Yilmaz"
    assert customer["email"] == "contact@abcindustrial.com"
    assert customer["notes"] == "Priority customer"


def test_list_customers_for_company():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    create_customer(token, company["id"], "First Customer")
    create_customer(token, company["id"], "Second Customer")

    response = client.get(
        f"/api/companies/{company['id']}/customers",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    customers = response.json()

    assert len(customers) == 2

    customer_names = {customer["name"] for customer in customers}

    assert "First Customer" in customer_names
    assert "Second Customer" in customer_names


def test_get_customer_detail():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])

    response = client.get(
        f"/api/companies/{company['id']}/customers/{customer['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    customer_detail = response.json()

    assert customer_detail["id"] == customer["id"]
    assert customer_detail["company_id"] == company["id"]
    assert customer_detail["name"] == "ABC Industrial Ltd."


def test_update_customer():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"])

    response = client.patch(
        f"/api/companies/{company['id']}/customers/{customer['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Updated Customer Ltd.",
            "contact_name": "Mehmet Kaya",
            "notes": "Updated customer note",
        },
    )

    assert response.status_code == 200

    updated_customer = response.json()

    assert updated_customer["id"] == customer["id"]
    assert updated_customer["name"] == "Updated Customer Ltd."
    assert updated_customer["contact_name"] == "Mehmet Kaya"
    assert updated_customer["notes"] == "Updated customer note"


def test_non_member_cannot_access_company_customers():
    owner_token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    outsider_token = register_and_login(f"customer-outsider-{uuid.uuid4()}@example.com")

    company = create_company(owner_token)
    customer = create_customer(owner_token, company["id"])

    list_response = client.get(
        f"/api/companies/{company['id']}/customers",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    detail_response = client.get(
        f"/api/companies/{company['id']}/customers/{customer['id']}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    update_response = client.patch(
        f"/api/companies/{company['id']}/customers/{customer['id']}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
        json={
            "name": "Unauthorized Update",
        },
    )

    assert list_response.status_code == 404
    assert detail_response.status_code == 404
    assert update_response.status_code == 404
