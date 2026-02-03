"""
Integrate KuaiRec Dataset with PROXIMA

Since KuaiRec doesn't have A/B test data, we'll simulate experiments:
- Treatment: Personalized recommendations (based on user features)
- Control: Random/popular recommendations
- Proxy metrics: Early engagement signals
- Long-term: Total engagement
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import os

print("=" * 80)
print("INTEGRATING KUAIREC DATASET WITH PROXIMA")
print("=" * 80)

# Create output directories
os.makedirs("outputs/kuairec", exist_ok=True)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("\nSTEP 1: Loading KuaiRec data...")

df_users = pd.read_csv('Data/user_features_raw.csv')
print(f"✓ Loaded {len(df_users):,} users")

# ============================================================================
# STEP 2: SIMULATE A/B TESTS
# ============================================================================
print("\nSTEP 2: Simulating A/B test experiments...")

# Create 30 synthetic experiments
np.random.seed(42)
n_experiments = 30

# Assign users to experiments (random assignment)
df_users['exp_id'] = np.random.randint(0, n_experiments, size=len(df_users))

# Random treatment assignment (50/50 split)
df_users['treatment'] = np.random.binomial(1, 0.5, size=len(df_users))

print(f"✓ Created {n_experiments} experiments")
print(f"  Avg users per experiment: {len(df_users) // n_experiments:,}")

# ============================================================================
# STEP 3: SIMULATE ENGAGEMENT METRICS
# ============================================================================
print("\nSTEP 3: Simulating engagement metrics...")

# Base engagement rates (vary by user characteristics)
base_engagement = 0.3  # 30% base engagement

# User characteristics affect engagement
gender_effect = (df_users['gender'] == 'F').astype(float) * 0.05
age_effect = df_users['age_range'].map({
    '12-17': 0.10,
    '18-23': 0.08,
    '24-30': 0.05,
    '31-40': 0.03,
    '50+': 0.01
}).fillna(0.05)

platform_effect = (df_users['platform'] == 'IPHONE').astype(float) * 0.08

# Treatment effect (personalization improves engagement)
treatment_effect = df_users['treatment'] * 0.12

# Combine effects
engagement_prob = base_engagement + gender_effect + age_effect + platform_effect + treatment_effect
engagement_prob = np.clip(engagement_prob, 0, 1)

# Simulate metrics
# Early metrics (proxy - first 10 seconds)
df_users['early_click'] = np.random.binomial(1, engagement_prob * 0.8)
df_users['early_watch_sec'] = df_users['early_click'] * np.random.exponential(5, size=len(df_users))
df_users['early_like'] = df_users['early_click'] * np.random.binomial(1, 0.3, size=len(df_users))

# Long-term metrics (outcome - full session)
long_engagement_prob = engagement_prob * 0.6  # Lower conversion to long-term
df_users['long_watch_min'] = np.random.exponential(2, size=len(df_users)) * long_engagement_prob * 10
df_users['long_retained'] = (df_users['long_watch_min'] > 5).astype(int)  # Retained if watched >5 min

print(f"✓ Simulated engagement metrics")
print(f"  Early click rate: {df_users['early_click'].mean():.2%}")
print(f"  Long-term retention: {df_users['long_retained'].mean():.2%}")

# ============================================================================
# STEP 4: MAP TO PROXIMA FORMAT
# ============================================================================
print("\nSTEP 4: Mapping to PROXIMA format...")

df_proxima = pd.DataFrame({
    'exp_id': df_users['exp_id'],
    'treatment': df_users['treatment'],
    
    # Segments
    'region': df_users['fre_city_level'].fillna('UNKNOWN'),
    'device': df_users['platform'],
    'tenure': df_users['age_range'],
    
    # Proxy metrics (early engagement)
    'early_watch_min': df_users['early_watch_sec'] / 60,  # Convert to minutes
    'early_starts': df_users['early_click'].astype(float),
    'early_ctr': df_users['early_click'].astype(float),
    'rebuffer_rate': 1 - df_users['early_click'].astype(float),  # Inverse of click
    
    # Long-term outcome
    'long_retained': df_users['long_retained']
})

print(f"✓ Created PROXIMA dataframe: {df_proxima.shape}")
print(f"\nFirst few rows:")
print(df_proxima.head())

# Save
df_proxima.to_csv('outputs/kuairec/kuairec_proxima_format.csv', index=False)
print(f"\n✓ Saved to outputs/kuairec/kuairec_proxima_format.csv")

# ============================================================================
# STEP 5: BASIC STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("BASIC STATISTICS")
print("=" * 80)

print(f"\nTreatment distribution:")
print(df_proxima['treatment'].value_counts())

print(f"\nOutcome rates:")
print(f"  Retention rate: {df_proxima['long_retained'].mean():.2%}")
print(f"  Early starts rate: {df_proxima['early_starts'].mean():.2%}")

print(f"\nTreatment effect (simple):")
control = df_proxima[df_proxima['treatment'] == 0]
treatment = df_proxima[df_proxima['treatment'] == 1]

print(f"  Retention: {treatment['long_retained'].mean() - control['long_retained'].mean():.4f}")
print(f"  Early starts: {treatment['early_starts'].mean() - control['early_starts'].mean():.4f}")

# ============================================================================
# STEP 6: RUN PROXIMA ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("RUNNING PROXIMA ANALYSIS")
print("=" * 80)

try:
    from proxima.models.baseline import score_proxies, find_top_fragility_segments
    from proxima.evaluation.decision_sim import compare_decision_strategies
    
    PROXY_METRICS = ['early_watch_min', 'early_starts', 'early_ctr', 'rebuffer_rate']
    
    print("\nScoring proxy metrics...")
    details, proxy_scores = score_proxies(df_proxima)
    
    print("\n" + "=" * 80)
    print("PROXY RELIABILITY SCORES")
    print("=" * 80)
    print(details.to_string(index=False))
    details.to_csv('outputs/kuairec/proxy_scores.csv', index=False)
    
    print("\nDetecting fragile segments...")
    top_proxy = proxy_scores[0].metric
    fragile_segments = find_top_fragility_segments(df_proxima, top_proxy, min_count=100)
    
    print("\n" + "=" * 80)
    print(f"FRAGILE SEGMENTS FOR {top_proxy}")
    print("=" * 80)
    print(fragile_segments.head(10).to_string(index=False))
    fragile_segments.to_csv('outputs/kuairec/fragility_segments.csv', index=False)
    
    print("\nSimulating shipping decisions...")
    decision_results = compare_decision_strategies(df_proxima, PROXY_METRICS)
    
    print("\n" + "=" * 80)
    print("DECISION SIMULATION RESULTS")
    print("=" * 80)
    print(decision_results.to_string(index=False))
    decision_results.to_csv('outputs/kuairec/decision_results.csv', index=False)
    
    print("\n" + "=" * 80)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"""
Results saved to:
  - outputs/kuairec/kuairec_proxima_format.csv ({len(df_proxima):,} rows)
  - outputs/kuairec/proxy_scores.csv
  - outputs/kuairec/fragility_segments.csv
  - outputs/kuairec/decision_results.csv

This is SIMULATED A/B test data from KuaiRec - ready for analysis!
""")
    
except Exception as e:
    print(f"\nError during analysis: {e}")
    import traceback
    traceback.print_exc()

