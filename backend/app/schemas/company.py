from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    industry: Optional[str] = Field(default=None, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = Field(default=None, max_length=255)
    tax_number: Optional[str] = Field(default=None, max_length=80)
    address: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> str:
        return str(value).strip()

    @field_validator("industry", "phone", "website", "tax_number", "address", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=160)
    industry: Optional[str] = Field(default=None, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = Field(default=None, max_length=255)
    tax_number: Optional[str] = Field(default=None, max_length=80)
    address: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        if value is None:
            return None

        return str(value).strip()

    @field_validator("industry", "phone", "website", "tax_number", "address", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None

        normalized = str(value).strip()

        if not normalized:
            return None

        return normalized


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    industry: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    website: Optional[str]
    tax_number: Optional[str]
    address: Optional[str]

    model_config = {
        "from_attributes": True,
    }


class CompanyWorkspaceResponse(BaseModel):
    membership_id: UUID
    role: str
    company: CompanyResponse
