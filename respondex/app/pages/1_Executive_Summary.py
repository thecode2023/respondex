"""
Page 1: Executive Summary
KPI cards + high-level trend charts.
"""

import streamlit as st
import pandas as pd
from utils.db import get_kpi_summary, get_monthly_trends, get_daily_trends
from utils.charts import line_chart, bar_chart, COLORS

st.set_page_config(page_title="Executive Summary | Respondex", layout="wide", page_icon="📊")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Newsreader:wght@400;600;700&display=swap');
    div[data-testid="stMetric"] {
        background: #1A1D29;
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
    }
    div[data-testid="stMetric"] label {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .takeaway-box {
        background: rgba(108, 99, 255, 0.08);
        border-left: 3px solid #6C63FF;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Executive Summary")
st.caption("High-level operational performance across all Boston 311 service requests")

# --- KPI Cards ---
try:
    kpis = get_kpi_summary()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Incidents", f"{kpis['total_incidents']:,}")
    k2.metric("SLA Compliance", f"{kpis['sla_compliance_pct']}%")
    k3.metric("Avg Resolution", f"{kpis['avg_resolution_hours']:.0f} hrs")
    k4.metric("Closure Rate", f"{kpis['closure_rate_pct']}%")
except Exception as e:
    st.error(f"Could not load KPIs: {e}")
    st.info("Make sure you've run the ETL pipeline first (`python run_etl.py`).")
    st.stop()

st.divider()

# --- Monthly Trends ---
monthly = get_monthly_trends()

if not monthly.empty:
    monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)

    col_left, col_right = st.columns(2)

    with col_left:
        fig = line_chart(
            monthly, x="period", y="total_incidents",
            title="Monthly Incident Volume",
            labels={"period": "Month", "total_incidents": "Incidents"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        fig = line_chart(
            monthly, x="period", y="sla_pct",
            title="Monthly SLA Compliance %",
            labels={"period": "Month", "sla_pct": "SLA %"},
        )
        fig.add_hline(y=90, line_dash="dash", line_color=COLORS["accent"],
                       annotation_text="90% target", annotation_position="top left")
        st.plotly_chart(fig, use_container_width=True)

    # Resolution time trend
    if "avg_resolution_hours" in monthly.columns:
        fig = bar_chart(
            monthly, x="period", y="avg_resolution_hours",
            title="Avg Resolution Time by Month (hours)",
            labels={"period": "Month", "avg_resolution_hours": "Hours"},
        )
        st.plotly_chart(fig, use_container_width=True)

# --- Daily volume (sparkline-style) ---
daily = get_daily_trends()

if not daily.empty:
    daily["full_date"] = pd.to_datetime(daily["full_date"])
    # Rolling 7-day average
    daily = daily.sort_values("full_date")
    daily["rolling_7d"] = daily["total_incidents"].rolling(7, min_periods=1).mean()

    fig = line_chart(
        daily, x="full_date", y="rolling_7d",
        title="Daily Incident Volume (7-day rolling avg)",
        labels={"full_date": "Date", "rolling_7d": "Incidents (7d avg)"},
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Key Takeaways ---
st.divider()
st.subheader("Key Takeaways")

sla_val = kpis["sla_compliance_pct"]
res_val = kpis["avg_resolution_hours"]
total_val = kpis["total_incidents"]

sla_assessment = "well below" if sla_val < 80 else "below" if sla_val < 90 else "near"
st.markdown(f"""
<div class="takeaway-box">
    <strong>SLA compliance is {sla_assessment} the 90% benchmark at {sla_val}%.</strong>
    Across {total_val:,} service requests, nearly {100 - sla_val:.0f}% of cases miss their target resolution deadline.
    This signals systemic capacity or prioritization challenges, not isolated failures.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="takeaway-box">
    <strong>Average resolution time of {res_val:.0f} hours is skewed by long-tail outliers.</strong>
    A small number of cases remain open for weeks or months, pulling the average up.
    Median resolution time would be significantly lower — the P50/P90 split matters here.
</div>
""", unsafe_allow_html=True)

if not monthly.empty:
    peak = monthly.loc[monthly["total_incidents"].idxmax()]
    trough = monthly.loc[monthly["total_incidents"].idxmin()]
    st.markdown(f"""
    <div class="takeaway-box">
        <strong>Seasonal swing:</strong> Peak volume hits in {peak['month_name']} ({int(peak['total_incidents']):,} incidents)
        and troughs in {trough['month_name']} ({int(trough['total_incidents']):,}).
        This ~{((peak['total_incidents'] - trough['total_incidents']) / trough['total_incidents'] * 100):.0f}% seasonal swing
        suggests staffing and resource planning should follow a seasonal model.
    </div>
    """, unsafe_allow_html=True)
