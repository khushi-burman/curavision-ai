import base64
import os
import streamlit as st

st.set_page_config(
    page_title="Home | CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def reset_session_and_logout():
    """Wipe auth details from session state and send the user back to login."""
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["user_email"] = None
    st.switch_page("app.py")  # app.py is the login/entry point


if not st.session_state.get("logged_in"):
    reset_session_and_logout()


def load_image_base64(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"


hero_robot_asset = load_image_base64("assets/robot.png")

st.markdown("""
<style>
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }

.stApp {
    background: linear-gradient(180deg, #040914 0%, #071224 100%);
}

[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    max-width: 1200px;
}

.nav-logo {
    font-weight: 800;
    font-size: 1.25rem;
    color: #e2e8f0;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(90deg, #7dd3fc, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
}

.hero-description {
    color: #94a3b8;
    font-size: 1.05rem;
    line-height: 1.6;
    max-width: 480px;
    margin-bottom: 26px;
}

.stat-card {
    text-align: center;
}

.stat-number {
    font-size: 1.6rem;
    font-weight: 800;
    color: #38bdf8;
}

.stat-title {
    color: #94a3b8;
    font-size: 0.8rem;
}

.robot-wrapper {
    width: 320px;
    height: 320px;
    margin: 20px auto;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 90px;
    background: radial-gradient(circle, rgba(56,189,248,0.18), transparent 70%);
    border: 1px solid rgba(56,189,248,0.25);
    animation: floatingAnimation 4s ease-in-out infinite;
}

@keyframes floatingAnimation {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-16px); }
}

.robot-wrapper img {
    width: 100%;
    border-radius: 50%;
}

.section-heading {
    color: #e2e8f0;
    font-weight: 700;
    font-size: 1.6rem;
    margin: 48px 0 24px 0;
    text-align: center;
}

.glass-card {
    background: rgba(15,23,42,0.55);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 16px;
    padding: 22px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    text-align: center;
    transition: transform 0.15s ease, border-color 0.15s ease;
    height: 100%;
}

.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(56,189,248,0.4);
}

.glass-card .card-icon {
    font-size: 1.8rem;
    margin-bottom: 8px;
}

.glass-card h4 {
    color: #e2e8f0;
    margin: 4px 0 6px 0;
}

.glass-card p {
    color: #94a3b8;
    font-size: 0.85rem;
    margin: 0;
}

.testimonial-card {
    background: rgba(15,23,42,0.45);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 16px;
    padding: 20px;
    color: #cbd5e1;
    font-size: 0.9rem;
    height: 100%;
}

.testimonial-card .author {
    color: #38bdf8;
    font-weight: 600;
    margin-top: 12px;
    font-size: 0.85rem;
}

.page-footer {
    text-align: center;
    color: #64748b;
    font-size: 0.8rem;
    padding: 30px 0 10px 0;
    border-top: 1px solid rgba(148,163,184,0.12);
    margin-top: 50px;
}
</style>
""", unsafe_allow_html=True)

nav_left, nav_right = st.columns([1, 3])

with nav_left:
    st.markdown('<div class="nav-logo">🩺 CuraVision AI</div>', unsafe_allow_html=True)

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
                if st.button("Logout", key="btn_logout"):
                    reset_session_and_logout()
            elif target:
                st.page_link(target, label=label)

st.divider()

# --- Hero ---
col_hero_text, col_hero_img = st.columns([1.1, 1])

with col_hero_text:
    st.markdown('<div class="hero-title">CuraVision AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-description">AI-powered healthcare platform offering symptom analysis, '
        'disease prediction, medical report insights, and intelligent healthcare assistance.</div>',
        unsafe_allow_html=True
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Start Diagnosis", type="primary", use_container_width=True):
            st.switch_page("pages/disease_detection.py")
    with btn_col2:
        if st.button("Talk with AI", use_container_width=True):
            st.switch_page("pages/assistant.py")

    st.write("")

    metrics_cols = st.columns(4)
    metrics_data = [
        ("98.7%", "Accuracy"),
        ("50K+", "Patients"),
        ("24/7", "Support"),
        ("100+", "Diseases")
    ]

    for col, (value, label) in zip(metrics_cols, metrics_data):
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-number">{value}</div>'
                f'<div class="stat-title">{label}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

with col_hero_img:
    if hero_robot_asset:
        st.markdown(f'<div class="robot-wrapper"><img src="{hero_robot_asset}"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="robot-wrapper">🤖</div>', unsafe_allow_html=True)

# --- Features ---
st.markdown('<div class="section-heading">Why Choose CuraVision</div>', unsafe_allow_html=True)

features_data = [
    ("\U0001F9E0", "AI Diagnosis", "Advanced models trained on millions of clinical data points."),
    ("\U0001F916", "Disease Prediction", "Early risk detection before symptoms fully develop."),
    ("\U0001F4CA", "Medical Reports", "Instant, easy-to-read insights from your lab results."),
    ("\U0001F4C4", "Secure Records", "End-to-end encrypted storage for all patient data.")
]

feature_columns = st.columns(4)
for col, (icon, title, desc) in zip(feature_columns, features_data):
    with col:
        st.markdown(
            f'<div class="glass-card">'
            f'<div class="card-icon">{icon}</div>'
            f'<h4>{title}</h4>'
            f'<p>{desc}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

# --- Services ---
st.markdown('<div class="section-heading">Healthcare Services</div>', unsafe_allow_html=True)

services_data = [
    ("\U0001F4AC", "AI Chat", "Talk to our assistant about symptoms, medication, or general health questions."),
    ("\U0001F52C", "Disease Detection", "Upload scans and images for instant AI-assisted analysis."),
    ("\U0001F4CA", "Report Analysis", "Upload lab reports and get a plain-language breakdown."),
    ("\u2764\uFE0F", "Health Monitoring", "Track vitals and trends over time on your dashboard.")
]

service_columns = st.columns(4)
for col, (icon, title, desc) in zip(service_columns, services_data):
    with col:
        st.markdown(
            f'<div class="glass-card">'
            f'<div class="card-icon">{icon}</div>'
            f'<h4>{title}</h4>'
            f'<p>{desc}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

# --- Reviews ---
st.markdown('<div class="section-heading">What Patients Say</div>', unsafe_allow_html=True)

reviews_data = [
    ("CuraVision caught something my regular checkup missed. Genuinely grateful.", "— Sarah M."),
    ("The AI assistant explained my report better than most doctors have.", "— James O."),
    ("Fast, private, and actually easy to use. Highly recommend.", "— Priya K.")
]

review_columns = st.columns(3)
for col, (review, author) in zip(review_columns, reviews_data):
    with col:
        st.markdown(
            f'<div class="testimonial-card">'
            f'"{review}"'
            f'<div class="author">{author}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown(
    '<div class="page-footer">'
    '© 2026 CuraVision AI · Not a substitute for professional medical advice · support@curavision.ai'
    '</div>',
    unsafe_allow_html=True
)