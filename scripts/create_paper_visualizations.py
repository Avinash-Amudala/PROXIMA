"""
Create publication-quality visualizations for PROXIMA research paper

Generates comprehensive comparison plots across all datasets:
- Synthetic (baseline)
- Criteo (13.9M rows, real A/B tests)
- KuaiRec (7.2K users, simulated A/B tests)
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set publication-quality style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Create output directory
os.makedirs("outputs/paper_figures", exist_ok=True)

print("=" * 80)
print("CREATING PUBLICATION-QUALITY VISUALIZATIONS")
print("=" * 80)

# ============================================================================
# LOAD ALL DATASETS
# ============================================================================
print("\nLoading datasets...")

datasets = {}

# Criteo
if os.path.exists('outputs/criteo/proxy_scores.csv'):
    datasets['Criteo\n(13.9M rows)'] = {
        'proxy_scores': pd.read_csv('outputs/criteo/proxy_scores.csv'),
        'decision_results': pd.read_csv('outputs/criteo/decision_results.csv'),
        'fragility': pd.read_csv('outputs/criteo/fragility_segments.csv')
    }
    print("✓ Loaded Criteo results")

# KuaiRec
if os.path.exists('outputs/kuairec/proxy_scores.csv'):
    datasets['KuaiRec\n(7.2K users)'] = {
        'proxy_scores': pd.read_csv('outputs/kuairec/proxy_scores.csv'),
        'decision_results': pd.read_csv('outputs/kuairec/decision_results.csv'),
        'fragility': pd.read_csv('outputs/kuairec/fragility_segments.csv')
    }
    print("✓ Loaded KuaiRec results")

if not datasets:
    print("ERROR: No datasets found!")
    sys.exit(1)

# ============================================================================
# FIGURE 1: PROXY RELIABILITY COMPARISON
# ============================================================================
print("\nCreating Figure 1: Proxy Reliability Comparison...")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Panel A: Reliability scores
ax = axes[0]
data_for_plot = []
for dataset_name, data in datasets.items():
    df = data['proxy_scores'].copy()
    df['dataset'] = dataset_name
    data_for_plot.append(df)

combined = pd.concat(data_for_plot, ignore_index=True)

# Create grouped bar chart
metrics = combined['metric'].unique()
x = np.arange(len(metrics))
width = 0.35
dataset_names = list(datasets.keys())

for i, dataset_name in enumerate(dataset_names):
    subset = combined[combined['dataset'] == dataset_name]
    subset = subset.set_index('metric').reindex(metrics)
    ax.bar(x + i*width, subset['reliability'], width, label=dataset_name, alpha=0.8)

ax.set_xlabel('Proxy Metric')
ax.set_ylabel('Reliability Score')
ax.set_title('(A) Proxy Reliability Across Datasets')
ax.set_xticks(x + width/2)
ax.set_xticklabels([m.replace('_', '\n') for m in metrics], rotation=0, ha='center')
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 1.0)

# Panel B: Correlation vs Directional Accuracy
ax = axes[1]
for dataset_name, data in datasets.items():
    df = data['proxy_scores']
    ax.scatter(df['effect_corr'], df['directional_accuracy'], 
              s=100, alpha=0.7, label=dataset_name)
    
    # Add metric labels
    for _, row in df.iterrows():
        ax.annotate(row['metric'].replace('_', '\n'), 
                   (row['effect_corr'], row['directional_accuracy']),
                   fontsize=7, alpha=0.6, ha='center')

ax.set_xlabel('Effect Correlation')
ax.set_ylabel('Directional Accuracy')
ax.set_title('(B) Correlation vs Directional Accuracy')
ax.legend()
ax.grid(alpha=0.3)
ax.set_xlim(-1, 1)
ax.set_ylim(0, 1)

plt.tight_layout()
plt.savefig('outputs/paper_figures/figure1_proxy_reliability.png', bbox_inches='tight')
print("✓ Saved: outputs/paper_figures/figure1_proxy_reliability.png")
plt.close()

# ============================================================================
# FIGURE 2: DECISION SIMULATION RESULTS
# ============================================================================
print("\nCreating Figure 2: Decision Simulation Results...")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Panel A: Win Rate Comparison
ax = axes[0]
data_for_plot = []
for dataset_name, data in datasets.items():
    df = data['decision_results'].copy()
    df = df[df['proxy_metric'] != 'Oracle (True Long-term)']  # Exclude oracle
    df['dataset'] = dataset_name
    data_for_plot.append(df)

combined = pd.concat(data_for_plot, ignore_index=True)

# Create grouped bar chart
metrics = combined['proxy_metric'].unique()
x = np.arange(len(metrics))
width = 0.35

for i, dataset_name in enumerate(dataset_names):
    subset = combined[combined['dataset'] == dataset_name]
    subset = subset.set_index('proxy_metric').reindex(metrics)
    ax.bar(x + i*width, subset['win_rate'], width, label=dataset_name, alpha=0.8)

ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Oracle')
ax.set_xlabel('Proxy Metric')
ax.set_ylabel('Win Rate')
ax.set_title('(A) Decision Win Rate by Proxy')
ax.set_xticks(x + width/2)
ax.set_xticklabels([m.replace('_', '\n') for m in metrics], rotation=0, ha='center')
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 1.1)

# Panel B: Error Rates
ax = axes[1]
for dataset_name, data in datasets.items():
    df = data['decision_results']
    df = df[df['proxy_metric'] != 'Oracle (True Long-term)']
    
    # Plot false positive and false negative rates
    x_pos = np.arange(len(df))
    ax.scatter(df['false_positive_rate'], df['false_negative_rate'],
              s=150, alpha=0.7, label=dataset_name)

ax.set_xlabel('False Positive Rate')
ax.set_ylabel('False Negative Rate')
ax.set_title('(B) Error Rate Trade-offs')
ax.legend()
ax.grid(alpha=0.3)
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)

# Add diagonal line (equal error rate)
ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Equal Error')

plt.tight_layout()
plt.savefig('outputs/paper_figures/figure2_decision_simulation.png', bbox_inches='tight')
print("✓ Saved: outputs/paper_figures/figure2_decision_simulation.png")
plt.close()

# ============================================================================
# SUMMARY TABLE
# ============================================================================
print("\nCreating summary table...")

summary_rows = []
for dataset_name, data in datasets.items():
    proxy_scores = data['proxy_scores']
    decision_results = data['decision_results']
    
    # Best proxy
    best_proxy = proxy_scores.iloc[0]
    best_decision = decision_results[decision_results['proxy_metric'] == best_proxy['metric']].iloc[0]
    
    summary_rows.append({
        'Dataset': dataset_name.replace('\n', ' '),
        'Best Proxy': best_proxy['metric'],
        'Reliability': f"{best_proxy['reliability']:.3f}",
        'Correlation': f"{best_proxy['effect_corr']:.3f}",
        'Dir. Accuracy': f"{best_proxy['directional_accuracy']:.3f}",
        'Win Rate': f"{best_decision['win_rate']:.3f}",
        'FP Rate': f"{best_decision['false_positive_rate']:.3f}",
        'FN Rate': f"{best_decision['false_negative_rate']:.3f}"
    })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv('outputs/paper_figures/summary_table.csv', index=False)
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print(summary_df.to_string(index=False))
print("\n✓ Saved: outputs/paper_figures/summary_table.csv")

print("\n" + "=" * 80)
print("✓ ALL VISUALIZATIONS COMPLETE!")
print("=" * 80)
print(f"""
Publication-ready figures saved to outputs/paper_figures/:
  - figure1_proxy_reliability.png
  - figure2_decision_simulation.png
  - summary_table.csv

These are ready for inclusion in your research paper!
""")

