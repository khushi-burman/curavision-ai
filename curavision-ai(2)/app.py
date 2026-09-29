
import streamlit as st
from theme import inject_theme, icon

st.set_page_config(
    page_title="CuraVision AI | AI-assisted health screening",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if st.session_state.get("logged_in"):
    st.switch_page("pages/home.py")

LANDING_CSS = """
[data-testid="stMainBlockContainer"] {
    max-width: 1180px;
    padding-top: 0.8rem;
    padding-bottom: 3rem;
}
.cv-landing-nav {
    display:flex; align-items:center; justify-content:space-between;
    padding:10px 0 18px; border-bottom:1px solid var(--line-strong);
    margin-bottom:52px;
}
.cv-landing-brand {
    display:flex; align-items:center; gap:10px;
    font-family:var(--font-serif); font-weight:600; font-size:1.6rem;
    color:var(--ink);
}
.cv-landing-nav-note { color:var(--ink-soft); font-size:.78rem; font-family:var(--font-mono); }
.cv-eyebrow {
    display:inline-flex; align-items:center; gap:8px; color:var(--accent-dark);
    background:var(--accent-soft); border:1px solid rgba(47,111,94,.2);
    border-radius:20px; padding:6px 11px; font-family:var(--font-mono);
    font-size:.72rem; letter-spacing:.02em; margin-bottom:18px;
}
.cv-hero-title {
    font-family:var(--font-serif); font-size:clamp(2.8rem,5.2vw,4.65rem);
    line-height:1.03; letter-spacing:-.035em; font-weight:600;
    color:var(--ink); max-width:760px; margin-bottom:20px;
}
.cv-hero-title em { color:var(--accent); font-style:normal; }
.cv-hero-copy {
    color:var(--ink-soft); font-size:1.04rem; line-height:1.7;
    max-width:670px; margin-bottom:25px;
}
.cv-hero-note { color:var(--ink-faint); font-size:.76rem; line-height:1.5; margin-top:13px; max-width:650px; }
.cv-hero-card {
    background:var(--surface); border:1px solid var(--line); border-radius:8px;
    padding:25px; box-shadow:0 12px 35px rgba(32,43,38,.07); margin-top:10px;
}
.cv-card-label { color:var(--ink-faint); font-family:var(--font-mono); font-size:.68rem; letter-spacing:.05em; margin-bottom:17px; }
.cv-signal {
    display:flex; justify-content:space-between; align-items:center;
    padding:12px 0; border-bottom:1px solid var(--line); font-size:.84rem;
}
.cv-signal:last-child { border-bottom:0; }
.cv-signal-name { color:var(--ink-soft); }
.cv-signal-value { color:var(--ink); font-family:var(--font-mono); font-size:.75rem; }
.cv-signal-value.good { color:var(--accent-dark); }
.cv-preview-result {
    background:var(--surface-sunken); border:1px solid var(--line);
    border-radius:5px; padding:13px 14px; margin-top:15px;
}
.cv-preview-result strong { display:block; color:var(--ink); font-size:.82rem; margin-bottom:3px; }
.cv-preview-result span { color:var(--ink-soft); font-size:.75rem; line-height:1.45; }
.cv-section { padding:48px 0 18px; }
.cv-section-kicker {
    color:var(--accent-dark); font-family:var(--font-mono); font-size:.7rem;
    letter-spacing:.06em; text-transform:uppercase; margin-bottom:8px;
}
.cv-section-title { font-family:var(--font-serif); font-size:1.8rem; font-weight:600; color:var(--ink); margin-bottom:10px; }
.cv-section-copy { color:var(--ink-soft); font-size:.92rem; line-height:1.6; max-width:650px; margin-bottom:24px; }
.cv-feature {
    height:100%; background:var(--surface); border:1px solid var(--line);
    border-radius:6px; padding:22px;
}
.cv-feature-icon {
    width:34px; height:34px; display:flex; align-items:center; justify-content:center;
    color:var(--accent-dark); background:var(--accent-soft); border-radius:5px; margin-bottom:16px;
}
.cv-feature h3 { font-family:var(--font-serif); font-size:1.05rem; margin:0 0 7px; color:var(--ink); }
.cv-feature p { margin:0; color:var(--ink-soft); font-size:.82rem; line-height:1.55; }
.cv-step { border-top:2px solid var(--line-strong); padding-top:15px; height:100%; }
.cv-step-num { font-family:var(--font-mono); font-size:.7rem; color:var(--accent-dark); margin-bottom:10px; }
.cv-step h3 { font-family:var(--font-serif); font-size:1rem; margin:0 0 6px; }
.cv-step p { color:var(--ink-soft); font-size:.81rem; line-height:1.5; margin:0; }
.cv-trust {
    background:var(--surface-sunken); border:1px solid var(--line);
    border-radius:7px; padding:24px; margin-top:26px;
}
.cv-trust strong { font-family:var(--font-serif); color:var(--ink); }
.cv-trust p { color:var(--ink-soft); font-size:.8rem; line-height:1.55; margin:7px 0 0; }
.cv-landing-footer {
    border-top:1px solid var(--line-strong); margin-top:58px; padding-top:17px;
    display:flex; justify-content:space-between; gap:20px; color:var(--ink-faint); font-size:.72rem;
}
"""

inject_theme(LANDING_CSS)

st.markdown(
    '<div class="cv-landing-nav">'
    '<div class="cv-landing-brand">' + icon("pulse") + ' CuraVision AI</div>'
    '<div class="cv-landing-nav-note">AI-assisted health screening</div>'
    '</div>',
    unsafe_allow_html=True,
)

hero_left, hero_right = st.columns([1.35, .8], gap="large")

with hero_left:
    st.markdown(
        '<div class="cv-eyebrow">' + icon("pulse") + ' SCREEN · UNDERSTAND · FOLLOW UP</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cv-hero-title">A clearer starting point for <em>health decisions.</em></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cv-hero-copy">CuraVision AI brings together image-based screening, '
        'symptom information, health guidance, and assessment history in one focused workspace. '
        'Use it to organize what you are noticing and prepare for a conversation with a healthcare professional.</div>',
        unsafe_allow_html=True,
    )
    b1, b2 = st.columns([1, 1], gap="small")
    with b1:
        if st.button("Get started", type="primary", use_container_width=True):
            st.switch_page("pages/signup.py")
    with b2:
        if st.button("Sign in", type="secondary", use_container_width=True):
            st.switch_page("pages/login.py")
    st.markdown(
        '<div class="cv-hero-note">CuraVision provides AI-assisted screening and educational guidance. '
        'It does not replace examination, diagnosis, or treatment by a qualified healthcare professional.</div>',
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown(
        '<div class="cv-hero-card">'
        '<div class="cv-card-label">HOW A CURAVISION ASSESSMENT CAN LOOK</div>'
        '<div class="cv-signal"><span class="cv-signal-name">Image signal</span><span class="cv-signal-value good">ANALYZED</span></div>'
        '<div class="cv-signal"><span class="cv-signal-name">Symptoms</span><span class="cv-signal-value">STRUCTURED</span></div>'
        '<div class="cv-signal"><span class="cv-signal-name">Risk context</span><span class="cv-signal-value">REVIEWED</span></div>'
        '<div class="cv-preview-result"><strong>Assessment summary</strong>'
        '<span>Signals are presented together so you can review the result and decide what to discuss next.</span></div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="cv-section"><div class="cv-section-kicker">One workspace</div>'
    '<div class="cv-section-title">Designed around the way health information connects.</div>'
    '<div class="cv-section-copy">Instead of treating every input as a separate screen, CuraVision keeps the important pieces together so your results have context.</div></div>',
    unsafe_allow_html=True,
)

features = [
    ("scan", "Image screening", "Upload supported medical or skin images and receive an AI-assisted screening result for review."),
    ("chat", "Health assistant", "Ask general health questions and get structured, easy-to-follow information in one place."),
    ("file", "Reports & history", "Keep assessments organized so previous results can be reviewed when you need them."),
    ("chart", "Health overview", "See your assessment activity and trends in a single dashboard instead of scattered notes."),
]
cols = st.columns(4, gap="medium")
for col, (ic, title, desc) in zip(cols, features):
    with col:
        st.markdown(
            '<div class="cv-feature"><div class="cv-feature-icon">' + icon(ic) + '</div>'
            f'<h3>{title}</h3><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="cv-section"><div class="cv-section-kicker">Simple workflow</div>'
    '<div class="cv-section-title">From information to a clearer next conversation.</div>'
    '<div class="cv-section-copy">The workflow is intentionally straightforward: provide information, review the AI-assisted output, then use it as context for the next step.</div></div>',
    unsafe_allow_html=True,
)

steps = [
    ("01", "Share information", "Upload an image or record symptoms and relevant details in the screening workspace."),
    ("02", "Review the result", "CuraVision organizes the available signals into a readable preliminary assessment."),
    ("03", "Decide what to discuss", "Use the report and history as supporting information when speaking with a qualified professional."),
]
cols = st.columns(3, gap="large")
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div class="cv-step"><div class="cv-step-num">{num}</div>'
            f'<h3>{title}</h3><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="cv-trust"><strong>A responsible role for AI in healthcare</strong>'
    '<p>CuraVision is intended to support awareness and preparation, not to make final medical decisions. '
    'AI outputs can be incomplete or incorrect. For urgent symptoms, worsening conditions, or concerns about a serious illness, seek appropriate medical care directly.</p></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="cv-landing-footer"><span>© 2026 CuraVision AI</span>'
    '<span>AI-assisted screening · Not a substitute for professional medical advice</span></div>',
    unsafe_allow_html=True,
)
