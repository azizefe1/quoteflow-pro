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
    assert customer["is_active"] is True


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

    payload = response.json()

    assert payload["total"] == 2
    assert payload["limit"] == 20
    assert payload["offset"] == 0
    assert len(payload["items"]) == 2

    customer_names = {customer["name"] for customer in payload["items"]}

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


def test_search_customers():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    create_customer(token, company["id"], "Alpha Machinery")
    create_customer(token, company["id"], "Beta Industrial")

    response = client.get(
        f"/api/companies/{company['id']}/customers?search=Alpha",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["name"] == "Alpha Machinery"


def test_customer_pagination():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)

    create_customer(token, company["id"], "Customer One")
    create_customer(token, company["id"], "Customer Two")
    create_customer(token, company["id"], "Customer Three")

    response = client.get(
        f"/api/companies/{company['id']}/customers?limit=2&offset=0",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 3
    assert payload["limit"] == 2
    assert payload["offset"] == 0
    assert len(payload["items"]) == 2


def test_deactivate_customer_hides_from_default_list_and_detail():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"], "Inactive Customer")

    delete_response = client.delete(
        f"/api/companies/{company['id']}/customers/{customer['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    list_response = client.get(
        f"/api/companies/{company['id']}/customers",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0
    assert list_response.json()["items"] == []

    detail_response = client.get(
        f"/api/companies/{company['id']}/customers/{customer['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert detail_response.status_code == 404


def test_include_inactive_customers():
    token = register_and_login(f"customer-owner-{uuid.uuid4()}@example.com")
    company = create_company(token)
    customer = create_customer(token, company["id"], "Inactive Customer")

    client.delete(
        f"/api/companies/{company['id']}/customers/{customer['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    response = client.get(
        f"/api/companies/{company['id']}/customers?include_inactive=true",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["is_active"] is False
