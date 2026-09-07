import base64
import os
import streamlit as st

st.set_page_config(
    page_title="Portal Login | CuraVision",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DEMO_EMAIL = "demo@curavision.ai"
DEMO_PASS = "password123"
FALLBACK_BG = "https://img.freepik.com/free-vector/clean-medical-background_53876-97927.jpg"


def get_background_image(path):
    # local bg if we have one, otherwise fall back to a stock image
    if not os.path.exists(path):
        return FALLBACK_BG

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"


bg_url = get_background_image("assets/background.png")

st.markdown(f"""
    <style>
    header {{ visibility: hidden; }}
    [data-testid="stSidebarCollapse"] {{ display: none; }}

    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"],
    #root > div:nth-child(1) > div:nth-child(1) > div > div {{
        background: transparent !important;
    }}

    .stApp {{
        background-image: url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* the actual login card sitting on top of the bg */
    div[data-key="login_frame"] {{
        background: rgba(255, 255, 255, 0.96);
        padding: 42px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #0056b3;
    }}

    .brand-head {{
        color: #0b2545;
        font-family: system-ui, sans-serif;
        font-weight: 800;
        text-align: center;
        margin: 0px 0px 6px 0px;
    }}

    .brand-sub {{
        color: #6c757d;
        text-align: center;
        font-size: 14px;
        margin-bottom: 28px;
    }}
    </style>
""", unsafe_allow_html=True)


with st.container(key="login_frame"):
    st.markdown('<h1 class="brand-head">CURAVISION AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="brand-sub">Secure Medical Insights & Advanced Diagnosis Portal</p>', unsafe_allow_html=True)

    user_type = st.segmented_control(
        "Select Portal Role",
        options=["Patient Portal", "Healthcare Provider"],
        default="Patient Portal"
    )

    uid = st.text_input("Email / Username", placeholder="name@example.com")
    pwd = st.text_input("Password", type="password", placeholder="••••••••")

    left, right = st.columns(2)
    with left:
        persist = st.checkbox("Keep me logged in")
    with right:
        st.markdown(
            "<p style='text-align: right; margin:0;'>"
            "<a href='#' style='color: #0056b3; font-size: 0.85rem; text-decoration: none;'>Forgot Password?</a></p>",
            unsafe_allow_html=True
        )

    if st.button("Login", type="primary", use_container_width=True):
        if not uid or not pwd:
            st.error("Please fill in both fields to authenticate.")
        elif uid == DEMO_EMAIL and pwd == DEMO_PASS:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = uid
            st.session_state["user_role"] = user_type
            st.switch_page("pages/home.py")
        else:
            st.error("Invalid credentials. Please verify your email and security code.")

    st.markdown(
        '<p style="text-align: center; margin-top: 24px; font-size: 0.85rem; color: #6c757d;">'
        'New to the platform? <a href="#" style="color: #0056b3; text-decoration: none; font-weight: bold;">Create a new account</a></p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p style="font-size: 11px; color: #adb5bd; text-align: center; margin-top: 36px; letter-spacing: 0.5px;">'
        'COMPLIANT & ENCRYPTED CONNECTION</p>',
        unsafe_allow_html=True
    )