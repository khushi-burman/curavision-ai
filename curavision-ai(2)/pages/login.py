import streamlit as st

from theme import inject_theme, FONT_IMPORT, icon
from supabase_client import supabase


st.set_page_config(
    page_title="Sign in | CuraVision AI",
    layout="centered",
    initial_sidebar_state="collapsed",
)


LOGIN_CSS = f"""
.stApp {{
    background: var(--bg);
}}

[data-testid="stMainBlockContainer"] {{
    max-width: 460px;
    padding-top: 8vh;
}}

div.st-key-login_frame {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-top: 3px solid var(--accent);
    border-radius: var(--radius-md);
    padding: 38px 40px 30px 40px;
}}

.cv-login-mark {{
    display: flex;
    justify-content: center;
    color: var(--ink-faint);
    margin-bottom: 6px;
}}

.cv-login-title {{
    font-family: var(--font-serif);
    font-size: 1.55rem;
    font-weight: 600;
    color: var(--ink);
    text-align: center;
    margin: 4px 0;
}}

.cv-login-sub {{
    color: var(--ink-soft);
    text-align: center;
    font-size: .88rem;
    margin-bottom: 26px;
}}

.cv-login-footline {{
    text-align: center;
    margin-top: 22px;
    font-size: .84rem;
    color: var(--ink-soft);
}}

.cv-login-fine {{
    font-family: var(--font-mono);
    font-size: .68rem;
    color: var(--ink-faint);
    text-align: center;
    margin-top: 22px;
}}
"""


inject_theme(LOGIN_CSS)


# ============================================================
# LOGIN UI
# ============================================================

with st.container(key="login_frame"):

    st.markdown(
        f'''
        <div class="cv-login-mark">
            {icon("pulse", "width:22px;height:22px;")}
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cv-login-title">CuraVision AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cv-login-sub">'
        'AI-assisted health screening workspace'
        '</div>',
        unsafe_allow_html=True,
    )


    # ========================================================
    # LOGIN FORM
    # ========================================================

    uid = st.text_input(
        "Email",
        placeholder="name@example.com",
    )

    pwd = st.text_input(
        "Password",
        type="password",
        placeholder="••••••••",
    )

    persist = st.checkbox(
        "Keep me logged in"
    )


    # ========================================================
    # SIGN IN
    # ========================================================

    if st.button(
        "Sign in",
        type="primary",
        use_container_width=True,
    ):

        email = uid.strip().lower()

        if not email or not pwd:

            st.error(
                "Please enter your email and password."
            )

        else:

            try:

                # ------------------------------------------------
                # Authenticate with Supabase Auth
                # ------------------------------------------------

                auth_response = (
                    supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": pwd,
                        }
                    )
                )

                # ------------------------------------------------
                # Verify that Supabase returned a user
                # ------------------------------------------------

                if (
                    auth_response is None
                    or auth_response.user is None
                ):

                    st.error(
                        "Login failed. No Supabase user was returned."
                    )

                else:

                    user = auth_response.user
                    user_id = str(user.id)

                    # ------------------------------------------------
                    # Ensure user profile exists in user_profiles table
                    # ------------------------------------------------

                    user_metadata = user.user_metadata or {}
                    full_name = user_metadata.get(
                        "full_name",
                        email.split("@")[0],
                    )

                    try:
                        # Check if profile already exists
                        existing_profile = (
                            supabase.table("user_profiles")
                            .select("user_id")
                            .eq("user_id", user_id)
                            .execute()
                        )

                        if not existing_profile.data:
                            # Insert profile if missing
                            supabase.table("user_profiles").insert({
                                "user_id": user_id,
                                "email": user.email or email,
                                "full_name": full_name
                            }).execute()
                    except Exception as profile_err:
                        st.error(f"Supabase Error: {str(profile_err)}")
                        st.stop()
                    # ------------------------------------------------
                    # Store application session information
                    # ------------------------------------------------

                    st.session_state.logged_in = True

                    st.session_state.user_email = (
                        user.email or email
                    )

                    st.session_state.user_id = user_id

                    st.session_state.keep_logged_in = (
                        persist
                    )

                    st.session_state.user_name = full_name

                    # ------------------------------------------------
                    # Confirm authentication
                    # ------------------------------------------------

                    st.success(
                        "Signed in successfully."
                    )

                    # ------------------------------------------------
                    # Go to home
                    # ------------------------------------------------

                    st.switch_page(
                        "pages/home.py"
                    )

            except Exception as exc:

                error_message = str(exc)

                # User-friendly messages for common Supabase errors

                if (
                    "Invalid login credentials"
                    in error_message
                ):

                    st.error(
                        "Email or password is incorrect."
                    )

                elif (
                    "Email not confirmed"
                    in error_message
                ):

                    st.error(
                        "Please verify your email before signing in."
                    )

                else:

                    st.error(
                        f"Login failed: {error_message}"
                    )


    # ============================================================
    # SIGN UP
    # ============================================================

    st.markdown(
        '<p class="cv-login-footline">New here?</p>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Create an account",
        type="secondary",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/signup.py"
        )