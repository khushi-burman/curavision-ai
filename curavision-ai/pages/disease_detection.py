import io
import os
import sys
import uuid
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

from theme import inject_theme, top_nav, page_header, risk_badge, panel
from backend import predict_chronic_risk
from supabase_client import supabase


st.set_page_config(
    page_title="Detection | CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------
# Authentication check
# ---------------------------------------------------------

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")


inject_theme()
top_nav()

page_header(
    "AI screening",
    "Use the trained skin-vision model for lesion images and the trained chronic-risk model for metabolic risk screening.",
    "scan"
)


VISION_MODEL_PATH = os.getenv(
    "CURAVISION_SKIN_MODEL_PATH",
    "models/best_skin_model.pth"
)


# ---------------------------------------------------------
# Skin model loading
# ---------------------------------------------------------

def load_skin_engine():

    project_root = Path(__file__).resolve().parents[1]

    candidates = [
        project_root / "skin_model" / "inference.py",
        project_root / "model" / "inference.py",
        project_root / "inference.py",
    ]

    for candidate in candidates:

        if candidate.exists():

            if str(candidate.parent) not in sys.path:
                sys.path.insert(0, str(candidate.parent))

            import inference

            return inference

    return None


def run_skin_prediction(uploaded):

    inference = load_skin_engine()

    if inference is None:
        raise RuntimeError(
            "Skin model inference.py is not included in the frontend package."
        )

    model_path = Path(VISION_MODEL_PATH)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Skin model weights not found: {model_path}"
        )

    model, device = inference.load_skin_model(
        str(model_path)
    )

    image = Image.open(uploaded).convert("RGB")

    return inference.predict_image(
        image,
        model,
        device,
        generate_heatmap=True
    )


# ---------------------------------------------------------
# Save scan to Supabase
# ---------------------------------------------------------

def generate_risk_explanation(payload: dict, risk_level: str) -> dict:
    """Generate layman-friendly clinical observations and recommended next steps."""

    findings = []
    actions = []

    # Glycemic indicators
    hba1c = payload.get("HbA1c_level", 0.0)

    if hba1c >= 6.5:
        findings.append(
            f"**Elevated HbA1c ({hba1c}%):** Suggests prolonged high blood sugar over recent months."
        )
        actions.append(
            "Schedule a comprehensive fasting glucose and HbA1c evaluation with a primary physician."
        )
    elif hba1c >= 5.7:
        findings.append(
            f"**Borderline HbA1c ({hba1c}%):** Falls within the prediabetes threshold, indicating early glycemic dysregulation."
        )
        actions.append(
            "Review dietary carbohydrate intake and consider a low glycemic index nutritional plan."
        )

    glucose = payload.get("blood_glucose_level", 0.0)

    if glucose >= 140:
        findings.append(
            f"**Elevated Blood Glucose ({glucose} mg/dL):** The submitted glucose value is elevated."
        )
        actions.append(
            "Monitor blood sugar at regular intervals and discuss the result with a healthcare professional."
        )

    # Cardiovascular indicators
    if payload.get("hypertension") == 1:
        findings.append(
            "**History of Hypertension:** Hypertension can contribute to cardiovascular and metabolic risk."
        )
        actions.append(
            "Maintain regular blood-pressure checks and monitor dietary sodium intake."
        )

    if payload.get("heart_disease") == 1:
        findings.append(
            "**Cardiac Comorbidity:** A history of heart disease is an important cardiovascular risk factor."
        )
        actions.append(
            "Continue appropriate follow-up care with your healthcare professional."
        )

    # Body composition
    bmi = payload.get("bmi", 0.0)

    if bmi >= 30:
        findings.append(
            f"**High BMI ({bmi}):** Higher BMI can be associated with increased insulin resistance."
        )
        actions.append(
            "Aim for regular physical activity as appropriate for your health and under clinical guidance."
        )
    elif bmi >= 25:
        findings.append(
            f"**Elevated BMI ({bmi}):** This falls in the overweight BMI range."
        )

    # Smoking
    smoking = payload.get("smoking_history")

    if smoking in ["current", "former"]:
        findings.append(
            "**Smoking History:** Smoking history is an important cardiovascular risk factor."
        )

    if smoking == "current":
        actions.append(
            "Consider discussing smoking-cessation resources with a healthcare professional."
        )

    if not findings:
        findings.append(
            "The submitted metabolic indicators did not trigger any of the configured clinical observations."
        )

    if not actions:
        actions.append(
            "Continue routine wellness checks, regular physical activity, and balanced nutrition."
        )

    summary = (
        "Based on the submitted metabolic indicators, the machine learning model identifies "
        + (
            "**a high likelihood of chronic metabolic dysregulation**."
            if risk_level == "high"
            else "**a low likelihood of chronic metabolic dysregulation**."
        )
    )

    return {
        "summary": summary,
        "findings": findings,
        "recommended_actions": actions,
    }


def save_health_scan(scan_data):

    user_id = st.session_state.get("user_id")

    if not user_id:
        raise RuntimeError(
            "User session not found. Please sign in again."
        )

    scan_data["user_id"] = user_id

    response = (
        supabase
        .table("health_scans")
        .insert(scan_data)
        .execute()
    )

    return response


# ---------------------------------------------------------
# Upload user image to Supabase Storage
# ---------------------------------------------------------

def upload_scan_image(uploaded):

    user_id = st.session_state.get("user_id")

    if not user_id:
        return None

    try:

        file_extension = Path(uploaded.name).suffix.lower()

        unique_name = (
            f"{uuid.uuid4().hex}{file_extension}"
        )

        storage_path = (
            f"{user_id}/scans/{unique_name}"
        )

        file_bytes = uploaded.getvalue()

        supabase.storage \
            .from_("curavision-user-images") \
            .upload(
                storage_path,
                file_bytes,
                {
                    "content-type": uploaded.type,
                    "upsert": "false"
                }
            )

        return storage_path

    except Exception:
        # Storage failure should not stop the scan
        # from being saved to the database.
        return None


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab_skin, tab_risk = st.tabs(
    [
        "Skin lesion analysis",
        "Chronic disease risk"
    ]
)


# =========================================================
# SKIN LESION ANALYSIS
# =========================================================

with tab_skin, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Trained skin-vision model'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "EfficientNet-B4 classifier trained for 7 HAM10000 "
        "lesion classes. Upload a clear skin-lesion image."
    )

    uploaded = st.file_uploader(
        "Upload lesion image",
        type=["jpg", "jpeg", "png"],
        key="skin_upload"
    )

    if uploaded:

        image = Image.open(uploaded).convert("RGB")

        st.image(
            image,
            caption="Uploaded image",
            width=420
        )

        if st.button(
            "Run skin analysis",
            type="primary",
            key="skin_run"
        ):

            with st.spinner(
                "Running the trained vision model..."
            ):

                try:

                    # -------------------------------
                    # Run ML model
                    # -------------------------------

                    result = run_skin_prediction(
                        uploaded
                    )

                    st.session_state.skin_result = result

                    # -------------------------------
                    # Upload image
                    # -------------------------------

                    image_path = upload_scan_image(
                        uploaded
                    )

                    # -------------------------------
                    # Prepare probabilities
                    # -------------------------------

                    probabilities = {
                        str(label): float(probability)
                        for label, probability
                        in result["all_probabilities"].items()
                    }

                    # -------------------------------
                    # Save scan
                    # -------------------------------

                    scan_data = {
                        "detection_type": "skin",

                        "image_path": image_path,

                        "predicted_class": str(
                            result["label"]
                        ),

                        "model_confidence": float(
                            result["confidence"]
                        ),

                        "class_probabilities": probabilities,

                        "risk_level": None,

                        "risk_score": None,

                        "prediction": None
                    }

                    save_health_scan(
                        scan_data
                    )

                    st.success(
                        "Skin analysis saved successfully."
                    )

                except Exception as exc:

                    st.error(str(exc))

                    st.info(
                        "Place the trained "
                        "best_skin_model.pth in the "
                        "configured model path and include "
                        "the vision inference package."
                    )

    # -----------------------------------------------------
    # Display result
    # -----------------------------------------------------

    result = st.session_state.get(
        "skin_result"
    )

    if result:

        st.divider()

        c1, c2 = st.columns(2)

        with c1:

            st.markdown(
                "**Predicted class**"
            )

            st.write(
                result["label"]
            )

        with c2:

            st.metric(
                "Model confidence",
                f"{result['confidence'] * 100:.2f}%"
            )

        if result.get(
            "gradcam_overlay"
        ) is not None:

            st.image(
                result["gradcam_overlay"],
                caption="Grad-CAM model attention",
                width=420
            )

        with st.expander(
            "All class probabilities"
        ):

            for label, probability in sorted(
                result["all_probabilities"].items(),
                key=lambda x: x[1],
                reverse=True
            ):

                st.write(
                    f"{label}: "
                    f"{probability * 100:.2f}%"
                )


# =========================================================
# CHRONIC DISEASE RISK
# =========================================================

with tab_risk, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Trained chronic-risk model'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Inputs match the 10 features expected by the "
        "supplied diabetes/chronic-risk model API."
    )

    with st.form("risk_form"):

        c1, c2 = st.columns(2)

        with c1:

            gender = st.selectbox(
                "Gender",
                ["Female", "Male"]
            )

            age = st.number_input(
                "Age",
                min_value=1.0,
                max_value=120.0,
                value=30.0,
                step=1.0
            )

            hypertension = st.selectbox(
                "Hypertension",
                [0, 1],
                format_func=lambda x:
                    "No" if x == 0 else "Yes"
            )

            heart_disease = st.selectbox(
                "Heart disease",
                [0, 1],
                format_func=lambda x:
                    "No" if x == 0 else "Yes"
            )

            bmi = st.number_input(
                "BMI",
                min_value=5.0,
                max_value=80.0,
                value=24.0,
                step=0.1
            )

        with c2:

            hba1c = st.number_input(
                "HbA1c level",
                min_value=3.0,
                max_value=20.0,
                value=5.5,
                step=0.1
            )

            glucose = st.number_input(
                "Blood glucose level",
                min_value=40.0,
                max_value=500.0,
                value=100.0,
                step=1.0
            )

            smoking = st.selectbox(
                "Smoking history",
                [
                    "never",
                    "current",
                    "former"
                ]
            )

        submitted = st.form_submit_button(
            "Calculate risk",
            type="primary",
            use_container_width=True
        )

    if submitted:

        payload = {

            "gender":
                0 if gender == "Female" else 1,

            "age":
                age,

            "hypertension":
                hypertension,

            "heart_disease":
                heart_disease,

            "bmi":
                bmi,

            "HbA1c_level":
                hba1c,

            "blood_glucose_level":
                glucose,

            "smoking_history":
                smoking,
        }

        try:

            with st.spinner(
                "Running the trained chronic-risk model..."
            ):

                st.session_state.last_risk_payload = payload

                result = predict_chronic_risk(
                    payload
                )

            st.session_state.risk_result = result

            # -----------------------------------------
            # Determine risk
            # -----------------------------------------

            prediction = int(
                result.get(
                    "prediction",
                    0
                )
            )

            risk = (
                "high"
                if prediction == 1
                else "low"
            )

            risk_score = float(
                result.get(
                    "risk_score",
                    0
                )
            )

            # -----------------------------------------
            # Generate clinical explanation
            # -----------------------------------------

            explanation = generate_risk_explanation(
                st.session_state.last_risk_payload,
                risk
            )

            # -----------------------------------------
            # Save chronic-risk scan
            # -----------------------------------------

            scan_data = {

                "detection_type":
                    "chronic_risk",

                "age":
                    float(age),

                "hypertension":
                    int(hypertension),

                "heart_disease":
                    int(heart_disease),

                "bmi":
                    float(bmi),

                "hba1c_level":
                    float(hba1c),

                "blood_glucose_level":
                    float(glucose),

                "smoking_history":
                    smoking,

                "risk_level":
                    risk,

                "risk_score":
                    risk_score,

                "prediction":
                    prediction,

                "summary":
                    explanation["summary"],

                "findings":
                    explanation["findings"],

                "recommended_actions":
                    explanation["recommended_actions"]
            }

            save_health_scan(
                scan_data
            )

        except requests.RequestException as exc:

            st.error(
                f"Could not reach the CuraVision backend: {exc}"
            )

            st.info(
                "Start the chronic-risk FastAPI service "
                "and set CURAVISION_BACKEND_URL if it is "
                "not running on http://127.0.0.1:8000."
            )

        except Exception as exc:

            st.error(
                f"Risk prediction failed: {exc}"
            )

    # -----------------------------------------------------
    # Display chronic-risk result
    # -----------------------------------------------------

    result = st.session_state.get(
        "risk_result"
    )

    if result:

        risk = (
            "high"
            if int(
                result.get(
                    "prediction",
                    0
                )
            ) == 1
            else "low"
        )

        st.markdown(
            risk_badge(
                risk,
                result.get(
                    "status",
                    "Prediction"
                )
            ),
            unsafe_allow_html=True
        )

        st.metric(
            "Predicted risk score",
            f"{float(result.get('risk_score', 0)) * 100:.2f}%"
        )

        # -------------------------------------------------
        # Clinical summary and interpretation
        # -------------------------------------------------

        last_payload = st.session_state.get(
            "last_risk_payload",
            {}
        )

        explanation = generate_risk_explanation(
            last_payload,
            risk
        )

        with st.container(border=True):

            st.subheader(
                "Clinical Summary & Interpretation"
            )

            st.markdown(
                "**What this means:** "
                + explanation["summary"]
            )

            col_findings, col_actions = st.columns(2)

            with col_findings:

                st.markdown(
                    "#### Primary Observations"
                )

                for finding in explanation["findings"]:
                    st.markdown(
                        f"- {finding}"
                    )

            with col_actions:

                st.markdown(
                    "#### Recommended Next Steps"
                )

                for action in explanation["recommended_actions"]:
                    st.markdown(
                        f"- {action}"
                    )

        st.caption(
            "This is an AI screening result and "
            "is not a medical diagnosis."
        )