# Respondex — Data Dictionary

Complete field-level documentation for every table in the Respondex star schema.

**Source data:** Boston 311 Service Requests (2024–2025) from [Analyze Boston](https://data.boston.gov/dataset/311-service-requests)  
**Database:** SQLite (`data/respondex.db`)  
**Record count:** 550,023 incidents

---

## Fact Table

### `fact_incidents`

The central fact table. One row per 311 service request.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `case_id` | TEXT | Unique identifier assigned by the city's 311 system | `101004567890` |
| `opened_date_key` | INTEGER | Foreign key → `dim_time.date_key`. Date the case was opened, in YYYYMMDD format | `20240315` |
| `closed_date_key` | INTEGER | Foreign key → `dim_time.date_key`. Date the case was closed. NULL if still open | `20240318` |
| `location_key` | INTEGER | Foreign key → `dim_location.location_key` | `42` |
| `category_key` | INTEGER | Foreign key → `dim_category.category_key` | `17` |
| `department_key` | INTEGER | Foreign key → `dim_department.department_key` | `3` |
| `case_status` | TEXT | Current status of the case | `Open`, `Closed` |
| `source_channel` | TEXT | How the request was submitted | `Citizens Connect App`, `Constituent Call`, `City Worker App`, `Self Service` |
| `sla_met` | BOOLEAN (0/1) | Whether the case was resolved within its SLA target window. Derived from the city's native `on_time` field | `1` (on time), `0` (overdue) |
| `resolution_hours` | REAL | Hours between case open and close. NULL if case is still open. Capped at 8,760 (1 year); negative values nulled | `48.5` |
| `sla_target_hours` | REAL | Hours allowed by the SLA target (open → target date). NULL if no target set | `72.0` |

**Notes:**
- `sla_met` is sourced from the city's own `on_time` field (values: ONTIME / OVERDUE), not a custom threshold
- `resolution_hours` values > 8,760 or < 0 are set to NULL during transform as data quality outliers
- Cases with NULL `closed_date_key` are still open

---

## Dimension Tables

### `dim_time`

Calendar dimension. One row per unique date across all case open and close dates.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date_key` | INTEGER | Primary key. YYYYMMDD format | `20240715` |
| `full_date` | TEXT | ISO date string | `2024-07-15` |
| `year` | INTEGER | Calendar year | `2024`, `2025` |
| `quarter` | INTEGER | Calendar quarter (1–4) | `3` |
| `month` | INTEGER | Calendar month (1–12) | `7` |
| `month_name` | TEXT | Full month name | `July` |
| `week` | INTEGER | ISO week number (1–53) | `29` |
| `day_of_week` | INTEGER | Day of week. 0 = Monday, 6 = Sunday | `0` |
| `day_name` | TEXT | Full day name | `Monday` |
| `is_weekend` | BOOLEAN (0/1) | 1 if Saturday or Sunday | `0` |

**Row count:** 752

---

### `dim_location`

Geography dimension. One row per unique neighborhood + zipcode combination.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `location_key` | INTEGER | Primary key (auto-generated) | `1` |
| `neighborhood` | TEXT | Boston neighborhood name. Title-cased during transform | `Dorchester`, `South Boston`, `Roxbury` |
| `zipcode` | TEXT | 5-digit zip code. Validated to 02xxx range (Boston area). Invalid zips set to NULL | `02125` |
| `latitude` | REAL | Median latitude for the neighborhood+zip combination. Validated to Boston bounding box (42.2–42.4). Out-of-bounds values set to NULL | `42.3187` |
| `longitude` | REAL | Median longitude for the neighborhood+zip combination. Validated to Boston bounding box (-71.2 to -70.9). Out-of-bounds values set to NULL | `-71.0589` |

**Row count:** 142  
**Notes:**
- Latitude/longitude are medians across all incidents in that neighborhood+zip, not centroids
- Some neighborhoods span multiple zip codes, producing multiple rows

---

### `dim_category`

Service type hierarchy. One row per unique subject → reason → type combination.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `category_key` | INTEGER | Primary key (auto-generated) | `1` |
| `subject` | TEXT | Top-level department/area. Sourced from the city's `subject` field | `Public Works Department`, `Transportation - Traffic Division`, `Inspectional Services` |
| `reason` | TEXT | Mid-level category within the subject | `Enforcement & Abandoned Vehicles`, `Street Cleaning`, `Housing` |
| `type` | TEXT | Specific incident type — the most granular classification | `Parking Enforcement`, `Request for Pothole Repair`, `Sidewalk Repair (Make Safe)` |
| `category_group` | TEXT | High-level grouping created during transform. Maps 200+ types into 8 groups for dashboard filtering | `Infrastructure`, `Transportation`, `Public Safety`, `Health & Sanitation`, `Inspections & Code`, `Parks & Environment`, `Property & Housing`, `General Services` |

**Row count:** 178  

**Category group mapping logic:**
1. Exact match on `subject` value (e.g., `Public Works Department` → `Infrastructure`)
2. Keyword fallback for unmatched subjects (e.g., contains "transport" → `Transportation`)
3. Final fallback: `General Services` (covers Mayor's Hotline + Animal Control)

---

### `dim_department`

City department dimension. One row per unique department.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `department_key` | INTEGER | Primary key (auto-generated) | `1` |
| `department` | TEXT | Name of the city department responsible for handling the case | `PWD - Public Works`, `BTDT - Traffic Division`, `ISD - Inspectional Services` |

**Row count:** 19

---

## Pre-Aggregated Tables

These tables are built during the ETL load phase to power the dashboard without querying the full fact table. They are not intended for direct analysis — use the fact + dimension tables for custom queries.

### `agg_monthly`

Monthly rollup of all incidents.

| Column | Type | Description |
|--------|------|-------------|
| `year` | INTEGER | Calendar year |
| `month` | INTEGER | Calendar month (1–12) |
| `month_name` | TEXT | Full month name |
| `total_incidents` | INTEGER | Count of incidents opened in this month |
| `sla_met_count` | INTEGER | Count of incidents where `sla_met = 1` |
| `sla_pct` | REAL | SLA compliance percentage (0–100) |
| `avg_resolution_hours` | REAL | Average resolution time in hours |

---

### `agg_by_category`

Rollup by category hierarchy.

| Column | Type | Description |
|--------|------|-------------|
| `category_group` | TEXT | High-level grouping |
| `subject` | TEXT | Department/area |
| `reason` | TEXT | Mid-level category |
| `type` | TEXT | Specific incident type |
| `total_incidents` | INTEGER | Count of incidents |
| `sla_pct` | REAL | SLA compliance percentage |
| `avg_resolution_hours` | REAL | Average resolution time |

---

### `agg_by_neighborhood`

Rollup by geography.

| Column | Type | Description |
|--------|------|-------------|
| `neighborhood` | TEXT | Neighborhood name |
| `zipcode` | TEXT | Zip code |
| `latitude` | REAL | Median latitude |
| `longitude` | REAL | Median longitude |
| `total_incidents` | INTEGER | Count of incidents |
| `sla_pct` | REAL | SLA compliance percentage |
| `avg_resolution_hours` | REAL | Average resolution time |

---

### `agg_daily`

Daily rollup.

| Column | Type | Description |
|--------|------|-------------|
| `full_date` | TEXT | ISO date string |
| `year` | INTEGER | Calendar year |
| `month` | INTEGER | Calendar month |
| `day_name` | TEXT | Day of week name |
| `is_weekend` | BOOLEAN | 1 if Saturday/Sunday |
| `total_incidents` | INTEGER | Count of incidents |
| `sla_pct` | REAL | SLA compliance percentage |

---

## Source Field Mapping

How raw Boston 311 CSV columns map to the transformed schema:

| Raw CSV Column | Transformed Column | Transform Applied |
|----------------|-------------------|-------------------|
| `case_enquiry_id` | `fact_incidents.case_id` | Renamed |
| `open_dt` | `dim_time.date_key` (via `opened_date_key`) | Parsed from string to datetime, normalized to date |
| `closed_dt` | `dim_time.date_key` (via `closed_date_key`) | Parsed from string to datetime, normalized to date |
| `sla_target_dt` | `fact_incidents.sla_target_hours` | Converted to hours delta from open_dt |
| `on_time` | `fact_incidents.sla_met` | `ONTIME` → 1, `OVERDUE` → 0 |
| `case_status` | `fact_incidents.case_status` | Passed through |
| `subject` | `dim_category.subject` | Passed through |
| `reason` | `dim_category.reason` | Passed through |
| `type` | `dim_category.type` | Passed through |
| `department` | `dim_department.department` | Passed through |
| `source` | `fact_incidents.source_channel` | Renamed |
| `neighborhood` | `dim_location.neighborhood` | Stripped whitespace, title-cased |
| `location_zipcode` | `dim_location.zipcode` | Extracted 5-digit format, validated 02xxx range |
| `latitude` | `dim_location.latitude` | Converted to float, validated Boston bounding box |
| `longitude` | `dim_location.longitude` | Converted to float, validated Boston bounding box |
| (derived) | `fact_incidents.resolution_hours` | `(closed_dt - open_dt)` in hours |
| (derived) | `dim_category.category_group` | Two-pass mapping: exact match → keyword fallback |
| (derived) | `dim_time.*` | Calendar attributes extracted from dates |
