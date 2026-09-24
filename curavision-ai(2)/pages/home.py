import textwrap
import streamlit as st
from theme import inject_theme, top_nav, icon, footnote

st.set_page_config(
    page_title="Overview | CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

HOME_CSS = """
.cv-hero-title {
    font-family: var(--font-serif);
    font-size: 2.6rem;
    font-weight: 600;
    line-height: 1.15;
    color: var(--ink);
    margin-bottom: 14px;
}
.cv-hero-desc {
    color: var(--ink-soft);
    font-size: 1.02rem;
    line-height: 1.6;
    max-width: 460px;
    margin-bottom: 24px;
}
.cv-facts { display: flex; gap: 28px; margin-top: 24px; flex-wrap: wrap; }
.cv-fact-value { font-family: var(--font-mono); font-size: 1.15rem; color: var(--accent-dark); font-weight: 600; }
.cv-fact-label { color: var(--ink-soft); font-size: 0.8rem; }

.cv-mock {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    box-shadow: 3px 3px 0 var(--line);
}
.cv-mock-head {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--line); padding-bottom: 10px; margin-bottom: 12px;
}
.cv-mock-title { font-family: var(--font-mono); font-size: 0.78rem; color: var(--ink-soft); letter-spacing: 0.02em; }
.cv-mock-row { display:flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px dashed var(--line); font-size: 0.87rem; }
.cv-mock-row:last-child { border-bottom: none; }
.cv-mock-row span:first-child { color: var(--ink-soft); }
.cv-mock-row span:last-child { font-family: var(--font-mono); color: var(--ink); }

.cv-feature {
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    height: 100%;
}
.cv-feature h4 { font-family: var(--font-serif); font-size: 1rem; margin: 8px 0 6px 0; color: var(--ink); }
.cv-feature p { color: var(--ink-soft); font-size: 0.86rem; margin: 0; line-height: 1.5; }

.cv-quote {
    background: var(--surface-sunken);
    border-left: 3px solid var(--line-strong);
    border-radius: var(--radius-sm);
    padding: 16px 18px;
    color: var(--ink);
    font-size: 0.88rem;
    line-height: 1.55;
    height: 100%;
}
.cv-quote .author { color: var(--ink-soft); font-size: 0.8rem; margin-top: 10px; font-family: var(--font-mono); }
"""

inject_theme(HOME_CSS)
top_nav()

# --- Hero ---
col_text, col_mock = st.columns([1.15, 1])

with col_text:
    st.markdown('<div class="cv-hero-title">A second read on<br>what your symptoms<br>and scans are saying.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cv-hero-desc">CuraVision AI pairs an uploaded image with a structured '
        'symptom log and gives you one combined read — a starting point for a conversation '
        'with your doctor, not a replacement for one.</div>',
        unsafe_allow_html=True,
    )

    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("Start a detection", type="primary", use_container_width=True):
            st.switch_page("pages/disease_detection.py")
    with btn2:
        if st.button("Ask the assistant", type="secondary", use_container_width=True):
            st.switch_page("pages/assistant.py")

    st.markdown(
        textwrap.dedent("""\
        <div class="cv-facts">
        <div><div class="cv-fact-value">2 signals</div><div class="cv-fact-label">image + symptoms, combined</div></div>
        <div><div class="cv-fact-value">&lt; 2 min</div><div class="cv-fact-label">to a preliminary read</div></div>
        <div><div class="cv-fact-value">local</div><div class="cv-fact-label">your data stays in your account</div></div>
        </div>
        """),
        unsafe_allow_html=True,
    )

with col_mock:
    st.markdown(
        textwrap.dedent("""\
        <div class="cv-mock">
        <div class="cv-mock-head">
        <span class="cv-mock-title">SAMPLE · COMBINED ASSESSMENT</span>
        </div>
        <div class="cv-mock-row"><span>Image analysis</span><span>No abnormality</span></div>
        <div class="cv-mock-row"><span>Reported symptoms</span><span>3 selected</span></div>
        <div class="cv-mock-row"><span>Duration</span><span>4 days</span></div>
        <div class="cv-mock-row"><span>Combined confidence</span><span>22.4%</span></div>
        <div class="cv-mock-row"><span>Risk band</span><span>Low</span></div>
        </div>
        """),
        unsafe_allow_html=True,
    )

st.write("")
st.write("")

# --- What it does ---
st.markdown('<div class="cv-section-heading" style="font-size:1.3rem;margin-top:10px;">What each part does</div>', unsafe_allow_html=True)

features_data = [
    ("scan", "Disease detection", "Upload an X-ray, scan, or lesion photo and log symptoms alongside it for one combined result."),
    ("chat", "Health assistant", "A chat window for quick questions about symptoms, medication, or general lifestyle guidance."),
    ("file", "Report history", "Every assessment is kept as a report you can filter, review, and export to PDF."),
    ("chart", "Trend dashboard", "Confidence scores and risk flags plotted over time, so a one-off result has context."),
]

cols = st.columns(4)
for col, (ic, title, desc) in zip(cols, features_data):
    with col:
        st.markdown(
            f'<div class="cv-feature">{icon(ic)}<h4>{title}</h4><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

st.write("")

# --- How people are using it ---
st.markdown('<div class="cv-section-heading" style="font-size:1.3rem;">Notes from early testers</div>', unsafe_allow_html=True)

reviews_data = [
    ("Flagged something my routine checkup hadn't come up yet — I brought the report to my GP the same week.", "S. Mehta, patient tester"),
    ("The combined view is the useful part. Neither signal alone would've moved me to book an appointment.", "J. Okafor, patient tester"),
    ("Straightforward enough that I didn't need a walkthrough. The report export is a nice touch for my files.", "P. Kaur, patient tester"),
]

cols = st.columns(3)
for col, (quote, author) in zip(cols, reviews_data):
    with col:
        st.markdown(
            f'<div class="cv-quote">\u201c{quote}\u201d<div class="author">{author}</div></div>',
            unsafe_allow_html=True,
        )

footnote(
    "CuraVision AI produces preliminary, AI-assisted screening results — not a medical "
    "diagnosis. Always follow up with a licensed healthcare professional. "
    "\u00a9 2026 CuraVision AI · support@curavision.ai"
)
