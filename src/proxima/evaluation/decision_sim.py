"""
Decision Simulation for Proxy Metric Evaluation

Simulates decision-making based on proxy metrics and evaluates:
- Win rate (agreement across all eligible decisions)
- Regret (loss relative to the measured outcome reference)
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
    correct_no_ships: int
    n_experiments: int
    precision: float
    n_positive: int
    n_negative: int


def simulate_shipping_decisions(
    df: pd.DataFrame,
    proxy_metric: str,
    long_metric: str = "long_retained",
    threshold: float = 0.0,
    direction: int | None = None,
    long_threshold: float = 0.0,
    min_per_arm: int = 2,
) -> DecisionSimulationResult:
    """
    Simulate shipping decisions based on proxy metric.
    
    Decision rule: Ship if proxy effect > threshold
    Evaluation: Compare against the measured outcome effect
    
    Args:
        df: DataFrame with experiment data
        proxy_metric: Name of proxy metric to use for decisions
        long_metric: Name of long-term outcome metric
        threshold: Decision threshold (default 0.0 = ship if positive)
    
    Returns:
        DecisionSimulationResult with performance metrics
    """
    from proxima.models.baseline import compute_diff_in_means_effect
    
    if min_per_arm < 1:
        raise ValueError("min_per_arm must be positive")
    # Use the same observed units for the proxy and reference outcome.
    work = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[proxy_metric, long_metric])
    counts = work.groupby(["exp_id", "treatment"], observed=True).size().unstack(fill_value=0).reindex(columns=[0, 1], fill_value=0)
    eligible = counts.index[(counts >= min_per_arm).all(axis=1)]
    work = work[work.exp_id.isin(eligible)]
    long_eff = compute_diff_in_means_effect(work, long_metric)
    proxy_eff = compute_diff_in_means_effect(work, proxy_metric)
    
    # Merge effects
    effects = long_eff.merge(proxy_eff, on="exp_id", suffixes=("_long", "_proxy"))

    # After merge, columns are: delta_{metric}_long and delta_{metric}_proxy
    long_col = f"delta_{long_metric}_long" if f"delta_{long_metric}_long" in effects.columns else f"delta_{long_metric}"
    proxy_col = f"delta_{proxy_metric}_proxy" if f"delta_{proxy_metric}_proxy" in effects.columns else f"delta_{proxy_metric}"

    if direction is None:
        direction = -1 if proxy_metric == "rebuffer_rate" else 1
    if direction not in (-1, 1) or not np.isfinite([threshold, long_threshold]).all():
        raise ValueError("Direction must be -1/+1 and thresholds must be finite")
    effects = effects.replace([np.inf, -np.inf], np.nan).dropna(subset=[long_col, proxy_col])
    if effects.empty:
        raise ValueError("No experiments have finite effects in both arms")
    # Metric orientation is specified before seeing outcomes.
    effects["proxy_decision"] = direction * effects[proxy_col] > threshold
    effects["true_positive"] = effects[long_col] > long_threshold
    
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
    
    correct_no_ships = int(effects["correct_no_ship"].sum())
    win_rate = (correct_ships + correct_no_ships) / len(effects)
    precision = correct_ships / total_shipped if total_shipped else float("nan")
    
    # False positive rate: of all truly negative experiments, how many did we ship?
    n_true_negative = int((~effects["true_positive"]).sum())
    false_positive_rate = incorrect_ships / n_true_negative if n_true_negative > 0 else float("nan")
    
    # False negative rate: of all truly positive experiments, how many did we miss?
    n_true_positive = int(effects["true_positive"].sum())
    false_negative_rate = missed_opportunities / n_true_positive if n_true_positive > 0 else float("nan")
    
    # Regret: opportunity cost of wrong decisions
    # Regret = sum of long-term losses from bad ships + sum of missed gains
    utility = effects[long_col] - long_threshold
    loss = np.where(effects["proxy_decision"] != effects["true_positive"], np.abs(utility), 0.0)
    avg_regret = float(np.mean(loss))

    return DecisionSimulationResult(
        proxy_metric=proxy_metric,
        win_rate=float(win_rate),
        false_positive_rate=float(false_positive_rate),
        false_negative_rate=float(false_negative_rate),
        avg_regret=avg_regret,
        total_shipped=total_shipped,
        correct_ships=correct_ships,
        incorrect_ships=incorrect_ships,
        missed_opportunities=missed_opportunities,
        correct_no_ships=correct_no_ships, n_experiments=len(effects),
        precision=float(precision), n_positive=n_true_positive, n_negative=n_true_negative
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
            "precision": sim_result.precision,
            "n_experiments": sim_result.n_experiments,
            "false_positive_rate": sim_result.false_positive_rate,
            "false_negative_rate": sim_result.false_negative_rate,
            "avg_regret": sim_result.avg_regret,
            "total_shipped": sim_result.total_shipped,
            "correct_ships": sim_result.correct_ships,
            "incorrect_ships": sim_result.incorrect_ships,
            "missed_opportunities": sim_result.missed_opportunities,
        })
    
    # Add measured-reference strategy (not a true-outcome oracle)
    oracle_result = simulate_shipping_decisions(df, long_metric, long_metric, threshold)
    results.append({
        "proxy_metric": "Measured outcome reference",
        "win_rate": oracle_result.win_rate,
        "precision": oracle_result.precision,
        "n_experiments": oracle_result.n_experiments,
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
    
    seg = seg.replace([np.inf, -np.inf], np.nan).dropna()
    direction = -1 if proxy_metric == "rebuffer_rate" else 1
    # Decisions
    seg["proxy_decision"] = direction * seg[f"delta_{proxy_metric}"] > threshold
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

