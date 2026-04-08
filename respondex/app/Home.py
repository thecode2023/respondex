"""
Respondex — Home / Landing Page
Dark navy SaaS aesthetic with Boston imagery.
"""

import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="Respondex",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_image_b64(filename: str) -> str:
    """Load an image from assets/ and return base64 string."""
    path = Path(__file__).parent / "assets" / filename
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return ""


harbor_b64 = load_image_b64("boston_harbor.webp")
mbta_b64 = load_image_b64("boston_mbta.jpg")

# Determine image mime types
harbor_mime = "image/webp"
mbta_mime = "image/jpeg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ========== RESET ========== */
    .stApp {{
        background: #080E1A !important;
    }}
    section[data-testid="stSidebar"] {{
        background: #0A1122 !important;
        border-right: 1px solid rgba(255,255,255,0.04) !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #CBD5E1 !important;
    }}
    section[data-testid="stSidebar"] a {{
        color: #E2E8F0 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span {{
        color: #CBD5E1 !important;
        font-size: 0.95rem !important;
    }}
    section[data-testid="stSidebar"] [aria-selected="true"] span {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* ========== HERO ========== */
    .hero {{
        position: relative;
        width: 100%;
        min-height: 92vh;
        background: linear-gradient(170deg, #080E1A 0%, #0D1B30 40%, #122444 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 5rem 2rem 4rem;
        overflow: hidden;
    }}
    .hero::before {{
        content: '';
        position: absolute;
        inset: 0;
        background:
            radial-gradient(ellipse 800px 600px at 30% 20%, rgba(59, 130, 246, 0.06) 0%, transparent 70%),
            radial-gradient(ellipse 600px 400px at 70% 80%, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
        pointer-events: none;
    }}
    .hero-tag {{
        position: relative;
        z-index: 1;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #3B82F6;
        margin-bottom: 2rem;
        padding: 0.4rem 1.2rem;
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 100px;
        background: rgba(59, 130, 246, 0.06);
    }}
    .hero-title {{
        position: relative;
        z-index: 1;
        font-family: 'Inter', sans-serif !important;
        font-size: clamp(3.5rem, 9vw, 7.5rem) !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.04em;
        line-height: 0.95;
        margin: 0;
    }}
    .hero-subtitle {{
        position: relative;
        z-index: 1;
        font-family: 'Inter', sans-serif;
        font-size: clamp(1rem, 1.8vw, 1.2rem);
        font-weight: 400;
        color: rgba(255,255,255,0.7);
        margin-top: 1.8rem;
        max-width: 600px;
        line-height: 1.75;
    }}
    .hero-divider {{
        position: relative;
        z-index: 1;
        width: 60px;
        height: 2px;
        background: #3B82F6;
        margin: 3rem auto 0;
    }}
    .hero-metrics {{
        position: relative;
        z-index: 1;
        display: flex;
        gap: 4rem;
        margin-top: 2.5rem;
    }}
    .hero-metric {{
        text-align: center;
    }}
    .hero-metric-val {{
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }}
    .hero-metric-lbl {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.58rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.3);
        margin-top: 0.3rem;
    }}

    /* ========== PHOTO SECTIONS ========== */
    .photo-section {{
        width: 100%;
        position: relative;
        overflow: hidden;
    }}
    .photo-harbor {{
        height: 380px;
        background: url('data:{harbor_mime};base64,{harbor_b64}') center/cover no-repeat;
    }}
    .photo-harbor::after {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, #080E1A 0%, rgba(8,14,26,0.3) 30%, rgba(8,14,26,0.3) 70%, #080E1A 100%);
    }}
    .photo-mbta {{
        height: 340px;
        background: url('data:{mbta_mime};base64,{mbta_b64}') center 40%/cover no-repeat;
    }}
    .photo-mbta::after {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, #080E1A 0%, rgba(8,14,26,0.2) 30%, rgba(8,14,26,0.2) 70%, #080E1A 100%);
    }}

    /* ========== CONTENT SECTIONS ========== */
    .section {{
        max-width: 860px;
        margin: 0 auto;
        padding: 5rem 2rem;
    }}
    .section-tag {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #3B82F6;
        margin-bottom: 1rem;
        display: block;
    }}
    .section-heading {{
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #F1F5F9;
        letter-spacing: -0.03em;
        line-height: 1.2;
        margin-bottom: 1.5rem;
    }}
    .section-text {{
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        line-height: 1.85;
        color: #94A3B8;
    }}
    .section-text strong {{
        color: #E2E8F0;
        font-weight: 600;
    }}

    /* ========== METRIC CARDS ========== */
    .card-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.25rem;
        margin-top: 2.5rem;
    }}
    .metric-card {{
        background: linear-gradient(135deg, #0F1829 0%, #131F36 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }}
    .metric-card:hover {{
        border-color: rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }}
    .mc-value {{
        font-family: 'Inter', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.03em;
        line-height: 1;
    }}
    .mc-title {{
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-top: 0.7rem;
        margin-bottom: 0.5rem;
    }}
    .mc-desc {{
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748B;
        line-height: 1.6;
    }}

    /* ========== PIPELINE ========== */
    .pipeline {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin: 3rem 0 2rem;
        flex-wrap: wrap;
    }}
    .pipe-step {{
        background: #0F1829;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        text-align: center;
        min-width: 150px;
        transition: all 0.2s ease;
    }}
    .pipe-step:hover {{
        border-color: rgba(59, 130, 246, 0.25);
        background: #131F36;
    }}
    .pipe-num {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.6rem;
        letter-spacing: 0.25em;
        color: #3B82F6;
        text-transform: uppercase;
    }}
    .pipe-name {{
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-top: 0.4rem;
    }}
    .pipe-tech {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #64748B;
        margin-top: 0.3rem;
    }}
    .pipe-arrow {{
        font-size: 1.4rem;
        color: rgba(255,255,255,0.12);
        padding: 0 0.8rem;
    }}

    /* ========== TECH PILLS ========== */
    .pills {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1.5rem;
    }}
    .pill {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 500;
        color: #94A3B8;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 0.45rem 1rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }}
    .pill:hover {{
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.25);
        color: #3B82F6;
    }}

    /* ========== CTA ========== */
    .cta {{
        max-width: 860px;
        margin: 0 auto;
        padding: 4rem 2rem 5rem;
        text-align: center;
    }}
    .cta-heading {{
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #F1F5F9;
        letter-spacing: -0.02em;
    }}
    .cta-text {{
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #64748B;
        margin-top: 0.8rem;
        line-height: 1.7;
    }}

    /* ========== FOOTER ========== */
    .footer {{
        border-top: 1px solid rgba(255,255,255,0.04);
        padding: 2.5rem 2rem;
        text-align: center;
    }}
    .footer-name {{
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 0.4rem;
    }}
    .footer-links {{
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #475569;
    }}
    .footer-links a {{
        color: #64748B;
        text-decoration: none;
        transition: color 0.15s ease;
    }}
    .footer-links a:hover {{
        color: #3B82F6;
    }}

    /* ========== RESPONSIVE ========== */
    @media (max-width: 768px) {{
        .hero {{ min-height: 80vh; padding: 3rem 1.5rem; }}
        .hero-metrics {{ flex-direction: column; gap: 1.5rem; }}
        .card-grid {{ grid-template-columns: 1fr; }}
        .pipeline {{ flex-direction: column; }}
        .pipe-arrow {{ transform: rotate(90deg); padding: 0.5rem 0; }}
        .section {{ padding: 3.5rem 1.5rem; }}
        .photo-harbor, .photo-mbta {{ height: 220px; }}
    }}
</style>

<!-- ==================== HERO ==================== -->
<div class="hero">
    <div class="hero-tag">Boston 311 · Operational Analytics</div>
    <h1 class="hero-title">Respondex</h1>
    <p class="hero-subtitle">
        How well does Boston respond to its residents?
        550,000+ service requests analyzed across 24 neighborhoods.
        SLA compliance, resolution times, and operational patterns — mapped, measured, and visualized.
    </p>
    <div class="hero-divider"></div>
    <div class="hero-metrics">
        <div class="hero-metric">
            <div class="hero-metric-val">550K+</div>
            <div class="hero-metric-lbl">Requests Analyzed</div>
        </div>
        <div class="hero-metric">
            <div class="hero-metric-val">71.4%</div>
            <div class="hero-metric-lbl">SLA Compliance</div>
        </div>
        <div class="hero-metric">
            <div class="hero-metric-val">24</div>
            <div class="hero-metric-lbl">Neighborhoods</div>
        </div>
        <div class="hero-metric">
            <div class="hero-metric-val">2024–25</div>
            <div class="hero-metric-lbl">Data Coverage</div>
        </div>
    </div>
</div>

<!-- ==================== BOSTON HARBOR ==================== -->
<div class="photo-section photo-harbor"></div>

<!-- ==================== WHY I BUILT THIS ==================== -->
<div class="section">
    <span class="section-tag">Background</span>
    <div class="section-heading">Why I Built This</div>
    <div class="section-text">
        <p>
            I work in security operations at <strong>State Street</strong>, a Fortune 500 financial services firm,
            where my day-to-day revolves around incident monitoring, SLA tracking, and operational reporting.
            Before that, I spent time at <strong>Allied Universal / athenahealth</strong> doing the same thing
            at a global scale — triaging alerts, tracking response times, measuring whether commitments were being met.
        </p>
        <p>
            That taught me something: <strong>the difference between organizations that improve and organizations
            that don't is whether they actually measure their operational performance</strong> — not just log it,
            but analyze it, find the patterns, and surface the gaps nobody talks about.
        </p>
        <p>
            Boston's 311 system is the city's incident management platform. Residents report problems,
            the city commits to timelines, and the data tells you whether those commitments are honored.
            Respondex is the analytics layer that should exist on top of that data — and doesn't.
        </p>
    </div>
</div>

<!-- ==================== WHY THESE METRICS ==================== -->
<div class="section" style="padding-top: 0;">
    <span class="section-tag">Methodology</span>
    <div class="section-heading">Why These Metrics</div>
    <div class="section-text">
        <p>
            Every metric maps to how enterprise operations teams measure performance.
            These are the same KPIs you'd find on a SOC dashboard, an ITSM report, or an ORM scorecard.
        </p>
    </div>
    <div class="card-grid">
        <div class="metric-card">
            <div class="mc-value">71.4%</div>
            <div class="mc-title">SLA Compliance Rate</div>
            <div class="mc-desc">
                When a resident files a complaint, the city commits to a resolution date.
                At 71.4%, Boston misses nearly 1 in 3. This is the metric that tells you
                whether the system is working.
            </div>
        </div>
        <div class="metric-card">
            <div class="mc-value">140h</div>
            <div class="mc-title">Avg Resolution Time</div>
            <div class="mc-desc">
                How long cases take to close. But averages lie — a few cases open for months
                pull the number up. The dashboard breaks this down by category to show
                where the delays actually live.
            </div>
        </div>
        <div class="metric-card">
            <div class="mc-value">178</div>
            <div class="mc-title">Incident Categories</div>
            <div class="mc-desc">
                From parking enforcement to tree maintenance. Parking alone is 22% of all
                volume. Resource allocation should follow demand — but often doesn't.
            </div>
        </div>
        <div class="metric-card">
            <div class="mc-value">24</div>
            <div class="mc-title">Neighborhoods Mapped</div>
            <div class="mc-desc">
                SLA performance varies wildly by geography. Hyde Park trails at 63%
                while others exceed 80%. That signals uneven resource distribution
                or systemic prioritization gaps.
            </div>
        </div>
    </div>
</div>

<!-- ==================== MBTA ==================== -->
<div class="photo-section photo-mbta"></div>

<!-- ==================== ARCHITECTURE ==================== -->
<div class="section">
    <span class="section-tag">Architecture</span>
    <div class="section-heading">How It Works</div>
    <div class="section-text">
        <p>
            Four-stage pipeline. Raw city data in, analytical insight out.
            Every stage mirrors production data engineering patterns.
        </p>
    </div>
    <div class="pipeline">
        <div class="pipe-step">
            <div class="pipe-num">01</div>
            <div class="pipe-name">Extract</div>
            <div class="pipe-tech">Boston Open Data → CSV</div>
        </div>
        <div class="pipe-arrow">→</div>
        <div class="pipe-step">
            <div class="pipe-num">02</div>
            <div class="pipe-name">Transform</div>
            <div class="pipe-tech">Pandas · Feature Eng.</div>
        </div>
        <div class="pipe-arrow">→</div>
        <div class="pipe-step">
            <div class="pipe-num">03</div>
            <div class="pipe-name">Model</div>
            <div class="pipe-tech">SQLite · Star Schema</div>
        </div>
        <div class="pipe-arrow">→</div>
        <div class="pipe-step">
            <div class="pipe-num">04</div>
            <div class="pipe-name">Visualize</div>
            <div class="pipe-tech">Streamlit · Plotly</div>
        </div>
    </div>
    <div class="section-text" style="margin-top: 1.5rem;">
        <p>
            The data model uses a <strong>star schema</strong> — a central fact table with 550K records
            surrounded by four dimension tables. Pre-aggregated summary tables power the dashboard
            for sub-second load times. Same modeling pattern used in enterprise data warehouses.
        </p>
    </div>
</div>

<!-- ==================== STACK ==================== -->
<div class="section" style="padding-top: 0;">
    <span class="section-tag">Stack</span>
    <div class="section-heading">Built With</div>
    <div class="pills">
        <span class="pill">Python</span>
        <span class="pill">Pandas</span>
        <span class="pill">SQL</span>
        <span class="pill">SQLite</span>
        <span class="pill">Streamlit</span>
        <span class="pill">Plotly</span>
        <span class="pill">Star Schema</span>
        <span class="pill">ETL Pipeline</span>
    </div>
</div>

<!-- ==================== CTA ==================== -->
<div class="cta">
    <div class="cta-heading">Explore the Dashboard →</div>
    <div class="cta-text">
        Use the sidebar to navigate the Executive Summary, Category Deep Dive,
        Time Series, and Geographic Analysis. Every chart is interactive.
    </div>
</div>

<!-- ==================== FOOTER ==================== -->
<div class="footer">
    <div class="footer-name">Built by Yusuf Masood</div>
    <div class="footer-links">
        <a href="https://github.com/thecode2023/respondex" target="_blank">GitHub</a> &nbsp;·&nbsp;
        <a href="https://data.boston.gov/dataset/311-service-requests" target="_blank">Data Source</a> &nbsp;·&nbsp;
        Boston 311 (2024–2025)
    </div>
</div>
""", unsafe_allow_html=True)
