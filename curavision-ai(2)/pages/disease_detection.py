import os
import sys
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

from theme import inject_theme, top_nav, page_header, risk_badge, panel
from backend import predict_chronic_risk, predict_integrated_diagnosis
from supabase_client import supabase

st.set_page_config(
    page_title="Detection | CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# AUTH CHECK
# ============================================================

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

inject_theme()
top_nav()

st.info(
    f"Logged in as: {st.session_state.get('user_email')}\n\n"
    f"Supabase User ID: {st.session_state.get('user_id')}"
)

page_header(
    "AI screening",
    "Use the trained skin-vision model for lesion images and the trained chronic-risk model for metabolic risk screening.",
    "scan",
)

BASE_DIR = Path(__file__).resolve().parents[1]
VISION_MODEL_PATH = os.getenv(
    "CURAVISION_SKIN_MODEL_PATH",
    str(BASE_DIR / "skin_model" / "best_skin_model.pth")
)

# ============================================================
# SKIN MODEL
# ============================================================

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


@st.cache_resource(show_spinner=False)
def get_skin_model(model_path: str):
    """Loads the skin model once and reuses it across button clicks / reruns."""
    inference = load_skin_engine()
    if inference is None:
        raise RuntimeError("Skin model inference.py is not included in the frontend package.")
    return inference.load_skin_model(model_path)


def run_skin_prediction(uploaded):
    inference = load_skin_engine()
    if inference is None:
        raise RuntimeError("Skin model inference.py is not included in the frontend package.")

    model_path = Path(VISION_MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(f"Skin model weights not found: {model_path}")

    model, device = get_skin_model(str(model_path))
    image = Image.open(uploaded).convert("RGB")

    return inference.predict_image(
        image,
        model,
        device,
        generate_heatmap=True,
    )


def generate_integrated_diagnosis(vision_label: str, confidence: float, symptoms_text: str) -> str:
    """Sends vision model outputs and patient-described symptoms to the FastAPI backend."""
    symptoms = symptoms_text.strip() if symptoms_text.strip() else "No specific symptoms reported by patient."

    try:
        response = predict_integrated_diagnosis(
            vision_prediction=vision_label,
            confidence=float(confidence),
            symptom_description=symptoms,
        )
        return response.get("diagnosis_report", "No diagnostic evaluation generated.")
    except requests.exceptions.ConnectionError:
        return (
            "Could not reach the CuraVision backend. Start FastAPI "
            "(`uvicorn main:app --reload`) and check that CURAVISION_BACKEND_URL is correct."
        )
    except requests.exceptions.ReadTimeout:
        return (
            "The language model took too long to respond. Make sure Ollama is running "
            "(`ollama ps`), then try again."
        )
    except Exception as exc:
        return f"Unable to generate integrated LLM synthesis: {exc}"


def generate_risk_explanation(payload: dict, risk_level: str) -> dict:
    """Analyzes contributing clinical vitals and returns layman explanations and actionable steps."""
    findings = []
    actions = []

    # Glycemic indicators
    hba1c = payload.get("HbA1c_level", 0.0)
    if hba1c >= 6.5:
        findings.append(
            f"**Elevated HbA1c ({hba1c}%):** "
            "Suggests prolonged high blood sugar over recent months, "
            "which heavily elevates chronic metabolic strain."
        )
        actions.append(
            "Schedule a comprehensive fasting glucose and HbA1c "
            "lab evaluation with a primary physician."
        )
    elif hba1c >= 5.7:
        findings.append(
            f"**Borderline HbA1c ({hba1c}%):** "
            "Falls within the prediabetes threshold, indicating "
            "early glycemic dysregulation."
        )
        actions.append(
            "Review dietary carbohydrate intake and adopt a "
            "low glycemic index nutritional plan."
        )

    glucose = payload.get("blood_glucose_level", 0.0)
    if glucose >= 140:
        findings.append(
            f"**Elevated Blood Glucose ({glucose} mg/dL):** "
            "Current circulating sugar exceeds normal "
            "fasting/postprandial benchmarks."
        )
        actions.append(
            "Monitor blood sugar at regular intervals "
            "(fasting and 2 hours post-meal)."
        )

    # Cardiovascular / blood pressure
    if payload.get("hypertension") == 1:
        findings.append(
            "**History of Hypertension:** "
            "Elevated arterial pressure compounds microvascular "
            "and kidney strain when combined with high glucose."
        )
        actions.append(
            "Maintain blood pressure checks and monitor "
            "daily dietary sodium intake."
        )

    if payload.get("heart_disease") == 1:
        findings.append(
            "**Cardiac Comorbidity:** "
            "Pre-existing cardiovascular indicators substantially "
            "increase systemic metabolic risk."
        )
        actions.append(
            "Coordinate ongoing care with a cardiologist "
            "to minimize compounding vascular risk."
        )

    # BMI
    bmi = payload.get("bmi", 0.0)
    if bmi >= 30:
        findings.append(
            f"**High BMI ({bmi}):** "
            "High adiposity is strongly correlated with "
            "increased cellular insulin resistance."
        )
        actions.append(
            "Incorporate 150 minutes of moderate aerobic activity "
            "weekly under clinical clearance."
        )
    elif bmi >= 25:
        findings.append(
            f"**Elevated BMI ({bmi}):** "
            "Borderline overweight range that contributes "
            "moderately to insulin resistance."
        )

    # Smoking
    smoking = payload.get("smoking_history")
    if smoking in ["current", "former"]:
        findings.append(
            "**Smoking History:** "
            "Nicotine exposure promotes systemic endothelial "
            "inflammation and impairs vascular elasticity."
        )
        if smoking == "current":
            actions.append(
                "Consult about smoking cessation resources "
                "to lower vascular inflammation."
            )

    # Fallback
    if not findings:
        findings.append(
            "Vitals and metabolic markers appear within target "
            "clinical ranges based on the submitted parameters."
        )

    if not actions:
        actions.append(
            "Continue routine annual wellness exams and maintain "
            "regular physical activity and balanced nutrition."
        )

    summary = (
        "Based on the submitted metabolic indicators, the machine "
        "learning model identifies "
        + (
            "**a high likelihood of chronic metabolic dysregulation**."
            if risk_level == "high"
            else "**a low likelihood of chronic metabolic dysregulation**."
        )
    )

    return {
        "summary": summary,
        "findings": findings,
        "actions": actions,
    }


# ============================================================
# SUPABASE HEALTH SCAN SAVE (ROBUST)
# ============================================================

def save_health_scan(scan_data: dict):
    """
    Save a health scan to Supabase for the currently logged-in user.
    Returns the inserted row on success.
    Raises an exception if the save fails.
    """

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

        except Exception as exc:
            raise RuntimeError(
                f"Could not retrieve Supabase session: {exc}"
            )

    if not user_id:
        raise RuntimeError(
            "No logged-in Supabase user ID found. "
            "Please sign in again."
        )

    
    st.session_state.user_id = user_id

    scan_data = dict(scan_data)
    scan_data["user_id"] = user_id

    try:
        response = (
            supabase
            .table("health_scans")
            .insert(scan_data)
            .execute()
        )
        if not response.data:
            raise RuntimeError(
                "Supabase returned no inserted health scan."
            )

        return response.data[0]

    except Exception as exc:
        raise RuntimeError(
            f"Supabase health scan insert failed: {exc}"
        )

# ============================================================
# TABS
# ============================================================

tab_skin, tab_risk = st.tabs([
    "Skin lesion analysis",
    "Chronic disease risk",
])

# ============================================================
# SKIN DISEASE DETECTION
# ============================================================

with tab_skin, panel():
    st.markdown(
        '<div class="cv-section-heading">Skin Lesion Assessment</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Upload a clear photo of the skin lesion and describe "
        "any symptoms you are experiencing."
    )

    symptoms = st.text_area(
        "Describe your symptoms & sensations",
        placeholder=(
            "e.g., Noticeable itching, mild tenderness, "
            "bleeding when scratched, rapid change in color or size..."
        ),
        key="skin_symptoms",
        height=100,
    )

    uploaded = st.file_uploader(
        "Upload lesion image",
        type=["jpg", "jpeg", "png"],
        key="skin_upload",
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", width=420)

        if st.button("Run skin analysis", type="primary", key="skin_run"):
            with st.spinner("Running vision model & synthesizing assessment..."):
                try:
                    result = run_skin_prediction(uploaded)
                    st.session_state.skin_result = result
                    st.session_state.recorded_symptoms = symptoms

                    # Run integrated diagnostic synthesis
                    integrated_report = generate_integrated_diagnosis(
                        result["label"],
                        result["confidence"],
                        symptoms
                    )
                    st.session_state.integrated_diagnosis = integrated_report
                except Exception as exc:
                    st.error(str(exc))
                    st.info(
                        "Place the trained best_skin_model.pth "
                        "in the configured model path and include "
                        "the vision inference package."
                    )

    result = st.session_state.get("skin_result")
    if result:
        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Predicted Class**")
            st.write(f"### {result['label']}")
        with c2:
            st.metric("Model Confidence", f"{result['confidence'] * 100:.2f}%")

        if st.session_state.get("recorded_symptoms"):
            with st.container(border=True):
                st.markdown("**Reported Symptoms:**")
                st.write(st.session_state.recorded_symptoms)

        if result.get("gradcam_overlay") is not None:
            st.image(
                result["gradcam_overlay"],
                caption="Grad-CAM model attention",
                width=420,
            )

        with st.expander("All class probabilities"):
            for label, probability in sorted(
                result["all_probabilities"].items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                st.write(f"{label}: {probability * 100:.2f}%")

        # Integrated Clinical Assessment Output Box
        integrated_report = st.session_state.get("integrated_diagnosis")
        if integrated_report:
            st.divider()
            with st.container(border=True):
                st.subheader("📋 Integrated Clinical Synthesis & Guidance")
                st.markdown(integrated_report)
                st.caption("This integrated multi-modifiable evaluation is generated for screening support and is not a formal medical diagnosis.")

            # Save skin scan button (ADDED)
            if st.button("💾 Save skin scan result", type="secondary", key="save_skin_scan"):
                try:
                    skin_scan_data = {
                        "detection_type": "skin",
                        "predicted_class": result["label"],
                        "model_confidence": float(result["confidence"]),
                        "symptoms_description": st.session_state.get(
                            "recorded_symptoms", ""
                        ),
                        "integrated_diagnosis": integrated_report,
                    }
                    save_health_scan(skin_scan_data)
                    st.success("Skin lesion assessment saved successfully to Supabase!")
                except Exception as e:
                    st.error(f"Failed to save skin scan: {e}")
        


# ============================================================
# CHRONIC DISEASE RISK
# ============================================================

with tab_risk, panel():
    st.markdown(
        '<div class="cv-section-heading">Trained chronic-risk model</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Inputs match the 10 features expected by the "
        "supplied diabetes/chronic-risk model API."
    )

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

            prediction = int(result.get("prediction", 0))
            risk = "high" if prediction == 1 else "low"
            risk_score = float(result.get("risk_score", 0))

            explanation = generate_risk_explanation(payload, risk)

            scan_data = {
                "detection_type": "chronic_risk",
                "age": float(age),
                "hypertension": int(hypertension),
                "heart_disease": int(heart_disease),
                "bmi": float(bmi),
                "hba1c_level": float(hba1c),
                "blood_glucose_level": float(glucose),
                "smoking_history": smoking,
                "risk_level": risk,
                "risk_score": risk_score,
                "prediction": prediction,
                "summary": explanation["summary"],
                "findings": explanation["findings"],
                "recommended_actions": explanation["actions"],
            }

            saved_row = save_health_scan(scan_data)

            st.success(
                f"Chronic-risk result saved successfully. "
                f"Record ID: {saved_row.get('id', 'unknown')}"
            )

        except requests.RequestException as exc:
            st.error(f"Could not reach the CuraVision backend: {exc}")
            st.info(
                "Start the chronic-risk FastAPI service and "
                "set CURAVISION_BACKEND_URL if it is not "
                "running on http://127.0.0.1:8000."
            )
        except Exception as exc:
            st.error(f"Risk prediction or Supabase save failed: {exc}")

    # ========================================================
    # DISPLAY RISK RESULT
    # ========================================================
    result = st.session_state.get("risk_result")
    if result:
        risk = "high" if int(result.get("prediction", 0)) == 1 else "low"

        st.markdown(
            risk_badge(risk, result.get("status", "Prediction")),
            unsafe_allow_html=True,
        )

        st.metric(
            "Predicted risk score",
            f"{float(result.get('risk_score', 0)) * 100:.2f}%",
        )

        if result.get("explanation"):
            st.divider()
            with st.container(border=True):
                st.subheader("📋 Clinical Assessment & Guidance")
                st.markdown(result["explanation"])

        st.divider()

        last_payload = st.session_state.get("last_risk_payload", {})
        explanation = generate_risk_explanation(last_payload, risk)

        with st.container(border=True):
            st.subheader("Clinical Summary & Interpretation")
            st.markdown("**What this means:** " + explanation["summary"])

            col_findings, col_actions = st.columns(2)

            with col_findings:
                st.markdown("#### Primary Observations")
                for finding in explanation["findings"]:
                    st.markdown(f"- {finding}")

            with col_actions:
                st.markdown("#### Recommended Next Steps")
                for action in explanation["actions"]:
                    st.markdown(f"- {action}")

        st.caption("This is an AI screening result and is not a medical diagnosis.")