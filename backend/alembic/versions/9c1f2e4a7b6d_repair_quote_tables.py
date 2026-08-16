"""repair missing quote tables

Revision ID: 9c1f2e4a7b6d
Revises: ffb6e2d756ba
Create Date: 2026-08-16 00:00:00.000000

"""
from collections.abc import Iterable
from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c1f2e4a7b6d"
down_revision: Union[str, None] = "ffb6e2d756ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


QUOTE_COLUMNS = {
    "id",
    "company_id",
    "customer_id",
    "created_by_user_id",
    "quote_number",
    "title",
    "status",
    "issue_date",
    "valid_until",
    "currency",
    "subtotal_amount",
    "tax_amount",
    "total_amount",
    "notes",
    "created_at",
    "updated_at",
}

QUOTE_ITEM_COLUMNS = {
    "id",
    "quote_id",
    "product_id",
    "description",
    "quantity",
    "unit",
    "unit_price",
    "tax_rate",
    "subtotal_amount",
    "tax_amount",
    "total_amount",
    "sort_order",
    "created_at",
}


def _require_columns(table_name: str, expected_columns: set[str]) -> None:
    inspector = sa.inspect(op.get_bind())
    actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing_columns = sorted(expected_columns - actual_columns)

    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(
            f"Existing {table_name} table is incomplete; missing columns: {missing}. "
            "Manual schema review is required before continuing."
        )


def _ensure_indexes(table_name: str, indexes: Iterable[tuple[str, str]]) -> None:
    inspector = sa.inspect(op.get_bind())
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}

    for index_name, column_name in indexes:
        if index_name not in existing_indexes:
            op.create_index(index_name, table_name, [column_name], unique=False)


def _create_quotes_table() -> None:
    op.create_table(
        "quotes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("quote_number", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("subtotal_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "quote_number",
            name="uq_quotes_company_quote_number",
        ),
    )
    op.create_index("ix_quotes_company_id", "quotes", ["company_id"], unique=False)
    op.create_index("ix_quotes_customer_id", "quotes", ["customer_id"], unique=False)
    op.create_index(
        "ix_quotes_created_by_user_id",
        "quotes",
        ["created_by_user_id"],
        unique=False,
    )


def _create_quote_items_table() -> None:
    op.create_table(
        "quote_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("quote_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("subtotal_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quote_items_product_id", "quote_items", ["product_id"], unique=False)
    op.create_index("ix_quote_items_quote_id", "quote_items", ["quote_id"], unique=False)


def upgrade() -> None:
    if context.is_offline_mode():
        _create_quotes_table()
        _create_quote_items_table()
        return

    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "quote_items" in table_names and "quotes" not in table_names:
        raise RuntimeError(
            "quote_items exists without quotes; manual schema review is required."
        )

    if "quotes" not in table_names:
        _create_quotes_table()
    else:
        _require_columns("quotes", QUOTE_COLUMNS)
        _ensure_indexes(
            "quotes",
            (
                ("ix_quotes_company_id", "company_id"),
                ("ix_quotes_customer_id", "customer_id"),
                ("ix_quotes_created_by_user_id", "created_by_user_id"),
            ),
        )

        inspector = sa.inspect(op.get_bind())
        unique_constraints = {
            constraint["name"]
            for constraint in inspector.get_unique_constraints("quotes")
        }

        if "uq_quotes_company_quote_number" not in unique_constraints:
            op.create_unique_constraint(
                "uq_quotes_company_quote_number",
                "quotes",
                ["company_id", "quote_number"],
            )

    if "quote_items" not in table_names:
        _create_quote_items_table()
    else:
        _require_columns("quote_items", QUOTE_ITEM_COLUMNS)
        _ensure_indexes(
            "quote_items",
            (
                ("ix_quote_items_quote_id", "quote_id"),
                ("ix_quote_items_product_id", "product_id"),
            ),
        )


def downgrade() -> None:
    if context.is_offline_mode():
        op.drop_index("ix_quote_items_product_id", table_name="quote_items")
        op.drop_index("ix_quote_items_quote_id", table_name="quote_items")
        op.drop_table("quote_items")
        op.drop_index("ix_quotes_created_by_user_id", table_name="quotes")
        op.drop_index("ix_quotes_customer_id", table_name="quotes")
        op.drop_index("ix_quotes_company_id", table_name="quotes")
        op.drop_table("quotes")
        return

    table_names = set(sa.inspect(op.get_bind()).get_table_names())

    if "quote_items" in table_names:
        quote_item_indexes = {
            index["name"]
            for index in sa.inspect(op.get_bind()).get_indexes("quote_items")
        }

        for index_name in ("ix_quote_items_product_id", "ix_quote_items_quote_id"):
            if index_name in quote_item_indexes:
                op.drop_index(index_name, table_name="quote_items")

        op.drop_table("quote_items")

    if "quotes" in table_names:
        quote_indexes = {
            index["name"]
            for index in sa.inspect(op.get_bind()).get_indexes("quotes")
        }

        for index_name in (
            "ix_quotes_created_by_user_id",
            "ix_quotes_customer_id",
            "ix_quotes_company_id",
        ):
            if index_name in quote_indexes:
                op.drop_index(index_name, table_name="quotes")

        op.drop_table("quotes")
