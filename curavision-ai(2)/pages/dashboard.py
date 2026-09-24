import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
from theme import inject_theme, top_nav, page_header, risk_badge, icon, footnote, panel

st.set_page_config(
    page_title="Dashboard • CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

DASHBOARD_CSS = """
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    border-left: 3px solid var(--kpi-stripe, var(--accent));
}
.kpi-label { color: var(--ink-soft); font-size: 0.78rem; margin-bottom: 6px; }
.kpi-value { font-family: var(--font-mono); font-size: 1.7rem; font-weight: 600; color: var(--ink); line-height: 1.1; }
.kpi-delta-up   { color: var(--accent-dark); font-size: 0.8rem; font-weight: 500; font-family: var(--font-mono); }
.kpi-delta-down { color: var(--alert); font-size: 0.8rem; font-weight: 500; font-family: var(--font-mono); }
.kpi-delta-flat { color: var(--ink-faint); font-size: 0.8rem; font-weight: 500; font-family: var(--font-mono); }

.insight-card {
    background: var(--accent-soft);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    margin-bottom: 18px;
}
.insight-title { font-weight: 600; color: var(--accent-dark); font-size: 0.82rem; margin-bottom: 5px; }
.insight-text { color: var(--ink); font-size: 0.92rem; line-height: 1.5; }

.activity-row {
    display: flex; justify-content: space-between; align-items: center;
    background: var(--surface-sunken);
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 10px 16px;
    margin-bottom: 8px;
}
"""

inject_theme(DASHBOARD_CSS)
top_nav()

page_header(
    "Dashboard",
    "Your health-monitoring overview — scans, risk trends, and recent activity at a glance.",
    "chart",
)

# --- mock / session data — replace with your real DB-backed metrics ---
if "dashboard_history" not in st.session_state:
    today = date.today()
    st.session_state.dashboard_history = pd.DataFrame([
        {"date": today - timedelta(days=42), "type": "Symptom Checker", "risk": "low", "confidence": 12},
        {"date": today - timedelta(days=38), "type": "Image Detection", "risk": "low", "confidence": 19},
        {"date": today - timedelta(days=34), "type": "Symptom Checker", "risk": "low", "confidence": 25},
        {"date": today - timedelta(days=30), "type": "Combined", "risk": "high", "confidence": 51},
        {"date": today - timedelta(days=27), "type": "Symptom Checker", "risk": "low", "confidence": 15},
        {"date": today - timedelta(days=24), "type": "Image Detection", "risk": "low", "confidence": 22},
        {"date": today - timedelta(days=20), "type": "Combined", "risk": "high", "confidence": 58},
        {"date": today - timedelta(days=17), "type": "Symptom Checker", "risk": "low", "confidence": 30},
        {"date": today - timedelta(days=14), "type": "Image Detection", "risk": "high", "confidence": 66},
        {"date": today - timedelta(days=10), "type": "Combined", "risk": "high", "confidence": 72},
        {"date": today - timedelta(days=7), "type": "Symptom Checker", "risk": "low", "confidence": 20},
        {"date": today - timedelta(days=4), "type": "Image Detection", "risk": "low", "confidence": 28},
        {"date": today - timedelta(days=1), "type": "Combined", "risk": "high", "confidence": 72},
    ])

df = st.session_state.dashboard_history.copy()
df["date"] = pd.to_datetime(df["date"])

# --- KPI metrics, with real period-over-period deltas ---
today_ts = pd.Timestamp(date.today())
last_14 = df[df["date"] >= today_ts - pd.Timedelta(days=14)]
prev_14 = df[(df["date"] < today_ts - pd.Timedelta(days=14)) & (df["date"] >= today_ts - pd.Timedelta(days=28))]


def pct_delta(current, previous):
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 1)


def delta_badge(value, unit="%", invert=False):
    """invert=True means a rise is bad (e.g. high-risk alerts)."""
    if value is None:
        return "kpi-delta-flat", "no prior data"
    if value == 0:
        return "kpi-delta-flat", "steady"
    good = (value > 0) != invert
    css = "kpi-delta-up" if good else "kpi-delta-down"
    arrow = "up" if value > 0 else "down"
    return css, f"{arrow} {abs(value)}{unit} vs prior 14d"


total_scans = len(df)
high_risk_count = int((df["risk"] == "high").sum())
avg_confidence = round(df["confidence"].mean(), 1)
low_risk_count = int((df["risk"] == "low").sum())

scans_delta = pct_delta(len(last_14), len(prev_14))
risk_delta = pct_delta(
    int((last_14["risk"] == "high").sum()), int((prev_14["risk"] == "high").sum())
)
conf_delta = pct_delta(
    last_14["confidence"].mean() if len(last_14) else 0,
    prev_14["confidence"].mean() if len(prev_14) else 0,
)

kpis = [
    ("Total scans", total_scans, delta_badge(scans_delta), "var(--accent)"),
    ("High-risk alerts", high_risk_count, delta_badge(risk_delta, invert=True), "var(--alert)"),
    ("Avg confidence", f"{avg_confidence}%", delta_badge(conf_delta), "var(--gold)"),
    ("Low-risk scans", low_risk_count, delta_badge(None), "var(--line-strong)"),
]

k1, k2, k3, k4 = st.columns(4)
for col, (label, value, (delta_css, delta_text), stripe) in zip([k1, k2, k3, k4], kpis):
    col.markdown(
        f'<div class="kpi-card" style="--kpi-stripe:{stripe};">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="{delta_css}">{delta_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.write("")

# --- insight summary, generated from the actual data above ---
if high_risk_count > low_risk_count:
    insight = (
        f"Most of your recent scans ({high_risk_count} of {total_scans}) came back high-risk. "
        "Consider following up on the most recent flagged result with a healthcare professional."
    )
elif risk_delta and risk_delta > 0:
    insight = (
        f"High-risk detections are up {risk_delta}% compared to the prior 14 days — "
        "worth keeping an eye on if this trend continues."
    )
else:
    insight = (
        f"Your scan history looks stable — {low_risk_count} of {total_scans} results were low-risk, "
        f"with an average confidence score of {avg_confidence}%."
    )

st.markdown(
    f'<div class="insight-card">'
    f'<div class="insight-title">Reading the trend</div>'
    f'<div class="insight-text">{insight}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# --- charts row ---
chart_col1, chart_col2 = st.columns([2, 1])

PLOT_BG = "rgba(0,0,0,0)"
FONT_COLOR = "#202B26"
GRID_COLOR = "rgba(32,43,38,0.10)"

with chart_col1, panel():
    st.markdown('<div class="cv-section-heading">Confidence score trend</div>', unsafe_allow_html=True)

    trend_df = df.sort_values("date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend_df["date"], y=trend_df["confidence"],
        mode="lines+markers",
        line=dict(color="#2F6F5E", width=2.5, shape="spline"),
        marker=dict(size=7, color="#2F6F5E", line=dict(width=1, color="#FBFAF5")),
        fill="tozeroy",
        fillcolor="rgba(47,111,94,0.10)",
        name="Confidence",
    ))
    fig.add_hline(y=45, line_dash="dash", line_color="#B5462F",
                  annotation_text="Risk threshold", annotation_font_color="#B5462F")
    fig.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, family="IBM Plex Sans"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title="Confidence %"),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)

with chart_col2, panel():
    st.markdown('<div class="cv-section-heading">Risk distribution</div>', unsafe_allow_html=True)

    risk_counts = df["risk"].value_counts().reindex(["low", "high"]).fillna(0)
    fig2 = go.Figure(data=[go.Pie(
        labels=["Low risk", "High risk"],
        values=[risk_counts.get("low", 0), risk_counts.get("high", 0)],
        hole=0.65,
        marker=dict(colors=["#2F6F5E", "#B5462F"], line=dict(color="#FBFAF5", width=2)),
        textfont=dict(color="#FBFAF5", size=13),
    )])
    fig2.add_annotation(
        text=f"{total_scans}<br><span style='font-size:11px;'>scans</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(color="#202B26", size=18),
    )
    fig2.update_layout(
        paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, family="IBM Plex Sans"),
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        height=300,
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- detection type breakdown + weekly volume side by side ---
chart_col3, chart_col4 = st.columns(2)

with chart_col3, panel():
    st.markdown('<div class="cv-section-heading">Scans by detection type</div>', unsafe_allow_html=True)

    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig3 = px.bar(
        type_counts, x="type", y="count", text="count",
        color="type",
        color_discrete_sequence=["#2F6F5E", "#A6792E", "#8FA98F"],
    )
    fig3.update_traces(textposition="outside", marker_line_width=0)
    fig3.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, family="IBM Plex Sans"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title="Scans"),
        showlegend=False,
        height=280,
    )
    st.plotly_chart(fig3, use_container_width=True)

with chart_col4, panel():
    st.markdown('<div class="cv-section-heading">Weekly scan volume</div>', unsafe_allow_html=True)

    weekly = df.set_index("date").resample("W")["confidence"].count().reset_index()
    weekly.columns = ["week", "scans"]
    fig4 = px.area(weekly, x="week", y="scans")
    fig4.update_traces(line_color="#2F6F5E", fillcolor="rgba(47,111,94,0.14)")
    fig4.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, family="IBM Plex Sans"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title="Scans"),
        height=280,
    )
    st.plotly_chart(fig4, use_container_width=True)

# --- recent activity + quick actions ---
left, right = st.columns([2, 1])

with left, panel():
    st.markdown('<div class="cv-section-heading">Recent activity</div>', unsafe_allow_html=True)

    recent = df.sort_values("date", ascending=False).head(5)
    for _, row in recent.iterrows():
        st.markdown(
            f'<div class="activity-row">'
            f'<div><strong>{row["type"]}</strong><br>'
            f'<span style="color:var(--ink-soft); font-size:0.85rem;">{row["date"].strftime("%b %d, %Y")}</span></div>'
            f'<div style="text-align:right;">{risk_badge(row["risk"])}<br>'
            f'<span style="color:var(--ink-soft); font-size:0.85rem;font-family:var(--font-mono);">{row["confidence"]}% confidence</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

with right, panel():
    st.markdown('<div class="cv-section-heading">Quick actions</div>', unsafe_allow_html=True)
    if st.button("New detection", use_container_width=True, type="secondary"):
        st.switch_page("pages/disease_detection.py")
    if st.button("View all reports", use_container_width=True, type="secondary"):
        st.switch_page("pages/reports.py")
    if st.button("Update profile", use_container_width=True, type="secondary"):
        st.switch_page("pages/profile.py")

footnote(
    "Dashboard metrics reflect AI-assisted preliminary screenings, not confirmed "
    "medical diagnoses. Always consult a licensed healthcare professional."
)
