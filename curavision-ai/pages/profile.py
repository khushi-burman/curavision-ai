import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Profile • CuraVision AI",
    page_icon="👤",
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
        padding: 26px 28px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
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
        margin-bottom: 24px;
    }

    .avatar-ring {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        margin: 0 auto 16px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        font-weight: 700;
        color: white;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        box-shadow: 0 0 0 4px rgba(125, 211, 252, 0.25), 0 8px 30px rgba(37, 99, 235, 0.4);
    }

    .profile-name {
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        color: #f1f6ff;
        margin-bottom: 2px;
    }
    .profile-email {
        text-align: center;
        color: #9db4d9;
        font-size: 0.9rem;
        margin-bottom: 18px;
    }

    .stat-pill {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 14px 10px;
        text-align: center;
    }
    .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f1f6ff;
    }
    .stat-label {
        color: #9db4d9;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .section-heading {
        font-size: 1.1rem;
        font-weight: 700;
        color: #cfe3ff;
        margin-bottom: 14px;
    }

    .badge-pill {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 999px;
        background: rgba(96, 165, 250, 0.15);
        border: 1px solid rgba(96, 165, 250, 0.4);
        color: #bfdbfe;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px 4px 3px 0;
    }

    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white; border: none; border-radius: 12px;
        padding: 8px 22px; font-weight: 600; transition: transform 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4);
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input {
        background: rgba(255,255,255,0.05);
        color: #e8f0ff;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- nav bar (same pattern as the rest of the app) ---
nav_left, nav_right = st.columns([1, 3])

with nav_left:
    st.markdown("## 🩺 CuraVision AI")

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
                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.switch_page("app.py")
            else:
                st.page_link(target, label=label)

st.divider()

# --- header ---
st.markdown('<div class="page-title">👤 Profile</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Manage your personal details, health info, and account preferences.</div>',
    unsafe_allow_html=True,
)

# --- mock / session data — replace with your real user record ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Alex Morgan",
        "email": "alex.morgan@example.com",
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

with left_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    initials = "".join([p[0] for p in profile["name"].split()[:2]]).upper()
    st.markdown(f'<div class="avatar-ring">{initials}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-name">{profile["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-email">{profile["email"]}</div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.markdown(
            f"""<div class="stat-pill"><div class="stat-value">{profile['total_scans']}</div>
            <div class="stat-label">Total Scans</div></div>""",
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""<div class="stat-pill"><div class="stat-value">{profile['reports_generated']}</div>
            <div class="stat-label">Reports</div></div>""",
            unsafe_allow_html=True,
        )

    st.write("")
    st.caption(f"Member since {profile['member_since'].strftime('%B %Y')}")

    st.markdown('<div class="section-heading" style="margin-top:16px;">Health Conditions</div>', unsafe_allow_html=True)
    if profile["conditions"]:
        badges_html = "".join(f'<span class="badge-pill">{c}</span>' for c in profile["conditions"])
        st.markdown(badges_html, unsafe_allow_html=True)
    else:
        st.caption("No conditions on file.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Personal Information</div>', unsafe_allow_html=True)

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

        submitted = st.form_submit_button("Save Changes")
        if submitted:
            st.session_state.user_profile.update({
                "name": name, "email": email, "phone": phone, "dob": dob,
                "gender": gender, "blood_group": blood_group,
                "height_cm": height_cm, "weight_kg": weight_kg,
                "conditions": [c.strip() for c in conditions_text.split(",") if c.strip()],
            })
            st.success("Profile updated successfully.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # BMI card
    bmi = round(profile["weight_kg"] / ((profile["height_cm"] / 100) ** 2), 1)
    bmi_category = (
        "Underweight" if bmi < 18.5 else
        "Normal" if bmi < 25 else
        "Overweight" if bmi < 30 else
        "Obese"
    )
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Body Mass Index (BMI)</div>', unsafe_allow_html=True)
    b1, b2 = st.columns([1, 2])
    with b1:
        st.markdown(f'<div class="stat-value" style="font-size:2rem;">{bmi}</div>', unsafe_allow_html=True)
        st.caption(bmi_category)
    with b2:
        st.progress(min(bmi / 40, 1.0))
        st.caption("Calculated from your saved height and weight. Not a medical assessment.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Account settings
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Account Settings</div>', unsafe_allow_html=True)
    st.toggle("Email notifications for new reports", value=True)
    st.toggle("Share anonymized data to improve detection models", value=False)
    if st.button("Change Password"):
        st.info("Password reset isn't wired up yet — hook this button to your auth backend's reset flow.")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.caption(
    "⚠️ Health details on this page support personalized AI screening and are not "
    "a substitute for professional medical records."
)