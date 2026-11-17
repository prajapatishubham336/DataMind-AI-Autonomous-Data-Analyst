from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def make_pdf_report(df, profile, insights):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [Paragraph("DataMind AI - Dataset Analysis Report", 
                       styles["Title"]),
             Paragraph("Prepared for Shubham Prajapati", styles["Normal"]), 
             Spacer(1, 14)]
    story.append(Paragraph(f"Dataset size: {profile['rows']} rows × {profile['columns']} columns", 
                           styles["Heading2"]))
    story.append(Paragraph(f"Missing cells: {profile['missing_cells']} ({profile['missing_percent']:.2f}%)", styles["Normal"]))
    story.append(Paragraph(f"Duplicate rows: {profile['duplicate_rows']}", 
                           styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Key insights", styles["Heading2"]))
    for item in insights:
        clean = item.replace("**", "")
        story.append(Paragraph(clean, styles["BodyText"]))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Column profile", styles["Heading2"]))
    data = [list(profile["column_summary"].columns)] + profile["column_summary"].astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#263653")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), .4, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(table)
    doc.build(story)
    return buffer.getvalue()
