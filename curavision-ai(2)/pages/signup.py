import streamlit as st
from theme import inject_theme, icon
from supabase_client import supabase

st.set_page_config(page_title="Create account | CuraVision AI", layout="centered", initial_sidebar_state="collapsed")

inject_theme("""
.stApp { background: var(--bg); }
[data-testid="stMainBlockContainer"] { max-width: 500px; padding-top: 7vh; }
div.st-key-signup_frame { background: var(--surface); border:1px solid var(--line); border-top:3px solid var(--accent); border-radius:var(--radius-md); padding:34px 38px 30px; }
.cv-title { font-family:var(--font-serif); font-size:1.55rem; font-weight:600; text-align:center; color:var(--ink); }
.cv-sub { text-align:center; color:var(--ink-soft); font-size:.88rem; margin:5px 0 24px; }
""")

with st.container(key="signup_frame"):
    st.markdown(f'<div style="text-align:center;color:var(--ink-faint);">{icon("pulse", "width:22px;height:22px;")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="cv-title">Create your CuraVision account</div>', unsafe_allow_html=True)
    st.markdown('<div class="cv-sub">Set up your personal AI-assisted screening workspace.</div>', unsafe_allow_html=True)

    with st.form("signup_form"):
        name = st.text_input("Full name", placeholder="Your name")
        email = st.text_input("Email", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="At least 6 characters")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

    if submitted:
        clean_email = email.strip().lower()
        if not name.strip() or not clean_email or not password:
            st.error("Please complete all fields.")
        elif "@" not in clean_email:
            st.error("Enter a valid email address.")
        elif len(password) < 6:
            st.error("Password must contain at least 6 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            try:
                # 1. Register account with Supabase Auth
                auth_response = supabase.auth.sign_up({
                    "email": clean_email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": name.strip()
                        }
                    }
                })

                if auth_response and auth_response.user:
                    user_id = str(auth_response.user.id)
                    
                    # 2. Insert profile record into user_profiles table
                    try:
                        supabase.table("user_profiles").upsert({
                            "user_id": user_id,
                            "email": clean_email,
                            "full_name": name.strip()
                        }).execute()
                    except Exception as profile_err:
                        st.error(f"Profile sync warning: {str(profile_err)}")

                    # 3. Establish active session state
                    st.session_state.logged_in = True
                    st.session_state.user_email = clean_email
                    st.session_state.user_id = user_id
                    st.session_state.user_name = name.strip()

                    st.success("Account created successfully!")
                    st.switch_page("pages/home.py")
                else:
                    st.error("Signup failed. No user was returned from Supabase.")

            except Exception as e:
                st.error(f"Signup error: {str(e)}")

    if st.button("Back to sign in", type="secondary", use_container_width=True):
        st.switch_page("pages/login.py")