"""Reusable Plotly chart components with consistent dark theme styling."""

import plotly.express as px
import plotly.graph_objects as go

# Respondex color palette
COLORS = {
    "primary": "#6C63FF",
    "secondary": "#4ECDC4",
    "accent": "#FF6B6B",
    "warning": "#FFE66D",
    "success": "#4ECDC4",
    "danger": "#FF6B6B",
    "bg": "#0E1117",
    "card_bg": "#1A1D29",
    "text": "#FAFAFA",
    "muted": "#8B8D97",
}

PALETTE = [
    "#6C63FF", "#4ECDC4", "#FF6B6B", "#FFE66D", "#45B7D1",
    "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="monospace", color=COLORS["text"], size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
)


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the Respondex dark theme to any Plotly figure."""
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
    return apply_theme(fig)


def donut_chart(df, values, names, title):
    fig = px.pie(
        df, values=values, names=names, title=title, hole=0.5,
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return apply_theme(fig)


def heatmap(df, x, y, z, title):
    fig = px.density_heatmap(
        df, x=x, y=y, z=z, title=title,
        color_continuous_scale=["#0E1117", "#6C63FF", "#4ECDC4"],
    )
    return apply_theme(fig)


def scatter_map(df, lat, lon, size, color, title, hover_name=None):
    fig = px.scatter_map(
        df, lat=lat, lon=lon, size=size, color=color,
        title=title, hover_name=hover_name,
        color_continuous_scale=["#4ECDC4", "#FFE66D", "#FF6B6B"],
        zoom=11, center={"lat": 42.36, "lon": -71.06},
        map_style="carto-darkmatter",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return apply_theme(fig)
