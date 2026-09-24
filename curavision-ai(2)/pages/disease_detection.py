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


tab_skin, tab_risk = st.tabs(["Skin lesion analysis", "Chronic disease risk"])

with tab_skin, panel():
    st.markdown('<div class="cv-section-heading">Trained skin-vision model</div>', unsafe_allow_html=True)
    st.caption("EfficientNet-B4 classifier trained for 7 HAM10000 lesion classes. Upload a clear skin-lesion image.")
    uploaded = st.file_uploader("Upload lesion image", type=["jpg", "jpeg", "png"], key="skin_upload")

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", width=420)
        if st.button("Run skin analysis", type="primary", key="skin_run"):
            with st.spinner("Running the trained vision model..."):
                try:
                    result = run_skin_prediction(uploaded)
                    st.session_state.skin_result = result
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
        if result.get("gradcam_overlay") is not None:
            st.image(result["gradcam_overlay"], caption="Grad-CAM model attention", width=420)
        with st.expander("All class probabilities"):
            for label, probability in sorted(result["all_probabilities"].items(), key=lambda x: x[1], reverse=True):
                st.write(f"{label}: {probability * 100:.2f}%")

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
    if result:
        risk = "high" if int(result.get("prediction", 0)) == 1 else "low"
        st.markdown(risk_badge(risk, result.get("status", "Prediction")), unsafe_allow_html=True)
        st.metric("Predicted risk score", f"{float(result.get('risk_score', 0)) * 100:.2f}%")
        st.caption("This is an AI screening result and is not a medical diagnosis.")
