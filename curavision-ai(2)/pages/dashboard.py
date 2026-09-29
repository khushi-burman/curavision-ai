import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from textwrap import dedent

from theme import (
    inject_theme,
    top_nav,
    page_header,
    risk_badge,
    footnote,
    panel,
)

from supabase_client import supabase


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dashboard • CuraVision AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# AUTH CHECK
# ============================================================

if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")


# ============================================================
# DASHBOARD CSS
# ============================================================

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

.kpi-sub {
    color: var(--ink-faint);
    font-size: 0.8rem;
    margin-top: 5px;
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


# ============================================================
# THEME / NAVIGATION
# ============================================================

inject_theme(DASHBOARD_CSS)

top_nav()


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "Dashboard",
    "Your health-monitoring overview — scans, risk trends, and recent activity at a glance.",
    "chart",
)


# ============================================================
# GET CURRENT USER
# ============================================================

user_id = st.session_state.get("user_id")


if not user_id:

    try:

        session_response = supabase.auth.get_session()

        if (
            session_response
            and session_response.session
            and session_response.session.user
        ):

            user_id = str(
                session_response.session.user.id
            )

            st.session_state.user_id = user_id

    except Exception as exc:

        st.error(
            f"Could not retrieve your Supabase session: {exc}"
        )


if not user_id:

    st.error(
        "No logged-in user was found. Please log in again."
    )

    if st.button("Go to Login"):

        st.switch_page("pages/login.py")

    st.stop()


# ============================================================
# LOAD DATA FROM SUPABASE
# ============================================================

@st.cache_data(ttl=10)
def get_dashboard_scans(current_user_id):

    response = (
        supabase
        .table("health_scans")
        .select("*")
        .eq("user_id", current_user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


try:

    records = get_dashboard_scans(user_id)

except Exception as exc:

    st.error(
        f"Could not load dashboard data from Supabase: {exc}"
    )

    st.stop()


# ============================================================
# EMPTY STATE
# ============================================================

if not records:

    with panel():

        st.info(
            "You don't have any health scans yet."
        )

        st.markdown(
            """
            Run a skin-lesion assessment or chronic-risk
            screening to populate your dashboard.
            """
        )

        if st.button(
            "Start New Detection",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/disease_detection.py"
            )

    st.stop()


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(records)


# ============================================================
# ENSURE COLUMNS EXIST
# ============================================================

expected_columns = [
    "id",
    "user_id",
    "scan_date",
    "created_at",
    "detection_type",
    "predicted_class",
    "model_confidence",
    "risk_level",
    "risk_score",
    "prediction",
]

for column in expected_columns:

    if column not in df.columns:

        df[column] = None


# ============================================================
# DATE PROCESSING
# ============================================================

df["date"] = pd.to_datetime(
    df["created_at"],
    errors="coerce",
)

df["scan_date_parsed"] = pd.to_datetime(
    df["scan_date"],
    errors="coerce",
)

df["date"] = df["date"].fillna(
    df["scan_date_parsed"]
)

df = df.dropna(
    subset=["date"]
)

df = df.sort_values(
    "date",
    ascending=False,
)


# ============================================================
# DETECTION TYPE LABELS
# ============================================================

df["display_type"] = df[
    "detection_type"
].map(
    {
        "skin": "Skin Assessment",
        "chronic_risk": "Chronic-Risk Assessment",
    }
).fillna(
    df["detection_type"].astype(str)
)


# ============================================================
# NUMERIC VALUES
# ============================================================

df["model_confidence_num"] = pd.to_numeric(
    df["model_confidence"],
    errors="coerce",
)

df["risk_score_num"] = pd.to_numeric(
    df["risk_score"],
    errors="coerce",
)


# ============================================================
# COUNTS
# ============================================================

total_scans = len(df)

skin_scans = int(
    (
        df["detection_type"]
        == "skin"
    ).sum()
)

chronic_scans = int(
    (
        df["detection_type"]
        == "chronic_risk"
    ).sum()
)


# ============================================================
# HIGH-RISK COUNT
# ============================================================

high_risk_mask = (
    (df["detection_type"] == "chronic_risk")
    &
    (
        df["risk_level"]
        .fillna("")
        .astype(str)
        .str.lower()
        == "high"
    )
)

high_risk_count = int(
    high_risk_mask.sum()
)


# ============================================================
# LOW-RISK COUNT
# ============================================================

low_risk_mask = (
    (df["detection_type"] == "chronic_risk")
    &
    (
        df["risk_level"]
        .fillna("")
        .astype(str)
        .str.lower()
        == "low"
    )
)

low_risk_count = int(
    low_risk_mask.sum()
)


# ============================================================
# AVERAGE SKIN CONFIDENCE
# ============================================================

skin_confidence = df.loc[
    df["detection_type"] == "skin",
    "model_confidence_num",
].dropna()


if len(skin_confidence):

    avg_confidence = float(
        skin_confidence.mean()
    )

    if avg_confidence <= 1:

        avg_confidence *= 100

else:

    avg_confidence = None


if avg_confidence is not None:

    confidence_display = (
        f"{avg_confidence:.1f}%"
    )

else:

    confidence_display = "N/A"


# ============================================================
# AVERAGE CHRONIC RISK
# ============================================================

chronic_scores = df.loc[
    df["detection_type"] == "chronic_risk",
    "risk_score_num",
].dropna()


if len(chronic_scores):

    avg_risk_score = float(
        chronic_scores.mean()
    )

    if avg_risk_score <= 1:

        avg_risk_score *= 100

else:

    avg_risk_score = None


# ============================================================
# KPI CARDS
# ============================================================

kpis = [

    (
        "Total scans",
        total_scans,
        "All saved assessments",
        "var(--accent)",
    ),

    (
        "High-risk alerts",
        high_risk_count,
        "Chronic-risk assessments",
        "var(--alert)",
    ),

    (
        "Skin assessments",
        skin_scans,
        "Image-based screenings",
        "var(--gold)",
    ),

    (
        "Avg skin confidence",
        confidence_display,
        "Vision model confidence",
        "var(--line-strong)",
    ),
]


k1, k2, k3, k4 = st.columns(4)


for col, (
    label,
    value,
    subtitle,
    stripe,
) in zip(
    [k1, k2, k3, k4],
    kpis,
):

    html = dedent(
        f"""
        <div class="kpi-card" style="--kpi-stripe:{stripe};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """
    ).strip()

    col.html(html)


st.write("")


# ============================================================
# DASHBOARD INSIGHT
# ============================================================

if high_risk_count > 0:

    plural = (
        "s"
        if high_risk_count != 1
        else ""
    )

    insight = (
        f"You have {high_risk_count} high-risk "
        f"chronic-risk assessment{plural}. "
        "Review the corresponding report for "
        "the recorded findings and recommended actions."
    )

elif total_scans == 1:

    insight = (
        "This is your first saved assessment. "
        "Future scans will appear here so you can "
        "review your history over time."
    )

else:

    skin_plural = (
        "s"
        if skin_scans != 1
        else ""
    )

    chronic_plural = (
        "s"
        if chronic_scans != 1
        else ""
    )

    insight = (
        f"You currently have {total_scans} saved assessments. "
        f"This includes {skin_scans} skin assessment{skin_plural} "
        f"and {chronic_scans} chronic-risk assessment{chronic_plural}."
    )


insight_html = dedent(
    f"""
    <div class="insight-card">
        <div class="insight-title">
            Dashboard summary
        </div>

        <div class="insight-text">
            {insight}
        </div>
    </div>
    """
).strip()


st.html(insight_html)


# ============================================================
# CHART COLORS
# ============================================================

PLOT_BG = "rgba(0,0,0,0)"
FONT_COLOR = "#202B26"
GRID_COLOR = "rgba(32,43,38,0.10)"


# ============================================================
# CHART ROW 1
# ============================================================

chart_col1, chart_col2 = st.columns(
    [2, 1]
)


# ============================================================
# CHRONIC RISK TREND
# ============================================================

with chart_col1, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Chronic-risk trend'
        '</div>',
        unsafe_allow_html=True,
    )


    chronic_df = df[
        df["detection_type"]
        == "chronic_risk"
    ].copy()


    chronic_df = chronic_df.dropna(
        subset=["risk_score_num"]
    )


    if len(chronic_df):

        chronic_df = chronic_df.sort_values(
            "date"
        )

        chronic_df[
            "risk_percentage"
        ] = chronic_df[
            "risk_score_num"
        ]

        mask = (
            chronic_df[
                "risk_percentage"
            ]
            <= 1
        )

        chronic_df.loc[
            mask,
            "risk_percentage",
        ] = (
            chronic_df.loc[
                mask,
                "risk_percentage",
            ]
            * 100
        )


        fig = go.Figure()


        fig.add_trace(
            go.Scatter(
                x=chronic_df["date"],
                y=chronic_df[
                    "risk_percentage"
                ],
                mode="lines+markers",
                line=dict(
                    color="#B5462F",
                    width=2.5,
                    shape="spline",
                ),
                marker=dict(
                    size=8,
                    color="#B5462F",
                ),
                name="Risk score",
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
                title="Risk score %",
                rangemode="tozero",
            ),
            height=300,
        )


        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No chronic-risk scores available yet."
        )


# ============================================================
# RISK DISTRIBUTION
# ============================================================

with chart_col2, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Risk distribution'
        '</div>',
        unsafe_allow_html=True,
    )


    chronic_risk_df = df[
        df["detection_type"]
        == "chronic_risk"
    ].copy()


    risk_counts = (
        chronic_risk_df[
            "risk_level"
        ]
        .fillna("unknown")
        .astype(str)
        .str.lower()
        .value_counts()
    )


    low_count = int(
        risk_counts.get(
            "low",
            0,
        )
    )

    medium_count = int(
        risk_counts.get(
            "medium",
            0,
        )
    )

    high_count = int(
        risk_counts.get(
            "high",
            0,
        )
    )

    unknown_count = int(
        risk_counts.get(
            "unknown",
            0,
        )
    )


    labels = []
    values = []


    if low_count:

        labels.append("Low risk")
        values.append(low_count)


    if medium_count:

        labels.append("Medium risk")
        values.append(medium_count)


    if high_count:

        labels.append("High risk")
        values.append(high_count)


    if unknown_count:

        labels.append("Unknown")
        values.append(unknown_count)


    if values:

        fig2 = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.65,
                    textinfo="label+percent",
                    marker=dict(
                        line=dict(
                            color="#FBFAF5",
                            width=2,
                        )
                    ),
                )
            ]
        )


        fig2.add_annotation(
            text=(
                f"{chronic_scans}"
                "<br>"
                "<span style='font-size:11px;'>"
                "chronic scans"
                "</span>"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                color=FONT_COLOR,
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
            height=300,
            showlegend=True,
        )


        st.plotly_chart(
            fig2,
            use_container_width=True,
        )

    else:

        st.info(
            "No chronic-risk assessments available yet."
        )


# ============================================================
# CHART ROW 2
# ============================================================

chart_col3, chart_col4 = st.columns(2)


# ============================================================
# DETECTION TYPE BREAKDOWN
# ============================================================

with chart_col3, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Scans by detection type'
        '</div>',
        unsafe_allow_html=True,
    )


    type_counts = (
        df["display_type"]
        .value_counts()
        .reset_index()
    )


    type_counts.columns = [
        "type",
        "count",
    ]


    if len(type_counts):

        fig3 = px.bar(
            type_counts,
            x="type",
            y="count",
            text="count",
        )


        fig3.update_traces(
            textposition="outside",
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

    else:

        st.info(
            "No detection data available."
        )


# ============================================================
# SKIN CONFIDENCE TREND
# ============================================================

with chart_col4, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Skin-model confidence'
        '</div>',
        unsafe_allow_html=True,
    )


    skin_df = df[
        df["detection_type"]
        == "skin"
    ].copy()


    skin_df = skin_df.dropna(
        subset=[
            "model_confidence_num"
        ]
    )


    if len(skin_df):

        skin_df = skin_df.sort_values(
            "date"
        )


        skin_df[
            "confidence_percentage"
        ] = skin_df[
            "model_confidence_num"
        ]


        mask = (
            skin_df[
                "confidence_percentage"
            ]
            <= 1
        )


        skin_df.loc[
            mask,
            "confidence_percentage",
        ] = (
            skin_df.loc[
                mask,
                "confidence_percentage",
            ]
            * 100
        )


        fig4 = go.Figure()


        fig4.add_trace(
            go.Scatter(
                x=skin_df["date"],
                y=skin_df[
                    "confidence_percentage"
                ],
                mode="lines+markers",
                line=dict(
                    color="#2F6F5E",
                    width=2.5,
                    shape="spline",
                ),
                marker=dict(
                    size=7,
                    color="#2F6F5E",
                ),
                name="Confidence",
            )
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
                title="Confidence %",
                range=[0, 100],
            ),
            height=280,
        )


        st.plotly_chart(
            fig4,
            use_container_width=True,
        )

    else:

        st.info(
            "No skin-model confidence data available yet."
        )


# ============================================================
# RECENT ACTIVITY + QUICK ACTIONS
# ============================================================

left, right = st.columns(
    [2, 1]
)


# ============================================================
# RECENT ACTIVITY
# ============================================================

with left, panel():

    st.markdown(
        '<div class="cv-section-heading">'
        'Recent activity'
        '</div>',
        unsafe_allow_html=True,
    )


    recent = df.head(5)


    for _, row in recent.iterrows():

        detection_type = row[
            "detection_type"
        ]

        display_type = row[
            "display_type"
        ]

        row_date = row[
            "date"
        ]


        if pd.notna(row_date):

            formatted_date = (
                row_date.strftime(
                    "%b %d, %Y • %I:%M %p"
                )
            )

        else:

            formatted_date = (
                "Unknown date"
            )


        # ====================================================
        # CHRONIC RISK ACTIVITY
        # ====================================================

        if detection_type == "chronic_risk":

            risk = (
                str(
                    row.get(
                        "risk_level",
                        "unknown",
                    )
                )
                .lower()
            )


            score = row.get(
                "risk_score_num"
            )


            if pd.notna(score):

                if score <= 1:

                    score *= 100

                secondary = (
                    f"{score:.2f}% risk score"
                )

            else:

                secondary = (
                    "Risk score unavailable"
                )


            badge = risk_badge(
                risk
            )


        # ====================================================
        # SKIN ACTIVITY
        # ====================================================

        elif detection_type == "skin":

            confidence = row.get(
                "model_confidence_num"
            )


            if pd.notna(confidence):

                if confidence <= 1:

                    confidence *= 100

                secondary = (
                    f"{confidence:.2f}% confidence"
                )

            else:

                secondary = (
                    "Confidence unavailable"
                )


            badge = (
                '<span style="'
                'display:inline-block;'
                'padding:4px 9px;'
                'border:1px solid var(--line-strong);'
                'border-radius:12px;'
                'font-size:0.75rem;'
                '">'
                'Skin'
                '</span>'
            )


        # ====================================================
        # UNKNOWN TYPE
        # ====================================================

        else:

            secondary = ""

            badge = ""


        activity_html = dedent(
            f"""
            <div class="activity-row">

                <div>
                    <strong>{display_type}</strong>

                    <br>

                    <span style="
                        color:var(--ink-soft);
                        font-size:0.85rem;
                    ">
                        {formatted_date}
                    </span>
                </div>

                <div style="text-align:right;">

                    {badge}

                    <br>

                    <span style="
                        color:var(--ink-soft);
                        font-size:0.85rem;
                        font-family:var(--font-mono);
                    ">
                        {secondary}
                    </span>

                </div>

            </div>
            """
        ).strip()


        st.html(activity_html)


# ============================================================
# QUICK ACTIONS
# ============================================================

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


    if st.button(
        "🔄 Refresh dashboard",
        use_container_width=True,
        type="secondary",
    ):

        get_dashboard_scans.clear()

        st.rerun()


# ============================================================
# FOOTNOTE
# ============================================================

footnote(
    "Dashboard metrics reflect AI-assisted preliminary screenings, "
    "not confirmed medical diagnoses. Always consult a licensed "
    "healthcare professional."
)