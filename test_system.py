"""
test_system.py - End-to-end verification script with UTF-8 encoding safe output
"""
import os
import sys
import data_engine
import ai_advisor

# Ensure stdout uses utf-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("1. VERIFYING SAMPLE DATASETS & DATA ENGINE")
print("=" * 60)

for key, info in data_engine.SAMPLE_DATASETS.items():
    df, name = data_engine.load_dataset(source_key=key)
    profile = data_engine.profile_dataset(df)
    print(f"Dataset: [{name}]")
    print(f"  Shape: {profile['rows']} rows x {profile['cols']} cols")
    print(f"  Identified Date: {profile.get('date_col')}, Revenue: {profile.get('revenue_col')}, Profit: {profile.get('profit_col')}")
    print(f"  KPIs extracted ({len(profile['kpis'])}): {[k['label'] + ': ' + str(k['value']) for k in profile['kpis']]}")
    
    # Test chart creation
    trend = data_engine.build_trend_chart(df, profile)
    breakdown = data_engine.build_breakdown_chart(df, profile)
    matrix = data_engine.build_matrix_chart(df, profile)
    comp = data_engine.build_composition_chart(df, profile)
    print(f"  Visuals: Trend={trend is not None}, Breakdown={breakdown is not None}, Matrix={matrix is not None}, Comp={comp is not None}")

print("\n" + "=" * 60)
print("2. VERIFYING GEMINI 2.0 FLASH LIVE CALL")
print("=" * 60)

df_sample, sample_name = data_engine.load_dataset(source_key="ecommerce")
profile_sample = data_engine.profile_dataset(df_sample)
summary = data_engine.generate_dataset_summary_for_ai(df_sample, profile_sample, sample_name)

print(f"Summary length: {len(summary)} characters")
print("Dispatching test executive brief query to Gemini 2.0 Flash...")

response = ai_advisor.generate_executive_brief(summary)
print("\n--- GEMINI 2.0 RESPONSE SAMPLE ---")
print(response[:800] if response else "NO RESPONSE")
print("...\n" + "=" * 60)
