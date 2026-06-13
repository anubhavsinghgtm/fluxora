"""
Fluxora  - AI Analytics Assistant — Streamlit UI
========================================
Run locally:
    streamlit run streamlit_app.py

Requires:
    ANALYTICS_API_URL in .env or set directly below
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv
import uuid

load_dotenv()



# add this near the top after imports
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())


# ── Config ────────────────────────────────────────────────────────────────────

API_URL = os.getenv("ANALYTICS_API_URL", "http://localhost:8000")
API_ENDPOINT = f"{API_URL}/api/v1/natural-query"

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Fluxora  - AI Analytics Assistant",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Input box */
    .stTextInput > div > div > input {
        background-color: #1e2130;
        color: #ffffff;
        border: 1px solid #2d6af6;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
    }

    /* Button */
    .stButton > button {
        background-color: #2d6af6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 28px;
        font-size: 15px;
        font-weight: 600;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton > button:hover { background-color: #1a56d6; }

    /* SQL code block */
    .sql-box {
        background-color: #1e2130;
        border-left: 3px solid #2d6af6;
        border-radius: 6px;
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #a8d8ff;
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* Metric cards */
    .metric-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        border: 1px solid #2a2f45;
    }
    .metric-label {
        color: #8892a4;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
    }

    /* Section headers */
    .section-header {
        color: #8892a4;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        margin-top: 24px;
    }

    /* Dataframe */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Error box */
    .error-box {
        background-color: #2d1515;
        border-left: 3px solid #e53e3e;
        border-radius: 6px;
        padding: 14px 16px;
        color: #fc8181;
        font-size: 14px;
    }

    /* Sample queries */
    .sample-query {
        background-color: #1e2130;
        border: 1px solid #2a2f45;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 13px;
        color: #a8d8ff;
        cursor: pointer;
        margin-bottom: 6px;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='text-align: center; padding: 32px 0 24px 0;'>
    <div style='font-size: 40px; margin-bottom: 8px;'>💻</div>
    <h1 style='color: #ffffff; font-size: 28px; font-weight: 700; margin: 0;'>
        Fluxora  - AI Analytics Assistant
    </h1>
    <p style='color: #8892a4; font-size: 15px; margin-top: 8px;'>
        Ask questions about sales, customers, products and deliveries in plain English
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sample Queries ─────────────────────────────────────────────────────────────

SAMPLE_QUERIES = [
    "Show top 5 customers by total spend",
    "Which product category generates the most revenue?",
    "Which delivery partner has the most delayed orders?",
    "What is the most popular payment method?",
    "Show me total revenue by city",
    "Which laptop processor is most popular?",
    "How many orders were cancelled last month?",
    "What are the top 5 selling products?",
]

st.markdown('<p class="section-header">Try a sample question</p>', unsafe_allow_html=True)

# show sample queries as clickable buttons in a grid
cols = st.columns(4)
for i, sample in enumerate(SAMPLE_QUERIES):
    with cols[i % 4]:
        if st.button(sample, key=f"sample_{i}", use_container_width=True):
            st.session_state["query_input"] = sample

# ── Query Input ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-header">Your question</p>', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])

with col_input:
    query = st.text_input(
        label="query",
        label_visibility="collapsed",
        placeholder="e.g. Show me top 5 customers by total spend...",
        key="query_input",
    )

with col_btn:
    submit = st.button("Ask →", use_container_width=True)

# ── Query Execution ───────────────────────────────────────────────────────────

if submit and query.strip():
    with st.spinner("Thinking..."):
        try:
            response = requests.get(
                API_ENDPOINT,
                params={"q": query.strip()},
                headers={"X-Session-ID": st.session_state["session_id"]},
                timeout=30,
            )

            st.write(f"Status code: {response.status_code}")
            st.write(f"Raw response: {response.text[:500]}")

            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])
                sql    = data.get("sql", "")
                explanation = data.get("explanation", "")
                count  = data.get("count", 0)
                insight = data.get("insight", "")

                # ── Metrics Row ───────────────────────────────────────────
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Rows Returned</div>
                        <div class="metric-value">{count}</div>
                    </div>""", unsafe_allow_html=True)
                with m2:
                    status_color = "#48bb78" if count > 0 else "#f6ad55"
                    status_text  = "Success" if count > 0 else "No Results"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Status</div>
                        <div class="metric-value" style="color:{status_color};font-size:18px;">
                            {status_text}
                        </div>
                    </div>""", unsafe_allow_html=True)
                with m3:
                    tables_used = len(set(
                        word for word in sql.lower().split()
                        if word.startswith("dell_")
                    ))
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Tables Queried</div>
                        <div class="metric-value">{tables_used}</div>
                    </div>""", unsafe_allow_html=True)

                # ── Generated SQL ─────────────────────────────────────────
                st.markdown(
                    '<p class="section-header">Generated SQL</p>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="sql-box">{sql}</div>',
                    unsafe_allow_html=True
                )

                # ── Explanation ─────────────────────────────────────────
                if explanation:
                    st.markdown(
                        '<p class="section-header">Explanation</p>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"""
                    <div style='
                        background-color: #1e2130;
                        border-left: 3px solid #8892a4;
                        border-radius: 6px;
                        padding: 14px 16px;
                        color: #cbd5e0;
                        font-size: 14px;
                        line-height: 1.5;
                    '>
                        🔍 {explanation}
                    </div>
                    """, unsafe_allow_html=True)

                # ── Insight ─────────────────────────────────────────
                
                if insight:
                    st.markdown(
                        '<p class="section-header">Insight</p>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"""
                    <div style='
                        background-color: #1a2744;
                        border-left: 3px solid #48bb78;
                        border-radius: 6px;
                        padding: 16px;
                        color: #e2e8f0;
                        font-size: 15px;
                        line-height: 1.6;
                    '>
                        💡 {insight}
                    </div>
                    """, unsafe_allow_html=True)

                # ── Results Table ─────────────────────────────────────────
                if results:
                    st.markdown(
                        '<p class="section-header">Results</p>',
                        unsafe_allow_html=True
                    )
                    st.dataframe(
                        results,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.markdown("""
                    <div style='text-align:center; padding: 32px; color: #8892a4;'>
                        No results found for this query.
                    </div>""", unsafe_allow_html=True)

            # ── Error Responses ───────────────────────────────────────────
            elif response.status_code == 422:
                st.markdown(f"""
                <div class="error-box">
                    ⚠️ Could not generate a valid SQL query for your question.
                    Try rephrasing it more specifically.
                </div>""", unsafe_allow_html=True)

            elif response.status_code == 429:
                st.markdown(f"""
                <div class="error-box">
                    ⏳ Rate limit reached. You can make up to 5 queries every 2 hours.
                    Please try again later.
                </div>""", unsafe_allow_html=True)

            elif response.status_code == 502:
                st.markdown(f"""
                <div class="error-box">
                    🔌 AI service is temporarily unavailable. Please try again in a moment.
                </div>""", unsafe_allow_html=True)

            else:
                    try:
                        detail = response.json().get("detail", "Unknown error")
                    except Exception:
                        detail = f"Unexpected response. Status: {response.status_code}. Body: '{response.text[:200]}'"

                    st.markdown(f"""
                    <div class="error-box">
                        ❌ {detail}
                    </div>""", unsafe_allow_html=True)

        except requests.exceptions.Timeout:
            st.markdown("""
            <div class="error-box">
                ⏱️ Request timed out. The server may be waking up — please try again.
            </div>""", unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.markdown("""
            <div class="error-box">
                🔌 Could not connect to the API. Check your ANALYTICS_API_URL setting.
            </div>""", unsafe_allow_html=True)

elif submit and not query.strip():
    st.warning("Please enter a question first.")

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='text-align: center; padding: 40px 0 16px 0; color: #4a5568; font-size: 12px;'>
    Built with FastAPI · Gemini · PostgreSQL · Streamlit
    <br/>Data is for demonstration purposes only.
</div>""", unsafe_allow_html=True)