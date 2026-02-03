"""
Quick check of dataset structure without heavy dependencies
"""

import gzip
import csv

print("=" * 80)
print("QUICK DATASET CHECK")
print("=" * 80)

# Check Criteo dataset
print("\n1. CRITEO UPLIFT DATASET")
print("-" * 80)

try:
    with gzip.open('Data/criteo-uplift-v2.1.csv.gz', 'rt') as f:
        reader = csv.reader(f)
        header = next(reader)
        print(f"Columns ({len(header)}): {header}")
        
        # Read first few rows
        print("\nFirst 5 rows:")
        for i, row in enumerate(reader):
            if i >= 5:
                break
            print(f"Row {i+1}: {row[:10]}...")  # First 10 columns
        
except Exception as e:
    print(f"Error: {e}")

# Check KuaiRec files
print("\n2. KUAIREC USER FEATURES")
print("-" * 80)

try:
    with open('Data/user_features_raw.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        print(f"Columns ({len(header)}): {header}")
        
        print("\nFirst 3 rows:")
        for i, row in enumerate(reader):
            if i >= 3:
                break
            print(f"Row {i+1}: {row}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n3. KUAIREC VIDEO CATEGORIES")
print("-" * 80)

try:
    with open('Data/video_raw_categories_multi.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        print(f"Columns ({len(header)}): {header}")
        
        print("\nFirst 3 rows:")
        for i, row in enumerate(reader):
            if i >= 3:
                break
            print(f"Row {i+1}: {row}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)
print("""
Based on the column names above, we need to identify:
1. Treatment/Control indicator (treatment, variant, group, etc.)
2. Outcome metrics (conversion, click, retention, etc.)
3. Segment attributes (age, gender, device, region, etc.)
4. Experiment ID (if multiple experiments)

The Criteo Uplift dataset is specifically designed for uplift modeling,
so it should have treatment and outcome columns.
""")

