"""
data_engine.py - Automated Executive Data Profiling, KPI Extraction, and Visualizations
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional, Tuple

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")

SAMPLE_DATASETS = {
    "ecommerce": {
        "name": "E-Commerce Revenue & Margin Trends",
        "file": os.path.join(DATASETS_DIR, "ecommerce_monthly_revenue.csv"),
        "description": "Multi-region monthly sales, gross/net margins, customer acquisition, and repeat rates.",
        "icon": "🛒"
    },
    "saas": {
        "name": "SaaS Churn, LTV & MRR Cohorts",
        "file": os.path.join(DATASETS_DIR, "saas_churn_and_ltv.csv"),
        "description": "Tiered SaaS performance, net retention (NRR), churn rate, ARPU, and LTV:CAC ratios.",
        "icon": "📈"
    },
    "marketing": {
        "name": "Omnichannel Marketing ROI & Attribution",
        "file": os.path.join(DATASETS_DIR, "marketing_campaign_roi.csv"),
        "description": "Multi-channel advertising spend, conversions, ROAS, CPA, and payback periods.",
        "icon": "🎯"
    },
    "financial": {
        "name": "Executive P&L & Cash Flow Performance",
        "file": os.path.join(DATASETS_DIR, "financial_pnl_quarterly.csv"),
        "description": "Multi-quarter corporate P&L statement, OPEX breakdown, EBITDA margins, and FCF.",
        "icon": "💼"
    }
}

# Executive Color Palette
EXECUTIVE_THEME = {
    "bg": "#0e1117",
    "card_bg": "#1e232d",
    "primary": "#3b82f6",     # Vibrant Blue
    "secondary": "#10b981",   # Emerald Green
    "accent": "#f59e0b",      # Amber Gold
    "danger": "#ef4444",      # Rose Red
    "purple": "#8b5cf6",      # Violet
    "cyan": "#06b6d4",        # Teal Cyan
    "text": "#f3f4f6",
    "grid": "rgba(255, 255, 255, 0.08)",
    "colors": ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#06b6d4", "#ec4899", "#14b8a6", "#f97316"]
}


def load_dataset(source_key: Optional[str] = None, uploaded_file = None) -> Tuple[pd.DataFrame, str]:
    """Load dataframe from uploaded file or preset dataset."""
    if uploaded_file is not None:
        filename = uploaded_file.name
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel.")
        dataset_name = f"Uploaded: {filename}"
        return df, dataset_name

    if source_key in SAMPLE_DATASETS:
        dataset_info = SAMPLE_DATASETS[source_key]
        filepath = dataset_info["file"]
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            return df, dataset_info["name"]
        else:
            raise FileNotFoundError(f"Sample dataset not found at {filepath}")

    # Default fallback to ecommerce
    default_info = SAMPLE_DATASETS["ecommerce"]
    df = pd.read_csv(default_info["file"])
    return df, default_info["name"]


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform automated executive profiling on dataframe."""
    df_clean = df.copy()
    
    # Identify column types
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df_clean.select_dtypes(include=["object", "category"]).columns.tolist()
    
    # Identify potential time/date column
    date_col = None
    for col in df_clean.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ["month", "quarter", "date", "year", "time", "period", "cohort"]):
            date_col = col
            break

    # Prioritize key business metrics
    revenue_col = None
    profit_col = None
    cost_col = None
    margin_col = None
    churn_col = None
    roas_col = None

    for col in numeric_cols:
        col_l = col.lower()
        if not revenue_col and any(k in col_l for k in ["revenue", "mrr", "sales", "gross_revenue"]):
            revenue_col = col
        elif not profit_col and any(k in col_l for k in ["net_profit", "gross_profit", "ebitda", "operating_income", "profit"]):
            profit_col = col
        elif not cost_col and any(k in col_l for k in ["cogs", "spend", "cost", "opex", "cac"]):
            cost_col = col
        elif not margin_col and any(k in col_l for k in ["margin", "retention", "rate_pct"]):
            margin_col = col
        elif not churn_col and any(k in col_l for k in ["churn", "attrition"]):
            churn_col = col
        elif not roas_col and any(k in col_l for k in ["roas", "ltv_cac", "ratio", "payback"]):
            roas_col = col

    # Summary Statistics
    summary_stats = df_clean[numeric_cols].describe().round(2).to_dict() if numeric_cols else {}

    # Key Aggregates
    kpis = []
    
    if revenue_col:
        total_rev = df_clean[revenue_col].sum()
        avg_rev = df_clean[revenue_col].mean()
        kpis.append({
            "label": f"Total {revenue_col.replace('_', ' ')}",
            "value": f"${total_rev:,.0f}" if total_rev > 1000 else f"{total_rev:,.2f}",
            "raw": total_rev,
            "col": revenue_col,
            "type": "currency"
        })

    if profit_col:
        total_profit = df_clean[profit_col].sum()
        kpis.append({
            "label": f"Total {profit_col.replace('_', ' ')}",
            "value": f"${total_profit:,.0f}" if abs(total_profit) > 1000 else f"{total_profit:,.2f}",
            "raw": total_profit,
            "col": profit_col,
            "type": "currency"
        })

    if margin_col:
        avg_margin = df_clean[margin_col].mean()
        kpis.append({
            "label": f"Avg {margin_col.replace('_', ' ')}",
            "value": f"{avg_margin:.1f}%",
            "raw": avg_margin,
            "col": margin_col,
            "type": "percentage"
        })

    if roas_col:
        avg_roas = df_clean[roas_col].mean()
        kpis.append({
            "label": f"Avg {roas_col.replace('_', ' ')}",
            "value": f"{avg_roas:.2f}x",
            "raw": avg_roas,
            "col": roas_col,
            "type": "ratio"
        })
    elif churn_col:
        avg_churn = df_clean[churn_col].mean()
        kpis.append({
            "label": f"Avg {churn_col.replace('_', ' ')}",
            "value": f"{avg_churn:.2f}%",
            "raw": avg_churn,
            "col": churn_col,
            "type": "percentage"
        })

    # If fewer than 4 KPIs, fill with top numeric columns
    for col in numeric_cols:
        if len(kpis) >= 4:
            break
        if not any(k["col"] == col for k in kpis):
            avg_val = df_clean[col].mean()
            kpis.append({
                "label": f"Avg {col.replace('_', ' ')}",
                "value": f"{avg_val:,.1f}",
                "raw": avg_val,
                "col": col,
                "type": "number"
            })

    # Growth & Anomaly Analysis
    anomalies = []
    growth_rate = None
    if date_col and revenue_col:
        # Group by date if multiple entries exist
        time_series = df_clean.groupby(date_col)[revenue_col].sum()
        if len(time_series) >= 2:
            first_val = time_series.iloc[0]
            last_val = time_series.iloc[-1]
            if first_val > 0:
                growth_rate = ((last_val - first_val) / first_val) * 100

    # Detect negative values or high variances
    for col in numeric_cols:
        if (df_clean[col] < 0).any():
            neg_count = (df_clean[col] < 0).sum()
            anomalies.append(f"⚠️ Column `{col}` contains {neg_count} negative entries (potential operating deficit/loss).")

    return {
        "rows": len(df_clean),
        "cols": len(df_clean.columns),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "date_col": date_col,
        "revenue_col": revenue_col,
        "profit_col": profit_col,
        "cost_col": cost_col,
        "margin_col": margin_col,
        "kpis": kpis,
        "growth_rate": growth_rate,
        "anomalies": anomalies,
        "summary_stats": summary_stats
    }


def create_theme_layout(fig: go.Figure, title: str) -> go.Figure:
    """Apply modern executive styling to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=15, color="#f8fafc", family="Inter, system-ui, sans-serif"),
            x=0.02,
            y=0.95
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.65)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font=dict(family="Inter, system-ui, sans-serif", color="#94a3b8", size=11),
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="#cbd5e1")
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.07)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color="#94a3b8", size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.07)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color="#94a3b8", size=10)
        ),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=12,
            font_family="Inter, system-ui, sans-serif"
        )
    )
    return fig


def build_trend_chart(df: pd.DataFrame, profile: Dict[str, Any]) -> Optional[go.Figure]:
    """Build time series executive trend chart."""
    date_col = profile.get("date_col")
    revenue_col = profile.get("revenue_col") or (profile["numeric_cols"][0] if profile["numeric_cols"] else None)

    if not date_col or not revenue_col:
        return None

    # Group by date column
    cat_col = profile["categorical_cols"][0] if profile["categorical_cols"] else None
    
    if cat_col and df[cat_col].nunique() <= 5:
        # Segmented time series
        grouped = df.groupby([date_col, cat_col])[revenue_col].sum().reset_index()
        fig = px.line(
            grouped,
            x=date_col,
            y=revenue_col,
            color=cat_col,
            markers=True,
            color_discrete_sequence=EXECUTIVE_THEME["colors"]
        )
        fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
    else:
        grouped = df.groupby(date_col)[revenue_col].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=grouped[date_col],
                y=grouped[revenue_col],
                mode="lines+markers",
                name=revenue_col.replace("_", " "),
                line=dict(color="#3b82f6", width=3),
                marker=dict(size=7, color="#60a5fa"),
                fill="tozeroy",
                fillcolor="rgba(59, 130, 246, 0.12)"
            )
        )

    title = f"{revenue_col.replace('_', ' ').title()} Trajectory Over Time"
    return create_theme_layout(fig, title)


def build_breakdown_chart(df: pd.DataFrame, profile: Dict[str, Any]) -> Optional[go.Figure]:
    """Build categorical breakdown chart (horizontal bar or donut)."""
    cat_cols = profile.get("categorical_cols", [])
    num_col = profile.get("revenue_col") or (profile["numeric_cols"][0] if profile["numeric_cols"] else None)

    if not cat_cols or not num_col:
        return None

    cat_col = cat_cols[0]
    grouped = df.groupby(cat_col)[num_col].sum().reset_index().sort_values(by=num_col, ascending=True)

    if len(grouped) <= 6:
        # Donut Chart for small categories
        fig = px.pie(
            grouped,
            names=cat_col,
            values=num_col,
            hole=0.55,
            color_discrete_sequence=EXECUTIVE_THEME["colors"]
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#0f172a", width=2))
        )
        title = f"{num_col.replace('_', ' ').title()} Contribution by {cat_col.replace('_', ' ').title()}"
    else:
        # Top 10 Horizontal Bar
        top_grouped = grouped.tail(10)
        fig = px.bar(
            top_grouped,
            x=num_col,
            y=cat_col,
            orientation="h",
            color=num_col,
            color_continuous_scale="Blues"
        )
        fig.update_coloraxes(showscale=False)
        title = f"Top {cat_col.replace('_', ' ').title()} by {num_col.replace('_', ' ').title()}"

    return create_theme_layout(fig, title)


def build_matrix_chart(df: pd.DataFrame, profile: Dict[str, Any]) -> Optional[go.Figure]:
    """Build 2x2 Strategic Scatter Matrix (e.g. CAC vs LTV or Spend vs Revenue)."""
    numeric_cols = profile.get("numeric_cols", [])
    if len(numeric_cols) < 2:
        return None

    # Try to pick meaningful pairs
    x_col = profile.get("cost_col") or numeric_cols[0]
    y_col = profile.get("revenue_col") or profile.get("profit_col") or numeric_cols[1]
    
    if x_col == y_col and len(numeric_cols) > 2:
        y_col = numeric_cols[2]

    cat_col = profile["categorical_cols"][0] if profile["categorical_cols"] else None
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=cat_col if cat_col else None,
        hover_data=df.columns.tolist()[:5],
        color_discrete_sequence=EXECUTIVE_THEME["colors"],
        size_max=18
    )
    fig.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=1, color="white")))

    # Add quadrant benchmark lines (medians)
    x_mid = df[x_col].median()
    y_mid = df[y_col].median()
    
    fig.add_vline(x=x_mid, line_dash="dash", line_color="rgba(255,255,255,0.2)", annotation_text="Median Benchmark")
    fig.add_hline(y=y_mid, line_dash="dash", line_color="rgba(255,255,255,0.2)")

    title = f"Efficiency Matrix: {x_col.replace('_', ' ').title()} vs {y_col.replace('_', ' ').title()}"
    return create_theme_layout(fig, title)


def build_composition_chart(df: pd.DataFrame, profile: Dict[str, Any]) -> Optional[go.Figure]:
    """Build multi-metric composition or OPEX/Revenue distribution bar."""
    numeric_cols = profile.get("numeric_cols", [])
    date_col = profile.get("date_col")

    if not date_col or len(numeric_cols) < 2:
        # Fallback to correlation heatmap
        if len(numeric_cols) >= 3:
            corr = df[numeric_cols[:7]].corr().round(2)
            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1
            )
            return create_theme_layout(fig, "Key Metrics Correlation Heatmap")
        return None

    # Pick top 2-3 numeric metrics
    metrics_to_plot = numeric_cols[:3]
    grouped = df.groupby(date_col)[metrics_to_plot].sum().reset_index()

    fig = go.Figure()
    for idx, metric in enumerate(metrics_to_plot):
        fig.add_trace(
            go.Bar(
                name=metric.replace("_", " ").title(),
                x=grouped[date_col],
                y=grouped[metric],
                marker_color=EXECUTIVE_THEME["colors"][idx % len(EXECUTIVE_THEME["colors"])]
            )
        )

    fig.update_layout(barmode="group")
    title = f"Multi-Metric Comparative Dynamics across {date_col.replace('_', ' ').title()}"
    return create_theme_layout(fig, title)


def generate_dataset_summary_for_ai(df: pd.DataFrame, profile: Dict[str, Any], dataset_name: str) -> str:
    """Generate dense structured executive summary string for Gemini LLM context."""
    kpi_lines = [f"- {kpi['label']}: {kpi['value']}" for kpi in profile.get("kpis", [])]
    kpis_text = "\n".join(kpi_lines) if kpi_lines else "None detected"

    anomalies_text = "\n".join(profile.get("anomalies", [])) if profile.get("anomalies") else "No immediate statistical anomalies detected."
    growth_str = f"{profile['growth_rate']:+.1f}% across tracked periods" if profile.get("growth_rate") is not None else "N/A"

    # Category summaries
    cat_summaries = []
    for cat in profile.get("categorical_cols", [])[:3]:
        counts = df[cat].value_counts().head(5).to_dict()
        cat_summaries.append(f"- **{cat} Breakdown**: {counts}")
    categories_text = "\n".join(cat_summaries) if cat_summaries else "None"

    # Statistical describe sample in markdown table
    num_cols_sample = profile.get("numeric_cols", [])[:6]
    stats_md = df[num_cols_sample].describe().round(2).to_markdown() if num_cols_sample else "No numeric columns"

    # Top 5 records preview
    preview_md = df.head(5).to_markdown(index=False)

    summary = f"""
=== EXECUTIVE DATASET CONTEXT ===
- **Dataset Name**: {dataset_name}
- **Total Volume**: {profile['rows']} rows, {profile['cols']} columns
- **Overall Trajectory / Growth**: {growth_str}
- **Identified Dimensions**: {', '.join(profile.get('categorical_cols', [])) or 'None'}
- **Identified Date/Time Dimension**: {profile.get('date_col') or 'None'}

### Core Executive KPIs:
{kpis_text}

### Dimensional Distributions:
{categories_text}

### Statistical Metrics Summary:
{stats_md}

### Data Health & Risk Indicators:
{anomalies_text}

### Sample Data Head (First 5 Rows):
{preview_md}
================================
"""
    return summary
