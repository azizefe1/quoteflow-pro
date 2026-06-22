from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class QuoteItemCreate(BaseModel):
    product_id: Optional[UUID] = None
    description: str = Field(min_length=2, max_length=255)
    quantity: Decimal = Field(default=Decimal("1.00"), gt=0)
    unit: str = Field(default="piece", min_length=1, max_length=40)
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_rate: Decimal = Field(default=Decimal("20.00"), ge=0, le=100)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("description", "unit", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        return str(value).strip()


class QuoteCreate(BaseModel):
    customer_id: UUID
    quote_number: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=2, max_length=180)
    valid_until: Optional[date] = None
    currency: str = Field(default="TRY", min_length=3, max_length=3)
    notes: Optional[str] = None
    items: list[QuoteItemCreate] = Field(min_length=1)

    @field_validator("quote_number", "title", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object) -> str:
        return str(value).strip()

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str:
        return str(value).strip().upper()

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized


class QuoteItemResponse(BaseModel):
    id: UUID
    product_id: Optional[UUID]
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    tax_rate: Decimal
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    sort_order: int

    model_config = {
        "from_attributes": True,
    }


class QuoteResponse(BaseModel):
    id: UUID
    company_id: UUID
    customer_id: UUID
    created_by_user_id: UUID
    quote_number: str
    title: str
    status: str
    issue_date: date
    valid_until: Optional[date]
    currency: str
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: Optional[str]
    items: list[QuoteItemResponse]


class QuoteListItemResponse(BaseModel):
    id: UUID
    company_id: UUID
    customer_id: UUID
    created_by_user_id: UUID
    quote_number: str
    title: str
    status: str
    issue_date: date
    valid_until: Optional[date]
    currency: str
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: Optional[str]

    model_config = {
        "from_attributes": True,
    }


class QuoteListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[QuoteListItemResponse]
