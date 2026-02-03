"""
Publication-Quality Visualization Utilities

Creates plots for:
- Proxy-long-term effect correlation
- Fragility heatmaps
- Decision simulation results
- Reliability comparisons
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional, Tuple, Dict
from pathlib import Path

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9


def plot_proxy_correlation(
    df: pd.DataFrame,
    proxy_metric: str,
    long_metric: str = "long_retained",
    save_path: Optional[Path] = None,
    show: bool = True
) -> plt.Figure:
    """
    Scatter plot of proxy effect vs long-term effect across experiments.
    
    Args:
        df: DataFrame with experiment data
        proxy_metric: Name of proxy metric
        long_metric: Name of long-term metric
        save_path: Optional path to save figure
        show: Whether to display the plot
    
    Returns:
        matplotlib Figure object
    """
    from proxima.models.baseline import compute_diff_in_means_effect
    
    # Compute effects
    long_eff = compute_diff_in_means_effect(df, long_metric)
    proxy_eff = compute_diff_in_means_effect(df, proxy_metric)
    
    effects = long_eff.merge(proxy_eff, on="exp_id")
    
    # Create plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Scatter plot
    ax.scatter(
        effects[f"delta_{proxy_metric}"],
        effects[f"delta_{long_metric}"],
        alpha=0.6,
        s=80,
        edgecolors='black',
        linewidths=0.5
    )
    
    # Add regression line
    z = np.polyfit(effects[f"delta_{proxy_metric}"], effects[f"delta_{long_metric}"], 1)
    p = np.poly1d(z)
    x_line = np.linspace(effects[f"delta_{proxy_metric}"].min(), 
                         effects[f"delta_{proxy_metric}"].max(), 100)
    ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label='Linear fit')
    
    # Add diagonal reference line (perfect correlation)
    lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),
        np.max([ax.get_xlim(), ax.get_ylim()]),
    ]
    ax.plot(lims, lims, 'k-', alpha=0.3, zorder=0, linewidth=1, label='Perfect correlation')
    
    # Compute correlation
    corr = effects[f"delta_{proxy_metric}"].corr(effects[f"delta_{long_metric}"])
    
    # Labels and title
    ax.set_xlabel(f'Proxy Effect: {proxy_metric}', fontweight='bold')
    ax.set_ylabel(f'Long-term Effect: {long_metric}', fontweight='bold')
    ax.set_title(f'Proxy-Long-term Correlation (r={corr:.3f})', fontweight='bold', pad=15)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add zero lines
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig


def plot_reliability_comparison(
    proxy_scores_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    show: bool = True
) -> plt.Figure:
    """
    Bar chart comparing reliability scores across proxy metrics.
    
    Args:
        proxy_scores_df: DataFrame from score_proxies() with reliability metrics
        save_path: Optional path to save figure
        show: Whether to display the plot
    
    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sort by reliability
    df_sorted = proxy_scores_df.sort_values('reliability', ascending=True)
    
    # Create horizontal bar chart
    y_pos = np.arange(len(df_sorted))
    bars = ax.barh(y_pos, df_sorted['reliability'], alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Color bars by reliability score
    colors = plt.cm.RdYlGn(df_sorted['reliability'])
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_sorted['metric'])
    ax.set_xlabel('Reliability Score', fontweight='bold')
    ax.set_title('Proxy Metric Reliability Comparison', fontweight='bold', pad=15)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.3, axis='x', linestyle='--')
    
    # Add value labels
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        ax.text(row['reliability'] + 0.02, i, f"{row['reliability']:.3f}", 
                va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig


def plot_fragility_heatmap(
    df: pd.DataFrame,
    proxy_metric: str,
    segment_cols: List[str] = ["region", "device"],
    save_path: Optional[Path] = None,
    show: bool = True
) -> plt.Figure:
    """
    Heatmap showing fragility (sign flip rate) across segments.
    
    Args:
        df: DataFrame with experiment data
        proxy_metric: Name of proxy metric to analyze
        segment_cols: Two segment columns for heatmap axes
        save_path: Optional path to save figure
        show: Whether to display the plot
    
    Returns:
        matplotlib Figure object
    """
    from proxima.models.baseline import (
        compute_diff_in_means_effect,
        compute_segment_effects
    )
    
    if len(segment_cols) != 2:
        raise ValueError("Heatmap requires exactly 2 segment columns")
    
    # Compute segment-level effects
    long_eff = compute_diff_in_means_effect(df, "long_retained").set_index("exp_id")["delta_long_retained"]
    seg_long = compute_segment_effects(df, "long_retained", segment_cols)
    seg_proxy = compute_segment_effects(df, proxy_metric, segment_cols)
    
    seg = seg_long.merge(seg_proxy, on=["exp_id", *segment_cols], how="inner")
    seg["global_long_sign"] = np.sign(seg["exp_id"].map(long_eff))
    seg["proxy_sign"] = np.sign(seg[f"delta_{proxy_metric}"])
    seg["flip"] = (seg["proxy_sign"] != seg["global_long_sign"]).astype(int)
    
    # Aggregate flip rate by segments
    pivot = seg.groupby(segment_cols)["flip"].mean().unstack(fill_value=0)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(
        pivot,
        annot=True,
        fmt='.2%',
        cmap='RdYlGn_r',
        center=0.5,
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Sign Flip Rate'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title(f'Proxy Fragility Heatmap: {proxy_metric}', fontweight='bold', pad=15)
    ax.set_xlabel(segment_cols[1].capitalize(), fontweight='bold')
    ax.set_ylabel(segment_cols[0].capitalize(), fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)
    
    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_decision_simulation_results(
    decision_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    show: bool = True
) -> plt.Figure:
    """
    Visualize decision simulation results comparing proxy strategies.

    Args:
        decision_df: DataFrame from compare_decision_strategies()
        save_path: Optional path to save figure
        show: Whether to display the plot

    Returns:
        matplotlib Figure object
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Sort by win rate
    df_sorted = decision_df.sort_values('win_rate', ascending=False)

    # 1. Win Rate
    ax = axes[0, 0]
    bars = ax.barh(range(len(df_sorted)), df_sorted['win_rate'], alpha=0.8, edgecolor='black')
    colors = plt.cm.RdYlGn(df_sorted['win_rate'])
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    ax.set_yticks(range(len(df_sorted)))
    ax.set_yticklabels(df_sorted['proxy_metric'], fontsize=9)
    ax.set_xlabel('Win Rate', fontweight='bold')
    ax.set_title('Decision Win Rate by Proxy', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    for i, val in enumerate(df_sorted['win_rate']):
        ax.text(val + 0.01, i, f'{val:.2%}', va='center', fontsize=8)

    # 2. Average Regret
    ax = axes[0, 1]
    bars = ax.barh(range(len(df_sorted)), df_sorted['avg_regret'], alpha=0.8, edgecolor='black')
    colors = plt.cm.RdYlGn_r(df_sorted['avg_regret'] / df_sorted['avg_regret'].max())
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    ax.set_yticks(range(len(df_sorted)))
    ax.set_yticklabels(df_sorted['proxy_metric'], fontsize=9)
    ax.set_xlabel('Average Regret', fontweight='bold')
    ax.set_title('Average Decision Regret', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    for i, val in enumerate(df_sorted['avg_regret']):
        ax.text(val + 0.001, i, f'{val:.4f}', va='center', fontsize=8)

    # 3. False Positive vs False Negative Rate
    ax = axes[1, 0]
    x = np.arange(len(df_sorted))
    width = 0.35
    ax.bar(x - width/2, df_sorted['false_positive_rate'], width, label='False Positive',
           alpha=0.8, edgecolor='black')
    ax.bar(x + width/2, df_sorted['false_negative_rate'], width, label='False Negative',
           alpha=0.8, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(df_sorted['proxy_metric'], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Rate', fontweight='bold')
    ax.set_title('Error Rates by Proxy', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 4. Ship Decisions Breakdown
    ax = axes[1, 1]
    x = np.arange(len(df_sorted))
    width = 0.25
    ax.bar(x - width, df_sorted['correct_ships'], width, label='Correct Ships',
           alpha=0.8, edgecolor='black', color='green')
    ax.bar(x, df_sorted['incorrect_ships'], width, label='Incorrect Ships',
           alpha=0.8, edgecolor='black', color='red')
    ax.bar(x + width, df_sorted['missed_opportunities'], width, label='Missed Opportunities',
           alpha=0.8, edgecolor='black', color='orange')
    ax.set_xticks(x)
    ax.set_xticklabels(df_sorted['proxy_metric'], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Ship Decision Breakdown', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_all_proxy_correlations(
    df: pd.DataFrame,
    proxy_metrics: List[str],
    long_metric: str = "long_retained",
    save_path: Optional[Path] = None,
    show: bool = True
) -> plt.Figure:
    """
    Grid of correlation plots for all proxy metrics.

    Args:
        df: DataFrame with experiment data
        proxy_metrics: List of proxy metric names
        long_metric: Long-term metric name
        save_path: Optional path to save figure
        show: Whether to display the plot

    Returns:
        matplotlib Figure object
    """
    from proxima.models.baseline import compute_diff_in_means_effect

    n_metrics = len(proxy_metrics)
    n_cols = 2
    n_rows = (n_metrics + 1) // 2

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 5 * n_rows))
    axes = axes.flatten() if n_metrics > 1 else [axes]

    long_eff = compute_diff_in_means_effect(df, long_metric)

    for idx, proxy in enumerate(proxy_metrics):
        ax = axes[idx]
        proxy_eff = compute_diff_in_means_effect(df, proxy)
        effects = long_eff.merge(proxy_eff, on="exp_id")

        # Scatter
        ax.scatter(
            effects[f"delta_{proxy}"],
            effects[f"delta_{long_metric}"],
            alpha=0.6,
            s=60,
            edgecolors='black',
            linewidths=0.5
        )

        # Regression line
        z = np.polyfit(effects[f"delta_{proxy}"], effects[f"delta_{long_metric}"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(effects[f"delta_{proxy}"].min(),
                             effects[f"delta_{proxy}"].max(), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)

        # Correlation
        corr = effects[f"delta_{proxy}"].corr(effects[f"delta_{long_metric}"])

        ax.set_xlabel(f'{proxy}', fontweight='bold')
        ax.set_ylabel(f'{long_metric}', fontweight='bold')
        ax.set_title(f'{proxy} (r={corr:.3f})', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
        ax.axvline(x=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)

    # Hide unused subplots
    for idx in range(n_metrics, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)

    if show:
        plt.show()
    else:
        plt.close()

    return fig
