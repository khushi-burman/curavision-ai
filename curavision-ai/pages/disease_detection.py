"""
CuraVision AI — Disease Detection Page
"""

import streamlit as st
from PIL import Image
import numpy as np
import time

st.set_page_config(
    page_title="Disease Detection • CuraVision AI",
    page_icon="🩺",
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
        padding: 28px 30px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        margin-bottom: 22px;
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

    .result-badge-high {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 999px;
        background: rgba(248, 113, 113, 0.15);
        border: 1px solid rgba(248, 113, 113, 0.5);
        color: #fca5a5;
        font-weight: 600;
    }

    .result-badge-low {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 999px;
        background: rgba(74, 222, 128, 0.15);
        border: 1px solid rgba(74, 222, 128, 0.5);
        color: #86efac;
        font-weight: 600;
    }

    div[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px dashed rgba(125, 211, 252, 0.4);
        border-radius: 14px;
        padding: 10px;
    }

    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 26px;
        font-weight: 600;
        transition: transform 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        color: #cbd5e1;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(96, 165, 250, 0.18);
        color: #ffffff;
        border-bottom: 2px solid #60a5fa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Navigation ----------------

left, right = st.columns([1, 3])

with left:
    st.markdown("## 🩺 CuraVision AI")

with right:
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    with c1:
        st.page_link("pages/home.py", label="🏠 Home")

    with c2:
        st.page_link("pages/assistant.py", label="💬 Assistant")

    with c3:
        st.page_link("pages/disease_detection.py", label="🩺 Detection")

    with c4:
        st.page_link("pages/reports.py", label="📄 Reports")

    with c5:
        st.page_link("pages/dashboard.py", label="📊 Dashboard")

    with c6:
        st.page_link("pages/profile.py", label="👤 Profile")

    with c7:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.switch_page("app.py")

st.divider()

# --- header ---
st.markdown('<div class="page-title">🩺 Disease Detection</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Upload a medical image and/or log your symptoms — '
    'CuraVision AI will combine both signals for a preliminary assessment.</div>',
    unsafe_allow_html=True,
)


# --- placeholder inference functions — wire these to your real models ---
def run_image_model(image: Image.Image):
    """Replace with your actual model.predict() call."""
    time.sleep(1.2)
    img_array = np.array(image.convert("L"))
    score = float(np.clip(img_array.std() / 255, 0, 1))
    return {
        "label": "Possible Abnormality Detected" if score > 0.45 else "No Abnormality Detected",
        "confidence": round(score * 100 + 20, 1) if score > 0.45 else round((1 - score) * 100, 1),
        "risk": "high" if score > 0.45 else "low",
    }


def run_symptom_model(symptoms: list, severity: int, duration_days: int):
    """Replace with your actual symptom-classifier call."""
    time.sleep(0.8)
    weight = len(symptoms) * 8 + severity * 6 + min(duration_days, 14) * 1.5
    risk_score = min(weight, 100)
    return {
        "label": "Elevated Risk" if risk_score > 45 else "Low Risk",
        "confidence": round(risk_score, 1),
        "risk": "high" if risk_score > 45 else "low",
    }


def combine_results(image_result, symptom_result):
    scores = []
    if image_result:
        scores.append(image_result["confidence"])
    if symptom_result:
        scores.append(symptom_result["confidence"])
    combined = round(sum(scores) / len(scores), 1) if scores else 0
    risk = "high" if combined > 45 else "low"
    return {"confidence": combined, "risk": risk}


if "image_result" not in st.session_state:
    st.session_state.image_result = None
if "symptom_result" not in st.session_state:
    st.session_state.symptom_result = None

tab_image, tab_symptoms, tab_result = st.tabs(
    ["🖼️ Image Detection", "📝 Symptom Checker", "📊 Combined Result"]
)

# ---- image tab ----
with tab_image:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Upload a Medical Image")
    st.caption("Supported: X-ray, MRI slice, skin lesion photo, etc. (JPG, PNG, JPEG)")

    uploaded_file = st.file_uploader(
        "Drag and drop or browse", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded image", use_container_width=True)

    with col2:
        if uploaded_file:
            if st.button("Run Image Analysis", key="run_image"):
                with st.spinner("Analyzing image..."):
                    st.session_state.image_result = run_image_model(image)

            result = st.session_state.image_result
            if result:
                badge_class = "result-badge-high" if result["risk"] == "high" else "result-badge-low"
                st.markdown(f'<span class="{badge_class}">{result["label"]}</span>', unsafe_allow_html=True)
                st.metric("Model Confidence", f"{result['confidence']}%")
        else:
            st.info("Upload an image to enable analysis.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---- symptoms tab ----
with tab_symptoms:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Log Your Symptoms")

    symptom_options = [
        "Fever", "Cough", "Fatigue", "Shortness of breath", "Headache",
        "Sore throat", "Body ache", "Nausea", "Chest pain", "Dizziness",
        "Loss of appetite", "Skin rash",
    ]

    selected_symptoms = st.multiselect("Select symptoms you're experiencing", symptom_options)
    severity = st.slider("Overall severity (1 = mild, 10 = severe)", 1, 10, 5)
    duration_days = st.number_input("Duration (days)", min_value=0, max_value=90, value=1, step=1)
    notes = st.text_area("Additional notes (optional)", placeholder="Anything else worth mentioning...")

    if st.button("Run Symptom Analysis", key="run_symptoms"):
        if not selected_symptoms:
            st.warning("Please select at least one symptom.")
        else:
            with st.spinner("Analyzing symptoms..."):
                st.session_state.symptom_result = run_symptom_model(
                    selected_symptoms, severity, duration_days
                )

    result = st.session_state.symptom_result
    if result:
        badge_class = "result-badge-high" if result["risk"] == "high" else "result-badge-low"
        st.markdown(f'<span class="{badge_class}">{result["label"]}</span>', unsafe_allow_html=True)
        st.metric("Model Confidence", f"{result['confidence']}%")

    st.markdown("</div>", unsafe_allow_html=True)

# ---- combined result tab ----
with tab_result:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Combined Assessment")

    img_res = st.session_state.image_result
    sym_res = st.session_state.symptom_result

    if not img_res and not sym_res:
        st.info("Run image and/or symptom analysis to see a combined result here.")
    else:
        colA, colB, colC = st.columns(3)
        with colA:
            st.markdown("**Image Analysis**")
            st.write(img_res["label"] if img_res else "Not run yet")
        with colB:
            st.markdown("**Symptom Analysis**")
            st.write(sym_res["label"] if sym_res else "Not run yet")
        with colC:
            combined = combine_results(img_res, sym_res)
            badge_class = "result-badge-high" if combined["risk"] == "high" else "result-badge-low"
            st.markdown("**Overall**")
            st.markdown(
                f'<span class="{badge_class}">{combined["confidence"]}% risk score</span>',
                unsafe_allow_html=True,
            )

        st.divider()
        st.caption(
            "⚠️ This is an AI-assisted preliminary screening tool, not a medical diagnosis. "
            "Please consult a licensed healthcare professional for confirmation and treatment."
        )

    st.markdown("</div>", unsafe_allow_html=True)