"""Page 1: Executive Summary — KPI cards + trend charts."""

import streamlit as st
import pandas as pd
from utils.db import get_kpi_summary, get_monthly_trends, get_daily_trends
from utils.charts import line_chart, bar_chart, COLORS
from utils.styles import inject_dashboard_css, section_label

st.set_page_config(page_title="Executive Summary | Respondex", layout="wide", page_icon="📊")
inject_dashboard_css()

st.title("Executive Summary")
st.caption("Operational performance across 550K+ Boston 311 service requests · 2024–2025")

st.markdown("<br>", unsafe_allow_html=True)

# --- KPI Cards ---
section_label("Key Metrics")
try:
    kpis = get_kpi_summary()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Incidents", f"{kpis['total_incidents']:,}")
    k2.metric("SLA Compliance", f"{kpis['sla_compliance_pct']}%")
    k3.metric("Avg Resolution", f"{kpis['avg_resolution_hours']:.0f} hrs")
    k4.metric("Closure Rate", f"{kpis['closure_rate_pct']}%")
except Exception as e:
    st.error(f"Could not load KPIs: {e}")
    st.info("Run the ETL pipeline first: `python run_etl.py`")
    st.stop()

st.divider()

# --- Monthly Trends ---
monthly = get_monthly_trends()

if not monthly.empty:
    monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)

    section_label("Monthly Trends")
    col_left, col_right = st.columns(2)

    with col_left:
        fig = line_chart(
            monthly, x="period", y="total_incidents",
            title="Incident Volume",
            labels={"period": "Month", "total_incidents": "Incidents"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        fig = line_chart(
            monthly, x="period", y="sla_pct",
            title="SLA Compliance %",
            labels={"period": "Month", "sla_pct": "SLA %"},
        )
        fig.add_hline(y=90, line_dash="dash", line_color=COLORS["accent"],
                       annotation_text="90% target", annotation_position="top left")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    section_label("Resolution Time")
    if "avg_resolution_hours" in monthly.columns:
        fig = bar_chart(
            monthly, x="period", y="avg_resolution_hours",
            title="Avg Resolution by Month (hours)",
            labels={"period": "Month", "avg_resolution_hours": "Hours"},
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Daily volume ---
daily = get_daily_trends()

if not daily.empty:
    daily["full_date"] = pd.to_datetime(daily["full_date"])
    daily = daily.sort_values("full_date")
    daily["rolling_7d"] = daily["total_incidents"].rolling(7, min_periods=1).mean()

    section_label("Daily Pattern")
    fig = line_chart(
        daily, x="full_date", y="rolling_7d",
        title="Daily Volume (7-day rolling avg)",
        labels={"full_date": "Date", "rolling_7d": "Incidents (7d avg)"},
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Key Takeaways ---
st.divider()
section_label("Key Takeaways")
st.markdown("<br>", unsafe_allow_html=True)

sla_val = kpis["sla_compliance_pct"]
res_val = kpis["avg_resolution_hours"]
total_val = kpis["total_incidents"]

sla_assessment = "well below" if sla_val < 80 else "below" if sla_val < 90 else "near"
st.markdown(f"""
<div class="takeaway-box">
    <strong>SLA compliance is {sla_assessment} the 90% benchmark at {sla_val}%.</strong>
    Across {total_val:,} service requests, nearly {100 - sla_val:.0f}% of cases miss their target
    resolution deadline — signaling systemic capacity challenges, not isolated failures.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="takeaway-box">
    <strong>Average resolution of {res_val:.0f} hours is skewed by long-tail outliers.</strong>
    A small number of cases stay open for weeks or months, pulling the average up.
    Median resolution would be significantly lower — the P50/P90 split matters here.
</div>
""", unsafe_allow_html=True)

if not monthly.empty:
    peak = monthly.loc[monthly["total_incidents"].idxmax()]
    trough = monthly.loc[monthly["total_incidents"].idxmin()]
    st.markdown(f"""
    <div class="takeaway-box">
        <strong>Seasonal swing:</strong> Peak volume hits in {peak['month_name']}
        ({int(peak['total_incidents']):,} incidents) and troughs in {trough['month_name']}
        ({int(trough['total_incidents']):,}) — a ~{((peak['total_incidents'] - trough['total_incidents']) / trough['total_incidents'] * 100):.0f}%
        swing that staffing models should account for.
    </div>
    """, unsafe_allow_html=True)
