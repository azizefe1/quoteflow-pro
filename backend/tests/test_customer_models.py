from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Company, CompanyMember, Customer, User
from app.services.security import hash_password


def test_create_customer_for_company():
    db: Session = SessionLocal()

    try:
        user = User(
            email="customer-owner@example.com",
            hashed_password=hash_password("Test12345"),
            full_name="Customer Owner",
        )

        company = Company(
            name="Customer Company",
            slug="customer-company",
            industry="Manufacturing",
        )

        db.add(user)
        db.add(company)
        db.commit()
        db.refresh(user)
        db.refresh(company)

        membership = CompanyMember(
            company_id=company.id,
            user_id=user.id,
            role="owner",
        )

        db.add(membership)
        db.commit()

        customer = Customer(
            company_id=company.id,
            name="ABC Industrial Ltd.",
            contact_name="Ahmet Yilmaz",
            email="contact@abcindustrial.com",
            phone="+90 555 111 22 33",
            tax_number="1234567890",
            address="Istanbul, Turkiye",
            notes="Priority customer",
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        assert customer.company_id == company.id
        assert customer.name == "ABC Industrial Ltd."
        assert customer.contact_name == "Ahmet Yilmaz"
        assert customer.email == "contact@abcindustrial.com"
        assert customer.notes == "Priority customer"

    finally:
        db.close()
