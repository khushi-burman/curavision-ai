import streamlit as st
from datetime import date
from theme import inject_theme, top_nav, page_header, icon, footnote, panel

st.set_page_config(
    page_title="Profile • CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

PROFILE_CSS = """
.avatar-ring {
    width: 108px;
    height: 108px;
    border-radius: 50%;
    margin: 0 auto 14px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-serif);
    font-size: 2.2rem;
    font-weight: 600;
    color: var(--surface);
    background: var(--accent);
    border: 3px solid var(--accent-soft);
}

.profile-name { text-align: center; font-size: 1.25rem; font-weight: 600; color: var(--ink); font-family: var(--font-serif); margin-bottom: 2px; }
.profile-email { text-align: center; color: var(--ink-soft); font-size: 0.88rem; margin-bottom: 16px; font-family: var(--font-mono); }

.stat-pill {
    background: var(--surface-sunken);
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 12px 10px;
    text-align: center;
}
.stat-value { font-family: var(--font-mono); font-size: 1.3rem; font-weight: 600; color: var(--ink); }
.stat-label { color: var(--ink-soft); font-size: 0.76rem; }

.badge-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 3px;
    background: var(--accent-soft);
    border: 1px solid rgba(47,111,94,0.28);
    color: var(--accent-dark);
    font-size: 0.78rem;
    font-weight: 500;
    margin: 3px 4px 3px 0;
}
"""

inject_theme(PROFILE_CSS)
top_nav()

page_header(
    "Profile",
    "Manage your personal details, health info, and account preferences.",
    "user",
)

# --- mock / session data — replace with your real user record ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": st.session_state.get("user_name", "User"),
        "email": st.session_state.get("user_email", ""),
        "phone": "+1 555 123 4567",
        "dob": date(1994, 3, 12),
        "gender": "Female",
        "blood_group": "O+",
        "height_cm": 168,
        "weight_kg": 61,
        "conditions": ["Seasonal Allergies", "Mild Asthma"],
        "total_scans": 9,
        "reports_generated": 6,
        "member_since": date(2025, 11, 2),
    }

profile = st.session_state.user_profile

# --- layout: left (avatar + stats) | right (editable details) ---
left_col, right_col = st.columns([1, 2])

with left_col, panel("flat"):
    initials = "".join([p[0] for p in profile["name"].split()[:2]]).upper()
    st.markdown(f'<div class="avatar-ring">{initials}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-name">{profile["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-email">{profile["email"]}</div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.markdown(
            f'<div class="stat-pill"><div class="stat-value">{profile["total_scans"]}</div>'
            f'<div class="stat-label">Total scans</div></div>',
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f'<div class="stat-pill"><div class="stat-value">{profile["reports_generated"]}</div>'
            f'<div class="stat-label">Reports</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.caption(f"Member since {profile['member_since'].strftime('%B %Y')}")

    st.markdown('<div class="cv-section-heading" style="margin-top:16px;">Health conditions</div>', unsafe_allow_html=True)
    if profile["conditions"]:
        badges_html = "".join(f'<span class="badge-pill">{c}</span>' for c in profile["conditions"])
        st.markdown(badges_html, unsafe_allow_html=True)
    else:
        st.caption("No conditions on file.")

with right_col:
    with panel():
        st.markdown('<div class="cv-section-heading">Personal information</div>', unsafe_allow_html=True)

        with st.form("profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", value=profile["name"])
                email = st.text_input("Email", value=profile["email"])
                phone = st.text_input("Phone", value=profile["phone"])
                dob = st.date_input("Date of Birth", value=profile["dob"])
            with c2:
                gender = st.selectbox(
                    "Gender", ["Female", "Male", "Non-binary", "Prefer not to say"],
                    index=["Female", "Male", "Non-binary", "Prefer not to say"].index(profile["gender"])
                    if profile["gender"] in ["Female", "Male", "Non-binary", "Prefer not to say"] else 0,
                )
                blood_group = st.selectbox(
                    "Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                    index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(profile["blood_group"]),
                )
                height_cm = st.number_input("Height (cm)", min_value=50, max_value=250, value=profile["height_cm"])
                weight_kg = st.number_input("Weight (kg)", min_value=10, max_value=300, value=profile["weight_kg"])

            conditions_text = st.text_area(
                "Health Conditions (comma-separated)",
                value=", ".join(profile["conditions"]),
            )

            submitted = st.form_submit_button("Save changes", type="primary")
            if submitted:
                st.session_state.user_profile.update({
                    "name": name, "email": email, "phone": phone, "dob": dob,
                    "gender": gender, "blood_group": blood_group,
                    "height_cm": height_cm, "weight_kg": weight_kg,
                    "conditions": [c.strip() for c in conditions_text.split(",") if c.strip()],
                })
                st.success("Profile updated successfully.")
                st.rerun()

    # BMI card
    bmi = round(profile["weight_kg"] / ((profile["height_cm"] / 100) ** 2), 1)
    bmi_category = (
        "Underweight" if bmi < 18.5 else
        "Normal" if bmi < 25 else
        "Overweight" if bmi < 30 else
        "Obese"
    )
    with panel("gold"):
        st.markdown('<div class="cv-section-heading">Body mass index</div>', unsafe_allow_html=True)
        b1, b2 = st.columns([1, 2])
        with b1:
            st.markdown(f'<div class="stat-value" style="font-size:2rem;">{bmi}</div>', unsafe_allow_html=True)
            st.caption(bmi_category)
        with b2:
            st.progress(min(bmi / 40, 1.0))
            st.caption("Calculated from your saved height and weight. Not a medical assessment.")

    # Account settings
    with panel("flat"):
        st.markdown('<div class="cv-section-heading">Account settings</div>', unsafe_allow_html=True)
        st.toggle("Email notifications for new reports", value=True)
        st.toggle("Share anonymized data to improve detection models", value=False)
        if st.button("Change password", type="secondary"):
            st.info("Password reset isn't wired up yet — hook this button to your auth backend's reset flow.")

footnote(
    "Health details on this page support personalized AI screening and are not a "
    "substitute for professional medical records."
)
