# Respondex

**Operational Incident & SLA Analytics Engine — Boston 311**

An end-to-end analytics platform that processes 550,000+ Boston 311 service requests to surface SLA compliance patterns, incident trends, neighborhood-level performance gaps, and AI-powered analytical narratives.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

**[Live Dashboard →](https://respondex.streamlit.app)** · **[Data Source →](https://data.boston.gov/dataset/311-service-requests)**

---

## What This Does

Every day, Boston residents file hundreds of 311 service requests — potholes, parking violations, noise complaints, street light outages, illegal dumping. The city assigns each case a target resolution date. Respondex analyzes whether those commitments are being met, where they're falling short, and why.

This is not a tutorial project. It mirrors how enterprise operations teams monitor service delivery against SLA commitments — the same pattern used in SOC dashboards, ITSM reporting, and operational risk management.

### Key Findings

- **71.4% SLA compliance** — Boston misses nearly 1 in 3 service request deadlines
- **Parking Enforcement** accounts for 22% of all incident volume (123K+ cases)
- **Hyde Park** trails other neighborhoods at ~63% SLA compliance while some exceed 80%
- **Weekend volume drops 35%** but SLA clocks keep ticking — Friday cases face the longest waits
- **Seasonal swing of ~40%** between peak (summer) and trough (winter) months

---

## Dashboard Pages

### Home
Editorial landing page with project background, methodology explanation, architecture overview, and Boston imagery.

### Executive Summary
Four KPI cards (total incidents, SLA compliance, avg resolution time, closure rate) with monthly trend charts, resolution time analysis, and a 7-day rolling average daily volume view.

### Category Deep Dive
Interactive donut chart of incident distribution by category group, SLA compliance comparison across categories, top 15 incident types by volume, and worst SLA performers. Filterable by category group via sidebar.

### Time Series Analysis
Daily volume with 7-day and 30-day moving averages, day-of-week patterns, year-over-year seasonality overlay (2024 vs 2025), and weekend vs weekday performance comparison.

### Geographic Analysis
Interactive scatter map of Boston on a dark basemap, color-coded by incident volume, SLA compliance, or resolution time. Neighborhood rankings by volume and worst SLA performers. Key takeaways on geographic service equity.

### AI Insights (RAG Chatbot)
Natural language interface powered by Gemini 2.5 Flash. Ask any question about the data — the system translates it to SQL, executes against the database, and returns a written analytical narrative with supporting data table and the generated SQL query. Includes conversation memory for follow-up questions and suggested next questions after each answer.

---

## Architecture

```
Boston Open Data (CSV)
        │
        ▼
Python/Pandas ETL Pipeline
  ├── extract.py   → Download 2024-2025 CSVs
  ├── transform.py → Clean, validate, engineer features
  └── load.py      → Build star schema in SQLite
        │
        ▼
SQLite Database (Star Schema)
  ├── fact_incidents     (550K+ rows)
  ├── dim_time           (calendar attributes)
  ├── dim_location       (neighborhood, zip, lat/lon)
  ├── dim_category       (subject → reason → type hierarchy)
  ├── dim_department     (city departments)
  └── agg_* tables       (pre-aggregated for dashboard speed)
        │
        ▼
Streamlit Dashboard
  ├── Executive Summary
  ├── Category Deep Dive
  ├── Time Series Analysis
  ├── Geographic Analysis (interactive map)
  └── AI Insights (Gemini RAG chatbot)
```

---

## Data Model

Star schema with a central fact table and four dimension tables:

| Table | Description | Key Fields |
|-------|-------------|------------|
| `fact_incidents` | One row per 311 case | case_id, sla_met, resolution_hours, foreign keys |
| `dim_time` | Calendar dimension | date_key, year, quarter, month, day_name, is_weekend |
| `dim_location` | Geography dimension | neighborhood, zipcode, latitude, longitude |
| `dim_category` | Service type hierarchy | subject → reason → type → category_group |
| `dim_department` | City department | department name |

Pre-aggregated tables (`agg_monthly`, `agg_by_category`, `agg_by_neighborhood`, `agg_daily`) power the dashboard for sub-second load times.

---

## Design Decisions

**SQLite over PostgreSQL.** Supabase free tier caps at 500MB — not enough for 550K fact rows plus dimensions and aggregations. SQLite ships with the app, needs zero infrastructure, and loads instantly on Streamlit Cloud. The star schema design is database-agnostic and transfers directly to PostgreSQL in a production context.

**Pre-aggregation over live queries.** The ETL pipeline builds `agg_*` tables at load time so the Streamlit app never scans the full fact table on page load. This keeps every page under 2 seconds on Streamlit Cloud's free tier.

**Parquet as intermediate format.** The transform step outputs `.parquet` instead of CSV for type preservation — dates stay as dates, booleans stay as booleans — with ~4x compression.

**Keyword-based category mapping.** Boston 311 has 200+ specific incident types across 10 subjects. A two-pass mapping strategy (exact match → keyword fallback) collapses these into 8 high-level category groups for dashboard filtering while preserving the full hierarchy for drill-down.

**SLA from source data.** The dataset includes a native `on_time` field (ONTIME/OVERDUE) derived from the city's own tracking. SLA compliance metrics use this official field rather than arbitrary thresholds.

**RAG chatbot over predefined templates.** The AI Insights page uses a genuine retrieval-augmented generation pattern: schema-aware SQL generation → execution → narrative synthesis. This demonstrates a real AI integration that does something a static page cannot. The system includes conversation memory for follow-up questions, automatic retry on SQL failures, and minimum volume filters to avoid statistically meaningless results.

**Dark navy aesthetic.** The dashboard uses a dark theme (#080E1A background) with Inter and JetBrains Mono typography, blue accent colors (#3B82F6), and subtle gradient cards. The Home page uses a contrasting editorial design with Boston harbor and MBTA imagery loaded as base64 from local assets — zero external image dependencies.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ETL | Python 3.11, Pandas |
| Storage | SQLite (star schema) |
| Dashboard | Streamlit, Plotly |
| AI | Gemini 2.5 Flash (google-genai) |
| Data Source | Boston 311 Open Data (2024-2025) |
| Deployment | Streamlit Cloud |

---

## Setup

### Prerequisites

- Python 3.10+
- ~500MB disk space for raw data + database
- Gemini API key (free from [Google AI Studio](https://aistudio.google.com/apikey)) for AI Insights page

### Install

```bash
git clone https://github.com/thecode2023/respondex.git
cd respondex/respondex
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run ETL Pipeline

Download the 2024 and 2025 Boston 311 CSVs from [Analyze Boston](https://data.boston.gov/dataset/311-service-requests) and place them in `data/raw/` as `boston_311_2024.csv` and `boston_311_2025.csv`. Then:

```bash
python -c "
from scripts.etl.transform import run as transform
from scripts.etl.load import run as load
transform()
load()
"
```

### Add API Key

```bash
mkdir -p app/.streamlit
echo 'GEMINI_API_KEY = "your_key_here"' > app/.streamlit/secrets.toml
```

### Launch Dashboard

```bash
cd app
streamlit run Home.py
```

---

## Future Work

- **Boston's new 311 backend:** Starting October 2025, Boston is migrating to a new system with a different schema (`case_topic`/`service_name` instead of `subject`/`reason`/`type`). The ETL pipeline is designed to accommodate this migration with an additional transform path.
- **Median/percentile resolution metrics:** SQLite lacks a native MEDIAN function. A custom aggregation or migration to DuckDB would enable P50/P90 breakdowns that better represent resolution time distributions.
- **Scheduled refresh:** Automate monthly data pulls and ETL runs to keep the dashboard current.

---

## License

MIT

---

Built by [Yusuf Masood](https://github.com/thecode2023)
