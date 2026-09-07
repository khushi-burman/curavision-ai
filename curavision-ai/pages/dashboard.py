import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(
    page_title="Dashboard • CuraVision AI",
    page_icon="📊",
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
        background: radial-gradient(circle at 15% 10%, #10264a 0%, #071224 45%, #030712 100%);
        color: #e8f0ff;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 24px 26px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
    }

    .page-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7dd3fc, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .page-subtitle {
        color: #93a8cc;
        font-size: 0.95rem;
        margin-bottom: 22px;
    }

    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 18px 20px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: -30px;
        right: -30px;
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: radial-gradient(circle, var(--kpi-glow, rgba(96,165,250,0.35)), transparent 70%);
    }
    .kpi-icon { font-size: 1.3rem; margin-bottom: 6px; }
    .kpi-label {
        color: #93a8cc;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #f1f6ff;
        line-height: 1.1;
    }
    .kpi-delta-up { 
    color: #86efac; 
    font-size: 0.8rem; 
    font-weight: 600; 
    }
    .kpi-delta-down {
      color: #fca5a5; 
      font-size: 0.8rem; 
      font-weight: 600; 
      }
    .kpi-delta-flat { 
    color: #93a8cc; 
    font-size: 0.8rem; 
    font-weight: 600; 
    }

    .section-heading {
        font-size: 1.15rem;
        font-weight: 700;
        color: #cfe3ff;
        margin-bottom: 14px;
    }

    .insight-card {
        background: linear-gradient(135deg, rgba(96,165,250,0.14), rgba(167,139,250,0.10));
        border: 1px solid rgba(125,211,252,0.3);
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 20px;
    }
    .insight-title {
        font-weight: 700;
        color: #bfdbfe;
        font-size: 0.9rem;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .insight-text {
        color: #e2ecff;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .activity-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 10px;
    }

    .risk-high {
        display: inline-block; padding: 3px 12px; border-radius: 999px;
        background: rgba(248, 113, 113, 0.15); border: 1px solid rgba(248, 113, 113, 0.5);
        color: #fca5a5; font-weight: 600; font-size: 0.78rem;
    }
    .risk-low {
        display: inline-block; padding: 3px 12px; border-radius: 999px;
        background: rgba(74, 222, 128, 0.15); border: 1px solid rgba(74, 222, 128, 0.5);
        color: #86efac; font-weight: 600; font-size: 0.78rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white; border: none; border-radius: 12px;
        padding: 8px 20px; font-weight: 600; transition: transform 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- nav bar ---

nav_left, nav_right = st.columns([1, 3])

with nav_left:
    st.markdown("## CuraVision AI")

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
st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Your health-monitoring overview — scans, risk trends, '
    'and recent activity at a glance.</div>',
    unsafe_allow_html=True,
)

# --- mock / session data — replace with your real DB-backed metrics ---
# widened to 45 days so week-over-week and month-over-month deltas below have
# a real "previous period" to compare against, instead of being hardcoded
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
    arrow = "▲" if value > 0 else "▼"
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
    ("🩻", "Total Scans", total_scans, delta_badge(scans_delta), "rgba(96,165,250,0.35)"),
    ("⚠️", "High-Risk Alerts", high_risk_count, delta_badge(risk_delta, invert=True), "rgba(248,113,113,0.35)"),
    ("📈", "Avg Confidence", f"{avg_confidence}%", delta_badge(conf_delta), "rgba(167,139,250,0.35)"),
    ("✅", "Low-Risk Scans", low_risk_count, delta_badge(None), "rgba(74,222,128,0.35)"),
]

k1, k2, k3, k4 = st.columns(4)
for col, (icon, label, value, (delta_css, delta_text), glow) in zip([k1, k2, k3, k4], kpis):
    col.markdown(
        f"""
        <div class="kpi-card" style="--kpi-glow:{glow};">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_css}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# --- AI insight summary, generated from the actual data above ---
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
    f"""
    <div class="insight-card">
        <div class="insight-title">🧠 AI Insight</div>
        <div class="insight-text">{insight}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- charts row ---
chart_col1, chart_col2 = st.columns([2, 1])

PLOT_BG = "rgba(0,0,0,0)"
FONT_COLOR = "#cfe3ff"

with chart_col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Confidence Score Trend</div>', unsafe_allow_html=True)

    trend_df = df.sort_values("date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend_df["date"], y=trend_df["confidence"],
        mode="lines+markers",
        line=dict(color="#60a5fa", width=3, shape="spline"),
        marker=dict(size=8, color="#a78bfa", line=dict(width=1, color="#e0e7ff")),
        fill="tozeroy",
        fillcolor="rgba(96,165,250,0.15)",
        name="Confidence",
    ))
    fig.add_hline(y=45, line_dash="dash", line_color="#f87171",
                  annotation_text="Risk threshold", annotation_font_color="#f87171")
    fig.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="Confidence %"),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Risk Distribution</div>', unsafe_allow_html=True)

    risk_counts = df["risk"].value_counts().reindex(["low", "high"]).fillna(0)
    fig2 = go.Figure(data=[go.Pie(
        labels=["Low Risk", "High Risk"],
        values=[risk_counts.get("low", 0), risk_counts.get("high", 0)],
        hole=0.65,
        marker=dict(colors=["#4ade80", "#f87171"], line=dict(color="#071224", width=2)),
        textfont=dict(color="#0b1120", size=13),
    )])
    fig2.add_annotation(
        text=f"{total_scans}<br><span style='font-size:11px;'>scans</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(color="#e8f0ff", size=18),
    )
    fig2.update_layout(
        paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR),
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        height=300,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- detection type breakdown + weekly volume side by side ---
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Scans by Detection Type</div>', unsafe_allow_html=True)

    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig3 = px.bar(
        type_counts, x="type", y="count", text="count",
        color="type",
        color_discrete_sequence=["#60a5fa", "#a78bfa", "#7dd3fc"],
    )
    fig3.update_traces(textposition="outside", marker_line_width=0)
    fig3.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="Scans"),
        showlegend=False,
        height=280,
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Weekly Scan Volume</div>', unsafe_allow_html=True)

    weekly = df.set_index("date").resample("W")["confidence"].count().reset_index()
    weekly.columns = ["week", "scans"]
    fig4 = px.area(weekly, x="week", y="scans")
    fig4.update_traces(line_color="#7dd3fc", fillcolor="rgba(125,211,252,0.18)")
    fig4.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="Scans"),
        height=280,
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- recent activity + quick actions ---
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Recent Activity</div>', unsafe_allow_html=True)

    recent = df.sort_values("date", ascending=False).head(5)
    for _, row in recent.iterrows():
        badge_class = "risk-high" if row["risk"] == "high" else "risk-low"
        st.markdown(
            f"""
            <div class="activity-row">
                <div>
                    <strong>{row['type']}</strong><br>
                    <span style="color:#93a8cc; font-size:0.85rem;">{row['date'].strftime('%b %d, %Y')}</span>
                </div>
                <div style="text-align:right;">
                    <span class="{badge_class}">{row['risk'].upper()}</span><br>
                    <span style="color:#cfe3ff; font-size:0.85rem;">{row['confidence']}% confidence</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Quick Actions</div>', unsafe_allow_html=True)
    if st.button("🩺 New Detection", use_container_width=True):
        st.switch_page("pages/disease_detection.py")
    if st.button("📋 View All Reports", use_container_width=True):
        st.switch_page("pages/reports.py")
    if st.button("👤 Update Profile", use_container_width=True):
        st.switch_page("pages/profile.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.caption(
    "⚠️ Dashboard metrics reflect AI-assisted preliminary screenings, not confirmed "
    "medical diagnoses. Always consult a licensed healthcare professional."
)
