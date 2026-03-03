"""
SODA_V3_PHASE1 - Streamlit Dashboard
KYC Data Quality Monitoring
"""

import os
import psycopg2
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "kyc_db")
DB_USER = os.getenv("POSTGRES_USER", "kyc_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "kyc_pass")


@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
    )


def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(query, conn)
    except Exception:
        # reconnect on stale connection
        st.cache_resource.clear()
        conn = get_connection()
        return pd.read_sql(query, conn)


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="KYC Data Quality Monitor",
    page_icon="🛡️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .kpi-card.green  { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .kpi-card.red    { background: linear-gradient(135deg, #e53935 0%, #e35d5b 100%); }
    .kpi-card.orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .kpi-card h2 { margin: 0; font-size: 2.2rem; }
    .kpi-card p  { margin: 0; font-size: 0.95rem; opacity: 0.9; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("## 🛡️ KYC Data Quality Monitoring Dashboard")
st.markdown("---")

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
total_users_df = run_query("SELECT COUNT(*) AS cnt FROM users")
total_docs_df  = run_query("SELECT COUNT(*) AS cnt FROM kyc_documents")
last_scan_df   = run_query("""
    SELECT scan_timestamp, failed_checks
    FROM scan_summary
    ORDER BY scan_id DESC
    LIMIT 1
""")

total_users = int(total_users_df["cnt"].iloc[0]) if not total_users_df.empty else 0
total_docs  = int(total_docs_df["cnt"].iloc[0])  if not total_docs_df.empty else 0

if not last_scan_df.empty:
    failed_checks = int(last_scan_df["failed_checks"].iloc[0])
    last_scan_time = last_scan_df["scan_timestamp"].iloc[0]
else:
    failed_checks = 0
    last_scan_time = "No scans yet"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <p>Total Users</p>
        <h2>{total_users}</h2>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card green">
        <p>Total Documents</p>
        <h2>{total_docs}</h2>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card red">
        <p>Failed Checks (Last Scan)</p>
        <h2>{failed_checks}</h2>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card orange">
        <p>Last Scan Time</p>
        <h2 style="font-size:1.1rem;">{last_scan_time}</h2>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

# --- Passed vs Failed Bar Chart ---
with chart_col1:
    st.markdown("### ✅ Passed vs ❌ Failed Checks (Last Scan)")
    latest_scan = run_query("""
        SELECT passed_checks, failed_checks
        FROM scan_summary
        ORDER BY scan_id DESC
        LIMIT 1
    """)
    if not latest_scan.empty:
        bar_data = pd.DataFrame({
            "Status": ["Passed", "Failed"],
            "Count": [
                int(latest_scan["passed_checks"].iloc[0]),
                int(latest_scan["failed_checks"].iloc[0]),
            ],
        })
        fig_bar = px.bar(
            bar_data, x="Status", y="Count", color="Status",
            color_discrete_map={"Passed": "#38ef7d", "Failed": "#e53935"},
            text="Count",
        )
        fig_bar.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis_title="",
            xaxis_title="",
            font=dict(size=14),
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No scan data available yet.")

# --- Scan History Trend ---
with chart_col2:
    st.markdown("### 📈 Scan History Trend")
    history = run_query("""
        SELECT scan_timestamp, total_checks, passed_checks, failed_checks
        FROM scan_summary
        ORDER BY scan_id
    """)
    if not history.empty:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=history["scan_timestamp"], y=history["passed_checks"],
            mode="lines+markers", name="Passed",
            line=dict(color="#38ef7d", width=3),
        ))
        fig_line.add_trace(go.Scatter(
            x=history["scan_timestamp"], y=history["failed_checks"],
            mode="lines+markers", name="Failed",
            line=dict(color="#e53935", width=3),
        ))
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Scan Time",
            yaxis_title="Checks",
            font=dict(size=13),
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No scan history available yet.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Detail Tables
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "❌ Failed Checks",
    "📅 Expired Documents",
    "🚫 Users Missing KYC",
])

with tab1:
    failed_df = run_query("""
        SELECT cr.table_name, cr.check_name, cr.severity, cr.result_message,
               ss.scan_timestamp
        FROM check_results cr
        JOIN scan_summary ss ON cr.scan_id = ss.scan_id
        WHERE cr.status = 'FAIL'
        ORDER BY ss.scan_timestamp DESC, cr.result_id
    """)
    if not failed_df.empty:
        st.dataframe(failed_df, use_container_width=True, hide_index=True)
    else:
        st.success("No failed checks! All data quality rules passed.")

with tab2:
    expired_df = run_query("""
        SELECT u.full_name, u.email, kd.doc_type, kd.expiry_date, kd.verified
        FROM kyc_documents kd
        JOIN users u ON kd.user_id = u.user_id
        WHERE kd.expiry_date < CURRENT_DATE
        ORDER BY kd.expiry_date
    """)
    if not expired_df.empty:
        st.dataframe(expired_df, use_container_width=True, hide_index=True)
    else:
        st.success("No expired documents found.")

with tab3:
    missing_kyc_df = run_query("""
        SELECT u.user_id, u.full_name, u.email, u.country, u.status
        FROM users u
        LEFT JOIN kyc_documents kd ON u.user_id = kd.user_id
        WHERE kd.doc_id IS NULL
        ORDER BY u.user_id
    """)
    if not missing_kyc_df.empty:
        st.dataframe(missing_kyc_df, use_container_width=True, hide_index=True)
    else:
        st.success("All users have KYC documents.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>SODA_V3_PHASE1 · KYC Data Quality Monitoring · Powered by Soda Core & Streamlit</p>",
    unsafe_allow_html=True,
)
