import streamlit as st
from theme import inject_theme, FONT_IMPORT, icon

st.set_page_config(
    page_title="Sign in | CuraVision AI",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DEMO_EMAIL = "demo@curavision.ai"
DEMO_PASS = "password123"

LOGIN_CSS = f"""
.stApp {{
    background: var(--bg);
}}
[data-testid="stMainBlockContainer"] {{ max-width: 460px; padding-top: 8vh; }}
div.st-key-login_frame {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-top: 3px solid var(--accent);
    border-radius: var(--radius-md);
    padding: 38px 40px 30px 40px;
}}
.cv-login-mark {{ display:flex; justify-content:center; color:var(--ink-faint); margin-bottom:6px; }}
.cv-login-title {{ font-family:var(--font-serif); font-size:1.55rem; font-weight:600; color:var(--ink); text-align:center; margin:4px 0; }}
.cv-login-sub {{ color:var(--ink-soft); text-align:center; font-size:.88rem; margin-bottom:26px; }}
.cv-login-footline {{ text-align:center; margin-top:22px; font-size:.84rem; color:var(--ink-soft); }}
.cv-login-fine {{ font-family:var(--font-mono); font-size:.68rem; color:var(--ink-faint); text-align:center; margin-top:22px; }}
"""

inject_theme(LOGIN_CSS)

if "accounts" not in st.session_state:
    st.session_state.accounts = {DEMO_EMAIL: {"password": DEMO_PASS, "name": "Demo User"}}

with st.container(key="login_frame"):
    st.markdown(f'<div class="cv-login-mark">{icon("pulse", "width:22px;height:22px;")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="cv-login-title">CuraVision AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="cv-login-sub">AI-assisted health screening workspace</div>', unsafe_allow_html=True)

    uid = st.text_input("Email", placeholder="name@example.com")
    pwd = st.text_input("Password", type="password", placeholder="••••••••")
    persist = st.checkbox("Keep me logged in")

    if st.button("Sign in", type="primary", use_container_width=True):
        account = st.session_state.accounts.get(uid.strip().lower())
        if account and account["password"] == pwd:
            st.session_state.logged_in = True
            st.session_state.user_email = uid.strip().lower()
            st.session_state.user_name = account.get("name", "User")
            st.session_state.keep_logged_in = persist
            st.switch_page("pages/home.py")
        else:
            st.error("Email or password is incorrect.")

    st.markdown('<p class="cv-login-footline">New here?</p>', unsafe_allow_html=True)
    if st.button("Create an account", type="secondary", use_container_width=True):
        st.switch_page("pages/signup.py")

    #st.markdown('<p class="cv-login-fine">Demo: demo@curavision.ai / password123</p>', unsafe_allow_html=True)
