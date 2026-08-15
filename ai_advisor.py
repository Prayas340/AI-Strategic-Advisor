"""
ai_advisor.py - Strategic Business Intelligence & Decision Engine
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# Candidate models in order of active availability
MODEL_CANDIDATES = [
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite"
]

SYSTEM_INSTRUCTION = """
You are AI Strategic Advisor, an elite C-level Executive Business Intelligence and Strategy Partner.
Your role is to translate raw business metrics, operational records, and financial data into decisive, high-impact executive guidance.

### Principles:
1. **Executive Gravitas**: Deliver concise, mathematically sound, actionable intelligence. Avoid fluff, filler phrases, and generic truisms.
2. **Data-Grounded**: Every claim, observation, or recommendation must anchor back to the dataset context provided (e.g. specific numbers, percentages, segments, trends).
3. **Structured Outputs**: Use standard executive formatting:
   - 📊 **Key Findings & Data Summary**
   - 🎯 **Strategic Recommendations** (with prioritized impact)
   - ⚠️ **Risk & Sensitivity Analysis**
   - 🚀 **Next Immediate Action Items** (30-60-90 day horizon)
4. **Strategic Frameworks**: Readily leverage BCG Matrix, SWOT, Ansoff Growth Matrix, Unit Economics (LTV:CAC, Payback, Rule of 40), and Sensitivity Stress Tests when relevant.
"""


def get_api_key(custom_key: Optional[str] = None) -> Optional[str]:
    """Retrieve API Key from custom input, environment, or .env."""
    if custom_key and custom_key.strip():
        return custom_key.strip()
    return os.environ.get("GEMINI_API_KEY", "").strip() or None


def get_client(api_key: Optional[str] = None) -> Optional[Any]:
    """Initialize and return the GenAI Client."""
    key = get_api_key(api_key)
    if not key:
        return None
    if not GENAI_AVAILABLE:
        raise ImportError("AI SDK is not installed. Please run `pip install google-genai`.")
    return genai.Client(api_key=key)


def execute_genai_call(client: Any, prompt: str, temperature: float = 0.3) -> str:
    """Execute AI call with resilient fallback across active models."""
    last_err = None
    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=temperature,
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue

    return f"❌ **Error communicating with Strategic AI Engine**: {str(last_err)}"


def generate_executive_brief(dataset_summary: str, api_key: Optional[str] = None, focus_area: Optional[str] = None) -> str:
    """Generate a comprehensive Executive Briefing from the dataset."""
    client = get_client(api_key)
    if not client:
        return "⚠️ **API Key missing**: Please ensure your API key is configured in the `.env` file."

    focus_prompt = f"Pay special attention to the strategic focus area: **{focus_area}**." if focus_area else ""

    prompt = f"""
{dataset_summary}

{focus_prompt}

TASK:
Perform an executive-grade strategic diagnosis on this dataset.
Structure your executive response using the following mandatory sections:

### 📊 1. Key Findings & Data Summary
- Highlight the 3-4 most critical metric trajectories, margins, unit economics, or anomalies.
- Quantify exact changes and dimensional leaders/laggards.

### 🎯 2. Strategic Recommendations
- Detail 3 high-impact strategic initiatives to accelerate growth, optimize margins, or mitigate risks.
- Assign an expected ROI and timeframe (Short / Medium / Long Term) to each.

### ⚠️ 3. Risk & Sensitivity Analysis
- Identify the top vulnerabilities (e.g. churn concentration, CAC inflation, channel over-reliance, margin compression).
- Outline the downside impact if these risks are left unmanaged.

### 🚀 4. Immediate Action Items (Next 30-60-90 Days)
- **Day 1-30**: Immediate quick wins and operational fixes.
- **Day 31-60**: Strategic alignment and resource reallocation.
- **Day 61-90**: Scaled execution and milestone validation.
"""
    return execute_genai_call(client, prompt, temperature=0.3)


def generate_swot_analysis(dataset_summary: str, api_key: Optional[str] = None) -> str:
    """Generate a data-driven SWOT matrix from the dataset context."""
    client = get_client(api_key)
    if not client:
        return "⚠️ **API Key missing**: Please ensure your API key is configured in the `.env` file."

    prompt = f"""
{dataset_summary}

TASK:
Produce an exhaustive, data-grounded **Strategic SWOT Matrix** based strictly on the empirical signals in this dataset.

Format clearly with markdown tables or structured callouts:
1. **💪 Strengths (Internal Core Competencies & Outperformers)**: What products, segments, cohorts, or channels demonstrate high efficiency, margins, or retention?
2. **⚠️ Weaknesses (Internal Gaps & Inefficiencies)**: Where is capital leaking, churn elevated, or margins compressed?
3. **🌟 Opportunities (External Growth & Expansion Vectors)**: What under-leveraged channels, product adjacencies, or customer tiers offer high upside?
4. **🛡️ Threats (Market, Financial & Operational Headwinds)**: What systemic risks, payback delays, or margin erosions could derail the business?

Conclude with a **🎯 Strategic Synthesis: The #1 Move the Leadership Team Should Make**.
"""
    return execute_genai_call(client, prompt, temperature=0.3)


def run_scenario_simulation(dataset_summary: str, scenario_description: str, api_key: Optional[str] = None) -> str:
    """Simulate what-if business scenarios and assess strategic impact."""
    client = get_client(api_key)
    if not client:
        return "⚠️ **API Key missing**: Please ensure your API key is configured in the `.env` file."

    prompt = f"""
{dataset_summary}

SCENARIO TO SIMULATE:
"{scenario_description}"

TASK:
Simulate this executive What-If scenario against the baseline metrics provided in the dataset context.
Deliver a structured simulation memo:

1. **🔮 Projected Impact on Core KPIs**:
   - Revenue / MRR delta
   - Gross & Net Margin impact
   - Customer acquisition & churn trajectory
2. **⚖️ Second-Order & Ripple Effects**:
   - Operational strain, cash flow requirements, competitive responses, or customer sentiment effects.
3. **📊 Probability & Feasibility Rating**:
   - Feasibility: (High / Medium / Low)
   - Downside Risk: (Low / Moderate / Severe)
4. **🛡️ Executive Go / No-Go Decision & Hedging Strategy**:
   - Clear recommendation on whether to pursue this scenario and how to mitigate primary failure modes.
"""
    return execute_genai_call(client, prompt, temperature=0.4)


def generate_decision_matrix(dataset_summary: str, strategic_goal: str, api_key: Optional[str] = None) -> str:
    """Generate an executive decision prioritization matrix."""
    client = get_client(api_key)
    if not client:
        return "⚠️ **API Key missing**: Please ensure your API key is configured in the `.env` file."

    prompt = f"""
{dataset_summary}

STRATEGIC OBJECTIVE:
"{strategic_goal}"

TASK:
Generate an **Executive Decision Prioritization Matrix** proposing 4 distinct strategic initiatives to achieve this objective based on the data.

Provide:
1. **Prioritization Scorecard (Markdown Table)**:
   Columns:
   - `Initiative Name`
   - `Strategic Lever (Revenue / Cost / Retention / Expansion)`
   - `Estimated Impact (1-10)`
   - `Execution Effort (1-10)`
   - `Risk Level (Low / Med / High)`
   - `Expected Payback`
   - `Executive Priority Rank`

2. **Deep-Dive on Rank #1 Initiative**:
   - Why this is the optimal capital/resource allocation.
   - Resource requirements and key milestones.
"""
    return execute_genai_call(client, prompt, temperature=0.3)


def ask_strategic_advisor(
    dataset_summary: str,
    user_query: str,
    chat_history: List[Dict[str, str]],
    api_key: Optional[str] = None
) -> str:
    """Multi-turn strategic conversation with live dataset context."""
    client = get_client(api_key)
    if not client:
        return "⚠️ **API Key missing**: Please ensure your API key is configured in the `.env` file."

    # Format chat history for context
    history_snippets = []
    for msg in chat_history[-6:]:  # Keep recent turns
        role = "User" if msg["role"] == "user" else "Advisor"
        history_snippets.append(f"{role}: {msg['content']}")
    
    history_text = "\n".join(history_snippets) if history_snippets else "No previous conversation."

    prompt = f"""
{dataset_summary}

--- RECENT CONVERSATION HISTORY ---
{history_text}
-----------------------------------

EXECUTIVE QUERY:
"{user_query}"

Provide a crisp, direct, highly strategic answer tailored for a CEO / Board of Directors.
Ground every recommendation in the dataset facts above.
Use markdown tables or bulleted lists wherever they clarify complex tradeoffs.
"""
    return execute_genai_call(client, prompt, temperature=0.4)
