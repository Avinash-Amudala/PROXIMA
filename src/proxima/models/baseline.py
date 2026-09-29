"""
Baseline Model + Proxy Scoring + Fragility Detection

This module provides:
- Treatment effect estimation (difference-in-means)
- Proxy reliability scoring
- Segment-level fragility detection
- Long-term outcome prediction model
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

EARLY_METRICS = ["early_watch_min", "early_starts", "early_ctr", "rebuffer_rate"]


@dataclass
class ProxyScore:
    """Container for proxy metric evaluation results."""
    metric: str
    reliability: float
    effect_corr: float
    directional_accuracy: float
    fragility_rate: float


def compute_diff_in_means_effect(df: pd.DataFrame, y_col: str) -> pd.DataFrame:
    """
    Compute experiment-level treatment effect using difference in means:
      effect(exp) = mean(y|t=1) - mean(y|t=0)
    
    Args:
        df: DataFrame with columns [exp_id, treatment, y_col]
        y_col: Name of the outcome column
    
    Returns:
        DataFrame with columns [exp_id, delta_{y_col}]
    """
    if not df["treatment"].isin([0, 1]).all():
        raise ValueError("treatment must contain only 0 and 1")
    g = df.groupby(["exp_id", "treatment"], observed=True)[y_col].mean().unstack().reindex(columns=[0, 1])
    g = g.rename(columns={0: "control_mean", 1: "treat_mean"})
    g["effect"] = g["treat_mean"] - g["control_mean"]
    g = g.reset_index()
    return g[["exp_id", "effect"]].rename(columns={"effect": f"delta_{y_col}"})


def compute_segment_effects(
    df: pd.DataFrame, 
    y_col: str, 
    segment_cols: List[str]
) -> pd.DataFrame:
    """
    Segment-level effects: effect(exp, segment) = mean(y|t=1) - mean(y|t=0)
    
    Args:
        df: DataFrame with experiment data
        y_col: Outcome column name
        segment_cols: List of segment column names
    
    Returns:
        DataFrame with segment-level treatment effects
    """
    g = df.groupby(["exp_id", *segment_cols, "treatment"], observed=True)[y_col].mean().unstack().reindex(columns=[0, 1])
    g = g.rename(columns={0: "control_mean", 1: "treat_mean"})
    g["effect"] = g["treat_mean"] - g["control_mean"]
    g = g.reset_index()
    return g[["exp_id", *segment_cols, "effect"]].rename(columns={"effect": f"delta_{y_col}"})


def train_long_term_model(df: pd.DataFrame) -> Tuple[Pipeline, float]:
    """
    Simple baseline: logistic regression predicting long_retained from:
      segments + treatment + early metrics
    
    Args:
        df: DataFrame with all features and long_retained outcome
    
    Returns:
        Tuple of (trained_model, test_auc)
    """
    X = df[["region", "device", "tenure", "treatment", *EARLY_METRICS]]
    y = df["long_retained"]

    cat_cols = ["region", "device", "tenure"]
    num_cols = ["treatment", *EARLY_METRICS]

    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", "passthrough", num_cols),
        ]
    )

    clf = LogisticRegression(max_iter=500, random_state=42)
    model = Pipeline(steps=[("pre", pre), ("clf", clf)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    return model, auc


def score_proxies(
    df: pd.DataFrame,
    segment_cols: List[str] = None,
    proxy_metrics: List[str] = None,
    long_metric: str = "long_retained",
    directions: dict = None,
    weights: Tuple[float, float, float] = (0.6, 0.2, 0.2),
    min_per_arm: int = 2,
) -> Tuple[pd.DataFrame, List[ProxyScore]]:
    """Descriptive score; not a probability or a guarantee about future effects.

    Fragility compares LOCAL proxy and LOCAL outcome decisions. Global discordance
    is reported separately. Missing/undersized cells are excluded and counted.
    Undefined correlation receives a neutral 0.5 component and an explicit flag.
    """
    from proxima.evaluation.audit import score_effects
    segment_cols = ["region", "device", "tenure"] if segment_cols is None else segment_cols
    proxy_metrics = EARLY_METRICS if proxy_metrics is None else proxy_metrics
    directions = {"rebuffer_rate": -1} if directions is None else directions
    if not segment_cols or min_per_arm < 1:
        raise ValueError("Provide segment columns and a positive arm-size minimum")
    details_rows = []
    for metric in proxy_metrics:
        # Pairwise complete cases preserve the same units for each proxy/outcome.
        work = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[metric, long_metric, *segment_cols])
        global_long = compute_diff_in_means_effect(work, long_metric).set_index("exp_id").iloc[:, 0]
        global_proxy = compute_diff_in_means_effect(work, metric).set_index("exp_id").iloc[:, 0]
        counts = work.groupby(["exp_id", "treatment"], observed=True).size().unstack(fill_value=0).reindex(columns=[0, 1], fill_value=0)
        aligned = pd.concat([global_long, global_proxy], axis=1).dropna()
        aligned = aligned.loc[aligned.index.intersection(counts.index[(counts >= min_per_arm).all(axis=1)])]
        aligned.columns = ["outcome", "proxy"]
        local_long = compute_segment_effects(work, long_metric, segment_cols)
        local_proxy = compute_segment_effects(work, metric, segment_cols)
        seg = local_long.merge(local_proxy, on=["exp_id", *segment_cols], suffixes=("_outcome", "_proxy"))
        # Same metric is permitted and should produce a perfect local match.
        lcol = f"delta_{long_metric}" + ("_outcome" if metric == long_metric else "")
        pcol = f"delta_{metric}" + ("_proxy" if metric == long_metric else "")
        counts = work.groupby(["exp_id", *segment_cols, "treatment"], observed=True).size().unstack(fill_value=0).reindex(columns=[0, 1], fill_value=0)
        eligible = counts[(counts >= min_per_arm).all(axis=1)].reset_index()[["exp_id", *segment_cols]]
        n_candidate = len(seg)
        seg = seg.merge(eligible, on=["exp_id", *segment_cols]).dropna(subset=[lcol, pcol])
        seg = seg[seg.exp_id.isin(aligned.index)]
        result = score_effects(aligned.proxy.to_numpy(), aligned.outcome.to_numpy(),
                              seg[pcol].to_numpy(), seg[lcol].to_numpy(),
                              direction=directions.get(metric, 1), weights=weights)
        result.update(metric=metric, n_experiments_scored=len(aligned),
                      n_segment_cells=len(seg), n_segment_cells_excluded=n_candidate-len(seg))
        direction = directions.get(metric, 1)
        result["global_discordance"] = float(((direction * seg[pcol] > 0) != (seg.exp_id.map(global_long) > 0)).mean()) if len(seg) else float("nan")
        details_rows.append(result)
    details = pd.DataFrame(details_rows).sort_values("reliability", ascending=False, na_position="last").reset_index(drop=True)
    scores = [ProxyScore(row.metric, row.reliability, row.effect_corr, row.directional_accuracy, row.fragility_rate)
              for row in details.itertuples()]
    return details, scores


def find_top_fragility_segments(
    df: pd.DataFrame, proxy_metric: str,
    segment_cols: List[str] = None, min_count: int = 500,
    min_per_arm: int = 2, direction: int = None,
) -> pd.DataFrame:
    """Rank descriptive within-segment disagreement; no significance claim."""
    segment_cols = ["region", "device", "tenure"] if segment_cols is None else segment_cols
    direction = (-1 if proxy_metric == "rebuffer_rate" else 1) if direction is None else direction
    if direction not in (-1, 1):
        raise ValueError("direction must be -1/+1")
    work = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[proxy_metric, "long_retained", *segment_cols])
    seg_long = compute_segment_effects(work, "long_retained", segment_cols)
    seg_proxy = compute_segment_effects(work, proxy_metric, segment_cols)
    seg = seg_long.merge(seg_proxy, on=["exp_id", *segment_cols]).dropna()
    counts = work.groupby(["exp_id", *segment_cols, "treatment"], observed=True).size().unstack(fill_value=0).reindex(columns=[0, 1], fill_value=0)
    counts = counts[(counts >= min_per_arm).all(axis=1)]
    counts["n"] = counts.sum(axis=1)
    seg = seg.merge(counts[["n"]].reset_index(), on=["exp_id", *segment_cols])
    seg = seg[seg.n >= min_count]
    seg["flip"] = ((direction * seg[f"delta_{proxy_metric}"] > 0) != (seg.delta_long_retained > 0)).astype(int)
    return seg.groupby(segment_cols, observed=True).agg(flip_rate=("flip", "mean"), n_cells=("flip", "size"), avg_cell_n=("n", "mean")).reset_index().sort_values("flip_rate", ascending=False)
