"""Database connection helpers for the Streamlit dashboard."""

import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "respondex.db"


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection. Cached per Streamlit session."""
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


@st.cache_data(ttl=3600)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame. Cached for 1 hour."""
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)


@st.cache_data(ttl=3600)
def get_kpi_summary() -> dict:
    """Fetch top-level KPIs for the executive summary."""
    conn = get_connection()

    total = pd.read_sql_query(
        "SELECT COUNT(*) as n FROM fact_incidents", conn
    ).iloc[0]["n"]

    sla = pd.read_sql_query(
        "SELECT ROUND(AVG(CASE WHEN sla_met=1 THEN 1.0 ELSE 0.0 END)*100, 1) as pct FROM fact_incidents",
        conn,
    ).iloc[0]["pct"]

    avg_res = pd.read_sql_query(
        "SELECT ROUND(AVG(resolution_hours), 1) as avg_h FROM fact_incidents WHERE resolution_hours IS NOT NULL",
        conn,
    ).iloc[0]["avg_h"]

    closed_pct = pd.read_sql_query(
        "SELECT ROUND(AVG(CASE WHEN case_status='Closed' THEN 1.0 ELSE 0.0 END)*100, 1) as pct FROM fact_incidents",
        conn,
    ).iloc[0]["pct"]

    return {
        "total_incidents": int(total) if total else 0,
        "sla_compliance_pct": float(sla) if sla else 0.0,
        "avg_resolution_hours": float(avg_res) if avg_res else 0.0,
        "closure_rate_pct": float(closed_pct) if closed_pct else 0.0,
    }


@st.cache_data(ttl=3600)
def get_monthly_trends() -> pd.DataFrame:
    return query("SELECT * FROM agg_monthly ORDER BY year, month")


@st.cache_data(ttl=3600)
def get_category_breakdown() -> pd.DataFrame:
    return query("SELECT * FROM agg_by_category ORDER BY total_incidents DESC")


@st.cache_data(ttl=3600)
def get_neighborhood_data() -> pd.DataFrame:
    return query("SELECT * FROM agg_by_neighborhood ORDER BY total_incidents DESC")


@st.cache_data(ttl=3600)
def get_daily_trends() -> pd.DataFrame:
    return query("SELECT * FROM agg_daily ORDER BY full_date")


@st.cache_data(ttl=3600)
def get_unique_years() -> list:
    df = query("SELECT DISTINCT year FROM dim_time ORDER BY year")
    return df["year"].tolist()


@st.cache_data(ttl=3600)
def get_unique_neighborhoods() -> list:
    df = query(
        "SELECT DISTINCT neighborhood FROM dim_location WHERE neighborhood IS NOT NULL ORDER BY neighborhood"
    )
    return df["neighborhood"].tolist()


@st.cache_data(ttl=3600)
def get_unique_category_groups() -> list:
    df = query(
        "SELECT DISTINCT category_group FROM dim_category WHERE category_group IS NOT NULL ORDER BY category_group"
    )
    return df["category_group"].tolist()
