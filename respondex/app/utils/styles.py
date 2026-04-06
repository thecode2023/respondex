"""Shared CSS styles for consistent dashboard design across all pages."""

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
        font-size: 2.2rem !important;
        color: #F1F5F9 !important;
    }
    h2, h3, [data-testid="stSubheader"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: #E2E8F0 !important;
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
        padding: 1.3rem 1.5rem !important;
    }
    div[data-testid="stMetric"] label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.65rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.14em !important;
        color: #64748B !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em !important;
    }

    /* ========== DIVIDERS ========== */
    hr {
        border-color: rgba(255,255,255,0.04) !important;
        margin: 2.5rem 0 !important;
    }

    /* ========== TAKEAWAY BOXES ========== */
    .takeaway-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(99, 102, 241, 0.03) 100%);
        border-left: 3px solid #3B82F6;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 0 12px 12px 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        line-height: 1.7;
        color: #94A3B8;
    }
    .takeaway-box strong {
        color: #E2E8F0;
        font-weight: 600;
    }

    /* ========== SIDEBAR LABELS ========== */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: #64748B !important;
    }

    /* ========== SPACING ========== */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
</style>
"""


def inject_dashboard_css():
    """Call this at the top of every dashboard page."""
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
