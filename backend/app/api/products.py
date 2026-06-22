from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models import Product, User
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.workspaces import require_company_membership

router = APIRouter(
    prefix="/api/companies/{company_id}/products",
    tags=["products"],
)


def get_product_for_company_or_404(
    db: Session,
    company_id: UUID,
    product_id: UUID,
    active_only: bool = True,
) -> Product:
    query = db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == company_id,
    )

    if active_only:
        query = query.filter(Product.is_active.is_(True))

    product = query.first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    company_id: UUID,
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    product = Product(
        company_id=company_id,
        sku=payload.sku,
        name=payload.name,
        description=payload.description,
        unit=payload.unit,
        unit_price=payload.unit_price,
        currency=payload.currency,
        tax_rate=payload.tax_rate,
        stock_quantity=payload.stock_quantity,
    )

    db.add(product)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product SKU already exists for this company",
        ) from exc

    return product


@router.get("", response_model=ProductListResponse)
def list_products(
    company_id: UUID,
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    include_inactive: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    query = db.query(Product).filter(Product.company_id == company_id)

    if not include_inactive:
        query = query.filter(Product.is_active.is_(True))

    if search is not None and search.strip():
        search_value = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Product.name.ilike(search_value),
                Product.sku.ilike(search_value),
                Product.description.ilike(search_value),
            )
        )

    total = query.count()

    products = (
        query.order_by(Product.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return ProductListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[
            ProductResponse.model_validate(product)
            for product in products
        ],
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    company_id: UUID,
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    return get_product_for_company_or_404(
        db=db,
        company_id=company_id,
        product_id=product_id,
    )


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    company_id: UUID,
    product_id: UUID,
    payload: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    product = get_product_for_company_or_404(
        db=db,
        company_id=company_id,
        product_id=product_id,
    )

    update_data = payload.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(product, field_name, value)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product SKU already exists for this company",
        ) from exc

    return product


@router.delete("/{product_id}", response_model=ProductResponse)
def deactivate_product(
    company_id: UUID,
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    product = get_product_for_company_or_404(
        db=db,
        company_id=company_id,
        product_id=product_id,
    )

    product.is_active = False

    db.commit()
    db.refresh(product)

    return product
