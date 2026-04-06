"""
Page 3: Time Series Analysis
Seasonality, day-of-week patterns, and trend decomposition.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_daily_trends, get_monthly_trends, query
from utils.charts import line_chart, bar_chart, apply_theme, COLORS, PALETTE

st.set_page_config(page_title="Time Series | Respondex", layout="wide", page_icon="📊")

st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background: #1A1D29;
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
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

st.title("Time Series Analysis")
st.caption("Temporal patterns, seasonality, and operational rhythm")

try:
    daily = get_daily_trends()
    monthly = get_monthly_trends()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

if daily.empty:
    st.warning("No daily data available.")
    st.stop()

daily["full_date"] = pd.to_datetime(daily["full_date"])
daily = daily.sort_values("full_date")

# --- Year filter ---
years = sorted(daily["year"].unique())
with st.sidebar:
    st.subheader("Filters")
    selected_years = st.multiselect("Years", years, default=years)

daily_f = daily[daily["year"].isin(selected_years)]

# --- Daily volume with moving averages ---
st.subheader("Daily Incident Volume")
daily_f = daily_f.copy()
daily_f["7d_avg"] = daily_f["total_incidents"].rolling(7, min_periods=1).mean()
daily_f["30d_avg"] = daily_f["total_incidents"].rolling(30, min_periods=1).mean()

fig = px.line(
    daily_f, x="full_date", y=["total_incidents", "7d_avg", "30d_avg"],
    title="Daily Volume with Moving Averages",
    labels={"full_date": "Date", "value": "Incidents", "variable": "Series"},
    color_discrete_map={
        "total_incidents": "rgba(108, 99, 255, 0.2)",
        "7d_avg": COLORS["primary"],
        "30d_avg": COLORS["secondary"],
    },
)
fig.update_traces(selector=dict(name="total_incidents"), line=dict(width=0.5))
fig.update_traces(selector=dict(name="7d_avg"), line=dict(width=2))
fig.update_traces(selector=dict(name="30d_avg"), line=dict(width=2.5))
fig = apply_theme(fig)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Day of Week Pattern ---
col_left, col_right = st.columns(2)

with col_left:
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = daily_f.groupby("day_name", as_index=False).agg(
        avg_incidents=("total_incidents", "mean"),
        avg_sla=("sla_pct", "mean"),
    )
    dow["day_name"] = pd.Categorical(dow["day_name"], categories=dow_order, ordered=True)
    dow = dow.sort_values("day_name")

    fig = bar_chart(
        dow, x="day_name", y="avg_incidents",
        title="Avg Daily Incidents by Day of Week",
        labels={"day_name": "", "avg_incidents": "Avg Incidents"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    fig = bar_chart(
        dow, x="day_name", y="avg_sla",
        title="Avg SLA Compliance by Day of Week",
        labels={"day_name": "", "avg_sla": "SLA %"},
    )
    fig.add_hline(y=90, line_dash="dash", line_color=COLORS["accent"])
    st.plotly_chart(fig, use_container_width=True)

# --- Monthly Seasonality (overlay years) ---
st.subheader("Monthly Seasonality")
if not monthly.empty:
    monthly_f = monthly[monthly["year"].isin(selected_years)].copy()
    monthly_f["year_str"] = monthly_f["year"].astype(str)

    fig = px.line(
        monthly_f, x="month", y="total_incidents", color="year_str",
        title="Monthly Volume by Year (Seasonality Overlay)",
        labels={"month": "Month", "total_incidents": "Incidents", "year_str": "Year"},
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    )
    fig = apply_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

# --- Weekend vs Weekday ---
st.subheader("Weekend vs Weekday Performance")
wkend = daily_f.groupby("is_weekend", as_index=False).agg(
    avg_incidents=("total_incidents", "mean"),
    avg_sla=("sla_pct", "mean"),
)
wkend["label"] = wkend["is_weekend"].map({0: "Weekday", 1: "Weekend"})

c1, c2 = st.columns(2)
with c1:
    st.metric("Weekday Avg", f"{wkend[wkend['label']=='Weekday']['avg_incidents'].values[0]:.0f} incidents/day")
with c2:
    wkend_val = wkend[wkend["label"] == "Weekend"]["avg_incidents"]
    if not wkend_val.empty:
        st.metric("Weekend Avg", f"{wkend_val.values[0]:.0f} incidents/day")

# --- Key Takeaways ---
st.divider()
st.subheader("Key Takeaways")

weekday_avg = wkend[wkend["label"] == "Weekday"]["avg_incidents"].values[0]
weekend_avg_val = wkend[wkend["label"] == "Weekend"]["avg_incidents"].values[0] if not wkend[wkend["label"] == "Weekend"].empty else 0
drop_pct = (1 - weekend_avg_val / weekday_avg) * 100 if weekday_avg > 0 else 0

st.markdown(f"""
<div class="takeaway-box">
    <strong>Weekend volume drops {drop_pct:.0f}%</strong> ({int(weekday_avg)} → {int(weekend_avg_val)} incidents/day).
    This is expected for a government service — but SLA clocks still tick on weekends.
    Cases filed Friday afternoon face the longest effective wait times.
</div>
""", unsafe_allow_html=True)

if not dow.empty:
    peak_day = dow.loc[dow["avg_incidents"].idxmax()]
    trough_day = dow.loc[dow["avg_incidents"].idxmin()]
    st.markdown(f"""
    <div class="takeaway-box">
        <strong>Day-of-week pattern:</strong> {peak_day['day_name']} is the busiest day
        ({peak_day['avg_incidents']:.0f} avg incidents) and {trough_day['day_name']} is quietest
        ({trough_day['avg_incidents']:.0f}). Staffing models that treat all weekdays equally
        are leaving capacity on the table.
    </div>
    """, unsafe_allow_html=True)

if not monthly.empty and len(selected_years) > 1:
    monthly_f_check = monthly[monthly["year"].isin(selected_years)]
    if len(monthly_f_check["year"].unique()) > 1:
        yoy = monthly_f_check.groupby("year")["total_incidents"].sum()
        if len(yoy) >= 2:
            years_sorted = sorted(yoy.index)
            change = (yoy[years_sorted[-1]] - yoy[years_sorted[-2]]) / yoy[years_sorted[-2]] * 100
            direction = "up" if change > 0 else "down"
            st.markdown(f"""
            <div class="takeaway-box">
                <strong>Year-over-year trend:</strong> Total incident volume is {direction}
                {abs(change):.1f}% from {years_sorted[-2]} to {years_sorted[-1]}.
                {"This increase may reflect population growth, expanded 311 awareness, or deteriorating infrastructure."
                if change > 0 else "This decrease could indicate improved preventive maintenance or reporting fatigue."}
            </div>
            """, unsafe_allow_html=True)
