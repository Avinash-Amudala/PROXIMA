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
    g = df.groupby(["exp_id", "treatment"])[y_col].mean().unstack()
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
    g = df.groupby(["exp_id", *segment_cols, "treatment"])[y_col].mean().unstack()
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
    segment_cols: List[str] = ["region", "device", "tenure"]
) -> Tuple[pd.DataFrame, List[ProxyScore]]:
    """
    Scores each early metric as a proxy for long_retained uplift.

    Reliability is a composite:
      0.6 * effect_correlation + 0.2 * directional_accuracy + 0.2 * (1 - fragility_rate)
    
    Args:
        df: DataFrame with experiment data
        segment_cols: List of segment column names for fragility detection
    
    Returns:
        Tuple of (details_dataframe, list_of_proxy_scores)
    """
    # Experiment-level long-term effect
    long_eff = compute_diff_in_means_effect(df, "long_retained")

    proxy_scores: List[ProxyScore] = []
    details_rows = []

    # Precompute global long-term sign per experiment
    long_by_exp = long_eff.set_index("exp_id")["delta_long_retained"]

    for m in EARLY_METRICS:
        m_eff = compute_diff_in_means_effect(df, m).set_index("exp_id")[f"delta_{m}"]

        # Align
        aligned = pd.concat([long_by_exp, m_eff], axis=1, join="inner").dropna()
        aligned.columns = ["delta_long", "delta_proxy"]

        # effect correlation
        if aligned["delta_proxy"].std() < 1e-12 or aligned["delta_long"].std() < 1e-12:
            corr = 0.0
        else:
            corr = float(aligned["delta_proxy"].corr(aligned["delta_long"]))

        # directional accuracy (sign match)
        dir_acc = float((np.sign(aligned["delta_proxy"]) == np.sign(aligned["delta_long"])).mean())

        # fragility: segment-level sign flips
        seg_long = compute_segment_effects(df, "long_retained", segment_cols)
        seg_proxy = compute_segment_effects(df, m, segment_cols)

        seg = seg_long.merge(seg_proxy, on=["exp_id", *segment_cols], how="inner", suffixes=("_long", "_proxy"))
        # attach global signs
        seg["global_long_sign"] = np.sign(seg["exp_id"].map(long_by_exp))
        seg["proxy_sign"] = np.sign(seg[f"delta_{m}"])
        # "flip" if proxy suggests opposite direction than global long-term
        seg["flip"] = (seg["proxy_sign"] != seg["global_long_sign"]).astype(int)
        fragility_rate = float(seg["flip"].mean())

        # Reliability composite (normalize corr to [0,1] via (corr+1)/2)
        corr01 = (corr + 1.0) / 2.0
        reliability = float(0.6 * corr01 + 0.2 * dir_acc + 0.2 * (1.0 - fragility_rate))

        proxy_scores.append(ProxyScore(
            metric=m,
            reliability=reliability,
            effect_corr=corr,
            directional_accuracy=dir_acc,
            fragility_rate=fragility_rate
        ))

        details_rows.append({
            "metric": m,
            "reliability": reliability,
            "effect_corr": corr,
            "directional_accuracy": dir_acc,
            "fragility_rate": fragility_rate,
            "n_experiments_scored": int(aligned.shape[0]),
        })

    details = pd.DataFrame(details_rows).sort_values("reliability", ascending=False).reset_index(drop=True)
    return details, proxy_scores


def find_top_fragility_segments(
    df: pd.DataFrame,
    proxy_metric: str,
    segment_cols: List[str] = ["region", "device", "tenure"],
    min_count: int = 500
) -> pd.DataFrame:
    """
    Returns segments where proxy sign differs from long-term sign most often.

    Args:
        df: DataFrame with experiment data
        proxy_metric: Name of the proxy metric to analyze
        segment_cols: List of segment column names
        min_count: Minimum number of users per segment to include

    Returns:
        DataFrame with fragile segments ranked by flip_rate
    """
    long_eff = compute_diff_in_means_effect(df, "long_retained").set_index("exp_id")["delta_long_retained"]
    seg_long = compute_segment_effects(df, "long_retained", segment_cols)
    seg_proxy = compute_segment_effects(df, proxy_metric, segment_cols)
    seg = seg_long.merge(seg_proxy, on=["exp_id", *segment_cols], how="inner")

    seg["global_long_sign"] = np.sign(seg["exp_id"].map(long_eff))
    seg["proxy_sign"] = np.sign(seg[f"delta_{proxy_metric}"])
    seg["flip"] = (seg["proxy_sign"] != seg["global_long_sign"]).astype(int)

    # count users per (exp, segment) for filtering
    counts = df.groupby(["exp_id", *segment_cols]).size().reset_index(name="n")
    seg = seg.merge(counts, on=["exp_id", *segment_cols], how="inner")
    seg = seg[seg["n"] >= min_count]

    out = seg.groupby(segment_cols).agg(
        flip_rate=("flip", "mean"),
        n_cells=("flip", "size"),
        avg_cell_n=("n", "mean"),
    ).reset_index().sort_values("flip_rate", ascending=False)

    return out

