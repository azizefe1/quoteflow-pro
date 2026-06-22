from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models import Company, Customer, Product, Quote, QuoteItem, User
from app.schemas.quote import (
    QuoteCreate,
    QuoteItemResponse,
    QuoteListItemResponse,
    QuoteListResponse,
    QuoteResponse,
    QuoteStatusUpdate,
)
from app.services.quote_calculator import calculate_quote_item, calculate_quote_totals
from app.services.quote_pdf import build_quote_pdf
from app.services.quote_status import (
    InvalidQuoteStatusError,
    InvalidQuoteStatusTransitionError,
    validate_quote_status_transition,
)
from app.services.workspaces import require_company_membership

router = APIRouter(
    prefix="/api/companies/{company_id}/quotes",
    tags=["quotes"],
)


def get_active_customer_for_company_or_404(
    db: Session,
    company_id: UUID,
    customer_id: UUID,
) -> Customer:
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == company_id,
            Customer.is_active.is_(True),
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


def get_active_product_for_company_or_404(
    db: Session,
    company_id: UUID,
    product_id: UUID,
) -> Product:
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.company_id == company_id,
            Product.is_active.is_(True),
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


def get_quote_for_company_or_404(
    db: Session,
    company_id: UUID,
    quote_id: UUID,
) -> Quote:
    quote = (
        db.query(Quote)
        .filter(
            Quote.id == quote_id,
            Quote.company_id == company_id,
        )
        .first()
    )

    if quote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found",
        )

    return quote


def get_quote_items(
    db: Session,
    quote_id: UUID,
) -> list[QuoteItem]:
    return (
        db.query(QuoteItem)
        .filter(QuoteItem.quote_id == quote_id)
        .order_by(QuoteItem.sort_order.asc(), QuoteItem.created_at.asc())
        .all()
    )


def build_quote_response(db: Session, quote: Quote) -> QuoteResponse:
    items = get_quote_items(db=db, quote_id=quote.id)

    return QuoteResponse(
        id=quote.id,
        company_id=quote.company_id,
        customer_id=quote.customer_id,
        created_by_user_id=quote.created_by_user_id,
        quote_number=quote.quote_number,
        title=quote.title,
        status=quote.status,
        issue_date=quote.issue_date,
        valid_until=quote.valid_until,
        currency=quote.currency,
        subtotal_amount=quote.subtotal_amount,
        tax_amount=quote.tax_amount,
        total_amount=quote.total_amount,
        notes=quote.notes,
        items=[
            QuoteItemResponse.model_validate(item)
            for item in items
        ],
    )


def safe_pdf_filename(value: str) -> str:
    safe_value = "".join(
        character if character.isalnum() or character in ("-", "_") else "-"
        for character in value
    ).strip("-")

    if not safe_value:
        return "quote"

    return safe_value


@router.post("", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_quote(
    company_id: UUID,
    payload: QuoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteResponse:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    get_active_customer_for_company_or_404(
        db=db,
        company_id=company_id,
        customer_id=payload.customer_id,
    )

    calculated_items: list[dict] = []

    for index, item_payload in enumerate(payload.items):
        if item_payload.product_id is not None:
            get_active_product_for_company_or_404(
                db=db,
                company_id=company_id,
                product_id=item_payload.product_id,
            )

        amounts = calculate_quote_item(
            quantity=item_payload.quantity,
            unit_price=item_payload.unit_price,
            tax_rate=item_payload.tax_rate,
        )

        calculated_items.append(
            {
                "payload": item_payload,
                "amounts": amounts,
                "sort_order": item_payload.sort_order or index,
            }
        )

    totals = calculate_quote_totals(
        [item["amounts"] for item in calculated_items]
    )

    quote = Quote(
        company_id=company_id,
        customer_id=payload.customer_id,
        created_by_user_id=current_user.id,
        quote_number=payload.quote_number,
        title=payload.title,
        status="draft",
        issue_date=date.today(),
        valid_until=payload.valid_until,
        currency=payload.currency,
        subtotal_amount=totals["subtotal_amount"],
        tax_amount=totals["tax_amount"],
        total_amount=totals["total_amount"],
        notes=payload.notes,
    )

    db.add(quote)

    try:
        db.flush()

        for item in calculated_items:
            item_payload = item["payload"]
            amounts = item["amounts"]

            quote_item = QuoteItem(
                quote_id=quote.id,
                product_id=item_payload.product_id,
                description=item_payload.description,
                quantity=item_payload.quantity,
                unit=item_payload.unit,
                unit_price=item_payload.unit_price,
                tax_rate=item_payload.tax_rate,
                subtotal_amount=amounts["subtotal_amount"],
                tax_amount=amounts["tax_amount"],
                total_amount=amounts["total_amount"],
                sort_order=item["sort_order"],
            )

            db.add(quote_item)

        db.commit()
        db.refresh(quote)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Quote number already exists for this company",
        ) from exc

    return build_quote_response(db=db, quote=quote)


@router.get("", response_model=QuoteListResponse)
def list_quotes(
    company_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: Optional[str] = Query(default=None, alias="status", max_length=40),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteListResponse:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    query = db.query(Quote).filter(Quote.company_id == company_id)

    if status_filter is not None and status_filter.strip():
        query = query.filter(Quote.status == status_filter.strip().lower())

    total = query.count()

    quotes = (
        query.order_by(Quote.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return QuoteListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[
            QuoteListItemResponse.model_validate(quote)
            for quote in quotes
        ],
    )


@router.get("/{quote_id}", response_model=QuoteResponse)
def get_quote(
    company_id: UUID,
    quote_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteResponse:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    quote = get_quote_for_company_or_404(
        db=db,
        company_id=company_id,
        quote_id=quote_id,
    )

    return build_quote_response(db=db, quote=quote)


@router.get("/{quote_id}/pdf")
def download_quote_pdf(
    company_id: UUID,
    quote_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    quote = get_quote_for_company_or_404(
        db=db,
        company_id=company_id,
        quote_id=quote_id,
    )

    company = db.get(Company, company_id)
    customer = db.get(Customer, quote.customer_id)
    items = get_quote_items(db=db, quote_id=quote.id)

    if company is None or customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote PDF data not found",
        )

    pdf_bytes = build_quote_pdf(
        company=company,
        customer=customer,
        quote=quote,
        items=items,
    )

    filename = f"{safe_pdf_filename(quote.quote_number)}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.patch("/{quote_id}/status", response_model=QuoteResponse)
def update_quote_status(
    company_id: UUID,
    quote_id: UUID,
    payload: QuoteStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuoteResponse:
    require_company_membership(
        db=db,
        company_id=company_id,
        current_user=current_user,
    )

    quote = get_quote_for_company_or_404(
        db=db,
        company_id=company_id,
        quote_id=quote_id,
    )

    try:
        next_status = validate_quote_status_transition(
            current_status=quote.status,
            next_status=payload.status,
        )
    except (InvalidQuoteStatusError, InvalidQuoteStatusTransitionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    quote.status = next_status

    db.commit()
    db.refresh(quote)

    return build_quote_response(db=db, quote=quote)
