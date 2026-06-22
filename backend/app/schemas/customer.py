from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    contact_name: Optional[str] = Field(default=None, max_length=160)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    tax_number: Optional[str] = Field(default=None, max_length=80)
    address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> str:
        return str(value).strip()

    @field_validator("contact_name", "phone", "tax_number", "address", "notes", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=180)
    contact_name: Optional[str] = Field(default=None, max_length=160)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    tax_number: Optional[str] = Field(default=None, max_length=80)
    address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        if value is None:
            return None

        return str(value).strip()

    @field_validator("contact_name", "phone", "tax_number", "address", "notes", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized


class CustomerResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    contact_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    tax_number: Optional[str]
    address: Optional[str]
    notes: Optional[str]
    is_active: bool

    model_config = {
        "from_attributes": True,
    }
