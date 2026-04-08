"""
RAG Chatbot Engine v2 — improved SQL generation, follow-up suggestions,
retry on failure, conversation memory, and source citation.
"""

import re
import sqlite3
import pandas as pd
import streamlit as st
from google import genai
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "respondex.db"

SCHEMA_CONTEXT = """
You have access to a SQLite database with Boston 311 service request data (2024-2025, ~550K records).
The database uses a star schema:

=== FACT TABLE ===
fact_incidents: case_id, opened_date_key (FK→dim_time YYYYMMDD), closed_date_key (FK→dim_time),
  location_key (FK→dim_location), category_key (FK→dim_category), department_key (FK→dim_department),
  case_status ('Open'/'Closed'), source_channel, sla_met (1=on time, 0=missed), resolution_hours, sla_target_hours

=== DIMENSIONS ===
dim_time: date_key (YYYYMMDD), full_date, year (2024/2025), quarter, month (1-12), month_name, week, day_of_week (0=Mon), day_name, is_weekend
dim_location: location_key, neighborhood, zipcode, latitude, longitude
dim_category: category_key, subject, reason, type, category_group ('Infrastructure','Transportation','Public Safety','Health & Sanitation','Inspections & Code','Parks & Environment','Property & Housing','General Services','Neighborhood Services')
dim_department: department_key, department

=== PRE-AGGREGATED (use for speed) ===
agg_monthly: year, month, month_name, total_incidents, sla_met_count, sla_pct, avg_resolution_hours
agg_by_category: category_group, subject, reason, type, total_incidents, sla_pct, avg_resolution_hours
agg_by_neighborhood: neighborhood, zipcode, latitude, longitude, total_incidents, sla_pct, avg_resolution_hours
agg_daily: full_date, year, month, day_name, is_weekend, total_incidents, sla_pct

=== KEY FACTS ===
Total: ~550K records | Date range: Jan 2024 – Dec 2025 | Overall SLA: ~71.4%
Top neighborhoods: Dorchester, South Boston, Roxbury | Top types: Parking Enforcement, Street Cleaning, Tree Maintenance
"""

SQL_RULES = """
Rules for writing SQL:
- SQLite-compatible SELECT only. No INSERT/UPDATE/DELETE/DROP/ALTER.
- ALWAYS filter out statistical noise: use HAVING COUNT(*) >= 50 for any grouped analysis.
- ALWAYS include supporting numeric columns (counts, percentages, hours) alongside names.
- Use agg_* tables when possible. JOIN to dimensions when you need attributes not in agg tables.
- ORDER by the most relevant metric. LIMIT 25 max.
- Return ONLY raw SQL. No markdown fences, no explanation, no comments.
"""


def get_gemini_client() -> genai.Client:
    api_key = None
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        import os
        api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY in .streamlit/secrets.toml")
    return genai.Client(api_key=api_key)


def extract_sql(raw: str) -> str:
    """Extract clean SQL from Gemini's response, handling fences and preamble."""
    sql = raw.strip()
    sql = re.sub(r"^```sql\s*", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"^```\s*", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"\s*```$", "", sql, flags=re.MULTILINE)
    sql = sql.strip()

    # Extract SELECT statement if there's preamble
    match = re.search(r"(SELECT\s.+)", sql, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()

    # Trim after last semicolon
    if ";" in sql:
        sql = sql[:sql.rfind(";") + 1]

    return sql


def validate_sql(sql: str) -> tuple[bool, str]:
    sql_check = sql.upper().strip().rstrip(";").strip()
    dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
    for kw in dangerous:
        if re.search(rf'\b{kw}\b', sql_check):
            return False, f"Blocked: contains {kw}."
    if not sql_check.startswith("SELECT"):
        return False, f"Must be SELECT. Got: {sql[:60]}..."
    return True, ""


def execute_sql(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def generate_sql(question: str, conversation_context: str, client: genai.Client) -> str:
    """Generate SQL with conversation context for follow-ups."""
    prompt = f"""{SCHEMA_CONTEXT}

{SQL_RULES}

Conversation so far:
{conversation_context}

Current question: "{question}"

If this is a follow-up question, use context from the conversation to understand what the user is referring to.
Write a single SQLite SELECT query to answer the current question."""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return extract_sql(response.text)


def generate_sql_retry(question: str, original_sql: str, error: str, client: genai.Client) -> str:
    """Retry SQL generation with the error context."""
    prompt = f"""{SCHEMA_CONTEXT}

{SQL_RULES}

The user asked: "{question}"

I tried this SQL but it failed:
{original_sql}

Error: {error}

Write a corrected, simpler SQL query. Use the agg_* tables if possible. Double-check table and column names against the schema above."""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return extract_sql(response.text)


def narrate_results(question: str, sql: str, df: pd.DataFrame, conversation_context: str, client: genai.Client) -> str:
    if len(df) > 25:
        data_str = df.head(25).to_string(index=False) + f"\n... ({len(df)} total rows)"
    else:
        data_str = df.to_string(index=False)

    prompt = f"""You are a senior operations analyst writing about Boston 311 data (2024-2025).

Conversation so far:
{conversation_context}

Current question: "{question}"

Query results:
{data_str}

Write a clear analytical response:
- Lead with the direct answer using specific numbers from the results.
- Cite actual values: percentages, counts, hours. Never approximate when exact figures are available.
- If comparing items, name the top and bottom with their exact numbers.
- Call out anything surprising or notable.
- 2-4 paragraphs max. Plain English. No database jargon.
- Don't mention SQL, queries, tables, or database structure.
- Don't say "the data shows" — just state findings directly."""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip()


def generate_follow_ups(question: str, narrative: str, client: genai.Client) -> list[str]:
    """Suggest 3 natural follow-up questions."""
    prompt = f"""Based on this Q&A about Boston 311 data:

Question: "{question}"
Answer summary: {narrative[:500]}

Suggest exactly 3 short follow-up questions the user might ask next. Each should:
- Be a natural next step from the answer
- Ask about a different angle (drill down, compare, explain why, etc.)
- Be specific enough to generate a SQL query

Return ONLY the 3 questions, one per line. No numbering, no bullets, no explanation."""

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        lines = [l.strip() for l in response.text.strip().split("\n") if l.strip()]
        return lines[:3]
    except Exception:
        return []


def build_conversation_context(messages: list) -> str:
    """Build a condensed conversation context from chat history."""
    if not messages:
        return "No previous conversation."

    context_parts = []
    # Only use last 4 exchanges to keep context window manageable
    recent = messages[-8:]
    for msg in recent:
        role = msg["role"].upper()
        if role == "USER":
            context_parts.append(f"USER: {msg['content']}")
        else:
            # Truncate long narratives
            content = msg.get("content", "")
            if len(content) > 300:
                content = content[:300] + "..."
            context_parts.append(f"ANALYST: {content}")

    return "\n".join(context_parts)


def ask_question(question: str, messages: list) -> dict:
    """Full RAG pipeline with retry and conversation memory."""
    result = {
        "question": question,
        "sql": None,
        "data": None,
        "narrative": None,
        "follow_ups": [],
        "error": None,
    }

    try:
        client = get_gemini_client()
    except Exception as e:
        result["error"] = f"API key error: {e}"
        return result

    conversation_context = build_conversation_context(messages)

    # Step 1: Generate SQL
    try:
        sql = generate_sql(question, conversation_context, client)
        result["sql"] = sql
    except Exception as e:
        result["error"] = f"Could not generate query: {e}"
        return result

    # Step 2: Validate
    is_safe, reason = validate_sql(sql)
    if not is_safe:
        result["error"] = reason
        return result

    # Step 3: Execute (with retry on failure)
    try:
        df = execute_sql(sql)
        result["data"] = df
    except Exception as e:
        # Retry with error context
        try:
            retry_sql = generate_sql_retry(question, sql, str(e), client)
            result["sql"] = retry_sql

            is_safe, reason = validate_sql(retry_sql)
            if not is_safe:
                result["error"] = reason
                return result

            df = execute_sql(retry_sql)
            result["data"] = df
        except Exception as e2:
            result["error"] = f"Query failed after retry: {e2}\n\nOriginal SQL:\n```\n{sql}\n```"
            return result

    # Step 4: Narrate
    try:
        narrative = narrate_results(question, result["sql"], df, conversation_context, client)
        result["narrative"] = narrative
    except Exception as e:
        result["error"] = f"Could not generate analysis: {e}"
        return result

    # Step 5: Suggest follow-ups
    try:
        result["follow_ups"] = generate_follow_ups(question, narrative, client)
    except Exception:
        result["follow_ups"] = []

    return result
