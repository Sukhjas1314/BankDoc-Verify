from pathlib import Path


def generate_validation_report(validation_run, issues, destination: str | Path) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(str(destination), pagesize=letter)
    story = [
        Paragraph("BankDoc Verify Validation Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"File: {validation_run.uploaded_file.file_name}", styles["Normal"]),
        Paragraph(f"Status: {validation_run.status.upper()}", styles["Normal"]),
        Paragraph(
            f"Checks: {validation_run.passed_checks} passed / {validation_run.failed_checks} failed / {validation_run.total_checks} total",
            styles["Normal"],
        ),
        Spacer(1, 16),
        Paragraph("Issues and Recommendations", styles["Heading2"]),
    ]
    data = [["Type", "Severity", "Description", "Expected", "Actual"]]
    if issues:
        for issue in issues:
            data.append(
                [
                    issue.issue_type,
                    issue.severity,
                    issue.description,
                    issue.expected_value or "-",
                    issue.actual_value or "-",
                ]
            )
    else:
        data.append(["None", "-", "No discrepancies were found.", "-", "-"])
    table = Table(data, repeatRows=1, colWidths=[88, 58, 190, 80, 80])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 16))
    story.append(Paragraph("Recommendation: review high severity items before distributing this banking report.", styles["Normal"]))
    document.build(story)
    return destination
