"""
Transform: Clean, engineer features, and shape Boston 311 data
into a star-schema-ready format using Pandas.

Key transformations:
  - Parse and validate dates (OPEN_DT, CLOSED_DT, TARGET_DT)
  - Calculate response_time_hours and resolution_time_hours
  - Derive SLA compliance from OnTime_Status + calculated fields
  - Build category groupings from SUBJECT → REASON → TYPE hierarchy
  - Clean location data (neighborhood, zip, lat/lon)
  - Generate dimension-ready DataFrames
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

# Boston 311 legacy columns we actually use
KEEP_COLS = [
    "case_enquiry_id",
    "open_dt",
    "sla_target_dt",
    "closed_dt",
    "on_time",
    "case_status",
    "closure_reason",
    "case_title",
    "subject",
    "reason",
    "type",
    "department",
    "source",
    "neighborhood",
    "location_street_name",
    "location_zipcode",
    "latitude",
    "longitude",
]


def load_raw_csvs() -> pd.DataFrame:
    """Load and concatenate all raw CSVs from data/raw/."""
    csv_files = sorted(RAW_DIR.glob("boston_311_*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DIR}. Run extract.py first."
        )

    frames = []
    for f in csv_files:
        print(f"  Reading {f.name}...")
        df = pd.read_csv(f, dtype=str, low_memory=False)
        print(f"    → {len(df):,} rows, {len(df.columns)} columns")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    print(f"\n  Combined: {len(combined):,} total rows")
    return combined


def select_and_rename(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only needed columns. Rename to snake_case."""
    # Some CSVs may have slightly different column names; be defensive
    available = [c for c in KEEP_COLS if c in df.columns]
    missing = set(KEEP_COLS) - set(available)
    if missing:
        print(f"  ⚠ Missing columns (will be NaN): {missing}")

    df = df[available].copy()

    rename_map = {
        "case_enquiry_id": "case_id",
        "open_dt": "opened_dt",
        "sla_target_dt": "target_dt",
        "closed_dt": "closed_dt",
        "on_time": "ontime_status",
        "case_status": "case_status",
        "closure_reason": "closure_reason",
        "case_title": "case_title",
        "subject": "subject",
        "reason": "reason",
        "type": "type",
        "department": "department",
        "source": "source_channel",
        "neighborhood": "neighborhood",
        "location_street_name": "street_name",
        "location_zipcode": "zipcode",
        "latitude": "latitude",
        "longitude": "longitude",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date columns. Boston 311 uses 'MM/DD/YYYY HH:MM:SS AM/PM' format."""
    for col in ["opened_dt", "target_dt", "closed_dt"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
    return df


def clean_locations(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate location fields."""
    # Zipcode: keep only valid 5-digit Boston zips (021xx range)
    if "zipcode" in df.columns:
        df["zipcode"] = df["zipcode"].astype(str).str.strip()
        df["zipcode"] = df["zipcode"].str.extract(r"(\d{5})", expand=False)
        # Keep only plausible Boston-area zips
        valid_zip = df["zipcode"].str.startswith("02", na=False)
        df.loc[~valid_zip, "zipcode"] = np.nan

    # Lat/lon: convert to float, null out clearly wrong values
    for col in ["latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Boston bounding box (rough): lat 42.2–42.4, lon -71.2– -70.9
    if "latitude" in df.columns and "longitude" in df.columns:
        out_of_bounds = (
            (df["latitude"] < 42.2) | (df["latitude"] > 42.4) |
            (df["longitude"] < -71.2) | (df["longitude"] > -70.9)
        )
        df.loc[out_of_bounds, ["latitude", "longitude"]] = np.nan

    # Neighborhood: strip whitespace, title case
    if "neighborhood" in df.columns:
        df["neighborhood"] = df["neighborhood"].str.strip().str.title()

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate response times and SLA compliance."""

    # Response time: opened → closed (hours)
    if "opened_dt" in df.columns and "closed_dt" in df.columns:
        delta = df["closed_dt"] - df["opened_dt"]
        df["resolution_hours"] = delta.dt.total_seconds() / 3600
        # Null out negative or absurd values (>8760 hours = 1 year)
        invalid = (df["resolution_hours"] < 0) | (df["resolution_hours"] > 8760)
        df.loc[invalid, "resolution_hours"] = np.nan

    # SLA target time: opened → target (hours)
    if "opened_dt" in df.columns and "target_dt" in df.columns:
        target_delta = df["target_dt"] - df["opened_dt"]
        df["sla_target_hours"] = target_delta.dt.total_seconds() / 3600
        invalid = (df["sla_target_hours"] < 0) | (df["sla_target_hours"] > 8760)
        df.loc[invalid, "sla_target_hours"] = np.nan

    # SLA met: use the built-in OnTime_Status field
    if "ontime_status" in df.columns:
        df["sla_met"] = df["ontime_status"].str.strip().str.upper() == "ONTIME"
    else:
        # Fallback: compare closed_dt vs target_dt
        if "closed_dt" in df.columns and "target_dt" in df.columns:
            df["sla_met"] = df["closed_dt"] <= df["target_dt"]

    # Time-based features from opened_dt
    if "opened_dt" in df.columns:
        df["opened_year"] = df["opened_dt"].dt.year
        df["opened_month"] = df["opened_dt"].dt.month
        df["opened_month_name"] = df["opened_dt"].dt.month_name()
        df["opened_quarter"] = df["opened_dt"].dt.quarter
        df["opened_day_of_week"] = df["opened_dt"].dt.day_name()
        df["opened_hour"] = df["opened_dt"].dt.hour
        df["is_weekend"] = df["opened_dt"].dt.dayofweek >= 5

    return df


def build_category_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create higher-level category groupings from SUBJECT field.
    Boston 311 has: SUBJECT (broad) → REASON (mid) → TYPE (specific)
    Uses keyword matching to minimize the 'Other' bucket.
    """
    if "subject" not in df.columns:
        return df

    # Exact match first
    group_map = {
        "Boston Police Department": "Public Safety",
        "Public Works Department": "Infrastructure",
        "Transportation - Loss of Use": "Transportation",
        "Transportation - Loss of Utility": "Transportation",
        "Transportation - Loss of Utilities": "Transportation",
        "Inspectional Services": "Inspections & Code",
        "Parks & Recreation Department": "Parks & Environment",
        "Property Management": "Property & Housing",
        "Neighborhood Services": "Neighborhood Services",
        "Environment": "Parks & Environment",
        "Environmental Services": "Parks & Environment",
        "Fire Department": "Public Safety",
        "Health": "Health & Sanitation",
        "Mayor's 24 Hour Hotline": "General Services",
        "Recycling": "Health & Sanitation",
        "Sanitation": "Health & Sanitation",
        "Street Lights": "Infrastructure",
        "Signs & Signals": "Infrastructure",
        "Street Cleaning": "Health & Sanitation",
        "Code Enforcement": "Inspections & Code",
        "Housing": "Property & Housing",
        "Graffiti": "Neighborhood Services",
        "Trees": "Parks & Environment",
        "Animal Control": "General Services",
        "Parking Enforcement": "Transportation",
        "Administrative & General Requests": "General Services",
        "General Request": "General Services",
        "AGR": "General Services",
        "Public Property": "Infrastructure",
        "Building": "Inspections & Code",
        "Weights and Measures": "Inspections & Code",
        "Noise Disturbance": "Public Safety",
        "Traffic Management & Engineering": "Transportation",
        "Cemetery": "General Services",
        "Catchbasin": "Infrastructure",
        "PWD": "Infrastructure",
        "ISD": "Inspections & Code",
        "INFO": "General Services",
        "Abandoned Building": "Inspections & Code",
        "Electrical": "Infrastructure",
        "Plumbing": "Inspections & Code",
    }

    df["category_group"] = df["subject"].map(group_map)

    # Keyword fallback for anything still unmapped
    keyword_rules = [
        ("police", "Public Safety"),
        ("fire", "Public Safety"),
        ("safety", "Public Safety"),
        ("noise", "Public Safety"),
        ("transport", "Transportation"),
        ("parking", "Transportation"),
        ("traffic", "Transportation"),
        ("signal", "Infrastructure"),
        ("street", "Infrastructure"),
        ("public works", "Infrastructure"),
        ("pwd", "Infrastructure"),
        ("sidewalk", "Infrastructure"),
        ("pothole", "Infrastructure"),
        ("light", "Infrastructure"),
        ("sewer", "Infrastructure"),
        ("water", "Infrastructure"),
        ("catch", "Infrastructure"),
        ("inspect", "Inspections & Code"),
        ("code", "Inspections & Code"),
        ("building", "Inspections & Code"),
        ("isd", "Inspections & Code"),
        ("permit", "Inspections & Code"),
        ("zoning", "Inspections & Code"),
        ("housing", "Property & Housing"),
        ("property", "Property & Housing"),
        ("health", "Health & Sanitation"),
        ("sanit", "Health & Sanitation"),
        ("recycl", "Health & Sanitation"),
        ("trash", "Health & Sanitation"),
        ("clean", "Health & Sanitation"),
        ("park", "Parks & Environment"),
        ("tree", "Parks & Environment"),
        ("environ", "Parks & Environment"),
        ("animal", "General Services"),
        ("mayor", "General Services"),
        ("admin", "General Services"),
        ("general", "General Services"),
        ("info", "General Services"),
        ("neighborhood", "Neighborhood Services"),
        ("graffiti", "Neighborhood Services"),
    ]

    unmapped = df["category_group"].isna()
    if unmapped.any():
        subject_lower = df.loc[unmapped, "subject"].str.lower().fillna("")
        for keyword, group in keyword_rules:
            matches = subject_lower.str.contains(keyword, na=False)
            still_unmapped = df.loc[unmapped, "category_group"].isna()
            df.loc[unmapped & df.index.isin(still_unmapped[still_unmapped].index), "category_group"] = \
                df.loc[unmapped & df.index.isin(still_unmapped[still_unmapped].index), "category_group"]
            # Simpler approach
            idx = unmapped & df["category_group"].isna()
            match_idx = idx & df["subject"].str.lower().str.contains(keyword, na=False)
            df.loc[match_idx, "category_group"] = group

    # Final fallback
    df["category_group"] = df["category_group"].fillna("General Services")

    # Log what ended up where
    unmapped_count = (df["category_group"] == "General Services").sum()
    total = len(df)
    print(f"    Category mapping: {total - unmapped_count:,} directly mapped, {unmapped_count:,} defaulted to General Services")
    print(f"    Groups: {df['category_group'].value_counts().to_dict()}")

    return df


def validate(df: pd.DataFrame) -> None:
    """Run basic data quality checks."""
    print("\n  Data Quality Checks:")

    total = len(df)
    print(f"    Total rows: {total:,}")

    # Null checks on critical fields
    for col in ["case_id", "opened_dt", "subject", "reason", "type"]:
        if col in df.columns:
            null_pct = df[col].isna().sum() / total * 100
            status = "✓" if null_pct < 5 else "⚠"
            print(f"    {status} {col}: {null_pct:.1f}% null")

    # Duplicate check
    if "case_id" in df.columns:
        dupes = df["case_id"].duplicated().sum()
        status = "✓" if dupes == 0 else "⚠"
        print(f"    {status} Duplicate case_ids: {dupes:,}")

    # Date range
    if "opened_dt" in df.columns:
        min_dt = df["opened_dt"].min()
        max_dt = df["opened_dt"].max()
        print(f"    Date range: {min_dt} → {max_dt}")

    # SLA coverage
    if "sla_met" in df.columns:
        sla_coverage = df["sla_met"].notna().sum() / total * 100
        print(f"    SLA coverage: {sla_coverage:.1f}%")


def run():
    print("=" * 50)
    print("RESPONDEX — Transform Phase")
    print("=" * 50)

    print("\n[1/6] Loading raw CSVs...")
    df = load_raw_csvs()

    print("\n[2/6] Selecting and renaming columns...")
    df = select_and_rename(df)

    print("\n[3/6] Parsing dates...")
    df = parse_dates(df)

    print("\n[4/6] Cleaning locations...")
    df = clean_locations(df)

    print("\n[5/6] Engineering features...")
    df = engineer_features(df)
    df = build_category_groups(df)

    print("\n[6/6] Validating...")
    validate(df)

    # Save processed data
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "boston_311_clean.parquet"
    df.to_parquet(out_path, index=False)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\n  ✓ Saved to {out_path} ({size_mb:.1f} MB)")

    return df


if __name__ == "__main__":
    run()
