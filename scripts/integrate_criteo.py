"""
Integrate Criteo Uplift Dataset with PROXIMA

The Criteo dataset has:
- treatment: 0/1 (control/treatment)
- conversion: binary outcome (long-term)
- visit: binary outcome (short-term proxy)
- exposure: binary outcome (very short-term proxy)
- f0-f11: feature columns (can be used as segments)
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from proxima.models.baseline import score_proxies, find_top_fragility_segments
from proxima.evaluation.decision_sim import compare_decision_strategies
from proxima.visualization.plots import (
    plot_all_proxy_correlations,
    plot_reliability_comparison,
    plot_fragility_heatmap,
    plot_decision_simulation_results
)
import os

print("=" * 80)
print("INTEGRATING CRITEO UPLIFT DATASET WITH PROXIMA")
print("=" * 80)

# Create output directories
os.makedirs("outputs/criteo", exist_ok=True)
os.makedirs("outputs/criteo/figures", exist_ok=True)

# ============================================================================
# STEP 1: LOAD AND EXPLORE DATA
# ============================================================================
print("\nSTEP 1: Loading Criteo dataset...")

# Load full dataset (13M rows - this might take a minute)
print("Loading data (this may take 1-2 minutes for 13M rows)...")
df_raw = pd.read_csv('Data/criteo-uplift-v2.1.csv.gz', compression='gzip')

print(f"✓ Loaded {len(df_raw):,} rows")
print(f"  Columns: {list(df_raw.columns)}")
print(f"\nData summary:")
print(df_raw.describe())

# ============================================================================
# STEP 2: CREATE SEGMENTS FROM FEATURES
# ============================================================================
print("\nSTEP 2: Creating segments from features...")

# Discretize continuous features into segments
# We'll use f0, f1, f2 as segment attributes (similar to region, device, tenure)

# Create segments by binning features
df_raw['segment_f0'] = pd.qcut(df_raw['f0'], q=4, labels=['f0_Q1', 'f0_Q2', 'f0_Q3', 'f0_Q4'], duplicates='drop')
df_raw['segment_f1'] = pd.qcut(df_raw['f1'], q=3, labels=['f1_Low', 'f1_Med', 'f1_High'], duplicates='drop')
df_raw['segment_f2'] = pd.qcut(df_raw['f2'], q=3, labels=['f2_Low', 'f2_Med', 'f2_High'], duplicates='drop')

print(f"✓ Created segments:")
print(f"  segment_f0: {df_raw['segment_f0'].value_counts().to_dict()}")
print(f"  segment_f1: {df_raw['segment_f1'].value_counts().to_dict()}")
print(f"  segment_f2: {df_raw['segment_f2'].value_counts().to_dict()}")

# ============================================================================
# STEP 3: CREATE SYNTHETIC EXPERIMENTS
# ============================================================================
print("\nSTEP 3: Creating synthetic experiments...")

# The Criteo dataset is one big experiment. We'll split it into multiple experiments
# by randomly assigning experiment IDs
np.random.seed(42)
n_experiments = 50
df_raw['exp_id'] = np.random.randint(0, n_experiments, size=len(df_raw))

print(f"✓ Created {n_experiments} synthetic experiments")
print(f"  Avg users per experiment: {len(df_raw) / n_experiments:,.0f}")

# ============================================================================
# STEP 4: MAP TO PROXIMA FORMAT
# ============================================================================
print("\nSTEP 4: Mapping to PROXIMA format...")

# Create PROXIMA-compatible dataframe
df_proxima = pd.DataFrame({
    'exp_id': df_raw['exp_id'],
    'treatment': df_raw['treatment'],
    'region': df_raw['segment_f0'].astype(str),  # Map to region
    'device': df_raw['segment_f1'].astype(str),  # Map to device
    'tenure': df_raw['segment_f2'].astype(str),  # Map to tenure
    
    # Proxy metrics (early/short-term)
    'early_visit': df_raw['visit'],        # Short-term proxy
    'early_exposure': df_raw['exposure'],  # Very short-term proxy
    
    # Long-term outcome
    'long_retained': df_raw['conversion']  # Long-term outcome
})

# Add more proxy metrics by creating variations
# (In real scenario, you'd have actual early metrics)
df_proxima['early_ctr'] = df_raw['visit'].astype(float)  # Use visit as CTR proxy
df_proxima['early_watch_min'] = df_raw['exposure'].astype(float) * 10  # Scale exposure

print(f"✓ Created PROXIMA dataframe:")
print(f"  Shape: {df_proxima.shape}")
print(f"  Columns: {list(df_proxima.columns)}")
print(f"\nFirst few rows:")
print(df_proxima.head())

# Save processed data
df_proxima.to_csv('outputs/criteo/criteo_proxima_format.csv', index=False)
print(f"\n✓ Saved to outputs/criteo/criteo_proxima_format.csv")

# ============================================================================
# STEP 5: RUN PROXIMA ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("RUNNING PROXIMA ANALYSIS ON CRITEO DATA")
print("=" * 80)

# Define proxy metrics
PROXY_METRICS = ['early_visit', 'early_exposure', 'early_ctr', 'early_watch_min']

print("\nSTEP 5: Scoring proxy metrics...")
details, proxy_scores = score_proxies(df_proxima)

print("\n" + "=" * 80)
print("PROXY RELIABILITY SCORES")
print("=" * 80)
print(details.to_string(index=False))

# Save results
details.to_csv('outputs/criteo/proxy_scores.csv', index=False)
print(f"\n✓ Saved to outputs/criteo/proxy_scores.csv")

# ============================================================================
# STEP 6: DETECT FRAGILITY
# ============================================================================
print("\nSTEP 6: Detecting fragile segments...")

top_proxy = proxy_scores[0].metric
fragile_segments = find_top_fragility_segments(df_proxima, top_proxy, min_count=1000)

print("\n" + "=" * 80)
print(f"FRAGILE SEGMENTS FOR {top_proxy}")
print("=" * 80)
print(fragile_segments.to_string(index=False))

# Save results
fragile_segments.to_csv('outputs/criteo/fragility_segments.csv', index=False)
print(f"\n✓ Saved to outputs/criteo/fragility_segments.csv")

# ============================================================================
# STEP 7: SIMULATE DECISIONS
# ============================================================================
print("\nSTEP 7: Simulating shipping decisions...")

decision_results = compare_decision_strategies(df_proxima, PROXY_METRICS)

print("\n" + "=" * 80)
print("DECISION SIMULATION RESULTS")
print("=" * 80)
print(decision_results.to_string(index=False))

# Save results
decision_results.to_csv('outputs/criteo/decision_results.csv', index=False)
print(f"\n✓ Saved to outputs/criteo/decision_results.csv")

# ============================================================================
# STEP 8: GENERATE VISUALIZATIONS
# ============================================================================
print("\nSTEP 8: Generating visualizations...")

try:
    # Proxy correlations
    plot_all_proxy_correlations(df_proxima, output_dir='outputs/criteo/figures')
    print("✓ Generated proxy correlation plots")
    
    # Reliability comparison
    plot_reliability_comparison(details, output_path='outputs/criteo/figures/reliability_comparison.png')
    print("✓ Generated reliability comparison")
    
    # Fragility heatmap
    plot_fragility_heatmap(df_proxima, top_proxy, output_path='outputs/criteo/figures/fragility_heatmap.png')
    print("✓ Generated fragility heatmap")
    
    # Decision simulation
    plot_decision_simulation_results(decision_results, output_path='outputs/criteo/figures/decision_simulation.png')
    print("✓ Generated decision simulation plots")
    
except Exception as e:
    print(f"Warning: Some visualizations failed: {e}")
    print("This is OK - the analysis results are still valid")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)

print(f"""
✓ Processed {len(df_proxima):,} users across {n_experiments} experiments
✓ Scored {len(PROXY_METRICS)} proxy metrics
✓ Detected {len(fragile_segments)} fragile segments
✓ Simulated decisions for all proxies

Results saved to:
  - outputs/criteo/criteo_proxima_format.csv
  - outputs/criteo/proxy_scores.csv
  - outputs/criteo/fragility_segments.csv
  - outputs/criteo/decision_results.csv
  - outputs/criteo/figures/*.png

Next steps:
  1. Review the proxy scores to see which metrics are most reliable
  2. Examine fragile segments to understand where proxies fail
  3. Use decision simulation results to quantify the value of each proxy
  4. Include these results in your research paper!
""")

