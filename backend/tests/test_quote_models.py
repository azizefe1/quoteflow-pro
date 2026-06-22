from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Company, CompanyMember, Customer, Product, Quote, QuoteItem, User
from app.services.security import hash_password


def create_quote_dependencies(db: Session) -> tuple[Company, User, Customer, Product]:
    user = User(
        email="quote-owner@example.com",
        hashed_password=hash_password("Test12345"),
        full_name="Quote Owner",
    )

    company = Company(
        name="Quote Company",
        slug="quote-company",
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

    customer = Customer(
        company_id=company.id,
        name="ABC Industrial Ltd.",
        contact_name="Ahmet Yilmaz",
        email="contact@abcindustrial.com",
    )

    product = Product(
        company_id=company.id,
        sku="GEN-001",
        name="Industrial Generator",
        unit="piece",
        unit_price=Decimal("125000.00"),
        currency="TRY",
        tax_rate=Decimal("20.00"),
        stock_quantity=Decimal("5.00"),
    )

    db.add(membership)
    db.add(customer)
    db.add(product)
    db.commit()
    db.refresh(customer)
    db.refresh(product)

    return company, user, customer, product


def test_create_quote_with_item():
    db: Session = SessionLocal()

    try:
        company, user, customer, product = create_quote_dependencies(db)

        quote = Quote(
            company_id=company.id,
            customer_id=customer.id,
            created_by_user_id=user.id,
            quote_number="Q-2026-0001",
            title="Industrial Generator Quote",
            status="draft",
            issue_date=date(2026, 1, 1),
            valid_until=date(2026, 1, 15),
            currency="TRY",
            subtotal_amount=Decimal("125000.00"),
            tax_amount=Decimal("25000.00"),
            total_amount=Decimal("150000.00"),
            notes="Delivery included.",
        )

        db.add(quote)
        db.commit()
        db.refresh(quote)

        quote_item = QuoteItem(
            quote_id=quote.id,
            product_id=product.id,
            description="Industrial Generator",
            quantity=Decimal("1.00"),
            unit="piece",
            unit_price=Decimal("125000.00"),
            tax_rate=Decimal("20.00"),
            subtotal_amount=Decimal("125000.00"),
            tax_amount=Decimal("25000.00"),
            total_amount=Decimal("150000.00"),
            sort_order=1,
        )

        db.add(quote_item)
        db.commit()
        db.refresh(quote_item)

        assert quote.company_id == company.id
        assert quote.customer_id == customer.id
        assert quote.created_by_user_id == user.id
        assert quote.quote_number == "Q-2026-0001"
        assert quote.status == "draft"
        assert quote.total_amount == Decimal("150000.00")

        assert quote_item.quote_id == quote.id
        assert quote_item.product_id == product.id
        assert quote_item.total_amount == Decimal("150000.00")

    finally:
        db.close()


def test_quote_number_must_be_unique_per_company():
    db: Session = SessionLocal()

    try:
        company, user, customer, _product = create_quote_dependencies(db)

        first_quote = Quote(
            company_id=company.id,
            customer_id=customer.id,
            created_by_user_id=user.id,
            quote_number="Q-DUP-001",
            title="First Quote",
        )
        second_quote = Quote(
            company_id=company.id,
            customer_id=customer.id,
            created_by_user_id=user.id,
            quote_number="Q-DUP-001",
            title="Second Quote",
        )

        db.add(first_quote)
        db.commit()

        db.add(second_quote)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            assert True
        else:
            assert False, "Duplicate quote number should not be allowed in same company"

    finally:
        db.close()
