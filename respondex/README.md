# Respondex

**Operational Incident & SLA Analytics Engine — Boston 311**

An end-to-end analytics platform that processes 600K+ Boston 311 service requests to surface SLA compliance patterns, incident trends, and neighborhood-level operational performance.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

**[Live Dashboard →](https://respondex.streamlit.app)** · **[Data Source →](https://data.boston.gov/dataset/311-service-requests)**

---

## What This Does

Respondex mirrors how enterprise operations teams monitor service delivery against SLA commitments. It takes raw municipal 311 data — every pothole report, noise complaint, and graffiti ticket filed in Boston — and transforms it into an analytical data product with:

- **SLA compliance tracking** across 30+ incident categories
- **Response time analysis** with percentile breakdowns
- **Seasonal and day-of-week pattern detection**
- **Neighborhood-level performance comparison**
- **Interactive filtering** by time range, category, and geography

---

## Architecture

```
Boston Open Data (CSV)
        │
        ▼
Python/Pandas ETL Pipeline
  ├── extract.py   → Download 2023-2024 CSVs
  ├── transform.py → Clean, validate, engineer features
  └── load.py      → Build star schema in SQLite
        │
        ▼
SQLite Database (Star Schema)
  ├── fact_incidents     (600K+ rows)
  ├── dim_time           (calendar attributes)
  ├── dim_location       (neighborhood, zip, lat/lon)
  ├── dim_category       (subject → reason → type hierarchy)
  ├── dim_department     (city departments)
  └── agg_* tables       (pre-aggregated for dashboard speed)
        │
        ▼
Streamlit Dashboard (Plotly)
  ├── Executive Summary  (KPIs, monthly trends, rolling averages)
  ├── Category Deep Dive (distribution, SLA by type, worst performers)
  └── Time Series        (seasonality, day-of-week, weekend vs weekday)
```

## Data Model

**Star schema** with a central fact table and four dimension tables:

| Table | Description | Key Fields |
|-------|-------------|------------|
| `fact_incidents` | One row per 311 case | case_id, sla_met, resolution_hours, foreign keys |
| `dim_time` | Calendar dimension | date_key, year, quarter, month, day_name, is_weekend |
| `dim_location` | Geography dimension | neighborhood, zipcode, latitude, longitude |
| `dim_category` | Service type hierarchy | subject → reason → type → category_group |
| `dim_department` | City department | department name |

Pre-aggregated tables (`agg_monthly`, `agg_by_category`, `agg_by_neighborhood`, `agg_daily`) power the dashboard for sub-second load times.

---

## How It Was Built

**Design decisions and tradeoffs:**

1. **SQLite over PostgreSQL for deployment.** Supabase free tier caps at 500MB — not enough for 600K+ fact rows plus dimensions. SQLite ships with the app, needs zero infrastructure, and loads instantly on Streamlit Cloud. The star schema design itself is database-agnostic and would transfer directly to PostgreSQL in a production context.

2. **Pre-aggregation over live queries.** The ETL pipeline builds `agg_*` tables at load time so the Streamlit app never scans the full fact table. This keeps page loads under 2 seconds on Streamlit Cloud's free tier.

3. **Parquet as intermediate format.** The transform step outputs `.parquet` (not CSV) for type preservation — dates stay as dates, booleans stay as booleans — and ~4x compression over CSV.

4. **Category grouping.** Boston 311 has 200+ specific `TYPE` values. The transform step maps these into 8 high-level `category_group` values for dashboard filtering, while preserving the full hierarchy for drill-down.

5. **SLA from source.** The dataset includes a native `OnTime_Status` field (ONTIME/OVERDUE), so SLA compliance is derived from official city tracking — not an arbitrary threshold I invented.

---

## Setup

### Prerequisites

- Python 3.10+
- ~500MB disk space for raw data + database

### Install

```bash
git clone https://github.com/thecode2023/respondex.git
cd respondex
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run ETL Pipeline

```bash
python run_etl.py
```

This will:
1. Download 2023 + 2024 Boston 311 CSVs (~200MB total)
2. Clean and transform with Pandas
3. Build the SQLite star schema at `data/respondex.db`

### Launch Dashboard

```bash
cd app
streamlit run Home.py
```

### Deploy to Streamlit Cloud

1. Push to GitHub (the `data/respondex.db` file is gitignored — you'll need to include it for deployment or run ETL in a setup script)
2. Connect your repo at [share.streamlit.io](https://share.streamlit.io)
3. Set the main file path to `app/Home.py`

---

## Project Structure

```
respondex/
├── app/
│   ├── Home.py                          # Landing page
│   ├── pages/
│   │   ├── 1_Executive_Summary.py       # KPIs + trends
│   │   ├── 2_Category_Deep_Dive.py      # Category analysis
│   │   └── 3_Time_Series.py             # Temporal patterns
│   └── utils/
│       ├── db.py                        # SQLite query helpers
│       └── charts.py                    # Plotly chart components
├── scripts/
│   └── etl/
│       ├── extract.py                   # Download from Boston Open Data
│       ├── transform.py                 # Pandas cleaning + feature engineering
│       └── load.py                      # Star schema build in SQLite
├── data/                                # Generated by ETL (gitignored)
├── run_etl.py                           # One-command pipeline runner
├── requirements.txt
└── .streamlit/config.toml               # Dark theme config
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ETL | Python, Pandas |
| Storage | SQLite (star schema) |
| Dashboard | Streamlit, Plotly |
| Data Source | Boston 311 Open Data |
| Deployment | Streamlit Cloud |

---

## License

MIT

---

Built by [Yusuf Masood](https://github.com/thecode2023)
