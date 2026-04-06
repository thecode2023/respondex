"""
Respondex — Operational Incident & SLA Analytics Engine
Home / Landing Page
"""

import streamlit as st

st.set_page_config(
    page_title="Respondex",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark editorial aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Newsreader:wght@400;600;700&display=swap');

    .main-title {
        font-family: 'Newsreader', serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #FAFAFA;
        margin-bottom: 0;
        line-height: 1.1;
    }
    .subtitle {
        font-family: 'DM Mono', monospace;
        font-size: 1rem;
        color: #8B8D97;
        margin-top: 0.5rem;
        letter-spacing: 0.05em;
    }
    .metric-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        color: #8B8D97;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .section-header {
        font-family: 'Newsreader', serif;
        font-size: 1.5rem;
        color: #FAFAFA;
        border-bottom: 1px solid rgba(108, 99, 255, 0.3);
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .tech-tag {
        display: inline-block;
        background: rgba(108, 99, 255, 0.15);
        color: #6C63FF;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-family: 'DM Mono', monospace;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    div[data-testid="stMetric"] {
        background: #1A1D29;
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Hero
st.markdown('<p class="main-title">Respondex</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Operational Incident & SLA Analytics Engine — Boston 311</p>',
    unsafe_allow_html=True,
)

st.divider()

# What this is
st.markdown('<p class="section-header">What This Is</p>', unsafe_allow_html=True)
st.markdown("""
An end-to-end analytics platform that processes **Boston 311 service requests** to
surface SLA compliance patterns, incident trends, and neighborhood-level
operational performance. Built to mirror how enterprise operations teams monitor
service delivery against commitments.
""")

# How it works
st.markdown('<p class="section-header">How It Works</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**① Extract**")
    st.caption("Pull 2 years of 311 data from Boston Open Data (600K+ records)")
with col2:
    st.markdown("**② Transform**")
    st.caption("Clean, validate, and engineer features with Pandas — SLA flags, response times, category groupings")
with col3:
    st.markdown("**③ Model**")
    st.caption("Load into a star schema (fact + 4 dimensions) optimized for analytical queries")
with col4:
    st.markdown("**④ Visualize**")
    st.caption("Interactive Streamlit dashboard with Plotly charts, filterable by time, category, and neighborhood")

# Tech stack
st.markdown('<p class="section-header">Stack</p>', unsafe_allow_html=True)
tags = ["Python", "Pandas", "SQLite", "SQL", "Streamlit", "Plotly", "Star Schema"]
tag_html = " ".join(f'<span class="tech-tag">{t}</span>' for t in tags)
st.markdown(tag_html, unsafe_allow_html=True)

# Navigation hint
st.markdown("")
st.info("👈 Use the sidebar to explore the dashboard pages.", icon="📊")

# Footer
st.divider()
st.caption("Built by Yusuf Masood · [GitHub](https://github.com/thecode2023/respondex) · Data: [Analyze Boston](https://data.boston.gov/dataset/311-service-requests)")
