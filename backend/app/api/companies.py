from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models import Company, CompanyMember, User
from app.schemas.company import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    CompanyWorkspaceResponse,
)
from app.services.slugs import slugify
from app.services.workspaces import (
    MANAGE_COMPANY_ROLES,
    require_company_membership,
    require_company_role,
)

router = APIRouter(prefix="/api/companies", tags=["companies"])


def create_unique_company_slug(db: Session, company_name: str) -> str:
    base_slug = slugify(company_name)
    slug = base_slug
    counter = 2

    while db.query(Company).filter(Company.slug == slug).first() is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


@router.post("", response_model=CompanyWorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_company_workspace(
    payload: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyWorkspaceResponse:
    company = Company(
        name=payload.name,
        slug=create_unique_company_slug(db, payload.name),
        industry=payload.industry,
        email=str(payload.email) if payload.email is not None else None,
        phone=payload.phone,
        website=payload.website,
        tax_number=payload.tax_number,
        address=payload.address,
    )

    db.add(company)

    try:
        db.flush()

        membership = CompanyMember(
            company_id=company.id,
            user_id=current_user.id,
            role="owner",
        )

        db.add(membership)
        db.commit()
        db.refresh(company)
        db.refresh(membership)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company workspace could not be created",
        ) from exc

    return CompanyWorkspaceResponse(
        membership_id=membership.id,
        role=membership.role,
        company=CompanyResponse.model_validate(company),
    )


@router.get("/me", response_model=list[CompanyWorkspaceResponse])
def list_my_company_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CompanyWorkspaceResponse]:
    memberships = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.user_id == current_user.id,
            CompanyMember.is_active.is_(True),
        )
        .order_by(CompanyMember.created_at.desc())
        .all()
    )

    workspaces: list[CompanyWorkspaceResponse] = []

    for membership in memberships:
        company = db.get(Company, membership.company_id)

        if company is None:
            continue

        workspaces.append(
            CompanyWorkspaceResponse(
                membership_id=membership.id,
                role=membership.role,
                company=CompanyResponse.model_validate(company),
            )
        )

    return workspaces


@router.get("/{company_id}", response_model=CompanyWorkspaceResponse)
def get_company_workspace(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyWorkspaceResponse:
    company, membership = require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    return CompanyWorkspaceResponse(
        membership_id=membership.id,
        role=membership.role,
        company=CompanyResponse.model_validate(company),
    )


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company_workspace(
    company_id: UUID,
    payload: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyResponse:
    company, _membership = require_company_role(
        db=db,
        company_id=company_id,
        current_user=current_user,
        allowed_roles=MANAGE_COMPANY_ROLES,
    )

    update_data = payload.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        if field_name == "email" and value is not None:
            value = str(value)

        setattr(company, field_name, value)

    db.commit()
    db.refresh(company)

    return CompanyResponse.model_validate(company)
