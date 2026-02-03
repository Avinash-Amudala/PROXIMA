"""
Generate publication-quality figures for PROXIMA paper.
Run this script to create PNG diagrams for the LaTeX paper.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

# Set style for publication
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.dpi'] = 300

# Create figures directory if not exists
os.makedirs('figures', exist_ok=True)

# =============================================================================
# Figure 1: System Architecture
# =============================================================================
def create_system_architecture():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Colors
    colors = {
        'data': '#E3F2FD',
        'core': '#FFF3E0', 
        'output': '#E8F5E9',
        'api': '#FCE4EC'
    }
    
    # Data Layer
    ax.add_patch(FancyBboxPatch((0.5, 5.5), 2.5, 2, boxstyle="round,pad=0.1", 
                                 facecolor=colors['data'], edgecolor='#1976D2', linewidth=2))
    ax.text(1.75, 6.5, 'Data Layer', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(1.75, 6.0, 'A/B Test Data\nProxy Metrics\nLong-term Outcomes', ha='center', va='center', fontsize=9)
    
    # Core Engine
    ax.add_patch(FancyBboxPatch((3.5, 4), 3, 3.5), boxstyle="round,pad=0.1",
                                 facecolor=colors['core'], edgecolor='#F57C00', linewidth=2))
    ax.text(5, 7, 'PROXIMA Core', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(5, 6.3, '• Composite Scoring', ha='center', va='center', fontsize=9)
    ax.text(5, 5.8, '• Fragility Detection', ha='center', va='center', fontsize=9)
    ax.text(5, 5.3, '• Decision Simulation', ha='center', va='center', fontsize=9)
    ax.text(5, 4.8, '• Statistical Analysis', ha='center', va='center', fontsize=9)
    
    # Output Layer
    ax.add_patch(FancyBboxPatch((7, 5.5), 2.5, 2, boxstyle="round,pad=0.1",
                                 facecolor=colors['output'], edgecolor='#388E3C', linewidth=2))
    ax.text(8.25, 6.5, 'Results', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(8.25, 6.0, 'Reliability Scores\nFragility Reports\nDecision Quality', ha='center', va='center', fontsize=9)
    
    # API Layer
    ax.add_patch(FancyBboxPatch((3.5, 0.5), 3, 2.5, boxstyle="round,pad=0.1",
                                 facecolor=colors['api'], edgecolor='#C2185B', linewidth=2))
    ax.text(5, 2.5, 'API & Dashboard', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(5, 1.8, 'FastAPI Backend\nReact Dashboard\nVisualization Suite', ha='center', va='center', fontsize=9)
    
    # Arrows
    ax.annotate('', xy=(3.4, 6.5), xytext=(3.1, 6.5),
                arrowprops=dict(arrowstyle='->', color='#333', lw=2))
    ax.annotate('', xy=(6.9, 6.5), xytext=(6.6, 6.5),
                arrowprops=dict(arrowstyle='->', color='#333', lw=2))
    ax.annotate('', xy=(5, 3.9), xytext=(5, 3.1),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=2))
    
    plt.title('PROXIMA System Architecture', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('figures/fig1_system_architecture.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: figures/fig1_system_architecture.png")

# =============================================================================
# Figure 2: Results Comparison Bar Chart
# =============================================================================
def create_results_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    
    # Data
    proxies = ['early_starts', 'early_ctr', 'early_watch', 'rebuffer_rate']
    
    # Criteo data
    criteo_rel = [0.799, 0.799, 0.652, 0.348]
    criteo_win = [1.0, 1.0, 1.0, 0.0]
    
    # KuaiRec data
    kuairec_rel = [0.622, 0.622, 0.618, 0.278]
    kuairec_win = [0.967, 0.967, 0.962, 0.0]
    
    x = np.arange(len(proxies))
    width = 0.35
    
    # Criteo plot
    bars1 = axes[0].bar(x - width/2, criteo_rel, width, label='Reliability', color='#1976D2')
    bars2 = axes[0].bar(x + width/2, criteo_win, width, label='Win Rate', color='#388E3C')
    axes[0].set_ylabel('Score')
    axes[0].set_title('Criteo Dataset (13.9M observations)', fontweight='bold')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(proxies, rotation=45, ha='right')
    axes[0].legend()
    axes[0].set_ylim(0, 1.1)
    axes[0].axhline(y=0.7, color='red', linestyle='--', alpha=0.5, label='Threshold')
    
    # KuaiRec plot
    bars3 = axes[1].bar(x - width/2, kuairec_rel, width, label='Reliability', color='#1976D2')
    bars4 = axes[1].bar(x + width/2, kuairec_win, width, label='Win Rate', color='#388E3C')
    axes[1].set_ylabel('Score')
    axes[1].set_title('KuaiRec Dataset (7.2K users)', fontweight='bold')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(proxies, rotation=45, ha='right')
    axes[1].legend()
    axes[1].set_ylim(0, 1.1)
    axes[1].axhline(y=0.7, color='red', linestyle='--', alpha=0.5)
    
    plt.suptitle('Proxy Metric Performance Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('figures/fig2_results_comparison.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: figures/fig2_results_comparison.png")

# =============================================================================
# Figure 3: Composite Score Components
# =============================================================================
def create_composite_score_diagram():
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Pie chart showing weight distribution
    weights = [0.6, 0.2, 0.2]
    labels = ['Correlation\n(60%)', 'Directional\nAccuracy (20%)', 'Fragility\n(20%)']
    colors = ['#1976D2', '#388E3C', '#F57C00']
    explode = (0.05, 0.05, 0.05)
    
    wedges, texts, autotexts = ax.pie(weights, explode=explode, labels=labels, colors=colors,
                                       autopct='%1.0f%%', startangle=90, 
                                       textprops={'fontsize': 11})
    
    # Add formula in center
    ax.text(0, 0, r'$R = 0.6\rho + 0.2DA$' + '\n' + r'$+ 0.2(1-FR)$', 
            ha='center', va='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.title('PROXIMA Composite Reliability Score Components', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('figures/fig3_composite_score.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: figures/fig3_composite_score.png")

if __name__ == '__main__':
    print("Generating PROXIMA paper figures...")
    create_system_architecture()
    create_results_comparison()
    create_composite_score_diagram()
    print("\nAll figures generated successfully!")
    print("Files are in: paper/figures/")

