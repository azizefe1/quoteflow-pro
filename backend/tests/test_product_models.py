from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Company, CompanyMember, Product, User
from app.services.security import hash_password


def create_company_with_owner(db: Session) -> Company:
    user = User(
        email="product-owner@example.com",
        hashed_password=hash_password("Test12345"),
        full_name="Product Owner",
    )

    company = Company(
        name="Product Company",
        slug="product-company",
        industry="Machinery",
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

    return company


def test_create_product_for_company():
    db: Session = SessionLocal()

    try:
        company = create_company_with_owner(db)

        product = Product(
            company_id=company.id,
            sku="GEN-001",
            name="Industrial Generator",
            description="Diesel generator for industrial use",
            unit="piece",
            unit_price=Decimal("125000.00"),
            currency="TRY",
            tax_rate=Decimal("20.00"),
            stock_quantity=Decimal("5.00"),
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        assert product.company_id == company.id
        assert product.sku == "GEN-001"
        assert product.name == "Industrial Generator"
        assert product.unit_price == Decimal("125000.00")
        assert product.currency == "TRY"
        assert product.tax_rate == Decimal("20.00")
        assert product.stock_quantity == Decimal("5.00")
        assert product.is_active is True

    finally:
        db.close()


def test_product_sku_must_be_unique_per_company():
    db: Session = SessionLocal()

    try:
        company = create_company_with_owner(db)

        first_product = Product(
            company_id=company.id,
            sku="DUP-001",
            name="First Product",
            unit_price=Decimal("100.00"),
        )
        second_product = Product(
            company_id=company.id,
            sku="DUP-001",
            name="Second Product",
            unit_price=Decimal("200.00"),
        )

        db.add(first_product)
        db.commit()

        db.add(second_product)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            assert True
        else:
            assert False, "Duplicate product SKU should not be allowed in same company"

    finally:
        db.close()
