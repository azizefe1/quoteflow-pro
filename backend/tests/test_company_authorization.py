import uuid
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.main import app
from app.models import CompanyMember, User


client = TestClient(app)


def register_and_login(email: str) -> str:
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Test12345",
            "full_name": "Workspace User",
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


def create_company(token: str, name: str = "Secure Company") -> dict:
    response = client.post(
        "/api/companies",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": name,
            "industry": "B2B Services",
        },
    )

    assert response.status_code == 201

    return response.json()


def add_member_to_company(
    company_id: str,
    user_email: str,
    role: str,
) -> None:
    db: Session = SessionLocal()

    try:
        user = db.query(User).filter(User.email == user_email).first()

        assert user is not None

        membership = CompanyMember(
            company_id=UUID(company_id),
            user_id=user.id,
            role=role,
        )

        db.add(membership)
        db.commit()

    finally:
        db.close()


def test_owner_can_get_company_workspace_detail():
    owner_token = register_and_login(f"owner-{uuid.uuid4()}@example.com")
    workspace = create_company(owner_token)

    company_id = workspace["company"]["id"]

    response = client.get(
        f"/api/companies/{company_id}",
        headers={
            "Authorization": f"Bearer {owner_token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "owner"
    assert response.json()["company"]["id"] == company_id


def test_non_member_cannot_get_company_workspace_detail():
    owner_token = register_and_login(f"owner-{uuid.uuid4()}@example.com")
    outsider_token = register_and_login(f"outsider-{uuid.uuid4()}@example.com")

    workspace = create_company(owner_token)
    company_id = workspace["company"]["id"]

    response = client.get(
        f"/api/companies/{company_id}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    assert response.status_code == 404


def test_owner_can_update_company_workspace():
    owner_token = register_and_login(f"owner-{uuid.uuid4()}@example.com")
    workspace = create_company(owner_token)

    company_id = workspace["company"]["id"]

    response = client.patch(
        f"/api/companies/{company_id}",
        headers={
            "Authorization": f"Bearer {owner_token}",
        },
        json={
            "name": "Updated Company",
            "industry": "Updated Industry",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Company"
    assert response.json()["industry"] == "Updated Industry"


def test_manager_can_update_company_workspace():
    owner_token = register_and_login(f"owner-{uuid.uuid4()}@example.com")
    manager_email = f"manager-{uuid.uuid4()}@example.com"
    manager_token = register_and_login(manager_email)

    workspace = create_company(owner_token)
    company_id = workspace["company"]["id"]

    add_member_to_company(
        company_id=company_id,
        user_email=manager_email,
        role="manager",
    )

    response = client.patch(
        f"/api/companies/{company_id}",
        headers={
            "Authorization": f"Bearer {manager_token}",
        },
        json={
            "industry": "Managed Industry",
        },
    )

    assert response.status_code == 200
    assert response.json()["industry"] == "Managed Industry"


def test_staff_cannot_update_company_workspace():
    owner_token = register_and_login(f"owner-{uuid.uuid4()}@example.com")
    staff_email = f"staff-{uuid.uuid4()}@example.com"
    staff_token = register_and_login(staff_email)

    workspace = create_company(owner_token)
    company_id = workspace["company"]["id"]

    add_member_to_company(
        company_id=company_id,
        user_email=staff_email,
        role="staff",
    )

    response = client.patch(
        f"/api/companies/{company_id}",
        headers={
            "Authorization": f"Bearer {staff_token}",
        },
        json={
            "industry": "Staff Updated Industry",
        },
    )

    assert response.status_code == 403


def test_non_member_cannot_update_company_workspace():
    owner_token = register_and_login(f"owner-{uuid.uuid4()}@example.com")
    outsider_token = register_and_login(f"outsider-{uuid.uuid4()}@example.com")

    workspace = create_company(owner_token)
    company_id = workspace["company"]["id"]

    response = client.patch(
        f"/api/companies/{company_id}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
        json={
            "industry": "Unauthorized Update",
        },
    )

    assert response.status_code == 404
