"""
Explore and prepare real datasets for PROXIMA
"""

import pandas as pd
import numpy as np
import gzip
import os

print("=" * 80)
print("EXPLORING REAL DATASETS FOR PROXIMA")
print("=" * 80)

# Create output directory
os.makedirs("Data/processed", exist_ok=True)

# ============================================================================
# 1. CRITEO UPLIFT DATASET
# ============================================================================
print("\n" + "=" * 80)
print("1. CRITEO UPLIFT DATASET")
print("=" * 80)

try:
    # Extract gzip file
    print("Extracting Criteo dataset...")
    with gzip.open('Data/criteo-uplift-v2.1.csv.gz', 'rb') as f_in:
        with open('Data/criteo-uplift-v2.1.csv', 'wb') as f_out:
            f_out.write(f_in.read())
    
    # Load dataset
    print("Loading Criteo dataset...")
    criteo = pd.read_csv('Data/criteo-uplift-v2.1.csv', nrows=100000)  # Load first 100k for exploration
    
    print(f"\nShape: {criteo.shape}")
    print(f"\nColumns: {list(criteo.columns)}")
    print(f"\nFirst few rows:")
    print(criteo.head())
    print(f"\nData types:")
    print(criteo.dtypes)
    print(f"\nMissing values:")
    print(criteo.isnull().sum())
    
    # Check for treatment and outcome columns
    print(f"\nUnique values in key columns:")
    for col in criteo.columns:
        if criteo[col].nunique() < 20:
            print(f"  {col}: {criteo[col].unique()}")
    
except Exception as e:
    print(f"Error loading Criteo dataset: {e}")

# ============================================================================
# 2. KUAIREC DATASET
# ============================================================================
print("\n" + "=" * 80)
print("2. KUAIREC DATASET")
print("=" * 80)

try:
    print("Loading KuaiRec user features...")
    kuairec_users = pd.read_csv('Data/user_features_raw.csv', nrows=10000)
    
    print(f"\nShape: {kuairec_users.shape}")
    print(f"\nColumns: {list(kuairec_users.columns)}")
    print(f"\nFirst few rows:")
    print(kuairec_users.head())
    
    print("\nLoading KuaiRec video categories...")
    kuairec_videos = pd.read_csv('Data/video_raw_categories_multi.csv', nrows=10000)
    
    print(f"\nShape: {kuairec_videos.shape}")
    print(f"\nColumns: {list(kuairec_videos.columns)}")
    print(f"\nFirst few rows:")
    print(kuairec_videos.head())
    
    print("\nLoading KuaiRec captions...")
    kuairec_captions = pd.read_csv('Data/kuairec_caption_category.csv', nrows=10000)
    
    print(f"\nShape: {kuairec_captions.shape}")
    print(f"\nColumns: {list(kuairec_captions.columns)}")
    print(f"\nFirst few rows:")
    print(kuairec_captions.head())
    
except Exception as e:
    print(f"Error loading KuaiRec dataset: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DATASET SUMMARY")
print("=" * 80)

print("""
Available Datasets:
1. Criteo Uplift Dataset - Treatment effect / uplift modeling data
2. KuaiRec Dataset - Recommendation system data

Next Steps:
1. Identify which dataset has A/B test structure (treatment/control)
2. Map columns to PROXIMA format (exp_id, treatment, segments, metrics)
3. Create preprocessing scripts for each dataset
4. Run PROXIMA analysis

The script will now create dataset-specific integration scripts...
""")

print("\n✓ Exploration complete! Check the output above to understand the data structure.")

