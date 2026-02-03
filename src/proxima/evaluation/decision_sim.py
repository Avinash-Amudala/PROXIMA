"""
Decision Simulation for Proxy Metric Evaluation

Simulates decision-making based on proxy metrics and evaluates:
- Win rate (% of correct ship decisions)
- Regret (loss compared to using true long-term metric)
- False positive/negative rates
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DecisionSimulationResult:
    """Container for decision simulation results."""
    proxy_metric: str
    win_rate: float
    false_positive_rate: float
    false_negative_rate: float
    avg_regret: float
    total_shipped: int
    correct_ships: int
    incorrect_ships: int
    missed_opportunities: int


def simulate_shipping_decisions(
    df: pd.DataFrame,
    proxy_metric: str,
    long_metric: str = "long_retained",
    threshold: float = 0.0
) -> DecisionSimulationResult:
    """
    Simulate shipping decisions based on proxy metric.
    
    Decision rule: Ship if proxy effect > threshold
    Evaluation: Compare against true long-term effect
    
    Args:
        df: DataFrame with experiment data
        proxy_metric: Name of proxy metric to use for decisions
        long_metric: Name of long-term outcome metric
        threshold: Decision threshold (default 0.0 = ship if positive)
    
    Returns:
        DecisionSimulationResult with performance metrics
    """
    from proxima.models.baseline import compute_diff_in_means_effect
    
    # Compute experiment-level effects
    long_eff = compute_diff_in_means_effect(df, long_metric)
    proxy_eff = compute_diff_in_means_effect(df, proxy_metric)
    
    # Merge effects
    effects = long_eff.merge(proxy_eff, on="exp_id", suffixes=("_long", "_proxy"))

    # After merge, columns are: delta_{metric}_long and delta_{metric}_proxy
    long_col = f"delta_{long_metric}_long" if f"delta_{long_metric}_long" in effects.columns else f"delta_{long_metric}"
    proxy_col = f"delta_{proxy_metric}_proxy" if f"delta_{proxy_metric}_proxy" in effects.columns else f"delta_{proxy_metric}"

    # Decision based on proxy
    effects["proxy_decision"] = effects[proxy_col] > threshold
    effects["true_positive"] = effects[long_col] > threshold
    
    # Outcomes
    effects["correct_ship"] = effects["proxy_decision"] & effects["true_positive"]
    effects["incorrect_ship"] = effects["proxy_decision"] & ~effects["true_positive"]
    effects["missed_opportunity"] = ~effects["proxy_decision"] & effects["true_positive"]
    effects["correct_no_ship"] = ~effects["proxy_decision"] & ~effects["true_positive"]
    
    # Metrics
    total_shipped = int(effects["proxy_decision"].sum())
    correct_ships = int(effects["correct_ship"].sum())
    incorrect_ships = int(effects["incorrect_ship"].sum())
    missed_opportunities = int(effects["missed_opportunity"].sum())
    
    # Win rate: of all shipped experiments, how many were actually positive?
    win_rate = correct_ships / total_shipped if total_shipped > 0 else 0.0
    
    # False positive rate: of all truly negative experiments, how many did we ship?
    n_true_negative = int((~effects["true_positive"]).sum())
    false_positive_rate = incorrect_ships / n_true_negative if n_true_negative > 0 else 0.0
    
    # False negative rate: of all truly positive experiments, how many did we miss?
    n_true_positive = int(effects["true_positive"].sum())
    false_negative_rate = missed_opportunities / n_true_positive if n_true_positive > 0 else 0.0
    
    # Regret: opportunity cost of wrong decisions
    # Regret = sum of long-term losses from bad ships + sum of missed gains
    regret_from_bad_ships = effects.loc[effects["incorrect_ship"], long_col].sum()
    regret_from_missed = -effects.loc[effects["missed_opportunity"], long_col].sum()
    avg_regret = float((abs(regret_from_bad_ships) + regret_from_missed) / len(effects))
    
    return DecisionSimulationResult(
        proxy_metric=proxy_metric,
        win_rate=float(win_rate),
        false_positive_rate=float(false_positive_rate),
        false_negative_rate=float(false_negative_rate),
        avg_regret=avg_regret,
        total_shipped=total_shipped,
        correct_ships=correct_ships,
        incorrect_ships=incorrect_ships,
        missed_opportunities=missed_opportunities
    )


def compare_decision_strategies(
    df: pd.DataFrame,
    proxy_metrics: List[str],
    long_metric: str = "long_retained",
    threshold: float = 0.0
) -> pd.DataFrame:
    """
    Compare multiple proxy metrics as decision strategies.
    
    Args:
        df: DataFrame with experiment data
        proxy_metrics: List of proxy metric names
        long_metric: Long-term outcome metric
        threshold: Decision threshold
    
    Returns:
        DataFrame comparing all strategies
    """
    results = []
    
    for proxy in proxy_metrics:
        sim_result = simulate_shipping_decisions(df, proxy, long_metric, threshold)
        results.append({
            "proxy_metric": sim_result.proxy_metric,
            "win_rate": sim_result.win_rate,
            "false_positive_rate": sim_result.false_positive_rate,
            "false_negative_rate": sim_result.false_negative_rate,
            "avg_regret": sim_result.avg_regret,
            "total_shipped": sim_result.total_shipped,
            "correct_ships": sim_result.correct_ships,
            "incorrect_ships": sim_result.incorrect_ships,
            "missed_opportunities": sim_result.missed_opportunities,
        })
    
    # Add oracle strategy (using true long-term metric)
    oracle_result = simulate_shipping_decisions(df, long_metric, long_metric, threshold)
    results.append({
        "proxy_metric": "Oracle (True Long-term)",
        "win_rate": oracle_result.win_rate,
        "false_positive_rate": oracle_result.false_positive_rate,
        "false_negative_rate": oracle_result.false_negative_rate,
        "avg_regret": oracle_result.avg_regret,
        "total_shipped": oracle_result.total_shipped,
        "correct_ships": oracle_result.correct_ships,
        "incorrect_ships": oracle_result.incorrect_ships,
        "missed_opportunities": oracle_result.missed_opportunities,
    })
    
    comparison_df = pd.DataFrame(results).sort_values("win_rate", ascending=False)
    return comparison_df


def compute_regret_by_segment(
    df: pd.DataFrame,
    proxy_metric: str,
    segment_cols: List[str] = ["region", "device", "tenure"],
    long_metric: str = "long_retained",
    threshold: float = 0.0
) -> pd.DataFrame:
    """
    Compute decision regret broken down by segments.
    
    Args:
        df: DataFrame with experiment data
        proxy_metric: Proxy metric for decisions
        segment_cols: Segment column names
        long_metric: Long-term outcome metric
        threshold: Decision threshold
    
    Returns:
        DataFrame with regret by segment
    """
    from proxima.models.baseline import compute_segment_effects
    
    # Get segment-level effects
    seg_long = compute_segment_effects(df, long_metric, segment_cols)
    seg_proxy = compute_segment_effects(df, proxy_metric, segment_cols)
    
    seg = seg_long.merge(seg_proxy, on=["exp_id", *segment_cols], how="inner")
    
    # Decisions
    seg["proxy_decision"] = seg[f"delta_{proxy_metric}"] > threshold
    seg["true_positive"] = seg[f"delta_{long_metric}"] > threshold
    seg["wrong_decision"] = seg["proxy_decision"] != seg["true_positive"]
    
    # Regret per segment
    seg["regret"] = np.where(
        seg["wrong_decision"],
        np.abs(seg[f"delta_{long_metric}"]),
        0.0
    )
    
    # Aggregate by segment
    regret_summary = seg.groupby(segment_cols).agg(
        avg_regret=("regret", "mean"),
        total_regret=("regret", "sum"),
        error_rate=("wrong_decision", "mean"),
        n_cells=("regret", "size")
    ).reset_index().sort_values("avg_regret", ascending=False)
    
    return regret_summary

