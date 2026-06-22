from decimal import Decimal, ROUND_HALF_UP


MONEY_QUANT = Decimal("0.01")
PERCENT_DIVISOR = Decimal("100")


def to_decimal(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value))


def money(value: Decimal | int | float | str) -> Decimal:
    return to_decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def validate_non_negative(value: Decimal, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")


def validate_tax_rate(tax_rate: Decimal) -> None:
    if tax_rate < 0 or tax_rate > 100:
        raise ValueError("tax_rate must be between 0 and 100")


def calculate_quote_item(
    quantity: Decimal | int | float | str,
    unit_price: Decimal | int | float | str,
    tax_rate: Decimal | int | float | str,
) -> dict[str, Decimal]:
    quantity_value = to_decimal(quantity)
    unit_price_value = to_decimal(unit_price)
    tax_rate_value = to_decimal(tax_rate)

    validate_non_negative(quantity_value, "quantity")
    validate_non_negative(unit_price_value, "unit_price")
    validate_tax_rate(tax_rate_value)

    subtotal_amount = money(quantity_value * unit_price_value)
    tax_amount = money(subtotal_amount * tax_rate_value / PERCENT_DIVISOR)
    total_amount = money(subtotal_amount + tax_amount)

    return {
        "subtotal_amount": subtotal_amount,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
    }


def calculate_quote_totals(
    items: list[dict[str, Decimal]],
) -> dict[str, Decimal]:
    subtotal_amount = money(
        sum((item["subtotal_amount"] for item in items), Decimal("0.00"))
    )
    tax_amount = money(
        sum((item["tax_amount"] for item in items), Decimal("0.00"))
    )
    total_amount = money(
        sum((item["total_amount"] for item in items), Decimal("0.00"))
    )

    return {
        "subtotal_amount": subtotal_amount,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
    }
