"""
Page 4: Geographic Analysis
Interactive map of Boston + neighborhood-level metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_neighborhood_data, query
from utils.charts import bar_chart, apply_theme, COLORS, PALETTE
from utils.styles import inject_dashboard_css, section_label

st.set_page_config(page_title="Geographic Analysis | Respondex", layout="wide", page_icon="📊")
inject_dashboard_css()

st.title("Geographic Analysis")
st.caption("Neighborhood-level incident patterns and SLA performance across Boston · 2024–2025")

st.markdown("<br>", unsafe_allow_html=True)

try:
    hood_data = get_neighborhood_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

if hood_data.empty:
    st.warning("No neighborhood data available.")
    st.stop()

# Filter out rows without coordinates
map_data = hood_data.dropna(subset=["latitude", "longitude"]).copy()
map_data = map_data[map_data["neighborhood"].notna()]

# --- KPI row ---
section_label("Overview")
k1, k2, k3 = st.columns(3)
k1.metric("Neighborhoods", f"{hood_data['neighborhood'].nunique()}")

top_hood = hood_data.nlargest(1, "total_incidents")
k2.metric("Highest Volume", f"{top_hood.iloc[0]['neighborhood']}", f"{int(top_hood.iloc[0]['total_incidents']):,} incidents")

worst_sla = hood_data[hood_data["total_incidents"] >= 500].nsmallest(1, "sla_pct")
if not worst_sla.empty:
    k3.metric("Worst SLA", f"{worst_sla.iloc[0]['neighborhood']}", f"{worst_sla.iloc[0]['sla_pct']}%")

st.divider()

# --- Interactive Map ---
st.markdown("<br>", unsafe_allow_html=True)
section_label("Incident Map")
st.subheader("Incident Density Map")

# Aggregate by neighborhood for map (sum incidents, weighted avg SLA)
map_agg = map_data.groupby("neighborhood", as_index=False).agg(
    total_incidents=("total_incidents", "sum"),
    sla_pct=("sla_pct", "mean"),
    avg_resolution_hours=("avg_resolution_hours", "mean"),
    latitude=("latitude", "mean"),
    longitude=("longitude", "mean"),
)

# Color toggle
color_metric = st.radio(
    "Color by:", ["Incident Volume", "SLA Compliance %", "Avg Resolution Hours"],
    horizontal=True,
)
color_col = {
    "Incident Volume": "total_incidents",
    "SLA Compliance %": "sla_pct",
    "Avg Resolution Hours": "avg_resolution_hours",
}[color_metric]

# Reverse color scale for SLA (higher = better = green)
if color_col == "sla_pct":
    color_scale = ["#FF6B6B", "#FFE66D", "#4ECDC4"]
elif color_col == "avg_resolution_hours":
    color_scale = ["#4ECDC4", "#FFE66D", "#FF6B6B"]
else:
    color_scale = ["#1A1D29", "#6C63FF", "#FF6B6B"]

fig = px.scatter_map(
    map_agg,
    lat="latitude",
    lon="longitude",
    size="total_incidents",
    color=color_col,
    hover_name="neighborhood",
    hover_data={
        "total_incidents": ":,",
        "sla_pct": ":.1f",
        "avg_resolution_hours": ":.0f",
        "latitude": False,
        "longitude": False,
    },
    color_continuous_scale=color_scale,
    size_max=40,
    zoom=11,
    center={"lat": 42.32, "lon": -71.06},
    map_style="carto-darkmatter",
    title="",
)
fig.update_layout(
    height=550,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="monospace", color=COLORS["text"]),
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Neighborhood Rankings ---
st.markdown("<br>", unsafe_allow_html=True)
section_label("Rankings")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 by Volume")
    top10 = map_agg.nlargest(10, "total_incidents")
    fig = bar_chart(
        top10, x="total_incidents", y="neighborhood",
        title="",
        orientation="h",
        labels={"total_incidents": "Incidents", "neighborhood": ""},
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Worst SLA (min 500 incidents)")
    qualified = map_agg[map_agg["total_incidents"] >= 500].nsmallest(10, "sla_pct")
    fig = bar_chart(
        qualified, x="sla_pct", y="neighborhood",
        title="",
        orientation="h",
        labels={"sla_pct": "SLA %", "neighborhood": ""},
    )
    fig.add_vline(x=90, line_dash="dash", line_color=COLORS["accent"])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- Key Takeaways ---
st.divider()
section_label("Key Takeaways")
st.markdown("<br>", unsafe_allow_html=True)

if not map_agg.empty:
    top_vol = map_agg.nlargest(3, "total_incidents")
    top_names = ", ".join(top_vol["neighborhood"].tolist())

    best_sla_hood = map_agg[map_agg["total_incidents"] >= 500].nlargest(1, "sla_pct")
    worst_sla_hood = map_agg[map_agg["total_incidents"] >= 500].nsmallest(1, "sla_pct")

    st.markdown(f"""
    <div class="takeaway-box">
        <strong>Volume concentration:</strong> {top_names} account for the highest incident volumes.
        Service demand is not evenly distributed — a small number of neighborhoods drive a disproportionate share of 311 activity.
    </div>
    """, unsafe_allow_html=True)

    if not worst_sla_hood.empty and not best_sla_hood.empty:
        spread = best_sla_hood.iloc[0]["sla_pct"] - worst_sla_hood.iloc[0]["sla_pct"]
        st.markdown(f"""
        <div class="takeaway-box">
            <strong>SLA disparity:</strong> {best_sla_hood.iloc[0]['neighborhood']} leads SLA compliance
            at {best_sla_hood.iloc[0]['sla_pct']:.1f}%, while {worst_sla_hood.iloc[0]['neighborhood']}
            trails at {worst_sla_hood.iloc[0]['sla_pct']:.1f}% — a {spread:.1f} percentage point gap.
            This suggests uneven resource allocation or differing case complexity by area.
        </div>
        """, unsafe_allow_html=True)

    fastest = map_agg[map_agg["total_incidents"] >= 500].nsmallest(1, "avg_resolution_hours")
    slowest = map_agg[map_agg["total_incidents"] >= 500].nlargest(1, "avg_resolution_hours")
    if not fastest.empty and not slowest.empty:
        st.markdown(f"""
        <div class="takeaway-box">
            <strong>Resolution speed:</strong> {fastest.iloc[0]['neighborhood']} resolves cases fastest
            (avg {fastest.iloc[0]['avg_resolution_hours']:.0f} hrs), while {slowest.iloc[0]['neighborhood']}
            averages {slowest.iloc[0]['avg_resolution_hours']:.0f} hrs — signaling potential capacity or
            prioritization differences.
        </div>
        """, unsafe_allow_html=True)
