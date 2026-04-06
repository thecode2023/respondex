"""
Load: Build star schema in SQLite from cleaned parquet data.

Creates:
  - dim_time: date dimension with calendar attributes
  - dim_location: neighborhood, zipcode, lat/lon
  - dim_category: subject → reason → type hierarchy + category_group
  - dim_department: department/agency dimension
  - fact_incidents: the central fact table with foreign keys + metrics
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "respondex.db"


def create_dim_time(df: pd.DataFrame, conn: sqlite3.Connection) -> pd.DataFrame:
    """Build date dimension from all unique dates in the dataset."""
    # Collect all dates from opened_dt and closed_dt
    dates = pd.concat([
        df["opened_dt"].dropna().dt.normalize(),
        df["closed_dt"].dropna().dt.normalize(),
    ]).drop_duplicates().sort_values().reset_index(drop=True)

    dim = pd.DataFrame({"full_date": dates})
    dim["date_key"] = dim["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["full_date"].dt.year
    dim["quarter"] = dim["full_date"].dt.quarter
    dim["month"] = dim["full_date"].dt.month
    dim["month_name"] = dim["full_date"].dt.month_name()
    dim["week"] = dim["full_date"].dt.isocalendar().week.astype(int)
    dim["day_of_week"] = dim["full_date"].dt.dayofweek  # 0=Mon
    dim["day_name"] = dim["full_date"].dt.day_name()
    dim["is_weekend"] = dim["full_date"].dt.dayofweek >= 5

    dim.drop_duplicates(subset=["date_key"], inplace=True)
    dim.to_sql("dim_time", conn, if_exists="replace", index=False)
    print(f"    dim_time: {len(dim):,} rows")
    return dim


def create_dim_location(df: pd.DataFrame, conn: sqlite3.Connection) -> pd.DataFrame:
    """Build location dimension from unique neighborhood + zipcode combos."""
    cols = ["neighborhood", "zipcode", "latitude", "longitude"]
    available = [c for c in cols if c in df.columns]

    loc = df[available].drop_duplicates(subset=["neighborhood", "zipcode"]).copy()
    loc = loc.dropna(subset=["neighborhood"])

    # For each neighborhood+zip combo, use the median lat/lon
    if "latitude" in loc.columns and "longitude" in loc.columns:
        agg = df.groupby(["neighborhood", "zipcode"], dropna=False).agg(
            latitude=("latitude", "median"),
            longitude=("longitude", "median"),
        ).reset_index()
        agg = agg.dropna(subset=["neighborhood"])
    else:
        agg = loc

    agg.insert(0, "location_key", range(1, len(agg) + 1))
    agg.to_sql("dim_location", conn, if_exists="replace", index=False)
    print(f"    dim_location: {len(agg):,} rows")
    return agg


def create_dim_category(df: pd.DataFrame, conn: sqlite3.Connection) -> pd.DataFrame:
    """Build category dimension from subject → reason → type hierarchy."""
    cols = ["subject", "reason", "type", "category_group"]
    available = [c for c in cols if c in df.columns]

    cat = df[available].drop_duplicates().copy()
    cat = cat.dropna(subset=["type"])
    cat.insert(0, "category_key", range(1, len(cat) + 1))
    cat.to_sql("dim_category", conn, if_exists="replace", index=False)
    print(f"    dim_category: {len(cat):,} rows")
    return cat


def create_dim_department(df: pd.DataFrame, conn: sqlite3.Connection) -> pd.DataFrame:
    """Build department dimension."""
    if "department" not in df.columns:
        print("    dim_department: skipped (no department column)")
        return pd.DataFrame()

    dept = df[["department"]].drop_duplicates().dropna().copy()
    dept.insert(0, "department_key", range(1, len(dept) + 1))
    dept.to_sql("dim_department", conn, if_exists="replace", index=False)
    print(f"    dim_department: {len(dept):,} rows")
    return dept


def create_fact_incidents(
    df: pd.DataFrame,
    dim_location: pd.DataFrame,
    dim_category: pd.DataFrame,
    dim_department: pd.DataFrame,
    conn: sqlite3.Connection,
) -> None:
    """Build the fact table with foreign keys to dimensions."""
    fact = df.copy()

    # Add opened_date_key
    fact["opened_date_key"] = fact["opened_dt"].dt.strftime("%Y%m%d")
    fact["opened_date_key"] = pd.to_numeric(fact["opened_date_key"], errors="coerce")

    # Add closed_date_key
    fact["closed_date_key"] = fact["closed_dt"].dt.strftime("%Y%m%d")
    fact["closed_date_key"] = pd.to_numeric(fact["closed_date_key"], errors="coerce")

    # Merge location_key
    if len(dim_location) > 0:
        merge_cols = ["neighborhood", "zipcode"]
        fact = fact.merge(
            dim_location[["location_key", "neighborhood", "zipcode"]],
            on=merge_cols,
            how="left",
        )

    # Merge category_key
    if len(dim_category) > 0:
        merge_cols = ["subject", "reason", "type", "category_group"]
        available = [c for c in merge_cols if c in dim_category.columns]
        fact = fact.merge(
            dim_category[["category_key"] + available],
            on=available,
            how="left",
        )

    # Merge department_key
    if len(dim_department) > 0 and "department" in fact.columns:
        fact = fact.merge(
            dim_department[["department_key", "department"]],
            on="department",
            how="left",
        )

    # Select fact columns
    fact_cols = [
        "case_id",
        "opened_date_key",
        "closed_date_key",
        "location_key",
        "category_key",
        "department_key",
        "case_status",
        "source_channel",
        "sla_met",
        "resolution_hours",
        "sla_target_hours",
    ]
    available_fact = [c for c in fact_cols if c in fact.columns]
    fact_out = fact[available_fact].copy()

    fact_out.to_sql("fact_incidents", conn, if_exists="replace", index=False)
    print(f"    fact_incidents: {len(fact_out):,} rows")


def create_aggregation_tables(conn: sqlite3.Connection) -> None:
    """
    Pre-aggregate data for dashboard performance.
    These tables power the Streamlit pages without querying the full fact table.
    """
    cursor = conn.cursor()

    # Monthly summary
    cursor.executescript("""
        DROP TABLE IF EXISTS agg_monthly;
        CREATE TABLE agg_monthly AS
        SELECT
            dt.year,
            dt.month,
            dt.month_name,
            COUNT(*) as total_incidents,
            SUM(CASE WHEN f.sla_met = 1 THEN 1 ELSE 0 END) as sla_met_count,
            ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct,
            ROUND(AVG(f.resolution_hours), 1) as avg_resolution_hours,
            ROUND(MEDIAN(f.resolution_hours), 1) as median_resolution_hours
        FROM fact_incidents f
        JOIN dim_time dt ON f.opened_date_key = dt.date_key
        GROUP BY dt.year, dt.month, dt.month_name
        ORDER BY dt.year, dt.month;

        DROP TABLE IF EXISTS agg_by_category;
        CREATE TABLE agg_by_category AS
        SELECT
            c.category_group,
            c.subject,
            c.reason,
            c.type,
            COUNT(*) as total_incidents,
            ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct,
            ROUND(AVG(f.resolution_hours), 1) as avg_resolution_hours
        FROM fact_incidents f
        JOIN dim_category c ON f.category_key = c.category_key
        GROUP BY c.category_group, c.subject, c.reason, c.type;

        DROP TABLE IF EXISTS agg_by_neighborhood;
        CREATE TABLE agg_by_neighborhood AS
        SELECT
            l.neighborhood,
            l.zipcode,
            l.latitude,
            l.longitude,
            COUNT(*) as total_incidents,
            ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct,
            ROUND(AVG(f.resolution_hours), 1) as avg_resolution_hours
        FROM fact_incidents f
        JOIN dim_location l ON f.location_key = l.location_key
        GROUP BY l.neighborhood, l.zipcode, l.latitude, l.longitude;

        DROP TABLE IF EXISTS agg_daily;
        CREATE TABLE agg_daily AS
        SELECT
            dt.full_date,
            dt.year,
            dt.month,
            dt.day_name,
            dt.is_weekend,
            COUNT(*) as total_incidents,
            ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct
        FROM fact_incidents f
        JOIN dim_time dt ON f.opened_date_key = dt.date_key
        GROUP BY dt.full_date, dt.year, dt.month, dt.day_name, dt.is_weekend;

        DROP TABLE IF EXISTS agg_hourly;
        CREATE TABLE agg_hourly AS
        SELECT
            dt.day_name,
            dt.is_weekend,
            CAST(substr(dt.full_date, 1, 4) AS INTEGER) as year,
            COUNT(*) as total_incidents
        FROM fact_incidents f
        JOIN dim_time dt ON f.opened_date_key = dt.date_key
        GROUP BY dt.day_name, dt.is_weekend, year;
    """)
    print("    ✓ Aggregation tables created")


def run():
    print("=" * 50)
    print("RESPONDEX — Load Phase")
    print("=" * 50)

    # Load cleaned data
    parquet_path = PROCESSED_DIR / "boston_311_clean.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Run transform.py first. Missing: {parquet_path}")

    print(f"\n  Loading {parquet_path.name}...")
    df = pd.read_parquet(parquet_path)
    print(f"  → {len(df):,} rows")

    # Create/overwrite SQLite database
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    print("\n  Building dimensions...")
    dim_time = create_dim_time(df, conn)
    dim_location = create_dim_location(df, conn)
    dim_category = create_dim_category(df, conn)
    dim_department = create_dim_department(df, conn)

    print("\n  Building fact table...")
    create_fact_incidents(df, dim_location, dim_category, dim_department, conn)

    print("\n  Building aggregation tables...")
    try:
        create_aggregation_tables(conn)
    except Exception as e:
        # SQLite doesn't have MEDIAN natively — handle gracefully
        print(f"    ⚠ Aggregation partial failure: {e}")
        print("    Retrying without MEDIAN...")
        cursor = conn.cursor()
        cursor.executescript("""
            DROP TABLE IF EXISTS agg_monthly;
            CREATE TABLE agg_monthly AS
            SELECT
                dt.year,
                dt.month,
                dt.month_name,
                COUNT(*) as total_incidents,
                SUM(CASE WHEN f.sla_met = 1 THEN 1 ELSE 0 END) as sla_met_count,
                ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct,
                ROUND(AVG(f.resolution_hours), 1) as avg_resolution_hours
            FROM fact_incidents f
            JOIN dim_time dt ON f.opened_date_key = dt.date_key
            GROUP BY dt.year, dt.month, dt.month_name
            ORDER BY dt.year, dt.month;

            DROP TABLE IF EXISTS agg_by_category;
            CREATE TABLE agg_by_category AS
            SELECT
                c.category_group,
                c.subject,
                c.reason,
                c.type,
                COUNT(*) as total_incidents,
                ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct,
                ROUND(AVG(f.resolution_hours), 1) as avg_resolution_hours
            FROM fact_incidents f
            JOIN dim_category c ON f.category_key = c.category_key
            GROUP BY c.category_group, c.subject, c.reason, c.type;

            DROP TABLE IF EXISTS agg_by_neighborhood;
            CREATE TABLE agg_by_neighborhood AS
            SELECT
                l.neighborhood,
                l.zipcode,
                l.latitude,
                l.longitude,
                COUNT(*) as total_incidents,
                ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct,
                ROUND(AVG(f.resolution_hours), 1) as avg_resolution_hours
            FROM fact_incidents f
            JOIN dim_location l ON f.location_key = l.location_key
            GROUP BY l.neighborhood, l.zipcode, l.latitude, l.longitude;

            DROP TABLE IF EXISTS agg_daily;
            CREATE TABLE agg_daily AS
            SELECT
                dt.full_date,
                dt.year,
                dt.month,
                dt.day_name,
                dt.is_weekend,
                COUNT(*) as total_incidents,
                ROUND(AVG(CASE WHEN f.sla_met = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as sla_pct
            FROM fact_incidents f
            JOIN dim_time dt ON f.opened_date_key = dt.date_key
            GROUP BY dt.full_date, dt.year, dt.month, dt.day_name, dt.is_weekend;
        """)
        print("    ✓ Aggregation tables created (without MEDIAN)")

    conn.commit()
    conn.close()

    size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"\n  ✓ Database saved: {DB_PATH} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    run()
