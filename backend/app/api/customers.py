from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models import Customer, User
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.workspaces import require_company_membership

router = APIRouter(
    prefix="/api/companies/{company_id}/customers",
    tags=["customers"],
)


def get_customer_for_company_or_404(
    db: Session,
    company_id: UUID,
    customer_id: UUID,
) -> Customer:
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == company_id,
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    company_id: UUID,
    payload: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Customer:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    customer = Customer(
        company_id=company_id,
        name=payload.name,
        contact_name=payload.contact_name,
        email=str(payload.email) if payload.email is not None else None,
        phone=payload.phone,
        tax_number=payload.tax_number,
        address=payload.address,
        notes=payload.notes,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Customer]:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    return (
        db.query(Customer)
        .filter(Customer.company_id == company_id)
        .order_by(Customer.created_at.desc())
        .all()
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    company_id: UUID,
    customer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Customer:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    return get_customer_for_company_or_404(
        db=db,
        company_id=company_id,
        customer_id=customer_id,
    )


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    company_id: UUID,
    customer_id: UUID,
    payload: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Customer:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    customer = get_customer_for_company_or_404(
        db=db,
        company_id=company_id,
        customer_id=customer_id,
    )

    update_data = payload.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        if field_name == "email" and value is not None:
            value = str(value)

        setattr(customer, field_name, value)

    db.commit()
    db.refresh(customer)

    return customer
