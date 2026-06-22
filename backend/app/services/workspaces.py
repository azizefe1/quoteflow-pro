import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Company, CompanyMember, User


ROLE_OWNER = "owner"
ROLE_MANAGER = "manager"
ROLE_STAFF = "staff"

MANAGE_COMPANY_ROLES = {
    ROLE_OWNER,
    ROLE_MANAGER,
}


def get_active_company_membership(
    db: Session,
    company_id: uuid.UUID,
    user_id: uuid.UUID,
) -> CompanyMember | None:
    return (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == user_id,
            CompanyMember.is_active.is_(True),
        )
        .first()
    )


def get_company_or_404(
    db: Session,
    company_id: uuid.UUID,
) -> Company:
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company workspace not found",
        )

    return company


def require_company_membership(
    db: Session,
    company_id: uuid.UUID,
    current_user: User,
) -> tuple[Company, CompanyMember]:
    company = get_company_or_404(db, company_id)

    membership = get_active_company_membership(
        db=db,
        company_id=company_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company workspace not found",
        )

    return company, membership


def require_company_role(
    db: Session,
    company_id: uuid.UUID,
    current_user: User,
    allowed_roles: set[str],
) -> tuple[Company, CompanyMember]:
    company, membership = require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this company workspace",
        )

    return company, membership
