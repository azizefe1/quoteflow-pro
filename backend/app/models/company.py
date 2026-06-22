import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(180),
        unique=True,
        index=True,
        nullable=False,
    )
    industry: Mapped[str] = mapped_column(
        String(120),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )
    website: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    tax_number: Mapped[str] = mapped_column(
        String(80),
        nullable=True,
    )
    address: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
