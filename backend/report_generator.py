"""
Official MoSPI-styled MPLADS Investigation Dossier & Verification Brief Generator.
Generates an auditable PDF dossier using ReportLab with exact evidentiary findings.
Prominently identifies demo records as synthetic for prototype evaluation.
"""

import io
import json
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_pdf_report(project: dict, risk: dict) -> bytes:
    """Generate official investigation dossier PDF in memory."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0f172a"),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e3a8a"),
        alignment=1
    )
    demo_warning_style = ParagraphStyle(
        'DemoWarning',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#b91c1c"),
        alignment=1
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )
    section_head = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=8,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    elements = []

    # 1. Header Banner & Prominent Synthetic Disclaimer
    elements.append(Paragraph("NIRIKSHAN AI • MPLADS DECISION SUPPORT PROTOTYPE", subtitle_style))
    elements.append(Spacer(1, 2))
    elements.append(Paragraph("INVESTIGATION DOSSIER & VERIFICATION BRIEF", title_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph("DEMO / SYNTHETIC DATA — FOR PROTOTYPE EVALUATION ONLY", demo_warning_style))
    elements.append(Paragraph("NIRIKSHAN does not declare a project fraudulent. It identifies unusual patterns and prioritizes projects for human verification.", disclaimer_style))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f172a"), spaceBefore=2, spaceAfter=8))

    # 2. Risk Score & Priority Callout Box
    score = risk.get("overall_risk_score", 0.0)
    level = risk.get("risk_level", "LOW")
    if level == "CRITICAL":
        badge_color = colors.HexColor("#b91c1c")
        badge_bg = colors.HexColor("#fef2f2")
    elif level == "HIGH":
        badge_color = colors.HexColor("#c2410c")
        badge_bg = colors.HexColor("#fff7ed")
    elif level == "MEDIUM":
        badge_color = colors.HexColor("#b45309")
        badge_bg = colors.HexColor("#fefce8")
    else:
        badge_color = colors.HexColor("#047857")
        badge_bg = colors.HexColor("#ecfdf5")

    risk_table_data = [
        [
            Paragraph(f"<b>PRIORITY VERIFICATION STATUS:</b> <font color='{badge_color.hexval()}'><b>{level} RISK ({score:.1f}/100)</b></font>", bold_body),
            Paragraph(f"<b>Dossier Ref:</b> {project.get('project_id')} | <b>Generated:</b> {datetime.now(timezone.utc).strftime('%d-%b-%Y %H:%M UTC')}", body_style)
        ],
        [
            Paragraph(f"<b>Recommended Action:</b> {risk.get('recommended_action', 'Prioritize for document/site verification')}", bold_body),
            Paragraph(f"<b>Audit Determination:</b> Requires Verification (Decision-Support Prioritization)", body_style)
        ]
    ]
    t_risk = Table(risk_table_data, colWidths=[3.6 * inch, 3.6 * inch])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), badge_bg),
        ('BOX', (0, 0), (-1, -1), 1, badge_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t_risk)
    elements.append(Spacer(1, 8))

    # 3. Project Information Table
    elements.append(Paragraph("1. Project Identification & Administrative Profile", section_head))
    proj_table_data = [
        [Paragraph("<b>Project ID:</b>", bold_body), Paragraph(f"{project.get('project_id')} (SYNTHETIC_DEMO)", body_style),
         Paragraph("<b>Work Category:</b>", bold_body), Paragraph(str(project.get("work_category")), body_style)],
        [Paragraph("<b>Work Title:</b>", bold_body), Paragraph(str(project.get("work_title")), body_style),
         Paragraph("<b>Project Status:</b>", bold_body), Paragraph(str(project.get("status")), bold_body)],
        [Paragraph("<b>State / District:</b>", bold_body), Paragraph(f"{project.get('state')} / {project.get('district')}", body_style),
         Paragraph("<b>Constituency:</b>", bold_body), Paragraph(str(project.get("constituency")), body_style)],
        [Paragraph("<b>Hon'ble MP:</b>", bold_body), Paragraph(str(project.get("mp_name")), body_style),
         Paragraph("<b>Implementing Agency:</b>", bold_body), Paragraph(str(project.get("implementing_agency")), body_style)],
        [Paragraph("<b>GIS Coordinates:</b>", bold_body), Paragraph(f"Lat: {project.get('latitude')}, Lon: {project.get('longitude')}", body_style),
         Paragraph("<b>Sanction Date:</b>", bold_body), Paragraph(str(project.get("sanction_date")), body_style)],
        [Paragraph("<b>Expected Completion:</b>", bold_body), Paragraph(str(project.get("expected_completion_date")), body_style),
         Paragraph("<b>Actual Completion:</b>", bold_body), Paragraph(str(project.get("actual_completion_date") or "Pending Completion"), body_style)]
    ]
    t_proj = Table(proj_table_data, colWidths=[1.5 * inch, 2.1 * inch, 1.6 * inch, 2.0 * inch])
    t_proj.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_proj)
    elements.append(Spacer(1, 8))

    # 4. Financial Breakdown Table
    elements.append(Paragraph("2. Financial Status & Utilization Metrics", section_head))
    sanction_val = float(project.get("sanction_amount", 0.0))
    expenditure_val = float(project.get("expenditure_amount", 0.0))
    util_rate = (expenditure_val / sanction_val * 100.0) if sanction_val > 0 else 0.0

    fin_table_data = [
        [Paragraph("<b>Sanctioned Amount (₹):</b>", bold_body), Paragraph(f"₹ {sanction_val:,.2f}", bold_body),
         Paragraph("<b>Total Expenditure (₹):</b>", bold_body), Paragraph(f"₹ {expenditure_val:,.2f}", bold_body)],
        [Paragraph("<b>Fund Utilization:</b>", bold_body), Paragraph(f"{util_rate:.1f} %", body_style),
         Paragraph("<b>Payment Tranches:</b>", bold_body), Paragraph(f"{project.get('number_of_payments', 1)} released", body_style)]
    ]
    t_fin = Table(fin_table_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch])
    t_fin.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_fin)
    elements.append(Spacer(1, 8))

    # 5. Multi-Signal Anomaly Breakdown
    elements.append(Paragraph("3. Multi-Signal AI Anomaly Analysis & Quantified Evidence", section_head))
    evidence_dict = risk.get("evidence", {})
    if isinstance(evidence_dict, str):
        try:
            evidence_dict = json.loads(evidence_dict)
        except Exception:
            evidence_dict = {}

    anom_table_data = [
        [Paragraph("<b>Signal Dimension</b>", bold_body), Paragraph("<b>Risk Score</b>", bold_body), Paragraph("<b>Benchmark / Evidentiary Findings</b>", bold_body)],
        [Paragraph("Cost Anomaly", body_style), Paragraph(f"{risk.get('cost_risk_score', 0):.1f} / 100", bold_body),
         Paragraph(f"Sanction: ₹{sanction_val:,.0f} vs Peer Median: ₹{evidence_dict.get('peer_median_cost', 0):,.0f} (Deviation: {evidence_dict.get('cost_deviation_pct', 0):+.1f}%)", body_style)],
        [Paragraph("Timeline Anomaly", body_style), Paragraph(f"{risk.get('timeline_risk_score', 0):.1f} / 100", bold_body),
         Paragraph(f"Elapsed: {evidence_dict.get('elapsed_months', 0):.0f} mo vs Planned: {evidence_dict.get('expected_months', 0):.0f} mo (Delay: {evidence_dict.get('delay_percentage', 0):+.1f}%)", body_style)],
        [Paragraph("Potential Spatial & Description Overlap", body_style), Paragraph(f"{risk.get('overlap_risk_score', 0):.1f} / 100", bold_body),
         Paragraph("Candidate match requiring verification. This is not evidence of duplicate work.", body_style)],
        [Paragraph("Expenditure Pattern", body_style), Paragraph(f"{risk.get('expenditure_risk_score', 0):.1f} / 100", bold_body),
         Paragraph(f"Utilization {evidence_dict.get('utilization_pct', 0):.1f}% across {evidence_dict.get('payment_tranches', 1)} tranches", body_style)],
        [Paragraph("Agency Concentration", body_style), Paragraph(f"{risk.get('agency_risk_score', 0):.1f} / 100", bold_body),
         Paragraph(f"Agency portfolio: {evidence_dict.get('agency_projects_count', 0)} works; Average Project Value Deviation: {evidence_dict.get('agency_cost_premium_pct', 0):+.1f}%", body_style)],
        [Paragraph("Regulatory Compliance", body_style), Paragraph(f"{risk.get('compliance_risk_score', 0):.1f} / 100", bold_body),
         Paragraph(str(evidence_dict.get('compliance_violations') or "All statutory guidelines & data completeness checks passed"), body_style)],
    ]
    t_anom = Table(anom_table_data, colWidths=[2.2 * inch, 1.1 * inch, 3.9 * inch])
    t_anom.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_anom)
    elements.append(Spacer(1, 8))

    # 6. Top Contributing Factors & Recommended Auditor Actions
    elements.append(Paragraph("4. Key Observations & Prescribed Auditor Steps", section_head))
    factors = risk.get("contributing_factors", [])
    if isinstance(factors, str):
        try:
            factors = json.loads(factors)
        except Exception:
            factors = []

    if factors:
        factor_items = []
        for i, f in enumerate(factors[:4], 1):
            dim_name = f.get('dimension', '')
            if dim_name == "Potential Overlap":
                dim_name = "Potential Spatial & Description Overlap"
            factor_items.append(Paragraph(f"<b>{i}. {dim_name}:</b> {f.get('flag_note')}", body_style))
            factor_items.append(Spacer(1, 2))
        for item in factor_items:
            elements.append(item)
    else:
        elements.append(Paragraph("No critical anomaly factors identified. Project parameters conform to standard distributions.", body_style))

    elements.append(Spacer(1, 10))

    # 7. Official Sign-Off Block
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=5, spaceAfter=10))
    signoff_data = [
        [Paragraph("<b>Investigating Auditor Signature:</b>", bold_body), Paragraph("<b>Superintending Officer Review:</b>", bold_body)],
        [Spacer(1, 15), Spacer(1, 15)],
        [Paragraph("Name: _______________________________", body_style), Paragraph("Name: _______________________________", body_style)],
        [Paragraph("Designation: ________________________", body_style), Paragraph("Designation: ________________________", body_style)],
        [Paragraph("Date: _______________________________", body_style), Paragraph("Date: _______________________________", body_style)]
    ]
    t_sign = Table(signoff_data, colWidths=[3.6 * inch, 3.6 * inch])
    t_sign.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t_sign)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
