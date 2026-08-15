"""
app.py - Strategic Business Intelligence & Executive Decision Support Assistant
Powered by Streamlit
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import data_engine
import ai_advisor

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Strategic Advisor | Executive Decision Support",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive CSS Styling
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }

    /* Backgrounds & Main Container */
    .stApp {
        background: radial-gradient(circle at 10% 10%, #0c1017 0%, #080b10 100%);
        color: #f1f5f9;
    }

    /* Top Hero Header */
    .hero-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px 0 rgba(59, 130, 246, 0.1);
        backdrop-filter: blur(12px);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #60a5fa, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 14px;
        font-weight: 400;
        margin-bottom: 0;
    }

    /* Executive Metric Scorecard */
    .metric-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 24px;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }
    .metric-sub {
        font-size: 12px;
        color: #38bdf8;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-ai {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-dataset {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Executive AI Callout Box */
    .ai-response-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 22px 24px;
        margin: 16px 0;
        color: #e2e8f0;
        line-height: 1.65;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f17;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.5);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.2) !important;
        color: #60a5fa !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "executive_brief" not in st.session_state:
    st.session_state.executive_brief = None
if "swot_result" not in st.session_state:
    st.session_state.swot_result = None
if "scenario_result" not in st.session_state:
    st.session_state.scenario_result = None
if "decision_result" not in st.session_state:
    st.session_state.decision_result = None


# ==============================================================================
# SIDEBAR: Dataset Selection & Engine Configuration
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚡ AI Strategic Advisor")
    st.markdown("<span class='badge badge-ai'>● Strategic AI Active</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("📁 Data Source Selection")
    data_source_mode = st.radio(
        "Choose Data Source:",
        ["Built-in Enterprise Datasets", "Upload CSV / Excel File"],
        index=0
    )

    df = None
    dataset_display_name = ""

    if data_source_mode == "Built-in Enterprise Datasets":
        selected_preset = st.selectbox(
            "Select Business Domain:",
            options=list(data_engine.SAMPLE_DATASETS.keys()),
            format_func=lambda k: f"{data_engine.SAMPLE_DATASETS[k]['icon']} {data_engine.SAMPLE_DATASETS[k]['name']}"
        )
        dataset_info = data_engine.SAMPLE_DATASETS[selected_preset]
        st.caption(f"ℹ️ *{dataset_info['description']}*")
        try:
            df, dataset_display_name = data_engine.load_dataset(source_key=selected_preset)
        except Exception as e:
            st.error(f"Error loading preset: {e}")
    else:
        uploaded_file = st.file_uploader(
            "Upload Business Dataset",
            type=["csv", "xlsx", "xls"],
            help="Upload your company's revenue, churn, financial or marketing performance data."
        )
        if uploaded_file is not None:
            try:
                df, dataset_display_name = data_engine.load_dataset(uploaded_file=uploaded_file)
            except Exception as e:
                st.error(f"Error parsing uploaded file: {e}")
        else:
            st.info("Please upload a CSV or Excel file to analyze, or switch to Built-in Datasets above.")

    st.markdown("---")
    st.caption("⚡ Enterprise Strategic Intelligence Engine")


# Ensure dataframe is available
if df is None:
    # Fallback to ecommerce
    df, dataset_display_name = data_engine.load_dataset(source_key="ecommerce")

# Profile active dataset
profile = data_engine.profile_dataset(df)
ai_context_summary = data_engine.generate_dataset_summary_for_ai(df, profile, dataset_display_name)


# ==============================================================================
# MAIN PAGE HERO HEADER
# ==============================================================================
st.markdown(f"""
<div class="hero-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <div class="hero-title">Strategic Executive Decision Support</div>
            <div class="hero-subtitle">Automated data intelligence, C-suite scenario simulation & strategic recommendations powered by Strategic AI</div>
        </div>
        <div>
            <span class="badge badge-dataset">Active Data: {dataset_display_name}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# NAVIGATION TABS
# ==============================================================================
tab_overview, tab_ai_advisor, tab_frameworks, tab_scenarios, tab_explorer = st.tabs([
    "📊 Executive Overview & KPIs",
    "🧠 AI Strategic Advisor (Q&A)",
    "🧭 Strategic Frameworks & SWOT",
    "🔮 What-If Scenario Simulator",
    "📑 Data Explorer & Health"
])


# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW & KPIS
# ------------------------------------------------------------------------------
with tab_overview:
    # Display Scorecard Cards
    kpis = profile.get("kpis", [])
    if kpis:
        cols = st.columns(len(kpis[:4]))
        for i, kpi in enumerate(kpis[:4]):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{kpi['label']}</div>
                    <div class="metric-val">{kpi['value']}</div>
                    <div class="metric-sub">● Real-time aggregate</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Anomaly Banners
    if profile.get("anomalies"):
        for alert in profile["anomalies"]:
            st.warning(alert)

    # Interactive Plotly Visualizations Grid
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        trend_fig = data_engine.build_trend_chart(df, profile)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("No time-series date column detected for trajectory chart.")

    with row1_col2:
        breakdown_fig = data_engine.build_breakdown_chart(df, profile)
        if breakdown_fig:
            st.plotly_chart(breakdown_fig, use_container_width=True)
        else:
            st.info("No categorical dimensions found for segment breakdown.")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        matrix_fig = data_engine.build_matrix_chart(df, profile)
        if matrix_fig:
            st.plotly_chart(matrix_fig, use_container_width=True)
        else:
            st.info("Insufficient numerical metrics for 2x2 efficiency matrix.")

    with row2_col2:
        comp_fig = data_engine.build_composition_chart(df, profile)
        if comp_fig:
            st.plotly_chart(comp_fig, use_container_width=True)
        else:
            st.info("No composition data available.")

    # Executive One-Click Synthesis Action
    st.markdown("---")
    col_btn, col_txt = st.columns([1, 3])
    with col_btn:
        generate_btn = st.button("🚀 Generate Executive Briefing", type="primary", use_container_width=True)
    with col_txt:
        st.caption("Synthesizes Key Findings, Strategic Recommendations, Risk Analysis, and a 30-60-90 Day Roadmap.")

    if generate_btn:
        with st.spinner("Synthesizing executive strategy & recommendations..."):
            st.session_state.executive_brief = ai_advisor.generate_executive_brief(
                ai_context_summary
            )

    if st.session_state.executive_brief:
        st.markdown("<div class='ai-response-box'>", unsafe_allow_html=True)
        st.markdown(st.session_state.executive_brief)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "📥 Download Executive Memo (Markdown)",
            data=st.session_state.executive_brief,
            file_name=f"executive_briefing_{dataset_display_name.replace(' ', '_').lower()}.md",
            mime="text/markdown"
        )


# ------------------------------------------------------------------------------
# TAB 2: AI STRATEGIC ADVISOR (MULTI-TURN Q&A)
# ------------------------------------------------------------------------------
with tab_ai_advisor:
    st.subheader("💬 Ask Your Strategic C-Suite Advisor")
    st.caption("Interact with your Strategic Advisor equipped with complete memory of your active dataset, trends, and financial indicators.")

    # Prompt Pills for Quick Strategic Queries
    st.markdown("**Strategic Preset Inquiries:**")
    pill_cols = st.columns(4)
    preset_query = None
    if pill_cols[0].button("💡 Where are we leaking revenue/margin?", use_container_width=True):
        preset_query = "Where are our primary revenue or margin leakages in this dataset, and what is the fastest path to rectify them?"
    if pill_cols[1].button("🎯 How do we improve CAC/LTV?", use_container_width=True):
        preset_query = "Analyze our acquisition efficiency, CAC to LTV dynamics, and provide 3 concrete levers to optimize unit economics."
    if pill_cols[2].button("⚡ Channel/Segment Expansion", use_container_width=True):
        preset_query = "Which customer segments or channels present the highest ROI expansion opportunity with lowest execution risk?"
    if pill_cols[3].button("🛡️ 12-Month Downside Exposure", use_container_width=True):
        preset_query = "Audit our critical vulnerabilities and sensitivity to market shifts over the next 12 months based on this data."

    # Render previous messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    # Handle input (from preset or user chat input)
    user_input = st.chat_input("Ask any strategic business question about your data...")
    query_to_process = preset_query if preset_query else user_input

    if query_to_process:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": query_to_process})
        with st.chat_message("user"):
            st.markdown(query_to_process)

        # Generate AI response
        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Analyzing dataset context & formulating strategic guidance..."):
                response_text = ai_advisor.ask_strategic_advisor(
                    dataset_summary=ai_context_summary,
                    user_query=query_to_process,
                    chat_history=st.session_state.chat_history
                )
                st.markdown(response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})

    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("🧹 Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


# ------------------------------------------------------------------------------
# TAB 3: STRATEGIC FRAMEWORKS & SWOT
# ------------------------------------------------------------------------------
with tab_frameworks:
    st.subheader("🧭 Strategic Analysis Frameworks")
    st.caption("Apply proven executive methodologies (SWOT, Decision Prioritization Matrix) grounded directly in your dataset.")

    framework_sub1, framework_sub2 = st.tabs(["📋 Data-Grounded SWOT Analysis", "⚖️ Executive Decision Matrix"])

    with framework_sub1:
        st.markdown("Generate a 4-quadrant SWOT matrix directly backed by empirical evidence in your dataset.")
        if st.button("🔍 Generate Comprehensive SWOT Matrix", type="primary"):
            with st.spinner("Compiling empirical SWOT matrix..."):
                st.session_state.swot_result = ai_advisor.generate_swot_analysis(
                    dataset_summary=ai_context_summary
                )

        if st.session_state.swot_result:
            st.markdown("<div class='ai-response-box'>", unsafe_allow_html=True)
            st.markdown(st.session_state.swot_result)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Export SWOT Analysis",
                data=st.session_state.swot_result,
                file_name="swot_analysis.md",
                mime="text/markdown"
            )

    with framework_sub2:
        st.markdown("Prioritize strategic initiatives against a specific executive goal.")
        strategic_objective = st.text_input(
            "Enter Primary Strategic Objective:",
            value="Double operating margins while sustaining >20% annual top-line growth",
            help="Define the executive target for the decision matrix evaluation."
        )

        if st.button("📊 Formulate Decision Matrix", type="primary"):
            with st.spinner("Synthesizing initiative prioritization scorecard..."):
                st.session_state.decision_result = ai_advisor.generate_decision_matrix(
                    dataset_summary=ai_context_summary,
                    strategic_goal=strategic_objective
                )

        if st.session_state.decision_result:
            st.markdown("<div class='ai-response-box'>", unsafe_allow_html=True)
            st.markdown(st.session_state.decision_result)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Export Decision Matrix",
                data=st.session_state.decision_result,
                file_name="executive_decision_matrix.md",
                mime="text/markdown"
            )


# ------------------------------------------------------------------------------
# TAB 4: WHAT-IF SCENARIO SIMULATOR
# ------------------------------------------------------------------------------
with tab_scenarios:
    st.subheader("🔮 Executive What-If Scenario Simulator")
    st.caption("Stress-test strategic decisions, pricing shifts, cost reallocations, and macroeconomic shocks before execution.")

    scenario_template = st.selectbox(
        "Choose a Preset Scenario or Write Your Own:",
        [
            "Custom Scenario (Enter Below)",
            "Price Increase: Increase product pricing by 12% with an estimated 3% customer dropoff",
            "Marketing Shift: Reallocate 35% of ad budget to organic inbound SEO and email lifecycle",
            "Margin Expansion: Renegotiate COGS down by 8% and reduce customer churn by 1.5%",
            "Macro Headwind: Demand contracts by 15% across all regions over the next 2 quarters"
        ]
    )

    default_scenario_text = "" if scenario_template.startswith("Custom") else scenario_template
    custom_scenario_input = st.text_area(
        "Describe Scenario Details & Parametric Changes:",
        value=default_scenario_text,
        height=100,
        placeholder="e.g., We plan to expand into the European Enterprise segment, doubling CAC to $3,000 while increasing ARPU by 50%..."
    )

    if st.button("⚡ Run Scenario Simulation", type="primary"):
        if not custom_scenario_input.strip():
            st.warning("Please provide scenario details to simulate.")
        else:
            with st.spinner("Simulating second-order financial & operational impacts..."):
                st.session_state.scenario_result = ai_advisor.run_scenario_simulation(
                    dataset_summary=ai_context_summary,
                    scenario_description=custom_scenario_input
                )

    if st.session_state.scenario_result:
        st.markdown("<div class='ai-response-box'>", unsafe_allow_html=True)
        st.markdown(st.session_state.scenario_result)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "📥 Export Simulation Memo",
            data=st.session_state.scenario_result,
            file_name="scenario_simulation_memo.md",
            mime="text/markdown"
        )


# ------------------------------------------------------------------------------
# TAB 5: DATA EXPLORER & HEALTH
# ------------------------------------------------------------------------------
with tab_explorer:
    st.subheader("📑 Dataset Inspection & Structural Health")
    st.caption("Examine raw data records, statistical summaries, missingness, and column definitions.")

    exp_col1, exp_col2, exp_col3 = st.columns(3)
    exp_col1.metric("Total Records", f"{profile['rows']:,}")
    exp_col2.metric("Total Columns", f"{profile['cols']:,}")
    exp_col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")

    st.markdown("### Raw Data Preview")
    st.dataframe(df, use_container_width=True, height=350)

    st.markdown("### Numerical Summary Statistics")
    st.dataframe(df.describe().round(2), use_container_width=True)

    st.markdown("### Column Data Types & Missing Breakdown")
    health_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Non-Null Count": df.notnull().sum(),
        "Null Count": df.isnull().sum(),
        "Unique Values": df.nunique()
    })
    st.dataframe(health_df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Cleaned Dataset (CSV)",
        data=csv_data,
        file_name=f"export_{dataset_display_name.replace(' ', '_').lower()}.csv",
        mime="text/csv"
    )
