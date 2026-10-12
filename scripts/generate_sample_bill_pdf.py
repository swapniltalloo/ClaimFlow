import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sample_bills")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_hospital_bill_pdf(
    filename: str,
    hospital_name: str,
    hospital_address: str,
    bill_number: str,
    patient_name: str,
    patient_age_sex: str,
    uhid: str,
    ipd_no: str,
    admit_date: str,
    discharge_date: str,
    diagnosis: str,
    icd10: str,
    doctor_name: str,
    line_items: list,
    discharge_notes: str
):
    pdf_path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'HospitalTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1  # Center
    )

    subtitle_style = ParagraphStyle(
        'HospitalSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748b'),
        alignment=1
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # Hospital Header
    story.append(Paragraph(hospital_name, title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(hospital_address, subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>INPATIENT FINAL DISCHARGE INVOICE & CLINICAL SUMMARY</b>", ParagraphStyle('Sub', parent=subtitle_style, fontSize=10, textColor=colors.HexColor('#2563eb'))))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceBefore=1, spaceAfter=10))

    # Patient & Encounter Info Table
    patient_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {patient_name}", body_style),
            Paragraph(f"<b>Invoice / Bill No:</b> {bill_number}", body_style),
        ],
        [
            Paragraph(f"<b>UHID / Reg No:</b> {uhid}", body_style),
            Paragraph(f"<b>IPD Encounter:</b> {ipd_no}", body_style),
        ],
        [
            Paragraph(f"<b>Age / Gender:</b> {patient_age_sex}", body_style),
            Paragraph(f"<b>Treating Consultant:</b> {doctor_name}", body_style),
        ],
        [
            Paragraph(f"<b>Admission Date:</b> {admit_date}", body_style),
            Paragraph(f"<b>Discharge Date:</b> {discharge_date}", body_style),
        ],
        [
            Paragraph(f"<b>Primary Diagnosis:</b> {diagnosis} (ICD-10: {icd10})", bold_label),
            Paragraph(f"<b>Billing Type:</b> Insurance / Cashless Claim", body_style)
        ]
    ]

    t_patient = Table(patient_data, colWidths=[270, 260])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 14))

    # Itemized Billing Table
    story.append(Paragraph("ITEMIZED HOSPITAL CHARGES", section_header))

    table_data = [
        [
            Paragraph("<b>#</b>", bold_label),
            Paragraph("<b>Particulars / Service Description</b>", bold_label),
            Paragraph("<b>Category</b>", bold_label),
            Paragraph("<b>Qty</b>", bold_label),
            Paragraph("<b>Rate (INR)</b>", bold_label),
            Paragraph("<b>Total Amount (INR)</b>", bold_label)
        ]
    ]

    subtotal = 0.0
    for idx, item in enumerate(line_items, 1):
        line_tot = item["qty"] * item["rate"]
        subtotal += line_tot
        table_data.append([
            Paragraph(str(idx), body_style),
            Paragraph(f"<b>{item['desc']}</b>", body_style),
            Paragraph(item["cat"], body_style),
            Paragraph(str(item["qty"]), body_style),
            Paragraph(f"{item['rate']:,.2f}", body_style),
            Paragraph(f"<b>{line_tot:,.2f}</b>", body_style),
        ])

    # Total Row
    table_data.append([
        Paragraph("", body_style),
        Paragraph("<b>TOTAL CLAIMED / BILLED AMOUNT</b>", bold_label),
        Paragraph("", body_style),
        Paragraph("", body_style),
        Paragraph("", body_style),
        Paragraph(f"<b>INR {subtotal:,.2f}</b>", bold_label)
    ])

    col_widths = [25, 230, 85, 40, 75, 75]
    t_billing = Table(table_data, colWidths=col_widths)
    t_billing.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0f2fe')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_billing)
    story.append(Spacer(1, 14))

    # Clinical Summary & Notes
    story.append(Paragraph("PHYSICIAN CLINICAL DISCHARGE SUMMARY", section_header))
    story.append(Paragraph(discharge_notes, body_style))
    story.append(Spacer(1, 25))

    # Signatures
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Prepared By (Billing Dept)</b>", body_style),
            Paragraph("____________________________<br/><b>Verified By (Medical Supt.)</b>", body_style),
            Paragraph(f"____________________________<br/><b>Dr. {doctor_name}</b><br/>(Attending Surgeon)", body_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[175, 175, 180])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_sig)

    doc.build(story)
    print(f"Generated: {pdf_path}")
    return pdf_path


def main():
    # 1. Clean Bill (Apollo Super Specialty)
    build_hospital_bill_pdf(
        filename="apollo_clean_hospital_bill.pdf",
        hospital_name="APOLLO SUPER SPECIALTY HOSPITAL",
        hospital_address="154/11 Bannerghatta Road, Bangalore - 560076 | Phone: +91-80-2630-4050",
        bill_number="BILL-APO-2026-9811",
        patient_name="Priya Sharma",
        patient_age_sex="38 Yrs / Female",
        uhid="UHID-99214432",
        ipd_no="IPD-2026-4412",
        admit_date="2026-10-10 09:30 AM",
        discharge_date="2026-10-12 11:30 AM",
        diagnosis="Acute Appendicitis",
        icd10="K35.80",
        doctor_name="Sanjay Rao, MS, MCh",
        line_items=[
            {"desc": "Standard Private AC Room (2 Days)", "cat": "ROOM_ICU", "qty": 2.0, "rate": 4500.0},
            {"desc": "Laparoscopic appendectomy", "cat": "PROCEDURE", "qty": 1.0, "rate": 55000.0},
            {"desc": "IV Antibiotic Therapy (Meropenem)", "cat": "MEDICATION", "qty": 1.0, "rate": 4500.0},
            {"desc": "Pre-op & Post-op CBC, CRP & USG Abdomen", "cat": "INVESTIGATION", "qty": 1.0, "rate": 4500.0}
        ],
        discharge_notes="Patient Priya Sharma, 38F, presented with acute right lower quadrant abdominal tenderness and fever. Ultrasound confirmed acute appendicitis (ICD-10 K35.80). Underwent uncomplicated laparoscopic appendectomy (CPT-44970) under general anesthesia. Post-operative period uneventful, patient tolerated oral feeds, surgical wound clean, discharged in stable hemodynamic state."
    )

    # 2. Unbundled Disputed Bill (Max Healthcare)
    build_hospital_bill_pdf(
        filename="max_unbundled_hospital_bill.pdf",
        hospital_name="MAX HEALTHCARE MULTISPECIALTY",
        hospital_address="1, Press Enclave Road, Saket, New Delhi - 110017 | Phone: +91-11-2651-5050",
        bill_number="BILL-MAX-2026-7734",
        patient_name="Rohan Verma",
        patient_age_sex="45 Yrs / Male",
        uhid="UHID-88123004",
        ipd_no="IPD-2026-8921",
        admit_date="2026-10-08 10:00 AM",
        discharge_date="2026-10-10 02:00 PM",
        diagnosis="Acute Appendicitis with unbundled lavage",
        icd10="K35.80",
        doctor_name="Alok Mittal, MS, DNB",
        line_items=[
            {"desc": "Deluxe Private Room (Cap: INR 3,000/day)", "cat": "ROOM_ICU", "qty": 2.0, "rate": 5000.0},
            {"desc": "Laparoscopic appendectomy", "cat": "PROCEDURE", "qty": 1.0, "rate": 55000.0},
            {"desc": "Peritoneal lavage (Unbundled)", "cat": "PROCEDURE", "qty": 1.0, "rate": 14500.0},
            {"desc": "Disposable Trocar Pack & Surgical Consumable Kit", "cat": "CONSUMABLE", "qty": 1.0, "rate": 13000.0}
        ],
        discharge_notes="Patient admitted for acute appendicitis. Laparoscopic appendectomy performed. Peritoneal irrigation and lavage carried out during surgery. Billed separate peritoneal lavage line item in addition to comprehensive appendectomy surgical fee."
    )


if __name__ == "__main__":
    main()
