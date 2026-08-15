from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def generate_inspection_report(data: dict) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=data["report"]["title"],
        author="Garuda Kavach",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=24,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        spaceAfter=8,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=10,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalReport",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
    )

    warning_style = ParagraphStyle(
        "Warning",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
    )

    story = []

    # --------------------------------------------------
    # COVER PAGE
    # --------------------------------------------------

    story.append(Spacer(1, 45 * mm))

    story.append(
        Paragraph(
            "GARUDA KAVACH",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Bridge Inspection Report",
            subtitle_style,
        )
    )

    story.append(Spacer(1, 15 * mm))

    story.append(
        Paragraph(
            data["report"]["generated_for"],
            ParagraphStyle(
                "BridgeTitle",
                parent=title_style,
                fontSize=20,
            ),
        )
    )

    story.append(
        Paragraph(
            data["report"]["inspection_name"],
            subtitle_style,
        )
    )

    story.append(Spacer(1, 20 * mm))

    story.append(
        Paragraph(
            "AI-assisted infrastructure inspection report",
            subtitle_style,
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "1. Executive Summary",
            section_style,
        )
    )

    risk = data["risk_assessment"]

    summary_data = [
        ["Metric", "Value"],
        [
            "Finding Count",
            str(data["overview"]["finding_count"]),
        ],
        [
            "Media Count",
            str(data["overview"]["media_count"]),
        ],
        [
            "Highest Severity",
            str(risk["highest_severity"] or "None"),
        ],
        [
            "Risk Score",
            str(risk["risk_score"]),
        ],
        [
            "Risk Level",
            str(risk["risk_level"]).upper(),
        ],
        [
            "Priority",
            str(risk["priority"]).replace(
                "_",
                " ",
            ).upper(),
        ],
        [
            "Human Review",
            "REQUIRED"
            if risk["human_review_required"]
            else "NOT REQUIRED",
        ],
    ]

    table = Table(
        summary_data,
        colWidths=[65 * mm, 95 * mm],
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 10 * mm))

    if risk["human_review_required"]:
        story.append(
            Paragraph(
                "<b>ENGINEERING REVIEW REQUIRED:</b> "
                "This inspection contains findings requiring "
                "qualified human engineering review before "
                "structural decisions are made.",
                warning_style,
            )
        )

    story.append(PageBreak())

    # --------------------------------------------------
    # BRIDGE INFORMATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "2. Bridge Information",
            section_style,
        )
    )

    bridge = data["bridge"]

    bridge_data = [
        ["Field", "Value"],
        ["Bridge Name", bridge["name"]],
        ["Bridge Type", bridge["bridge_type"] or "N/A"],
        ["Location", bridge["location"] or "N/A"],
        ["Latitude", str(bridge["latitude"] or "N/A")],
        ["Longitude", str(bridge["longitude"] or "N/A")],
    ]

    bridge_table = Table(
        bridge_data,
        colWidths=[55 * mm, 105 * mm],
    )

    bridge_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    story.append(bridge_table)
    story.append(Spacer(1, 10 * mm))

    # --------------------------------------------------
    # INSPECTION INFORMATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "3. Inspection Information",
            section_style,
        )
    )

    inspection = data["inspection"]

    inspection_data = [
        ["Field", "Value"],
        ["Inspection Name", inspection["name"]],
        ["Inspection ID", str(inspection["id"])],
        ["Status", inspection["status"]],
        ["Inspection Date", str(inspection["created_at"])],
        ["Notes", inspection["notes"] or "N/A"],
    ]

    inspection_table = Table(
        inspection_data,
        colWidths=[55 * mm, 105 * mm],
    )

    inspection_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    story.append(inspection_table)

    story.append(PageBreak())

    # --------------------------------------------------
    # SEVERITY SUMMARY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "4. Finding Summary",
            section_style,
        )
    )

    severity = data["severity_summary"]

    severity_data = [
        ["Severity", "Count"],
        ["Critical", str(severity["critical"])],
        ["High", str(severity["high"])],
        ["Medium", str(severity["medium"])],
        ["Low", str(severity["low"])],
    ]

    severity_table = Table(
        severity_data,
        colWidths=[80 * mm, 80 * mm],
    )

    severity_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ])
    )

    story.append(severity_table)
    story.append(Spacer(1, 10 * mm))

    # --------------------------------------------------
    # FINDINGS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "5. Inspection Findings",
            section_style,
        )
    )

    for index, finding in enumerate(
        data["findings"],
        start=1,
    ):

        story.append(
            Paragraph(
                f"<b>Finding {index}: "
                f"{finding['defect_type']}</b>",
                normal_style,
            )
        )

        finding_data = [
            ["Field", "Value"],
            [
                "Defect Type",
                finding["defect_type"],
            ],
            [
                "Severity",
                finding["severity"],
            ],
            [
                "Confidence",
                (
                    str(finding["confidence"])
                    if finding["confidence"]
                    is not None
                    else "N/A"
                ),
            ],
            [
                "Component",
                finding["component_name"]
                or "Unassigned",
            ],
            [
                "Description",
                finding["description"]
                or "N/A",
            ],
        ]

        finding_table = Table(
            finding_data,
            colWidths=[55 * mm, 105 * mm],
        )

        finding_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#374151"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
            ])
        )

        story.append(finding_table)
        story.append(Spacer(1, 8 * mm))

    # --------------------------------------------------
    # COMPONENT CONDITION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "6. Component Condition",
            section_style,
        )
    )

    component_data = [
        [
            "Component",
            "Type",
            "Findings",
            "Risk",
            "Condition",
        ]
    ]

    for component in data["components"]:
        component_data.append([
            component["name"],
            component["type"],
            str(component["finding_count"]),
            str(component["risk_score"]),
            component["condition"],
        ])

    if len(component_data) == 1:
        component_data.append(
            ["None", "-", "0", "0", "no_findings"]
        )

    component_table = Table(
        component_data,
        colWidths=[
            42 * mm,
            30 * mm,
            25 * mm,
            25 * mm,
            38 * mm,
        ],
    )

    component_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#374151"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8,
            ),
        ])
    )

    story.append(component_table)

    story.append(PageBreak())

    # --------------------------------------------------
    # MEDIA
    # --------------------------------------------------

    story.append(
        Paragraph(
            "7. Inspection Media",
            section_style,
        )
    )

    media_data = [
        [
            "Filename",
            "Type",
            "Size",
            "Processing",
        ]
    ]

    for media in data["media"]:
        media_data.append([
            media["filename"],
            media["media_type"],
            (
                f"{media['file_size'] / 1024:.1f} KB"
                if media["file_size"]
                else "N/A"
            ),
            media["processing_status"],
        ])

    if len(media_data) == 1:
        media_data.append(
            ["No media", "-", "-", "-"]
        )

    media_table = Table(
        media_data,
        colWidths=[
            55 * mm,
            40 * mm,
            30 * mm,
            35 * mm,
        ],
    )

    media_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#374151"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8,
            ),
        ])
    )

    story.append(media_table)

    story.append(Spacer(1, 12 * mm))

    # --------------------------------------------------
    # RISK ASSESSMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "8. Risk Assessment",
            section_style,
        )
    )

    risk_data = [
        ["Metric", "Value"],
        ["Risk Score", str(risk["risk_score"])],
        ["Risk Level", str(risk["risk_level"]).upper()],
        ["Priority", str(risk["priority"]).replace("_", " ").upper()],
        [
            "Human Review",
            "REQUIRED"
            if risk["human_review_required"]
            else "NOT REQUIRED",
        ],
    ]

    risk_table = Table(
        risk_data,
        colWidths=[65 * mm, 95 * mm],
    )

    risk_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#374151"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTNAME",
                (0, 1),
                (0, -1),
                "Helvetica-Bold",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9,
            ),
        ])
    )

    story.append(risk_table)

    story.append(Spacer(1, 15 * mm))

    # --------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "9. Engineering Disclaimer",
            section_style,
        )
    )

    story.append(
        Paragraph(
            data["report_notes"],
            warning_style,
        )
    )

    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph(
            "Generated by Garuda Kavach",
            subtitle_style,
        )
    )

    # --------------------------------------------------
    # BUILD
    # --------------------------------------------------

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()