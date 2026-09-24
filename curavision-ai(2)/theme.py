"""
CuraVision AI — shared visual language.

One place for the palette, type scale, and the bits of chrome (nav bar,
page header, badges, icons) that every page reuses. Keeps every screen
consistent and means a palette or copy tweak happens in one file instead
of seven.
"""

import textwrap
from contextlib import contextmanager
import itertools
import streamlit as st

# ---------------------------------------------------------------- tokens --

FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=IBM+Plex+Serif:wght@500;600;700&"
    "family=IBM+Plex+Sans:wght@400;500;600;700&"
    "family=IBM+Plex+Mono:wght@400;500;600&"
    "display=swap"
)

# Warm, paper-and-ink clinical chart — not the dark blue/violet glass look.
TOKENS = """
:root {
    --bg: #E7EAE1;
    --surface: #FBFAF5;
    --surface-sunken: #EFF1E8;
    --ink: #202B26;
    --ink-soft: #57635C;
    --ink-faint: #8B9389;
    --line: #D6D9CA;
    --line-strong: #B9BFAE;

    --accent: #2F6F5E;
    --accent-dark: #1F4E42;
    --accent-soft: #E1EBE4;

    --alert: #B5462F;
    --alert-soft: #F5E3DC;

    --gold: #A6792E;
    --gold-soft: #F2E8D6;

    --radius-sm: 4px;
    --radius-md: 6px;

    --font-serif: 'IBM Plex Serif', Georgia, serif;
    --font-sans: 'IBM Plex Sans', -apple-system, sans-serif;
    --font-mono: 'IBM Plex Mono', 'SF Mono', monospace;
}
"""

BASE_CSS = """
#MainMenu, header, footer { visibility: hidden; }
[data-testid="stSidebarCollapse"] { display: none; }
[data-testid="stSidebarNav"] { display: none; }

html, body, [class*="css"] { font-family: var(--font-sans); }

.stApp {
    background:
        repeating-linear-gradient(
            0deg, rgba(32,43,38,0.035) 0px, rgba(32,43,38,0.035) 1px,
            transparent 1px, transparent 28px
        ),
        var(--bg);
}

[data-testid="stMainBlockContainer"] {
    max-width: 1180px;
    padding-top: 1.6rem;
}

h1, h2, h3 { font-family: var(--font-serif); color: var(--ink); }

p, span, label, div { color: var(--ink); }

::selection { background: var(--accent-soft); color: var(--accent-dark); }

/* ---------- top nav ---------- */

.cv-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 14px;
    margin-bottom: 22px;
    border-bottom: 1px solid var(--line-strong);
}

.cv-brand {
    display: flex;
    align-items: center;
    gap: 9px;
    font-family: var(--font-serif);
    font-weight: 600;
    font-size: 1.2rem;
    color: var(--ink);
    letter-spacing: 0.01em;
}

.cv-brand svg { flex-shrink: 0; }

.cv-navlinks { display: flex; gap: 2px; }

/* Streamlit page_link + button chrome inside the top nav specifically,
   restyled to look like plain text tabs with an underline rather than
   pill buttons. Scoped to the nav container so it doesn't leak onto
   ordinary buttons that happen to sit inside st.columns elsewhere. */
div.st-key-cv_top_nav [data-testid="stPageLink"] a,
div.st-key-cv_top_nav .stButton > button {
    font-family: var(--font-sans) !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    color: var(--ink-soft) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    padding: 6px 10px !important;
    box-shadow: none !important;
    transition: color 0.12s ease, border-color 0.12s ease;
}
div.st-key-cv_top_nav [data-testid="stPageLink"] a:hover,
div.st-key-cv_top_nav .stButton > button:hover {
    color: var(--accent-dark) !important;
    border-bottom-color: var(--accent) !important;
    transform: none !important;
}
div.st-key-cv_top_nav [data-testid="stPageLink"] a p { font-size: 0.86rem !important; }
/* Highlight the current page's nav link (Streamlit marks it aria-current) */
div.st-key-cv_top_nav [data-testid="stPageLink"] a[aria-current="page"] {
    color: var(--ink) !important;
    border-bottom-color: var(--accent) !important;
    font-weight: 600 !important;
}

/* ---------- page header ---------- */

.cv-page-title {
    font-family: var(--font-serif);
    font-size: 1.9rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.cv-page-subtitle {
    color: var(--ink-soft);
    font-size: 0.94rem;
    margin-bottom: 22px;
    max-width: 640px;
    line-height: 1.5;
}

/* ---------- panels (the card replacement) ----------
   Applied via the panel() context manager in this module, which wraps
   content in a real st.container so it's actually nested in the DOM —
   plain st.markdown('<div>')...st.markdown('</div>') calls do NOT nest
   across separate Streamlit elements, they just render as two stray,
   unconnected tags. Matched by a substring on the container's
   st-key-* class since each panel gets a unique key. */
div[class*="st-key-cvpanel_"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius-md);
    padding: 20px 24px 4px 24px;
    margin-bottom: 18px;
}
div[class*="st-key-cvpanel_alert_"] { border-left-color: var(--alert); }
div[class*="st-key-cvpanel_gold_"] { border-left-color: var(--gold); }
div[class*="st-key-cvpanel_flat_"] { border-left-color: var(--line-strong); }

.cv-section-heading {
    font-family: var(--font-serif);
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 12px;
}

/* ---------- badges ---------- */

.cv-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: var(--font-mono);
    font-size: 0.76rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 3px;
    letter-spacing: 0.01em;
}
.cv-badge-alert { background: var(--alert-soft); color: var(--alert); border: 1px solid rgba(181,70,47,0.3); }
.cv-badge-good  { background: var(--accent-soft); color: var(--accent-dark); border: 1px solid rgba(47,111,94,0.28); }
.cv-badge-gold  { background: var(--gold-soft); color: var(--gold); border: 1px solid rgba(166,121,46,0.3); }
.cv-badge-flat  { background: var(--surface-sunken); color: var(--ink-soft); border: 1px solid var(--line-strong); }

.cv-mono { font-family: var(--font-mono); }

/* ---------- buttons & inputs ---------- */

.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: var(--surface) !important;
    border: 1px solid var(--accent-dark) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
    box-shadow: none !important;
    transition: background 0.12s ease;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-dark) !important;
    transform: none !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--ink) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent-dark) !important;
    transform: none !important;
}

/* st.form_submit_button renders under a different testid than st.button,
   so it needs its own rule to pick up the same primary/secondary look. */
div[data-testid="stFormSubmitButton"] > button {
    background: var(--accent) !important;
    color: var(--surface) !important;
    border: 1px solid var(--accent-dark) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background: var(--accent-dark) !important;
    transform: none !important;
}

/* Default progress bar is Streamlit red; recolor to the accent teal. */
div[data-testid="stProgress"] > div > div > div {
    background-color: var(--accent) !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-sans) !important;
}

div[data-testid="stFileUploader"] {
    background: var(--surface-sunken);
    border: 1px dashed var(--line-strong);
    border-radius: var(--radius-md);
    padding: 10px;
}

div[data-testid="stDownloadButton"] > button {
    background: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent-dark) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    box-shadow: none !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line-strong); }
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 0;
    padding: 8px 4px;
    margin-right: 22px;
    color: var(--ink-soft);
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: transparent;
    color: var(--ink);
    border-bottom: 2px solid var(--accent);
}
/* The active-tab indicator bar renders as this element in current
   Streamlit versions (not the older [data-baseweb] tab markup). */
.react-aria-SelectionIndicator { background-color: var(--accent) !important; }
[data-testid="stTab"] { color: var(--ink-soft); }
[data-testid="stTab"][aria-selected="true"] { color: var(--ink) !important; font-weight: 600; }

[data-testid="stMetricValue"] { font-family: var(--font-mono); color: var(--ink); }
[data-testid="stMetricLabel"] { color: var(--ink-soft); }

hr, [data-testid="stDivider"] { border-color: var(--line) !important; }

/* ---------- footer note ---------- */

.cv-footnote {
    text-align: left;
    color: var(--ink-faint);
    font-size: 0.8rem;
    padding: 18px 0 6px 0;
    margin-top: 10px;
    border-top: 1px solid var(--line);
}
"""


def inject_theme(extra_css: str = ""):
    # Every line here must start in column 0 — Streamlit's markdown parser
    # treats 4+ leading spaces as a fenced code block, which would print
    # the CSS as visible text instead of applying it. The font is loaded
    # via @import *inside* the <style> tag rather than a separate <link>
    # line — a standalone <link> before <style> throws off the parser's
    # HTML-block detection and the whole stylesheet renders as plain text.
    block = "\n".join([
        "<style>",
        f'@import url("{FONT_IMPORT}");',
        textwrap.dedent(TOKENS),
        textwrap.dedent(BASE_CSS),
        textwrap.dedent(extra_css),
        "</style>",
    ])
    st.markdown(block, unsafe_allow_html=True)


# --------------------------------------------------------------- icons ---
# Small line-icon set (20x20, stroke=currentColor) standing in for emoji.

def _icon(paths: str, extra: str = "") -> str:
    return (
        f'<svg width="17" height="17" viewBox="0 0 20 20" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" style="{extra}">'
        f'<g stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</g></svg>'
    )


ICONS = {
    "pulse": _icon(
        '<path d="M1.5 10.5h4l2-6 3.5 12 2.5-9 1.5 3h4"/>'
    ),
    "home": _icon(
        '<path d="M3 9.5 10 3.5l7 6"/><path d="M4.5 8.5V16h11V8.5"/><path d="M8 16v-4.5h4V16"/>'
    ),
    "chat": _icon(
        '<path d="M3 4.5h14v9H8.5L5 16.5V13.5H3z"/><path d="M6.5 8h7"/><path d="M6.5 10.5h4.5"/>'
    ),
    "scan": _icon(
        '<path d="M4 4h-1.5V7"/><path d="M16 4h1.5V7"/><path d="M4 16H2.5V13"/><path d="M16 16h1.5V13"/>'
        '<circle cx="10" cy="10" r="3.2"/>'
    ),
    "file": _icon(
        '<path d="M6 2.5h6l3 3V17.5H6z"/><path d="M12 2.5V5.5h3"/><path d="M8 10h4"/><path d="M8 12.7h4"/>'
    ),
    "chart": _icon(
        '<path d="M3.5 16.5v-11"/><path d="M3.5 16.5h13"/><path d="M6.5 14V9.5"/>'
        '<path d="M10 14V6.5"/><path d="M13.5 14v-5"/>'
    ),
    "user": _icon(
        '<circle cx="10" cy="6.8" r="3.1"/><path d="M4 17c0-3.3 2.7-5.3 6-5.3s6 2 6 5.3"/>'
    ),
    "logout": _icon(
        '<path d="M8 3.5H4.5v13H8"/><path d="M9 10h7.5"/><path d="M13.5 6.8 16.5 10l-3 3.2"/>'
    ),
    "alert": _icon(
        '<path d="M10 3 2.5 16.5h15z"/><path d="M10 8.3v3.6"/><circle cx="10" cy="14" r="0.15" fill="currentColor"/>'
    ),
    "check": _icon(
        '<circle cx="10" cy="10" r="7.2"/><path d="M6.8 10.2l2.1 2.1 4.3-4.6"/>'
    ),
    "upload": _icon(
        '<path d="M10 3v9"/><path d="M6.3 6.7 10 3l3.7 3.7"/><path d="M3.5 14v2.5h13V14"/>'
    ),
    "id": _icon(
        '<path d="M2.5 5h15v10h-15z"/><circle cx="7" cy="10" r="1.7"/>'
        '<path d="M11.5 8.3h4"/><path d="M11.5 11.7h4"/>'
    ),
}


def icon(name: str, extra: str = "") -> str:
    svg = ICONS.get(name, "")
    if extra:
        svg = svg.replace('style=""', f'style="{extra}"')
    return svg


# ------------------------------------------------------------ nav / hdr --

NAV_ITEMS = [
    ("Overview", "pages/home.py", "home"),
    ("Assistant", "pages/assistant.py", "chat"),
    ("Detection", "pages/disease_detection.py", "scan"),
    ("Reports", "pages/reports.py", "file"),
    ("Dashboard", "pages/dashboard.py", "chart"),
    ("Profile", "pages/profile.py", "user"),
]


_panel_counter = itertools.count()


@contextmanager
def panel(variant: str = ""):
    """A hairline-bordered chart panel that actually contains its content.

    Use as: `with panel(): st.write(...)`. variant is one of
    "", "alert", "gold", "flat" and controls the left accent stripe.
    """
    key = f"cvpanel_{variant or 'default'}_{next(_panel_counter)}"
    with st.container(key=key):
        yield


def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.switch_page("pages/login.py")


def top_nav():
    """Brand mark + section links + logout, styled as plain underlined tabs."""
    with st.container(key="cv_top_nav"):
        left, right = st.columns([1.3, 3.2])
        with left:
            st.markdown(
                f'<div class="cv-brand">{icon("pulse")} CuraVision</div>',
                unsafe_allow_html=True,
            )
        with right:
            cols = st.columns(len(NAV_ITEMS) + 1)
            for col, (label, target, _) in zip(cols, NAV_ITEMS):
                with col:
                    st.page_link(target, label=label)
            with cols[-1]:
                if st.button("Log out", key="cv_logout_btn"):
                    logout()
    st.markdown('<div style="margin-top:-14px;border-bottom:1px solid var(--line-strong);margin-bottom:22px;"></div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str, icon_key: str | None = None):
    icon_html = icon(icon_key) if icon_key else ""
    st.markdown(f'<div class="cv-page-title">{icon_html} {title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cv-page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def risk_badge(risk: str, text: str | None = None) -> str:
    label = text if text else risk.upper()
    key = (risk or "").lower()
    cls = "cv-badge-alert" if key == "high" else "cv-badge-good" if key == "low" else "cv-badge-flat"
    ic = icon("alert") if key == "high" else icon("check") if key == "low" else ""
    return f'<span class="cv-badge {cls}">{ic}{label}</span>'


def footnote(text: str):
    st.markdown(f'<div class="cv-footnote">{text}</div>', unsafe_allow_html=True)
