from decimal import Decimal

import pytest

from app.services.quote_calculator import (
    calculate_quote_item,
    calculate_quote_totals,
    money,
)


def test_calculate_quote_item_with_tax():
    result = calculate_quote_item(
        quantity=2,
        unit_price="1000.00",
        tax_rate="20.00",
    )

    assert result["subtotal_amount"] == Decimal("2000.00")
    assert result["tax_amount"] == Decimal("400.00")
    assert result["total_amount"] == Decimal("2400.00")


def test_calculate_quote_item_without_tax():
    result = calculate_quote_item(
        quantity=3,
        unit_price="500.00",
        tax_rate="0.00",
    )

    assert result["subtotal_amount"] == Decimal("1500.00")
    assert result["tax_amount"] == Decimal("0.00")
    assert result["total_amount"] == Decimal("1500.00")


def test_calculate_quote_totals_from_multiple_items():
    first_item = calculate_quote_item(
        quantity=1,
        unit_price="1000.00",
        tax_rate="20.00",
    )
    second_item = calculate_quote_item(
        quantity=2,
        unit_price="250.00",
        tax_rate="10.00",
    )

    totals = calculate_quote_totals([first_item, second_item])

    assert totals["subtotal_amount"] == Decimal("1500.00")
    assert totals["tax_amount"] == Decimal("250.00")
    assert totals["total_amount"] == Decimal("1750.00")


def test_money_rounds_to_two_decimal_places():
    assert money("10.235") == Decimal("10.24")
    assert money("10.234") == Decimal("10.23")


def test_negative_quantity_fails():
    with pytest.raises(ValueError):
        calculate_quote_item(
            quantity="-1",
            unit_price="100.00",
            tax_rate="20.00",
        )


def test_invalid_tax_rate_fails():
    with pytest.raises(ValueError):
        calculate_quote_item(
            quantity="1",
            unit_price="100.00",
            tax_rate="101.00",
        )
