"""
PDF Export
==========
Generates a nicely formatted PDF from a list of chat messages
using ReportLab.
"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
)


def _build_styles() -> dict:
    """Create custom paragraph styles for the chat PDF."""
    base = getSampleStyleSheet()

    styles = {
        "title": base["Title"],
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontSize=10,
            textColor=HexColor("#888888"),
            spaceAfter=16,
        ),
        "user_label": ParagraphStyle(
            "UserLabel",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=HexColor("#4f46e5"),
            spaceBefore=12,
            spaceAfter=2,
        ),
        "assistant_label": ParagraphStyle(
            "AssistantLabel",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=HexColor("#16a34a"),
            spaceBefore=12,
            spaceAfter=2,
        ),
        "user_text": ParagraphStyle(
            "UserText",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=HexColor("#1e293b"),
            leftIndent=12,
            spaceAfter=4,
        ),
        "assistant_text": ParagraphStyle(
            "AssistantText",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=HexColor("#1e293b"),
            leftIndent=12,
            spaceAfter=4,
        ),
        "source_header": ParagraphStyle(
            "SourceHeader",
            parent=base["Normal"],
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=HexColor("#94a3b8"),
            leftIndent=12,
            spaceBefore=4,
            spaceAfter=2,
        ),
        "source_text": ParagraphStyle(
            "SourceText",
            parent=base["Normal"],
            fontSize=8,
            leading=11,
            textColor=HexColor("#64748b"),
            leftIndent=20,
            spaceAfter=2,
        ),
    }
    return styles


def _escape(text: str) -> str:
    """Escape XML special characters for ReportLab Paragraphs."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_chat_pdf(messages: list[dict]) -> bytes:
    """
    Generate a PDF from a list of chat messages.

    Each message dict should have:
      - role: "user" | "assistant"
      - text: str
      - sources: list[dict] (optional, each with "content" and "source" keys)

    Returns the PDF as bytes.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = _build_styles()
    story = []

    # Title
    story.append(Paragraph("RAG Chat Export", styles["title"]))
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Exported on {timestamp}", styles["subtitle"]))
    story.append(
        HRFlowable(
            width="100%", thickness=1, color=HexColor("#e2e8f0"), spaceAfter=12
        )
    )

    # Messages
    for msg in messages:
        role = msg.get("role", "user")
        text = msg.get("text", "")
        sources = msg.get("sources", [])

        if role == "user":
            story.append(Paragraph("You", styles["user_label"]))
            story.append(Paragraph(_escape(text), styles["user_text"]))
        else:
            story.append(Paragraph("Assistant", styles["assistant_label"]))
            story.append(Paragraph(_escape(text), styles["assistant_text"]))

            if sources:
                story.append(Paragraph("Sources:", styles["source_header"]))
                for src in sources:
                    source_file = src.get("source", "unknown").split("/")[-1]
                    content = src.get("content", "")
                    # Truncate long source content
                    if len(content) > 200:
                        content = content[:200] + "..."
                    story.append(
                        Paragraph(
                            f"<b>{_escape(source_file)}</b>: {_escape(content)}",
                            styles["source_text"],
                        )
                    )

        story.append(Spacer(1, 6))

    # Build
    doc.build(story)
    return buf.getvalue()
