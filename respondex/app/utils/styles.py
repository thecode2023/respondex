"""Shared CSS styles v3 — proper spacing, section labels, KPI differentiation."""

import streamlit as st

DASHBOARD_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ========== BASE ========== */
    .stApp {
        background: #080E1A !important;
    }
    section[data-testid="stSidebar"] {
        background: #0A1122 !important;
        border-right: 1px solid rgba(255,255,255,0.04) !important;
    }

    /* ========== TYPOGRAPHY ========== */
    h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        font-size: 2.4rem !important;
        color: #F1F5F9 !important;
        margin-bottom: 0 !important;
    }
    h2, h3, [data-testid="stSubheader"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: #E2E8F0 !important;
        margin-top: 0.5rem !important;
    }
    p, li, span, div {
        font-family: 'Inter', sans-serif;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: #475569 !important;
    }

    /* ========== KPI CARDS ========== */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #0F1829 0%, #131F36 100%) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 14px !important;
        padding: 1.4rem 1.6rem !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(59,130,246,0.15) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stMetric"] label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.62rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        color: #64748B !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
    }

    /* ========== PRIMARY KPI (first column) ========== */
    div[data-testid="stHorizontalBlock"] > div:first-child div[data-testid="stMetric"] {
        border-left: 3px solid #3B82F6 !important;
        background: linear-gradient(135deg, #0F1829 0%, #111D38 100%) !important;
    }

    /* ========== DIVIDERS ========== */
    hr {
        border-color: rgba(255,255,255,0.04) !important;
        margin: 3rem 0 !important;
    }

    /* ========== SECTION LABELS ========== */
    .section-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #3B82F6;
        margin-bottom: 0.6rem;
        display: block;
    }

    /* ========== TAKEAWAY BOXES ========== */
    .takeaway-box {
        background: linear-gradient(135deg, rgba(59,130,246,0.04) 0%, rgba(99,102,241,0.02) 100%);
        border-left: 3px solid #3B82F6;
        padding: 1.1rem 1.4rem;
        margin: 1rem 0;
        border-radius: 0 12px 12px 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        line-height: 1.75;
        color: #94A3B8;
    }
    .takeaway-box strong {
        color: #E2E8F0;
        font-weight: 600;
    }

    /* ========== CHART CONTAINERS ========== */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
        background: rgba(15,24,41,0.5);
        padding: 0.5rem;
        border: 1px solid rgba(255,255,255,0.03);
    }

    /* ========== DATAFRAMES ========== */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: #64748B !important;
    }

    /* ========== EXPANDERS ========== */
    details {
        border: 1px solid rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        background: #0C1322 !important;
    }
    details summary {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
    }

    /* ========== BUTTONS ========== */
    .stButton > button[kind="primary"] {
        background: #3B82F6 !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2563EB !important;
    }

    /* ========== SPACING ========== */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1100px !important;
    }

    /* ========== CHART SECTION WRAPPER ========== */
    .chart-section {
        margin-top: 2.5rem;
        margin-bottom: 1rem;
    }
</style>
"""


def inject_dashboard_css():
    """Call at the top of every dashboard page."""
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


def section_label(text: str):
    """Render a styled section label like 'KEY METRICS' or 'TRENDS'."""
    st.markdown(f'<span class="section-tag">{text}</span>', unsafe_allow_html=True)
