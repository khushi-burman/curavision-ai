import io
import uuid
from datetime import datetime

import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from theme import (
    inject_theme,
    top_nav,
    page_header,
    risk_badge,
    footnote,
    panel,
)
from supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Reports • CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# AUTHENTICATION
# =========================================================

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")


user_id = st.session_state.get("user_id")

if not user_id:
    st.error("User session not found. Please sign in again.")
    st.stop()


# =========================================================
# THEME
# =========================================================

REPORTS_CSS = """
div[class*="st-key-reportrow_"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 14px 18px 2px 18px;
    margin-bottom: 10px;
}
"""

inject_theme(REPORTS_CSS)
top_nav()

page_header(
    "Medical reports",
    "Review past detection results, drill into details, or export any report as a PDF.",
    "file",
)


# =========================================================
# FETCH REPORTS
# =========================================================

def fetch_reports():
    response = (
        supabase
        .table("medical_reports")
        .select("*")
        .eq("user_id", user_id)
        .order("report_date", desc=True)
        .execute()
    )

    return response.data or []


# =========================================================
# FETCH HEALTH SCANS
# =========================================================

def fetch_health_scans():
    response = (
        supabase
        .table("health_scans")
        .select("*")
        .eq("user_id", user_id)
        .order("scan_date", desc=True)
        .execute()
    )

    return response.data or []


# =========================================================
# PDF GENERATION
# =========================================================

def build_report_pdf(report: dict) -> bytes:

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleTeal",
        parent=styles["Title"],
        textColor=colors.HexColor("#1F4E42"),
        fontName="Helvetica-Bold",
    )

    heading_style = ParagraphStyle(
        "HeadingTeal",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#2F6F5E"),
    )

    body_style = styles["BodyText"]

    elements = []

    elements.append(
        Paragraph(
            "CuraVision AI — Medical Report",
            title_style,
        )
    )

    elements.append(
        Spacer(1, 0.4 * cm)
    )

    elements.append(
        Paragraph(
            f"Report ID: {report.get('id', 'N/A')}",
            body_style,
        )
    )

    report_date = report.get("report_date")

    if report_date:
        try:
            formatted_date = datetime.fromisoformat(
                report_date.replace("Z", "+00:00")
            ).strftime("%B %d, %Y")
        except Exception:
            formatted_date = str(report_date)
    else:
        formatted_date = "N/A"

    elements.append(
        Paragraph(
            f"Date: {formatted_date}",
            body_style,
        )
    )

    elements.append(
        Paragraph(
            f"Patient: {st.session_state.get('user_name', 'User')}",
            body_style,
        )
    )

    elements.append(
        Spacer(1, 0.6 * cm)
    )

    elements.append(
        Paragraph(
            "Assessment Details",
            heading_style,
        )
    )

    risk = report.get("risk_level") or "N/A"

    confidence = report.get("confidence")

    if confidence is not None:
        try:
            confidence_text = f"{float(confidence) * 100:.2f}%"
        except Exception:
            confidence_text = str(confidence)
    else:
        confidence_text = "N/A"

    table_data = [
        [
            "Detection Type",
            report.get("report_type", "N/A"),
        ],
        [
            "Risk Level",
            str(risk).upper(),
        ],
        [
            "Confidence Score",
            confidence_text,
        ],
    ]

    table = Table(
        table_data,
        colWidths=[6 * cm, 9 * cm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#B9BFAE"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#E1EBE4"),
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(table)

    elements.append(
        Spacer(1, 0.6 * cm)
    )

    elements.append(
        Paragraph(
            "Summary",
            heading_style,
        )
    )

    elements.append(
        Paragraph(
            report.get("summary") or "No summary available.",
            body_style,
        )
    )

    elements.append(
        Spacer(1, 0.8 * cm)
    )

    disclaimer = (
        "Disclaimer: This report was generated by an AI-assisted "
        "preliminary screening tool and does not constitute a medical "
        "diagnosis. Please consult a licensed healthcare professional "
        "for confirmation, further testing, and treatment."
    )

    elements.append(
        Paragraph(
            disclaimer,
            ParagraphStyle(
                "Disclaimer",
                parent=body_style,
                textColor=colors.HexColor("#57635C"),
                fontSize=8.5,
            ),
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer.read()


# =========================================================
# CREATE REPORT FROM HEALTH SCAN
# =========================================================

def create_report_from_scan(scan: dict):

    report_id = str(uuid.uuid4())

    detection_type = scan.get(
        "detection_type",
        "unknown",
    )

    if detection_type == "skin":
        report_type = "Image Detection"

        predicted_class = (
            scan.get("predicted_class")
            or "Unknown"
        )

        confidence = scan.get(
            "model_confidence"
        )

        summary = (
            f"Skin lesion analysis completed. "
            f"Predicted class: {predicted_class}."
        )

        risk_level = scan.get("risk_level")

    elif detection_type == "chronic_risk":
        report_type = "Chronic Disease Risk"

        prediction = scan.get(
            "prediction"
        )

        risk_level = (
            scan.get("risk_level")
            or (
                "high"
                if prediction == 1
                else "low"
            )
        )

        risk_score = scan.get(
            "risk_score"
        )

        if risk_score is not None:
            summary = (
                "Chronic disease risk screening completed. "
                f"Risk score: {float(risk_score) * 100:.2f}%."
            )
        else:
            summary = (
                "Chronic disease risk screening completed."
            )

        confidence = None

    else:
        report_type = "Combined Assessment"

        risk_level = scan.get(
            "risk_level"
        )

        confidence = scan.get(
            "model_confidence"
        )

        summary = (
            "Combined CuraVision AI assessment completed."
        )

    report = {
        "id": report_id,
        "user_id": user_id,
        "scan_id": scan.get("id"),
        "report_date": datetime.now().isoformat(),
        "report_type": report_type,
        "risk_level": risk_level,
        "confidence": confidence,
        "summary": summary,
    }

    pdf_bytes = build_report_pdf(report)

    file_name = (
        f"curavision_report_{report_id}.pdf"
    )

    storage_path = (
        f"{user_id}/reports/{file_name}"
    )

    # -----------------------------------------------------
    # Upload PDF to Supabase Storage
    # -----------------------------------------------------

    supabase.storage \
        .from_("curavision-reports") \
        .upload(
            storage_path,
            pdf_bytes,
            {
                "content-type": "application/pdf",
                "upsert": "false",
            },
        )

    # -----------------------------------------------------
    # Save report metadata to database
    # -----------------------------------------------------

    db_report = {
        "user_id": user_id,
        "scan_id": scan.get("id"),
        "report_type": report_type,
        "risk_level": risk_level,
        "confidence": confidence,
        "summary": summary,
        "file_name": file_name,
        "storage_path": storage_path,
    }

    response = (
        supabase
        .table("medical_reports")
        .insert(db_report)
        .execute()
    )

    return pdf_bytes, file_name, response.data


# =========================================================
# FILTER BAR
# =========================================================

with panel("flat"):

    f1, f2, f3 = st.columns([2, 2, 2])

    reports = fetch_reports()

    report_types = sorted(
        list(
            {
                r.get("report_type")
                for r in reports
                if r.get("report_type")
            }
        )
    )

    with f1:

        type_filter = st.multiselect(
            "Detection type",
            report_types,
            default=[],
            placeholder="All types",
        )

    with f2:

        risk_filter = st.multiselect(
            "Risk level",
            ["high", "low"],
            default=[],
            placeholder="All risk levels",
        )

    with f3:

        sort_order = st.selectbox(
            "Sort by",
            [
                "Newest first",
                "Oldest first",
            ],
        )


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_reports = reports.copy()

if type_filter:

    filtered_reports = [
        r
        for r in filtered_reports
        if r.get("report_type") in type_filter
    ]

if risk_filter:

    filtered_reports = [
        r
        for r in filtered_reports
        if r.get("risk_level") in risk_filter
    ]

filtered_reports.sort(
    key=lambda r: r.get("report_date") or "",
    reverse=(
        sort_order == "Newest first"
    ),
)


# =========================================================
# GENERATE NEW REPORT FROM HEALTH SCAN
# =========================================================

st.subheader("Generate a new report")

scans = fetch_health_scans()

if not scans:

    st.info(
        "No health scans are available yet. "
        "Complete a skin or chronic-risk scan first."
    )

else:

    scan_options = {}

    for scan in scans:

        scan_date = scan.get(
            "scan_date",
            "Unknown date",
        )

        detection_type = scan.get(
            "detection_type",
            "Unknown",
        )

        predicted_class = scan.get(
            "predicted_class"
        )

        label = (
            f"{scan_date[:10]} — "
            f"{detection_type}"
        )

        if predicted_class:
            label += (
                f" — {predicted_class}"
            )

        scan_options[label] = scan

    selected_label = st.selectbox(
        "Select a health scan",
        list(scan_options.keys()),
    )

    selected_scan = scan_options[
        selected_label
    ]

    if st.button(
        "Generate medical report",
        type="primary",
    ):

        try:

            with st.spinner(
                "Generating and saving your medical report..."
            ):

                pdf_bytes, file_name, _ = (
                    create_report_from_scan(
                        selected_scan
                    )
                )

            st.success(
                "Medical report generated and saved successfully."
            )

            st.download_button(
                "Download generated PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                key=f"new_report_{file_name}",
            )

            st.rerun()

        except Exception as exc:

            st.error(
                f"Could not generate report: {exc}"
            )


# =========================================================
# REPORT LIST
# =========================================================

st.subheader("Saved reports")

if not filtered_reports:

    st.info(
        "No reports match the selected filters."
    )

else:

    for report in filtered_reports:

        report_id = report.get(
            "id",
            str(uuid.uuid4()),
        )

        with st.container(
            key=f"reportrow_{report_id}"
        ):

            c1, c2, c3, c4, c5 = st.columns(
                [2, 3, 2, 2, 2]
            )

            with c1:

                report_date = report.get(
                    "report_date",
                    "",
                )

                try:

                    formatted_date = (
                        datetime.fromisoformat(
                            report_date.replace(
                                "Z",
                                "+00:00",
                            )
                        ).strftime(
                            "%b %d, %Y"
                        )
                    )

                except Exception:

                    formatted_date = (
                        str(report_date)[:10]
                    )

                st.markdown(
                    f"**{formatted_date}**"
                )

                st.caption(
                    f"ID: {report_id}"
                )

            with c2:

                st.write(
                    report.get(
                        "report_type",
                        "Unknown",
                    )
                )

            with c3:

                risk = report.get(
                    "risk_level"
                )

                if risk:

                    st.markdown(
                        risk_badge(risk),
                        unsafe_allow_html=True,
                    )

                else:

                    st.write("N/A")

            with c4:

                confidence = report.get(
                    "confidence"
                )

                if confidence is not None:

                    st.write(
                        f"{float(confidence) * 100:.2f}%"
                    )

                else:

                    st.write("N/A")

            with c5:

                storage_path = report.get(
                    "storage_path"
                )

                if storage_path:

                    try:

                        pdf_response = (
                            supabase.storage
                            .from_("curavision-reports")
                            .download(
                                storage_path
                            )
                        )

                        st.download_button(
                            "Download PDF",
                            data=pdf_response,
                            file_name=report.get(
                                "file_name",
                                f"report_{report_id}.pdf",
                            ),
                            mime="application/pdf",
                            key=f"dl_{report_id}",
                        )

                    except Exception:

                        st.caption(
                            "PDF unavailable"
                        )

                else:

                    st.caption(
                        "No PDF file"
                    )

            with st.expander(
                "View full summary"
            ):

                st.write(
                    report.get(
                        "summary",
                        "No summary available.",
                    )
                )

                st.caption(
                    "This report was generated by "
                    "CuraVision AI's detection models."
                )


# =========================================================
# FOOTNOTE
# =========================================================

footnote(
    "All reports on this page are AI-generated preliminary "
    "assessments, not medical diagnoses. Always consult a "
    "licensed healthcare professional."
)