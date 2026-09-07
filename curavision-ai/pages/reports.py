

import streamlit as st
from datetime import date
import io
import uuid

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(
    page_title="Medical Reports • CuraVision AI",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

# --- theme ---
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at 20% 20%, #0f2447 0%, #060b1a 60%, #04060f 100%);
        color: #e8f0ff;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 26px 28px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
    }

    .report-row {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: background 0.15s ease;
    }
    .report-row:hover {
        background: rgba(255, 255, 255, 0.07);
    }

    .page-title {
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #7dd3fc, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .page-subtitle {
        color: #9db4d9;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    .risk-high {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        background: rgba(248, 113, 113, 0.15);
        border: 1px solid rgba(248, 113, 113, 0.5);
        color: #fca5a5;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .risk-low {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        background: rgba(74, 222, 128, 0.15);
        border: 1px solid rgba(74, 222, 128, 0.5);
        color: #86efac;
        font-weight: 600;
        font-size: 0.85rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 8px 22px;
        font-weight: 600;
        transition: transform 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4);
    }

    div[data-testid="stDownloadButton"] > button {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(125, 211, 252, 0.4);
        color: #bfe3ff;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- nav bar (same pattern as the rest of the app) ---
nav_left, nav_right = st.columns([1, 3])

with nav_left:
    st.markdown("## 🩺 CuraVision AI")

with nav_right:
    menu_items = [
        ("Home", "pages/home.py"),
        ("Assistant", "pages/assistant.py"),
        ("Detection", "pages/disease_detection.py"),
        ("Reports", "pages/reports.py"),
        ("Dashboard", "pages/dashboard.py"),
        ("Profile", "pages/profile.py"),
        ("Logout", None)
    ]
    nav_columns = st.columns(len(menu_items))

    for col, (label, target) in zip(nav_columns, menu_items):
        with col:
            if label == "Logout":
                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.switch_page("app.py")
            else:
                st.page_link(target, label=label)

st.divider()

# --- header ---
st.markdown('<div class="page-title">📋 Medical Reports</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Review past detection results, drill into details, '
    'or export any report as a PDF.</div>',
    unsafe_allow_html=True,
)

# --- mock / session data — replace with your DB or storage-backed fetch ---
if "reports" not in st.session_state:
    st.session_state.reports = [
        {
            "id": str(uuid.uuid4())[:8],
            "date": date(2026, 8, 4),
            "type": "Combined (Image + Symptoms)",
            "risk": "high",
            "confidence": 72.3,
            "summary": "Chest X-ray flagged density irregularity; symptoms included fever and shortness of breath.",
            "patient": "You",
        },
        {
            "id": str(uuid.uuid4())[:8],
            "date": date(2026, 7, 28),
            "type": "Symptom Checker",
            "risk": "low",
            "confidence": 18.5,
            "summary": "Mild headache and fatigue, short duration, low overall severity.",
            "patient": "You",
        },
        {
            "id": str(uuid.uuid4())[:8],
            "date": date(2026, 7, 15),
            "type": "Image Detection",
            "risk": "low",
            "confidence": 22.0,
            "summary": "Skin lesion photo analyzed, no abnormality detected.",
            "patient": "You",
        },
    ]


# --- PDF generation ---
# cached so a rerun (filter change, expander click, etc.) doesn't rebuild
# every visible report's PDF from scratch each time
@st.cache_data
def build_report_pdf(report: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleBlue", parent=styles["Title"], textColor=colors.HexColor("#1e3a8a")
    )
    heading_style = ParagraphStyle(
        "HeadingBlue", parent=styles["Heading2"], textColor=colors.HexColor("#1e40af")
    )
    body_style = styles["BodyText"]

    elements = []
    elements.append(Paragraph("CuraVision AI — Medical Report", title_style))
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph(f"Report ID: {report['id']}", body_style))
    elements.append(Paragraph(f"Date: {report['date'].strftime('%B %d, %Y')}", body_style))
    elements.append(Paragraph(f"Patient: {report['patient']}", body_style))
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph("Assessment Details", heading_style))
    table_data = [
        ["Detection Type", report["type"]],
        ["Risk Level", report["risk"].upper()],
        ["Confidence Score", f"{report['confidence']}%"],
    ]
    table = Table(table_data, colWidths=[6 * cm, 9 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#93c5fd")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#dbeafe")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph("Summary", heading_style))
    elements.append(Paragraph(report["summary"], body_style))
    elements.append(Spacer(1, 0.8 * cm))

    disclaimer = (
        "Disclaimer: This report was generated by an AI-assisted preliminary screening "
        "tool and does not constitute a medical diagnosis. Please consult a licensed "
        "healthcare professional for confirmation, further testing, and treatment."
    )
    elements.append(Paragraph(disclaimer, ParagraphStyle(
        "Disclaimer", parent=body_style, textColor=colors.HexColor("#6b7280"), fontSize=8.5
    )))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


# --- filter bar ---
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 2, 2])
with f1:
    type_filter = st.multiselect(
        "Detection type",
        ["Image Detection", "Symptom Checker", "Combined (Image + Symptoms)"],
        default=[],
        placeholder="All types",
    )
with f2:
    risk_filter = st.multiselect(
        "Risk level", ["high", "low"], default=[], placeholder="All risk levels"
    )
with f3:
    sort_order = st.selectbox("Sort by", ["Newest first", "Oldest first"])
st.markdown("</div>", unsafe_allow_html=True)

# --- apply filters ---
reports = st.session_state.reports.copy()
if type_filter:
    reports = [r for r in reports if r["type"] in type_filter]
if risk_filter:
    reports = [r for r in reports if r["risk"] in risk_filter]
reports.sort(key=lambda r: r["date"], reverse=(sort_order == "Newest first"))

# --- report list ---
if not reports:
    st.info("No reports match the selected filters.")
else:
    for report in reports:
        st.markdown('<div class="report-row">', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 2])

        with c1:
            st.markdown(f"**{report['date'].strftime('%b %d, %Y')}**")
            st.caption(f"ID: {report['id']}")
        with c2:
            st.write(report["type"])
        with c3:
            badge_class = "risk-high" if report["risk"] == "high" else "risk-low"
            st.markdown(f'<span class="{badge_class}">{report["risk"].upper()}</span>', unsafe_allow_html=True)
        with c4:
            st.write(f"{report['confidence']}%")
        with c5:
            pdf_bytes = build_report_pdf(report)
            st.download_button(
                "⬇ PDF",
                data=pdf_bytes,
                file_name=f"curavision_report_{report['id']}.pdf",
                mime="application/pdf",
                key=f"dl_{report['id']}",
            )

        with st.expander("View full summary"):
            st.write(report["summary"])
            st.caption("This report was generated by CuraVision AI's detection models.")

        st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.caption(
    " All reports on this page are AI-generated preliminary assessments, not medical "
    "diagnoses. Always consult a licensed healthcare professional."
)