import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from theme import (
    inject_theme,
    top_nav,
    page_header,
    risk_badge,
    footnote,
    panel,
)
from supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dashboard • CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# AUTHENTICATION
# =========================================================

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")


user_id = st.session_state.get("user_id")

if not user_id:
    st.error("User session not found. Please sign in again.")
    st.stop()


# =========================================================
# CSS
# =========================================================

DASHBOARD_CSS = """
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    border-left: 3px solid var(--kpi-stripe, var(--accent));
}

.kpi-label {
    color: var(--ink-soft);
    font-size: 0.78rem;
    margin-bottom: 6px;
}

.kpi-value {
    font-family: var(--font-mono);
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--ink);
    line-height: 1.1;
}

.kpi-delta-up {
    color: var(--accent-dark);
    font-size: 0.8rem;
    font-weight: 500;
    font-family: var(--font-mono);
}

.kpi-delta-down {
    color: var(--alert);
    font-size: 0.8rem;
    font-weight: 500;
    font-family: var(--font-mono);
}

.kpi-delta-flat {
    color: var(--ink-faint);
    font-size: 0.8rem;
    font-weight: 500;
    font-family: var(--font-mono);
}

.insight-card {
    background: var(--accent-soft);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    margin-bottom: 18px;
}

.insight-title {
    font-weight: 600;
    color: var(--accent-dark);
    font-size: 0.82rem;
    margin-bottom: 5px;
}

.insight-text {
    color: var(--ink);
    font-size: 0.92rem;
    line-height: 1.5;
}

.activity-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--surface-sunken);
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 10px 16px;
    margin-bottom: 8px;
}
"""

inject_theme(DASHBOARD_CSS)
top_nav()


# =========================================================
# HEADER
# =========================================================

page_header(
    "Dashboard",
    "Your health-monitoring overview — scans, risk trends, and recent activity at a glance.",
    "chart",
)


# =========================================================
# FETCH HEALTH SCANS
# =========================================================

def fetch_health_scans():

    response = (
        supabase
        .table("health_scans")
        .select("*")
        .eq("user_id", user_id)
        .order("scan_date", desc=True)
        .execute()
    )

    return response.data or []


# =========================================================
# LOAD DATA
# =========================================================

scans = fetch_health_scans()


# =========================================================
# EMPTY STATE
# =========================================================

if not scans:

    st.info(
        "No health scans are available yet. "
        "Complete a skin or chronic-risk scan first."
    )

    st.markdown("### Quick actions")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "New detection",
            use_container_width=True,
            type="primary",
        ):
            st.switch_page(
                "pages/disease_detection.py"
            )

    with c2:
        if st.button(
            "View reports",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/reports.py"
            )

    with c3:
        if st.button(
            "Update profile",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/profile.py"
            )

    footnote(
        "Dashboard metrics reflect AI-assisted preliminary "
        "screenings, not confirmed medical diagnoses. "
        "Always consult a licensed healthcare professional."
    )

    st.stop()


# =========================================================
# CONVERT SUPABASE DATA TO DATAFRAME
# =========================================================

df = pd.DataFrame(scans)


# Date
df["date"] = pd.to_datetime(
    df["scan_date"],
    errors="coerce",
)


# Detection type
def display_detection_type(value):

    mapping = {
        "skin": "Image Detection",
        "chronic_risk": "Chronic Disease Risk",
        "combined": "Combined",
    }

    return mapping.get(
        value,
        str(value).replace("_", " ").title(),
    )


df["type"] = df["detection_type"].apply(
    display_detection_type
)


# Risk
df["risk"] = (
    df["risk_level"]
    .fillna("low")
    .astype(str)
    .str.lower()
)


# =========================================================
# CONFIDENCE / SCORE
# =========================================================

# Skin scans have model_confidence.
# Chronic-risk scans have risk_score instead.
#
# We use model_confidence when available.
# If unavailable, risk_score is shown as the
# available model score for dashboard visualization.

df["score"] = pd.to_numeric(
    df["model_confidence"],
    errors="coerce",
)

risk_score_numeric = pd.to_numeric(
    df["risk_score"],
    errors="coerce",
)

df["score"] = df["score"].fillna(
    risk_score_numeric
)

df["confidence"] = (
    df["score"] * 100
)


# Remove invalid dates
df = df.dropna(
    subset=["date"]
).copy()


# =========================================================
# DATE PERIODS
# =========================================================

today = pd.Timestamp.today().normalize()

last_14 = df[
    df["date"] >= today - pd.Timedelta(days=14)
]

prev_14 = df[
    (df["date"] < today - pd.Timedelta(days=14))
    &
    (df["date"] >= today - pd.Timedelta(days=28))
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def pct_delta(current, previous):

    if previous == 0:
        return None

    return round(
        ((current - previous) / previous) * 100,
        1,
    )


def delta_badge(
    value,
    unit="%",
    invert=False,
):

    if value is None:
        return (
            "kpi-delta-flat",
            "no prior data",
        )

    if value == 0:
        return (
            "kpi-delta-flat",
            "steady",
        )

    good = (
        value > 0
    ) != invert

    css = (
        "kpi-delta-up"
        if good
        else "kpi-delta-down"
    )

    arrow = (
        "up"
        if value > 0
        else "down"
    )

    return (
        css,
        f"{arrow} {abs(value)}{unit} vs prior 14d",
    )


# =========================================================
# KPI METRICS
# =========================================================

total_scans = len(df)

high_risk_count = int(
    (df["risk"] == "high").sum()
)

low_risk_count = int(
    (df["risk"] == "low").sum()
)


valid_scores = df[
    df["confidence"].notna()
]["confidence"]


if len(valid_scores):

    avg_confidence = round(
        valid_scores.mean(),
        1,
    )

else:

    avg_confidence = 0


scans_delta = pct_delta(
    len(last_14),
    len(prev_14),
)


risk_delta = pct_delta(
    int(
        (
            last_14["risk"] == "high"
        ).sum()
    ),
    int(
        (
            prev_14["risk"] == "high"
        ).sum()
    ),
)


last_confidence = (
    last_14["confidence"].mean()
    if len(last_14)
    else 0
)

prev_confidence = (
    prev_14["confidence"].mean()
    if len(prev_14)
    else 0
)


conf_delta = pct_delta(
    last_confidence,
    prev_confidence,
)


# =========================================================
# KPI CARDS
# =========================================================

kpis = [

    (
        "Total scans",
        total_scans,
        delta_badge(scans_delta),
        "var(--accent)",
    ),

    (
        "High-risk alerts",
        high_risk_count,
        delta_badge(
            risk_delta,
            invert=True,
        ),
        "var(--alert)",
    ),

    (
        "Avg model score",
        f"{avg_confidence:.1f}%",
        delta_badge(conf_delta),
        "var(--gold)",
    ),

    (
        "Low-risk scans",
        low_risk_count,
        delta_badge(None),
        "var(--line-strong)",
    ),
]


k1, k2, k3, k4 = st.columns(4)


for col, (
    label,
    value,
    delta,
    stripe,
) in zip(
    [k1, k2, k3, k4],
    kpis,
):

    delta_css, delta_text = delta

    col.markdown(
        f'<div class="kpi-card" '
        f'style="--kpi-stripe:{stripe};">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="{delta_css}">'
        f'{delta_text}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


st.write("")


# =========================================================
# INSIGHT
# =========================================================

if high_risk_count > low_risk_count:

    insight = (
        f"{high_risk_count} of {total_scans} "
        "recorded scans were marked high-risk. "
        "Review flagged results with a healthcare professional."
    )

elif risk_delta is not None and risk_delta > 0:

    insight = (
        f"High-risk detections increased by "
        f"{risk_delta}% compared with the previous "
        "14-day period."
    )

else:

    insight = (
        f"{low_risk_count} of {total_scans} "
        f"recorded scans were low-risk."
    )


st.markdown(
    f'<div class="insight-card">'
    f'<div class="insight-title">Reading the trend</div>'
    f'<div class="insight-text">{insight}</div>'
    f'</div>',
    unsafe_allow_html=True,
)


# =========================================================
# CHARTS
# =========================================================

chart_col1, chart_col2 = st.columns(
    [2, 1]
)

PLOT_BG = "rgba(0,0,0,0)"
FONT_COLOR = "#202B26"
GRID_COLOR = "rgba(32,43,38,0.10)"


# ---------------------------------------------------------
# CONFIDENCE / SCORE TREND
# ---------------------------------------------------------

with chart_col1, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Model score trend'
        '</div>',
        unsafe_allow_html=True,
    )

    trend_df = (
        df.sort_values("date")
        .dropna(
            subset=["confidence"]
        )
    )

    fig = go.Figure()

    if not trend_df.empty:

        fig.add_trace(
            go.Scatter(
                x=trend_df["date"],
                y=trend_df["confidence"],
                mode="lines+markers",
                line=dict(
                    color="#2F6F5E",
                    width=2.5,
                    shape="spline",
                ),
                marker=dict(
                    size=7,
                    color="#2F6F5E",
                    line=dict(
                        width=1,
                        color="#FBFAF5",
                    ),
                ),
                fill="tozeroy",
                fillcolor=(
                    "rgba(47,111,94,0.10)"
                ),
                name="Score",
            )
        )

    fig.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        font=dict(
            color=FONT_COLOR,
            family="IBM Plex Sans",
        ),
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),
        xaxis=dict(
            showgrid=False,
            title=None,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            title="Model score %",
        ),
        height=300,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ---------------------------------------------------------
# RISK DISTRIBUTION
# ---------------------------------------------------------

with chart_col2, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Risk distribution'
        '</div>',
        unsafe_allow_html=True,
    )

    risk_counts = (
        df["risk"]
        .value_counts()
        .reindex(
            ["low", "high"]
        )
        .fillna(0)
    )

    fig2 = go.Figure(
        data=[
            go.Pie(
                labels=[
                    "Low risk",
                    "High risk",
                ],
                values=[
                    risk_counts.get(
                        "low",
                        0,
                    ),
                    risk_counts.get(
                        "high",
                        0,
                    ),
                ],
                hole=0.65,
                marker=dict(
                    colors=[
                        "#2F6F5E",
                        "#B5462F",
                    ],
                    line=dict(
                        color="#FBFAF5",
                        width=2,
                    ),
                ),
                textfont=dict(
                    color="#FBFAF5",
                    size=13,
                ),
            )
        ]
    )

    fig2.add_annotation(
        text=(
            f"{total_scans}"
            "<br>"
            "<span style='font-size:11px;'>"
            "scans"
            "</span>"
        ),
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(
            color="#202B26",
            size=18,
        ),
    )

    fig2.update_layout(
        paper_bgcolor=PLOT_BG,
        font=dict(
            color=FONT_COLOR,
            family="IBM Plex Sans",
        ),
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.1,
        ),
        height=300,
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
    )


# =========================================================
# DETECTION TYPE + WEEKLY VOLUME
# =========================================================

chart_col3, chart_col4 = st.columns(2)


# ---------------------------------------------------------
# DETECTION TYPE
# ---------------------------------------------------------

with chart_col3, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Scans by detection type'
        '</div>',
        unsafe_allow_html=True,
    )

    type_counts = (
        df["type"]
        .value_counts()
        .reset_index()
    )

    type_counts.columns = [
        "type",
        "count",
    ]

    fig3 = px.bar(
        type_counts,
        x="type",
        y="count",
        text="count",
        color="type",
        color_discrete_sequence=[
            "#2F6F5E",
            "#A6792E",
            "#8FA98F",
        ],
    )

    fig3.update_traces(
        textposition="outside",
        marker_line_width=0,
    )

    fig3.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        font=dict(
            color=FONT_COLOR,
            family="IBM Plex Sans",
        ),
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),
        xaxis=dict(
            showgrid=False,
            title=None,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            title="Scans",
        ),
        showlegend=False,
        height=280,
    )

    st.plotly_chart(
        fig3,
        use_container_width=True,
    )


# ---------------------------------------------------------
# WEEKLY VOLUME
# ---------------------------------------------------------

with chart_col4, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Weekly scan volume'
        '</div>',
        unsafe_allow_html=True,
    )

    weekly = (
        df.set_index("date")
        .resample("W")
        .size()
        .reset_index(
            name="scans"
        )
    )

    fig4 = px.area(
        weekly,
        x="date",
        y="scans",
    )

    fig4.update_traces(
        line_color="#2F6F5E",
        fillcolor="rgba(47,111,94,0.14)",
    )

    fig4.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        font=dict(
            color=FONT_COLOR,
            family="IBM Plex Sans",
        ),
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),
        xaxis=dict(
            showgrid=False,
            title=None,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            title="Scans",
        ),
        height=280,
    )

    st.plotly_chart(
        fig4,
        use_container_width=True,
    )


# =========================================================
# RECENT ACTIVITY + QUICK ACTIONS
# =========================================================

left, right = st.columns(
    [2, 1]
)


# ---------------------------------------------------------
# RECENT ACTIVITY
# ---------------------------------------------------------

with left, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Recent activity'
        '</div>',
        unsafe_allow_html=True,
    )

    recent = (
        df.sort_values(
            "date",
            ascending=False,
        )
        .head(5)
    )

    for _, row in recent.iterrows():

        risk = row["risk"]

        confidence = row["confidence"]

        if pd.isna(confidence):
            confidence_text = "Score unavailable"
        else:
            confidence_text = (
                f"{float(confidence):.1f}% score"
            )

        st.markdown(
            f'<div class="activity-row">'
            f'<div>'
            f'<strong>{row["type"]}</strong><br>'
            f'<span style="color:var(--ink-soft); '
            f'font-size:0.85rem;">'
            f'{row["date"].strftime("%b %d, %Y")}'
            f'</span>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'{risk_badge(risk)}<br>'
            f'<span style="color:var(--ink-soft); '
            f'font-size:0.85rem;'
            f'font-family:var(--font-mono);">'
            f'{confidence_text}'
            f'</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# QUICK ACTIONS
# ---------------------------------------------------------

with right, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Quick actions'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "New detection",
        use_container_width=True,
        type="secondary",
    ):
        st.switch_page(
            "pages/disease_detection.py"
        )

    if st.button(
        "View all reports",
        use_container_width=True,
        type="secondary",
    ):
        st.switch_page(
            "pages/reports.py"
        )

    if st.button(
        "Update profile",
        use_container_width=True,
        type="secondary",
    ):
        st.switch_page(
            "pages/profile.py"
        )


# =========================================================
# FOOTNOTE
# =========================================================

footnote(
    "Dashboard metrics reflect AI-assisted preliminary "
    "screenings, not confirmed medical diagnoses. "
    "Always consult a licensed healthcare professional."
)