"""
Analyze KuaiRec Dataset Structure

KuaiRec is a recommendation dataset from Kuaishou (Chinese short video platform).
We need to understand if it has A/B test data or if we need to simulate experiments.
"""

import pandas as pd
import os

print("=" * 80)
print("ANALYZING KUAIREC DATASET")
print("=" * 80)

# ============================================================================
# 1. USER FEATURES
# ============================================================================
print("\n" + "=" * 80)
print("1. USER FEATURES")
print("=" * 80)

try:
    df_users = pd.read_csv('Data/user_features_raw.csv', nrows=1000)
    
    print(f"\nShape: {df_users.shape}")
    print(f"\nColumns ({len(df_users.columns)}):")
    for i, col in enumerate(df_users.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nFirst 5 rows:")
    print(df_users.head())
    
    print(f"\nData types:")
    print(df_users.dtypes)
    
    print(f"\nSample statistics:")
    print(df_users.describe())
    
    # Check for potential segment attributes
    print(f"\nPotential segment attributes:")
    categorical_cols = ['gender', 'age_range', 'phone_brand', 'fre_city_level', 'platform']
    for col in categorical_cols:
        if col in df_users.columns:
            print(f"  {col}: {df_users[col].value_counts().head().to_dict()}")
    
except Exception as e:
    print(f"Error loading user features: {e}")

# ============================================================================
# 2. VIDEO CATEGORIES
# ============================================================================
print("\n" + "=" * 80)
print("2. VIDEO CATEGORIES")
print("=" * 80)

try:
    df_videos = pd.read_csv('Data/video_raw_categories_multi.csv', nrows=1000)
    
    print(f"\nShape: {df_videos.shape}")
    print(f"\nColumns: {list(df_videos.columns)}")
    print(f"\nFirst 5 rows:")
    print(df_videos.head())
    
except Exception as e:
    print(f"Error loading video categories: {e}")

# ============================================================================
# 3. CAPTIONS
# ============================================================================
print("\n" + "=" * 80)
print("3. CAPTIONS")
print("=" * 80)

try:
    df_captions = pd.read_csv('Data/kuairec_caption_category.csv', nrows=1000)
    
    print(f"\nShape: {df_captions.shape}")
    print(f"\nColumns: {list(df_captions.columns)}")
    print(f"\nFirst 5 rows:")
    print(df_captions.head())
    
except Exception as e:
    print(f"Error loading captions: {e}")

# ============================================================================
# 4. CHECK FOR INTERACTION DATA
# ============================================================================
print("\n" + "=" * 80)
print("4. LOOKING FOR INTERACTION/BEHAVIOR DATA")
print("=" * 80)

# Check if there are other CSV files in the Data directory
import glob
csv_files = glob.glob('Data/*.csv')
print(f"\nAll CSV files in Data/:")
for f in csv_files:
    file_size = os.path.getsize(f) / (1024 * 1024)  # MB
    print(f"  {os.path.basename(f)}: {file_size:.2f} MB")

# ============================================================================
# ANALYSIS SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)

print("""
KuaiRec Dataset Structure:

1. USER FEATURES (user_features_raw.csv):
   - User demographics and behavior patterns
   - Potential segments: gender, age_range, device, location
   
2. VIDEO CATEGORIES (video_raw_categories_multi.csv):
   - Video metadata and categories
   - Can be used to create content-based features
   
3. CAPTIONS (kuairec_caption_category.csv):
   - Video captions and categories
   - Additional content features

NEXT STEPS:

Option A: If there's interaction data (watch time, clicks, etc.):
   - Look for treatment/control indicators
   - Map to PROXIMA format with actual A/B test data
   
Option B: If no A/B test data (most likely):
   - Simulate A/B tests using recommendation algorithms
   - Create synthetic experiments:
     * Treatment: Personalized recommendations
     * Control: Random/popular recommendations
   - Proxy metrics: Click rate, watch time (first 10 seconds)
   - Long-term: Total watch time, retention

Recommendation: Since KuaiRec is a recommendation dataset, we should:
1. Simulate A/B tests comparing different recommendation strategies
2. Use early engagement (clicks, first 10s watch) as proxy metrics
3. Use long-term engagement (total watch time, return visits) as outcome
""")

print("\n✓ Analysis complete!")

