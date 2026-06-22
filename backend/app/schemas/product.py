from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    sku: Optional[str] = Field(default=None, max_length=80)
    name: str = Field(min_length=2, max_length=180)
    description: Optional[str] = None
    unit: str = Field(default="piece", min_length=1, max_length=40)
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="TRY", min_length=3, max_length=3)
    tax_rate: Decimal = Field(default=Decimal("20.00"), ge=0, le=100)
    stock_quantity: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("sku", "description", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized

    @field_validator("name", "unit", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object) -> str:
        return str(value).strip()

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str:
        return str(value).strip().upper()


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, max_length=80)
    name: Optional[str] = Field(default=None, min_length=2, max_length=180)
    description: Optional[str] = None
    unit: Optional[str] = Field(default=None, min_length=1, max_length=40)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    tax_rate: Optional[Decimal] = Field(default=None, ge=0, le=100)
    stock_quantity: Optional[Decimal] = Field(default=None, ge=0)

    @field_validator("sku", "description", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized

    @field_validator("name", "unit", mode="before")
    @classmethod
    def normalize_required_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        return str(value).strip()

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        if value is None:
            return None

        return str(value).strip().upper()


class ProductResponse(BaseModel):
    id: UUID
    company_id: UUID
    sku: Optional[str]
    name: str
    description: Optional[str]
    unit: str
    unit_price: Decimal
    currency: str
    tax_rate: Decimal
    stock_quantity: Decimal
    is_active: bool

    model_config = {
        "from_attributes": True,
    }


class ProductListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ProductResponse]
