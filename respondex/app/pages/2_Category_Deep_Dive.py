"""
Page 2: Category Deep Dive
Drill into incident types, SLA performance by category, and top offenders.
"""

import streamlit as st
import pandas as pd
from utils.db import get_category_breakdown, get_unique_category_groups
from utils.charts import bar_chart, donut_chart, COLORS
from utils.styles import inject_dashboard_css

st.set_page_config(page_title="Category Deep Dive | Respondex", layout="wide", page_icon="📊")
inject_dashboard_css()

st.title("Category Deep Dive")
st.caption("Incident distribution and SLA performance by service category")

try:
    cat_data = get_category_breakdown()
    groups = get_unique_category_groups()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

# --- Sidebar Filter ---
with st.sidebar:
    st.subheader("Filters")
    selected_groups = st.multiselect(
        "Category Groups",
        options=groups,
        default=groups,
    )

filtered = cat_data[cat_data["category_group"].isin(selected_groups)]

if filtered.empty:
    st.warning("No data for selected filters.")
    st.stop()

# --- KPI row for filtered data ---
k1, k2, k3 = st.columns(3)
total = filtered["total_incidents"].sum()
avg_sla = (filtered["sla_pct"] * filtered["total_incidents"]).sum() / total if total else 0
avg_res = (filtered["avg_resolution_hours"] * filtered["total_incidents"]).sum() / total if total else 0

k1.metric("Incidents (filtered)", f"{total:,}")
k2.metric("Weighted SLA %", f"{avg_sla:.1f}%")
k3.metric("Weighted Avg Resolution", f"{avg_res:.0f} hrs")

st.divider()

# --- Category Group Distribution ---
col_left, col_right = st.columns(2)

with col_left:
    group_agg = filtered.groupby("category_group", as_index=False).agg(
        total_incidents=("total_incidents", "sum")
    ).sort_values("total_incidents", ascending=False)

    fig = donut_chart(
        group_agg, values="total_incidents", names="category_group",
        title="Incident Share by Category Group",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    group_sla = filtered.groupby("category_group", as_index=False).apply(
        lambda g: pd.Series({
            "sla_pct": (g["sla_pct"] * g["total_incidents"]).sum() / g["total_incidents"].sum()
            if g["total_incidents"].sum() > 0 else 0,
            "total": g["total_incidents"].sum(),
        })
    ).sort_values("sla_pct", ascending=True)

    fig = bar_chart(
        group_sla, x="sla_pct", y="category_group",
        title="SLA Compliance by Category Group",
        orientation="h",
        labels={"sla_pct": "SLA %", "category_group": ""},
    )
    fig.add_vline(x=90, line_dash="dash", line_color=COLORS["accent"])
    st.plotly_chart(fig, use_container_width=True)

# --- Top 15 Specific Types ---
st.subheader("Top 15 Incident Types")
top_types = filtered.nlargest(15, "total_incidents")

fig = bar_chart(
    top_types, x="total_incidents", y="type",
    title="Most Common Incident Types",
    orientation="h",
    labels={"total_incidents": "Count", "type": ""},
    color="sla_pct",
)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# --- Worst SLA performers ---
st.subheader("Worst SLA Performers (min 100 incidents)")
min_vol = filtered[filtered["total_incidents"] >= 100]
if not min_vol.empty:
    worst = min_vol.nsmallest(10, "sla_pct")
    fig = bar_chart(
        worst, x="sla_pct", y="type",
        title="Lowest SLA Compliance (≥100 incidents)",
        orientation="h",
        labels={"sla_pct": "SLA %", "type": ""},
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- Key Takeaways ---
st.divider()
st.subheader("Key Takeaways")

if not filtered.empty:
    top_type = filtered.nlargest(1, "total_incidents").iloc[0]
    top3 = filtered.nlargest(3, "total_incidents")
    top3_pct = top3["total_incidents"].sum() / total * 100

    st.markdown(f"""
    <div class="takeaway-box">
        <strong>Volume is heavily concentrated:</strong> "{top_type['type']}" alone accounts for
        {int(top_type['total_incidents']):,} incidents ({top_type['total_incidents']/total*100:.1f}% of filtered total).
        The top 3 types represent {top3_pct:.0f}% of all activity — resource allocation should follow this distribution.
    </div>
    """, unsafe_allow_html=True)

    if not min_vol.empty:
        worst_type = min_vol.nsmallest(1, "sla_pct").iloc[0]
        st.markdown(f"""
        <div class="takeaway-box">
            <strong>Worst SLA performer:</strong> "{worst_type['type']}" hits only {worst_type['sla_pct']:.1f}% SLA compliance
            across {int(worst_type['total_incidents']):,} incidents. This isn't a low-volume edge case — it's a
            systemic miss that warrants root-cause investigation (staffing? complexity? unclear SLA targets?).
        </div>
        """, unsafe_allow_html=True)

    # High volume + low SLA = biggest impact
    high_impact = filtered[filtered["total_incidents"] >= 100].copy()
    if not high_impact.empty:
        high_impact["impact_score"] = high_impact["total_incidents"] * (100 - high_impact["sla_pct"])
        worst_impact = high_impact.nlargest(1, "impact_score").iloc[0]
        st.markdown(f"""
        <div class="takeaway-box">
            <strong>Highest-impact gap:</strong> "{worst_impact['type']}" combines high volume
            ({int(worst_impact['total_incidents']):,} incidents) with poor SLA ({worst_impact['sla_pct']:.1f}%).
            Improving this single category would move the overall SLA needle more than any other intervention.
        </div>
        """, unsafe_allow_html=True)
