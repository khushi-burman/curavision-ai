import io
import os
import sys
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

from theme import inject_theme, top_nav, page_header, risk_badge, panel
from backend import predict_chronic_risk 

st.set_page_config(page_title="Detection | CuraVision AI", page_icon="🩺", layout="wide", initial_sidebar_state="collapsed")

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

inject_theme()
top_nav()
page_header("AI screening", "Use the trained skin-vision model for lesion images and the trained chronic-risk model for metabolic risk screening.", "scan")

VISION_MODEL_PATH = os.getenv("CURAVISION_SKIN_MODEL_PATH", "models/best_skin_model.pth")


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
        raise RuntimeError("Skin model inference.py is not included in the frontend package.")
    model_path = Path(VISION_MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(f"Skin model weights not found: {model_path}")
    model, device = inference.load_skin_model(str(model_path))
    image = Image.open(uploaded).convert("RGB")
    return inference.predict_image(image, model, device, generate_heatmap=True)


def generate_risk_explanation(payload: dict, risk_level: str) -> dict:
    """Analyzes contributing clinical vitals and returns layman explanations and actionable steps."""
    findings = []
    actions = []

    # 1. Glycemic Indicators (HbA1c & Blood Glucose)
    hba1c = payload.get("HbA1c_level", 0.0)
    if hba1c >= 6.5:
        findings.append(f"**Elevated HbA1c ({hba1c}%):** Suggests prolonged high blood sugar over recent months, which heavily elevates chronic metabolic strain.")
        actions.append("Schedule a comprehensive fasting glucose and HbA1c lab evaluation with a primary physician.")
    elif hba1c >= 5.7:
        findings.append(f"**Borderline HbA1c ({hba1c}%):** Falls within the prediabetes threshold, indicating early glycemic dysregulation.")
        actions.append("Review dietary carbohydrate intake and adopt a low glycemic index nutritional plan.")

    glucose = payload.get("blood_glucose_level", 0.0)
    if glucose >= 140:
        findings.append(f"**Elevated Blood Glucose ({glucose} mg/dL):** Current circulating sugar exceeds normal fasting/postprandial benchmarks.")
        actions.append("Monitor blood sugar at regular intervals (fasting and 2 hours post-meal).")

    # 2. Cardiovascular & Blood Pressure
    if payload.get("hypertension") == 1:
        findings.append("**History of Hypertension:** Elevated arterial pressure compounds microvascular and kidney strain when combined with high glucose.")
        actions.append("Maintain blood pressure checks and monitor daily dietary sodium intake.")

    if payload.get("heart_disease") == 1:
        findings.append("**Cardiac Comorbidity:** Pre-existing cardiovascular indicators substantially increase systemic metabolic risk.")
        actions.append("Coordinate ongoing care with a cardiologist to minimize compounding vascular risk.")

    # 3. Lifestyle & Body Composition
    bmi = payload.get("bmi", 0.0)
    if bmi >= 30:
        findings.append(f"**High BMI ({bmi}):** High adiposity is strongly correlated with increased cellular insulin resistance.")
        actions.append("Incorporate 150 minutes of moderate aerobic activity weekly under clinical clearance.")
    elif bmi >= 25:
        findings.append(f"**Elevated BMI ({bmi}):** Borderline overweight range that contributes moderately to insulin resistance.")

    smoking = payload.get("smoking_history")
    if smoking in ["current", "former"]:
        findings.append("**Smoking History:** Nicotine exposure promotes systemic endothelial inflammation and impairs vascular elasticity.")
        if smoking == "current":
            actions.append("Consult about smoking cessation resources to lower vascular inflammation.")

    # Fallback recommendations if inputs are within normal parameters
    if not findings:
        findings.append("Vitals and metabolic markers appear within target clinical ranges based on the submitted parameters.")
    if not actions:
        actions.append("Continue routine annual wellness exams and maintain regular physical activity and balanced nutrition.")

    return {
        "findings": findings,
        "actions": actions
    }


tab_skin, tab_risk = st.tabs(["Skin lesion analysis", "Chronic disease risk"])

# skin disease detection

with tab_skin, panel():
    st.markdown('<div class="cv-section-heading">Skin Lesion Assessment</div>', unsafe_allow_html=True)
    st.caption("Upload a clear photo of the skin lesion and describe any symptoms you are experiencing.")

    # Symptom input box for patient observations
    symptoms = st.text_area(
        "Describe your symptoms & sensations",
        placeholder="e.g., Noticeable itching, mild tenderness, bleeding when scratched, rapid change in color or size...",
        key="skin_symptoms",
        height=100
    )

    uploaded = st.file_uploader("Upload lesion image", type=["jpg", "jpeg", "png"], key="skin_upload")

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", width=420)
        if st.button("Run skin analysis", type="primary", key="skin_run"):
            with st.spinner("Running the trained vision model..."):
                try:
                    result = run_skin_prediction(uploaded)
                    st.session_state.skin_result = result
                    st.session_state.recorded_symptoms = symptoms
                except Exception as exc:
                    st.error(str(exc))
                    st.info("Place the trained best_skin_model.pth in the configured model path and include the vision inference package.")

    result = st.session_state.get("skin_result")
    if result:
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Predicted class**")
            st.write(result["label"])
        with c2:
            st.metric("Model confidence", f"{result['confidence'] * 100:.2f}%")

        if st.session_state.get("recorded_symptoms"):
            with st.container(border=True):
                st.markdown("**Reported Symptoms:**")
                st.write(st.session_state.recorded_symptoms)

        if result.get("gradcam_overlay") is not None:
            st.image(result["gradcam_overlay"], caption="Grad-CAM model attention", width=420)
        with st.expander("All class probabilities"):
            for label, probability in sorted(result["all_probabilities"].items(), key=lambda x: x[1], reverse=True):
                st.write(f"{label}: {probability * 100:.2f}%")

# diabetes risk evaluation

with tab_risk, panel():
    st.markdown('<div class="cv-section-heading">Trained chronic-risk model</div>', unsafe_allow_html=True)
    st.caption("Inputs match the 10 features expected by the supplied diabetes/chronic-risk model API.")

    with st.form("risk_form"):
        c1, c2 = st.columns(2)
        with c1:
            gender = st.selectbox("Gender", ["Female", "Male"])
            age = st.number_input("Age", min_value=1.0, max_value=120.0, value=30.0, step=1.0)
            hypertension = st.selectbox("Hypertension", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
            heart_disease = st.selectbox("Heart disease", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
            bmi = st.number_input("BMI", min_value=5.0, max_value=80.0, value=24.0, step=0.1)
        with c2:
            hba1c = st.number_input("HbA1c level", min_value=3.0, max_value=20.0, value=5.5, step=0.1)
            glucose = st.number_input("Blood glucose level", min_value=40.0, max_value=500.0, value=100.0, step=1.0)
            smoking = st.selectbox("Smoking history", ["never", "current", "former"])
        submitted = st.form_submit_button("Calculate risk", type="primary", use_container_width=True)

    if submitted:
        payload = {
            "gender": 0 if gender == "Female" else 1,
            "age": age,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "bmi": bmi,
            "HbA1c_level": hba1c,
            "blood_glucose_level": glucose,
            "smoking_history": smoking,
        }
        st.session_state.last_risk_payload = payload
        try:
            with st.spinner("Running the trained chronic-risk model..."):
                result = predict_chronic_risk(payload)
            st.session_state.risk_result = result
        except requests.RequestException as exc:
            st.error(f"Could not reach the CuraVision backend: {exc}")
            st.info("Start the chronic-risk FastAPI service and set CURAVISION_BACKEND_URL if it is not running on http://127.0.0.1:8000.")
        except Exception as exc:
            st.error(f"Risk prediction failed: {exc}")

    result = st.session_state.get("risk_result")
    result = st.session_state.get("risk_result")
    if result:
        risk = "high" if int(result.get("prediction", 0)) == 1 else "low"
        st.markdown(risk_badge(risk, result.get("status", "Prediction")), unsafe_allow_html=True)
        st.metric("Predicted risk score", f"{float(result.get('risk_score', 0)) * 100:.2f}%")

        # Human-readable explanation box generated by Llama 3.2
        if result.get("explanation"):
            st.divider()
            with st.container(border=True):
                st.subheader("📋 Clinical Assessment & Guidance")
                st.markdown(result["explanation"])

        st.caption("This is an AI screening result and is not a medical diagnosis.")
        
        st.divider()
        last_payload = st.session_state.get("last_risk_payload", {})
        explanation = generate_risk_explanation(last_payload, risk)

        with st.container(border=True):
            st.subheader("Clinical Summary & Interpretation")
            st.markdown(
                "**What this means:** Based on the submitted metabolic indicators, the machine learning model identifies "
                + ("**a high likelihood of chronic metabolic dysregulation**." if risk == "high" else "**a low likelihood of chronic metabolic dysregulation**.")
            )

            col_findings, col_actions = st.columns(2)
            with col_findings:
                st.markdown("#### Primary Observations")
                for f in explanation["findings"]:
                    st.markdown(f"- {f}")

            with col_actions:
                st.markdown("#### Recommended Next Steps")
                for a in explanation["actions"]:
                    st.markdown(f"- {a}")

        st.caption("This is an AI screening result and is not a medical diagnosis.")