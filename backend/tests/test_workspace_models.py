from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Company, CompanyMember, User
from app.services.security import hash_password


def test_create_company_and_owner_membership():
    db: Session = SessionLocal()

    try:
        user = User(
            email="owner@example.com",
            hashed_password=hash_password("Test12345"),
            full_name="Owner User",
        )

        company = Company(
            name="Example Machinery",
            slug="example-machinery",
            industry="Machinery",
            email="info@example.com",
            phone="+90 555 000 00 00",
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
        db.refresh(membership)

        assert membership.company_id == company.id
        assert membership.user_id == user.id
        assert membership.role == "owner"
        assert membership.is_active is True

    finally:
        db.close()


def test_company_slug_must_be_unique():
    db: Session = SessionLocal()

    try:
        first_company = Company(
            name="First Company",
            slug="same-company",
        )
        second_company = Company(
            name="Second Company",
            slug="same-company",
        )

        db.add(first_company)
        db.commit()

        db.add(second_company)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            assert True
        else:
            assert False, "Duplicate company slug should not be allowed"

    finally:
        db.close()


def test_user_can_join_company_only_once():
    db: Session = SessionLocal()

    try:
        user = User(
            email="member@example.com",
            hashed_password=hash_password("Test12345"),
            full_name="Member User",
        )
        company = Company(
            name="Unique Company",
            slug="unique-company",
        )

        db.add(user)
        db.add(company)
        db.commit()
        db.refresh(user)
        db.refresh(company)

        first_membership = CompanyMember(
            company_id=company.id,
            user_id=user.id,
            role="owner",
        )
        second_membership = CompanyMember(
            company_id=company.id,
            user_id=user.id,
            role="manager",
        )

        db.add(first_membership)
        db.commit()

        db.add(second_membership)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            assert True
        else:
            assert False, "Duplicate company membership should not be allowed"

    finally:
        db.close()
