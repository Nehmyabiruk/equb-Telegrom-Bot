"""
Generate a PDF report of approved Ethio Car Equb participants.
"""

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _format_date(value) -> str:
    if not value:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %H:%M")
    return str(value)


def generate_approved_users_pdf(participants: list[dict]) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#1B4332"),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#52796F"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    elements = [
        Paragraph("ETHIO CAR EQUB", title_style),
        Paragraph("Approved Participants Report", subtitle_style),
        Paragraph(
            f"Generated: {datetime.utcnow().strftime('%d %B %Y at %H:%M UTC')}",
            subtitle_style,
        ),
        Spacer(1, 0.4 * cm),
    ]

    if not participants:
        elements.append(
            Paragraph(
                "No approved participants yet.",
                styles["Normal"],
            )
        )
    else:
        headers = [
            "#",
            "Participant No.",
            "Full Name",
            "Phone",
            "Payment Method",
            "Payment For",
            "Approved On",
        ]

        rows = [headers]
        for index, participant in enumerate(participants, start=1):
            rows.append(
                [
                    str(index),
                    f"#{participant['participant_number']:03d}"
                    if participant.get("participant_number")
                    else "—",
                    participant.get("participant_name", "—"),
                    participant.get("phone", "—"),
                    (participant.get("payment_method") or "—").upper(),
                    participant.get("payment_for", "—").title()
                    if participant.get("payment_for")
                    else "—",
                    _format_date(participant.get("verified_at")),
                ]
            )

        table = Table(
            rows,
            repeatRows=1,
            colWidths=[
                1.2 * cm,
                3.2 * cm,
                5.5 * cm,
                3.5 * cm,
                3.5 * cm,
                3 * cm,
                4.5 * cm,
            ],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#F0F7F4")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B7E4C7")),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(table)

        elements.append(Spacer(1, 0.6 * cm))
        elements.append(
            Paragraph(
                f"Total approved participants: <b>{len(participants)}</b>",
                styles["Normal"],
            )
        )

    doc.build(elements)
    buffer.seek(0)
    return buffer
