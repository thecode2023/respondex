"""Plotly chart components v2 — polished dark theme with proper formatting."""

import plotly.express as px
import plotly.graph_objects as go

# Color system
COLORS = {
    "primary": "#3B82F6",
    "secondary": "#06B6D4",
    "accent": "#F43F5E",
    "warning": "#F59E0B",
    "success": "#10B981",
    "text": "#F1F5F9",
    "muted": "#64748B",
    "bg": "#080E1A",
    "card": "#0F1829",
}

PALETTE = [
    "#3B82F6", "#06B6D4", "#8B5CF6", "#F59E0B", "#10B981",
    "#F43F5E", "#EC4899", "#14B8A6", "#6366F1", "#84CC16",
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94A3B8", size=12),
    margin=dict(l=50, r=20, t=55, b=45),
    title=dict(
        font=dict(family="Inter, sans-serif", size=15, color="#E2E8F0", weight=600),
        x=0, xanchor="left", y=0.98,
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.03)",
        zerolinecolor="rgba(255,255,255,0.05)",
        tickfont=dict(size=11, color="#64748B"),
        title_font=dict(size=12, color="#94A3B8"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.03)",
        zerolinecolor="rgba(255,255,255,0.05)",
        tickfont=dict(size=11, color="#64748B"),
        title_font=dict(size=12, color="#94A3B8"),
    ),
    legend=dict(
        font=dict(size=11, color="#94A3B8"),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
    ),
    hoverlabel=dict(
        bgcolor="#1E293B",
        bordercolor="rgba(255,255,255,0.1)",
        font=dict(family="Inter, sans-serif", size=13, color="#F1F5F9"),
    ),
)


def apply_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(**LAYOUT_DEFAULTS)
    return fig


def line_chart(df, x, y, title, color=None, labels=None):
    fig = px.line(
        df, x=x, y=y, title=title, color=color, labels=labels,
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(line=dict(width=2.5))
    return apply_theme(fig)


def bar_chart(df, x, y, title, color=None, orientation="v", labels=None):
    fig = px.bar(
        df, x=x, y=y, title=title, color=color, labels=labels,
        orientation=orientation, color_discrete_sequence=PALETTE,
    )
    fig.update_traces(
        marker=dict(
            cornerradius=4,
            line=dict(width=0),
        ),
        opacity=0.92,
    )
    return apply_theme(fig)


def donut_chart(df, values, names, title):
    fig = px.pie(
        df, values=values, names=names, title=title, hole=0.55,
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(size=11, family="Inter, sans-serif"),
        marker=dict(line=dict(color="#080E1A", width=2)),
    )
    return apply_theme(fig)


def heatmap(df, x, y, z, title):
    fig = px.density_heatmap(
        df, x=x, y=y, z=z, title=title,
        color_continuous_scale=["#080E1A", "#3B82F6", "#06B6D4"],
    )
    return apply_theme(fig)


def scatter_map(df, lat, lon, size, color, title, hover_name=None):
    fig = px.scatter_map(
        df, lat=lat, lon=lon, size=size, color=color,
        title=title, hover_name=hover_name,
        color_continuous_scale=["#06B6D4", "#F59E0B", "#F43F5E"],
        zoom=11, center={"lat": 42.32, "lon": -71.06},
        map_style="carto-darkmatter",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return apply_theme(fig)
