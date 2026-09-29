import streamlit as st
import pandas as pd

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet

from theme import (
    inject_theme,
    top_nav,
    page_header,
    risk_badge,
    panel,
)

from supabase_client import supabase


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Reports | CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# AUTH CHECK
# ============================================================

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")


# ============================================================
# THEME / NAVIGATION
# ============================================================

inject_theme()
top_nav()

page_header(
    "Health Reports",
    "View your previous skin-lesion assessments and chronic-risk screening results.",
    "file",
)


# ============================================================
# GET CURRENT USER
# ============================================================

user_id = st.session_state.get("user_id")


if not user_id:

    try:

        session_response = supabase.auth.get_session()

        if (
            session_response
            and session_response.session
            and session_response.session.user
        ):

            user_id = str(
                session_response.session.user.id
            )

            st.session_state.user_id = user_id

    except Exception as exc:

        st.error(
            f"Could not retrieve your Supabase session: {exc}"
        )


if not user_id:

    st.error(
        "No logged-in user was found. Please log in again."
    )

    if st.button("Go to Login"):
        st.switch_page("pages/login.py")

    st.stop()


# ============================================================
# FETCH REPORTS FROM SUPABASE
# ============================================================

@st.cache_data(ttl=10)
def get_health_scans(current_user_id):

    response = (
        supabase
        .table("health_scans")
        .select("*")
        .eq("user_id", current_user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


try:

    reports = get_health_scans(user_id)

except Exception as exc:

    st.error(
        f"Could not load reports from Supabase: {exc}"
    )

    st.stop()


# ============================================================
# EMPTY STATE
# ============================================================

if not reports:

    with panel():

        st.info(
            "No health reports are available yet."
        )

        st.markdown(
            """
            Run a skin-lesion assessment or chronic-risk
            screening to create your first report.
            """
        )

    st.stop()


# ============================================================
# SEPARATE REPORT TYPES
# ============================================================

skin_reports = [
    report
    for report in reports
    if report.get("detection_type") == "skin"
]


chronic_reports = [
    report
    for report in reports
    if report.get("detection_type") == "chronic_risk"
]


# ============================================================
# SUMMARY
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Reports",
        len(reports),
    )


with col2:

    st.metric(
        "Skin Assessments",
        len(skin_reports),
    )


with col3:

    st.metric(
        "Chronic-Risk Assessments",
        len(chronic_reports),
    )


st.divider()


# ============================================================
# FILTER
# ============================================================

filter_option = st.selectbox(
    "Filter reports",
    [
        "All Reports",
        "Skin Assessments",
        "Chronic-Risk Assessments",
    ],
)


if filter_option == "Skin Assessments":

    filtered_reports = skin_reports

elif filter_option == "Chronic-Risk Assessments":

    filtered_reports = chronic_reports

else:

    filtered_reports = reports


# ============================================================
# PDF GENERATOR
# ============================================================

def create_report_pdf(report):

    """
    Generate a downloadable PDF for one CuraVision AI report.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []

    detection_type = report.get(
        "detection_type"
    )

    created_at = (
        report.get("created_at")
        or report.get("scan_date")
        or "N/A"
    )

    # ========================================================
    # PDF TITLE
    # ========================================================

    story.append(
        Paragraph(
            "CuraVision AI — Health Report",
            title_style,
        )
    )

    story.append(
        Spacer(1, 15)
    )


    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    report_id = escape(
        str(report.get("id", "N/A"))
    )

    report_date = escape(
        str(created_at)
    )

    story.append(
        Paragraph(
            f"<b>Report ID:</b> {report_id}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> {report_date}",
            body_style,
        )
    )

    story.append(
        Spacer(1, 15)
    )


    # ========================================================
    # SKIN REPORT
    # ========================================================

    if detection_type == "skin":

        story.append(
            Paragraph(
                "Skin Lesion Assessment",
                heading_style,
            )
        )

        story.append(
            Spacer(1, 8)
        )


        # ----------------------------------------------------
        # Predicted class
        # ----------------------------------------------------

        predicted_class = escape(
            str(
                report.get(
                    "predicted_class",
                    "N/A"
                )
            )
        )

        story.append(
            Paragraph(
                f"<b>Predicted Class:</b> "
                f"{predicted_class}",
                body_style,
            )
        )


        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        confidence = report.get(
            "model_confidence"
        )

        if confidence is not None:

            try:

                confidence_value = float(
                    confidence
                )

                if confidence_value <= 1:
                    confidence_value *= 100

                confidence_text = (
                    f"{confidence_value:.2f}%"
                )

            except (
                TypeError,
                ValueError,
            ):

                confidence_text = escape(
                    str(confidence)
                )

        else:

            confidence_text = "N/A"


        story.append(
            Paragraph(
                f"<b>Model Confidence:</b> "
                f"{confidence_text}",
                body_style,
            )
        )

        story.append(
            Spacer(1, 10)
        )


        # ----------------------------------------------------
        # Symptoms
        # ----------------------------------------------------

        symptoms = report.get(
            "symptoms_description"
        )

        if symptoms:

            story.append(
                Paragraph(
                    "Symptoms / Sensations",
                    heading_style,
                )
            )

            symptoms_text = escape(
                str(symptoms)
            ).replace(
                "\n",
                "<br/>"
            )

            story.append(
                Paragraph(
                    symptoms_text,
                    body_style,
                )
            )

            story.append(
                Spacer(1, 10)
            )


        # ----------------------------------------------------
        # Integrated diagnosis
        # ----------------------------------------------------

        diagnosis = report.get(
            "integrated_diagnosis"
        )

        if diagnosis:

            story.append(
                Paragraph(
                    "Clinical Assessment",
                    heading_style,
                )
            )

            diagnosis_text = escape(
                str(diagnosis)
            ).replace(
                "\n",
                "<br/>"
            )

            story.append(
                Paragraph(
                    diagnosis_text,
                    body_style,
                )
            )


    # ========================================================
    # CHRONIC-RISK REPORT
    # ========================================================

    elif detection_type == "chronic_risk":

        story.append(
            Paragraph(
                "Chronic Disease Risk Assessment",
                heading_style,
            )
        )

        story.append(
            Spacer(1, 8)
        )


        # ----------------------------------------------------
        # Risk level
        # ----------------------------------------------------

        risk_level = escape(
            str(
                report.get(
                    "risk_level",
                    "N/A"
                )
            )
        )

        story.append(
            Paragraph(
                f"<b>Risk Level:</b> "
                f"{risk_level}",
                body_style,
            )
        )


        # ----------------------------------------------------
        # Risk score
        # ----------------------------------------------------

        risk_score = report.get(
            "risk_score"
        )

        if risk_score is not None:

            try:

                score = float(
                    risk_score
                )

                if score <= 1:
                    score *= 100

                score_text = (
                    f"{score:.2f}%"
                )

            except (
                TypeError,
                ValueError,
            ):

                score_text = escape(
                    str(risk_score)
                )

        else:

            score_text = "N/A"


        story.append(
            Paragraph(
                f"<b>Predicted Risk Score:</b> "
                f"{score_text}",
                body_style,
            )
        )


        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = escape(
            str(
                report.get(
                    "prediction",
                    "N/A"
                )
            )
        )

        story.append(
            Paragraph(
                f"<b>Model Prediction:</b> "
                f"{prediction}",
                body_style,
            )
        )

        story.append(
            Spacer(1, 10)
        )


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        summary = report.get(
            "summary"
        )

        if summary:

            story.append(
                Paragraph(
                    "Summary",
                    heading_style,
                )
            )

            summary_text = escape(
                str(summary)
            ).replace(
                "\n",
                "<br/>"
            )

            story.append(
                Paragraph(
                    summary_text,
                    body_style,
                )
            )

            story.append(
                Spacer(1, 10)
            )


        # ----------------------------------------------------
        # Findings
        # ----------------------------------------------------

        findings = report.get(
            "findings"
        )

        if findings:

            story.append(
                Paragraph(
                    "Clinical Findings",
                    heading_style,
                )
            )


            if isinstance(
                findings,
                list,
            ):

                for finding in findings:

                    finding_text = escape(
                        str(finding)
                    )

                    story.append(
                        Paragraph(
                            f"• {finding_text}",
                            body_style,
                        )
                    )

            else:

                findings_text = escape(
                    str(findings)
                ).replace(
                    "\n",
                    "<br/>"
                )

                story.append(
                    Paragraph(
                        findings_text,
                        body_style,
                    )
                )


            story.append(
                Spacer(1, 10)
            )


        # ----------------------------------------------------
        # Recommended actions
        # ----------------------------------------------------

        actions = report.get(
            "recommended_actions"
        )

        if actions:

            story.append(
                Paragraph(
                    "Recommended Actions",
                    heading_style,
                )
            )


            if isinstance(
                actions,
                list,
            ):

                for action in actions:

                    action_text = escape(
                        str(action)
                    )

                    story.append(
                        Paragraph(
                            f"• {action_text}",
                            body_style,
                        )
                    )

            else:

                actions_text = escape(
                    str(actions)
                ).replace(
                    "\n",
                    "<br/>"
                )

                story.append(
                    Paragraph(
                        actions_text,
                        body_style,
                    )
                )


    # ========================================================
    # DISCLAIMER
    # ========================================================

    story.append(
        Spacer(1, 20)
    )

    disclaimer = (
        "This report is generated by CuraVision AI "
        "and is intended for screening and support purposes. "
        "It is not a medical diagnosis."
    )

    story.append(
        Paragraph(
            disclaimer,
            body_style,
        )
    )


    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# REPORT CARDS
# ============================================================

for report in filtered_reports:

    detection_type = report.get(
        "detection_type"
    )

    created_at = report.get(
        "created_at"
    )

    scan_date = report.get(
        "scan_date"
    )

    report_date = (
        created_at
        or scan_date
        or "Unknown date"
    )


    # ========================================================
    # SKIN REPORT
    # ========================================================

    if detection_type == "skin":

        predicted_class = report.get(
            "predicted_class"
        )

        confidence = report.get(
            "model_confidence"
        )

        symptoms = report.get(
            "symptoms_description"
        )

        integrated_diagnosis = report.get(
            "integrated_diagnosis"
        )

        image_path = report.get(
            "image_path"
        )


        with st.container(
            border=True
        ):

            # ------------------------------------------------
            # Header
            # ------------------------------------------------

            col_title, col_date = st.columns(
                [3, 1]
            )


            with col_title:

                st.markdown(
                    "### 🩹 Skin Lesion Assessment"
                )


            with col_date:

                st.caption(
                    str(report_date)
                )


            # ------------------------------------------------
            # Prediction
            # ------------------------------------------------

            st.markdown(
                f"**Predicted class:** "
                f"`{predicted_class or 'N/A'}`"
            )


            # ------------------------------------------------
            # Confidence
            # ------------------------------------------------

            if confidence is not None:

                try:

                    confidence_value = float(
                        confidence
                    )

                    if confidence_value <= 1:
                        confidence_value *= 100

                    st.metric(
                        "Model Confidence",
                        f"{confidence_value:.2f}%",
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    st.write(
                        f"Model Confidence: "
                        f"{confidence}"
                    )


            # ------------------------------------------------
            # Symptoms
            # ------------------------------------------------

            if symptoms:

                st.markdown(
                    "#### Symptoms / Sensations"
                )

                st.write(
                    symptoms
                )


            # ------------------------------------------------
            # Clinical assessment
            # ------------------------------------------------

            if integrated_diagnosis:

                st.markdown(
                    "#### Clinical Assessment"
                )

                st.markdown(
                    integrated_diagnosis
                )


            # ------------------------------------------------
            # Image path
            # ------------------------------------------------

            if image_path:

                st.caption(
                    f"Stored image: {image_path}"
                )


            # ------------------------------------------------
            # Report ID
            # ------------------------------------------------

            report_id = report.get(
                "id",
                "report"
            )

            st.caption(
                f"Report ID: {report_id}"
            )


            # ------------------------------------------------
            # DOWNLOAD PDF
            # ------------------------------------------------

            pdf_data = create_report_pdf(
                report
            )

            st.download_button(
                label="📥 Download Report",
                data=pdf_data,
                file_name=(
                    f"curavision_skin_report_"
                    f"{report_id}.pdf"
                ),
                mime="application/pdf",
                key=f"download_skin_{report_id}",
            )


    # ========================================================
    # CHRONIC-RISK REPORT
    # ========================================================

    elif detection_type == "chronic_risk":

        risk_level = report.get(
            "risk_level"
        )

        risk_score = report.get(
            "risk_score"
        )

        prediction = report.get(
            "prediction"
        )

        summary = report.get(
            "summary"
        )

        findings = report.get(
            "findings"
        )

        recommended_actions = report.get(
            "recommended_actions"
        )


        with st.container(
            border=True
        ):

            # ------------------------------------------------
            # Header
            # ------------------------------------------------

            col_title, col_date = st.columns(
                [3, 1]
            )


            with col_title:

                st.markdown(
                    "### 🫀 Chronic Disease Risk Assessment"
                )


            with col_date:

                st.caption(
                    str(report_date)
                )


            # ------------------------------------------------
            # Risk badge
            # ------------------------------------------------

            if risk_level:

                st.markdown(
                    risk_badge(
                        str(risk_level),
                        "Risk Assessment",
                    ),
                    unsafe_allow_html=True,
                )


            # ------------------------------------------------
            # Risk score
            # ------------------------------------------------

            if risk_score is not None:

                try:

                    score = float(
                        risk_score
                    )

                    if score <= 1:

                        percentage = (
                            score * 100
                        )

                    else:

                        percentage = score


                    st.metric(
                        "Predicted Risk Score",
                        f"{percentage:.2f}%",
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    st.write(
                        f"Risk Score: "
                        f"{risk_score}"
                    )


            # ------------------------------------------------
            # Summary
            # ------------------------------------------------

            if summary:

                st.markdown(
                    "#### Summary"
                )

                st.markdown(
                    str(summary)
                )


            # ------------------------------------------------
            # Clinical findings
            # ------------------------------------------------

            if findings:

                st.markdown(
                    "#### Clinical Findings"
                )


                if isinstance(
                    findings,
                    list,
                ):

                    for finding in findings:

                        st.markdown(
                            f"- {finding}"
                        )

                else:

                    st.markdown(
                        str(findings)
                    )


            # ------------------------------------------------
            # Recommended actions
            # ------------------------------------------------

            if recommended_actions:

                st.markdown(
                    "#### Recommended Actions"
                )


                if isinstance(
                    recommended_actions,
                    list,
                ):

                    for action in recommended_actions:

                        st.markdown(
                            f"- {action}"
                        )

                else:

                    st.markdown(
                        str(recommended_actions)
                    )


            # ------------------------------------------------
            # Model prediction
            # ------------------------------------------------

            if prediction is not None:

                st.caption(
                    f"Model prediction: "
                    f"{prediction}"
                )


            # ------------------------------------------------
            # Report ID
            # ------------------------------------------------

            report_id = report.get(
                "id",
                "report"
            )

            st.caption(
                f"Report ID: {report_id}"
            )


            # ------------------------------------------------
            # DOWNLOAD PDF
            # ------------------------------------------------

            pdf_data = create_report_pdf(
                report
            )

            st.download_button(
                label="📥 Download Report",
                data=pdf_data,
                file_name=(
                    f"curavision_chronic_report_"
                    f"{report_id}.pdf"
                ),
                mime="application/pdf",
                key=f"download_chronic_{report_id}",
            )


# ============================================================
# REFRESH
# ============================================================

st.divider()


if st.button(
    "🔄 Refresh Reports",
    use_container_width=False,
):

    get_health_scans.clear()

    st.rerun()