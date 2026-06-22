from decimal import Decimal
from io import BytesIO
from typing import Iterable
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Company, Customer, Quote, QuoteItem


def text(value: object) -> str:
    if value is None:
        return "-"

    return escape(str(value))


def money(value: Decimal, currency: str) -> str:
    return f"{value:,.2f} {currency}"


def build_quote_pdf(
    company: Company,
    customer: Customer,
    quote: Quote,
    items: Iterable[QuoteItem],
) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Quote {quote.quote_number}",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "QuoteTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=8,
        spaceAfter=5,
    )

    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
    )

    story = []

    story.append(Paragraph("QuoteFlow Pro", title_style))
    story.append(Paragraph(f"Quote No: <b>{text(quote.quote_number)}</b>", normal_style))
    story.append(Paragraph(f"Status: <b>{text(quote.status).upper()}</b>", normal_style))
    story.append(Paragraph(f"Issue Date: {text(quote.issue_date)}", normal_style))
    story.append(Paragraph(f"Valid Until: {text(quote.valid_until)}", normal_style))
    story.append(Spacer(1, 8))

    info_table = Table(
        [
            [
                Paragraph("<b>Company</b>", section_style),
                Paragraph("<b>Customer</b>", section_style),
            ],
            [
                Paragraph(
                    f"{text(company.name)}<br/>"
                    f"Industry: {text(company.industry)}<br/>"
                    f"Email: {text(company.email)}<br/>"
                    f"Phone: {text(company.phone)}<br/>"
                    f"Tax No: {text(company.tax_number)}<br/>"
                    f"Address: {text(company.address)}",
                    normal_style,
                ),
                Paragraph(
                    f"{text(customer.name)}<br/>"
                    f"Contact: {text(customer.contact_name)}<br/>"
                    f"Email: {text(customer.email)}<br/>"
                    f"Phone: {text(customer.phone)}<br/>"
                    f"Tax No: {text(customer.tax_number)}<br/>"
                    f"Address: {text(customer.address)}",
                    normal_style,
                ),
            ],
        ],
        colWidths=[85 * mm, 85 * mm],
    )

    info_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(info_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph(text(quote.title), section_style))

    item_rows = [
        [
            Paragraph("<b>Description</b>", small_style),
            Paragraph("<b>Qty</b>", small_style),
            Paragraph("<b>Unit</b>", small_style),
            Paragraph("<b>Unit Price</b>", small_style),
            Paragraph("<b>Tax</b>", small_style),
            Paragraph("<b>Total</b>", small_style),
        ]
    ]

    for item in items:
        item_rows.append(
            [
                Paragraph(text(item.description), small_style),
                Paragraph(f"{item.quantity:,.2f}", small_style),
                Paragraph(text(item.unit), small_style),
                Paragraph(money(item.unit_price, quote.currency), small_style),
                Paragraph(f"{item.tax_rate:,.2f}%", small_style),
                Paragraph(money(item.total_amount, quote.currency), small_style),
            ]
        )

    items_table = Table(
        item_rows,
        colWidths=[58 * mm, 18 * mm, 20 * mm, 31 * mm, 18 * mm, 31 * mm],
        repeatRows=1,
    )

    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(items_table)
    story.append(Spacer(1, 12))

    totals_table = Table(
        [
            ["Subtotal", money(quote.subtotal_amount, quote.currency)],
            ["Tax", money(quote.tax_amount, quote.currency)],
            ["Total", money(quote.total_amount, quote.currency)],
        ],
        colWidths=[35 * mm, 45 * mm],
        hAlign="RIGHT",
    )

    totals_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#F3F4F6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(totals_table)

    if quote.notes:
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Notes</b>", section_style))
        story.append(Paragraph(text(quote.notes), normal_style))

    story.append(Spacer(1, 16))
    story.append(Paragraph("Generated by QuoteFlow Pro", small_style))

    document.build(story)

    return buffer.getvalue()
