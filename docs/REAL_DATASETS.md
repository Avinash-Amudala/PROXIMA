# Real Dataset Integration Guide

This document provides guidance on integrating real A/B testing datasets with PROXIMA for research and validation purposes.

## Recommended Public Datasets

### 1. **Criteo A/B Testing Dataset**
- **Source**: Criteo AI Lab
- **URL**: https://ailab.criteo.com/criteo-releases-industry-first-large-scale-dataset-for-ai-based-ab-testing/
- **Description**: Large-scale online advertising A/B test data with treatment assignments and conversion outcomes
- **Size**: ~25M observations
- **Metrics**: Click-through rate (CTR), conversion rate, revenue
- **Segments**: User features, ad features, context features
- **Use Case**: Excellent for testing proxy reliability in advertising/marketing context

**Integration Steps**:
```python
import pandas as pd
from proxima.models.baseline import score_proxies

# Load Criteo data
df = pd.read_csv('criteo_ab_test.csv')

# Map to PROXIMA format
df_proxima = df.rename(columns={
    'treatment_id': 'treatment',
    'experiment_id': 'exp_id',
    'click': 'early_ctr',  # Proxy metric
    'conversion': 'long_retained'  # Long-term outcome
})

# Add segment columns if available
# df_proxima['region'] = ...
# df_proxima['device'] = ...

# Run PROXIMA analysis
details, scores = score_proxies(df_proxima)
```

### 2. **Microsoft News Recommendation Dataset**
- **Source**: Microsoft Research
- **URL**: https://msnews.github.io/
- **Description**: User interactions with news articles, including clicks and dwell time
- **Size**: ~1M users, ~160K articles
- **Metrics**: Click-through rate, dwell time, return visits
- **Segments**: User demographics, device type, time of day
- **Use Case**: Testing proxy metrics for content recommendation systems

### 3. **MovieLens Dataset (for simulated A/B tests)**
- **Source**: GroupLens Research
- **URL**: https://grouplens.org/datasets/movielens/
- **Description**: Movie ratings and user behavior
- **Size**: 25M ratings from 162K users
- **Metrics**: Rating, watch completion, re-watch behavior
- **Use Case**: Can be used to simulate A/B tests for recommendation algorithms

**Simulation Approach**:
```python
# Create synthetic experiments from MovieLens
# Treat different recommendation algorithms as "treatments"
# Use early ratings as proxy, long-term engagement as outcome
```

### 4. **Booking.com Dataset (if available)**
- **Source**: Booking.com (via research partnerships)
- **Description**: Hotel booking experiments
- **Metrics**: Click-through, booking rate, cancellation rate, customer lifetime value
- **Segments**: Geography, device, user tenure
- **Use Case**: E-commerce A/B testing with clear proxy-outcome relationships

### 5. **Kaggle A/B Testing Datasets**
- **URL**: https://www.kaggle.com/datasets?search=ab+test
- **Notable Datasets**:
  - "Mobile Games A/B Testing" - retention and monetization
  - "E-commerce A/B Test Results" - conversion funnels
  - "Marketing A/B Test" - campaign effectiveness

## Data Format Requirements

PROXIMA expects data in the following format:

### Required Columns

| Column | Type | Description |
|--------|------|-------------|
| `exp_id` | int/str | Unique experiment identifier |
| `treatment` | int (0/1) | Treatment assignment (0=control, 1=treatment) |
| `long_retained` | int (0/1) | Long-term outcome (binary) |

### Proxy Metric Columns (at least one required)

| Column | Type | Description |
|--------|------|-------------|
| `early_watch_min` | float | Early engagement metric (e.g., minutes watched) |
| `early_starts` | float | Early activity metric (e.g., sessions started) |
| `early_ctr` | float | Click-through rate (0-1) |
| `rebuffer_rate` | float | Quality metric (0-1) |

### Segment Columns (optional but recommended)

| Column | Type | Description |
|--------|------|-------------|
| `region` | str | Geographic region |
| `device` | str | Device type (Mobile, Desktop, TV, etc.) |
| `tenure` | str | User tenure (New, Existing) |

### Example Data Structure

```python
import pandas as pd

# Example dataset
data = pd.DataFrame({
    'exp_id': [1, 1, 1, 2, 2, 2, ...],
    'treatment': [0, 1, 0, 1, 0, 1, ...],
    'region': ['NA', 'EU', 'NA', 'EU', 'IN', 'NA', ...],
    'device': ['Mobile', 'Desktop', 'TV', 'Mobile', 'Mobile', 'Desktop', ...],
    'tenure': ['New', 'Existing', 'New', 'New', 'Existing', 'Existing', ...],
    'early_ctr': [0.12, 0.15, 0.11, 0.18, 0.09, 0.14, ...],
    'early_watch_min': [45.2, 67.8, 42.1, 71.3, 38.9, 65.4, ...],
    'long_retained': [0, 1, 0, 1, 0, 1, ...]
})
```

## Data Preprocessing Steps

### 1. Load and Inspect
```python
import pandas as pd

df = pd.read_csv('your_dataset.csv')
print(df.head())
print(df.info())
print(df.describe())
```

### 2. Map to PROXIMA Format
```python
# Rename columns to match PROXIMA expectations
df = df.rename(columns={
    'experiment_id': 'exp_id',
    'variant': 'treatment',
    'day_7_retention': 'long_retained',
    'day_1_engagement': 'early_watch_min'
})

# Convert treatment to binary (0/1)
df['treatment'] = (df['treatment'] == 'treatment').astype(int)

# Convert outcome to binary if needed
df['long_retained'] = (df['long_retained'] > 0).astype(int)
```

### 3. Handle Missing Values
```python
# Remove rows with missing critical columns
df = df.dropna(subset=['exp_id', 'treatment', 'long_retained'])

# Impute missing proxy metrics (if appropriate)
df['early_ctr'] = df['early_ctr'].fillna(df['early_ctr'].median())
```

### 4. Filter Experiments
```python
# Keep only experiments with sufficient sample size
exp_counts = df.groupby('exp_id').size()
valid_exps = exp_counts[exp_counts >= 1000].index
df = df[df['exp_id'].isin(valid_exps)]

# Ensure both treatment and control exist
def has_both_arms(group):
    return (0 in group['treatment'].values) and (1 in group['treatment'].values)

valid_exps = df.groupby('exp_id').filter(has_both_arms)['exp_id'].unique()
df = df[df['exp_id'].isin(valid_exps)]
```

### 5. Validate Data
```python
from proxima.generator.simulate import EARLY_METRICS

# Check required columns
required = ['exp_id', 'treatment', 'long_retained']
assert all(col in df.columns for col in required), "Missing required columns"

# Check treatment is binary
assert set(df['treatment'].unique()).issubset({0, 1}), "Treatment must be 0/1"

# Check outcome is binary
assert set(df['long_retained'].unique()).issubset({0, 1}), "Outcome must be 0/1"

print("✓ Data validation passed")
```

## Running PROXIMA on Real Data

```python
from proxima.models.baseline import score_proxies, find_top_fragility_segments
from proxima.evaluation.decision_sim import compare_decision_strategies
from proxima.visualization.plots import plot_all_proxy_correlations

# 1. Score proxies
details, proxy_scores = score_proxies(df)
print("\nProxy Reliability Scores:")
print(details)

# 2. Detect fragility for top proxy
top_proxy = proxy_scores[0].metric
fragile_segments = find_top_fragility_segments(df, top_proxy, min_count=500)
print(f"\nFragile segments for {top_proxy}:")
print(fragile_segments)

# 3. Simulate decisions
decision_results = compare_decision_strategies(df, [p.metric for p in proxy_scores])
print("\nDecision Simulation Results:")
print(decision_results)

# 4. Generate visualizations
plot_all_proxy_correlations(df, output_dir='outputs/figures')
```

## Tips for Research Papers

1. **Compare Multiple Datasets**: Run PROXIMA on 2-3 different datasets to show generalizability
2. **Baseline Comparisons**: Compare PROXIMA's proxy selection to manual/heuristic selection
3. **Ablation Studies**: Test reliability score with different weight combinations
4. **Temporal Validation**: Split data by time, train on early period, validate on later period
5. **Statistical Significance**: Report confidence intervals and p-values for all metrics

## Contact for Dataset Access

If you need help accessing specific datasets or have questions about data integration:
- Email: aa9429@g.rit.edu
- Include: Dataset name, research purpose, institutional affiliation

