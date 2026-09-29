"""
Statistical significance tests and confidence intervals for PROXIMA

Adds rigorous statistical validation to proxy metric evaluation.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple
from dataclasses import dataclass


@dataclass
class SignificanceTest:
    """Results from statistical significance test."""
    metric: str
    test_statistic: float
    p_value: float
    is_significant: bool
    confidence_interval_95: Tuple[float, float]
    effect_size: float
    sample_size: int


def compute_correlation_significance(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05
) -> SignificanceTest:
    """
    Test if correlation between proxy and long-term metric is significant.
    
    Args:
        x: Proxy metric values
        y: Long-term metric values
        alpha: Significance level (default 0.05)
    
    Returns:
        SignificanceTest with correlation test results
    """
    # Remove NaN values
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape != y.shape or x.ndim != 1 or not 0 < alpha < 1:
        raise ValueError("Provide paired one-dimensional inputs and 0 < alpha < 1")
    mask = np.isfinite(x) & np.isfinite(y)
    x_clean = x[mask]
    y_clean = y[mask]
    
    n = len(x_clean)
    
    if n <= 3 or np.std(x_clean) == 0 or np.std(y_clean) == 0:
        return SignificanceTest(
            metric="correlation",
            test_statistic=float("nan"),
            p_value=float("nan"),
            is_significant=False,
            confidence_interval_95=(float("nan"), float("nan")),
            effect_size=float("nan"),
            sample_size=n
        )
    
    # Pearson correlation
    r, p_value = stats.pearsonr(x_clean, y_clean)
    
    # Fisher's z-transformation for confidence interval
    z = np.arctanh(np.clip(r, -1+1e-15, 1-1e-15))
    se = 1 / np.sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - alpha/2)
    
    ci_lower = np.tanh(z - z_crit * se)
    ci_upper = np.tanh(z + z_crit * se)
    
    return SignificanceTest(
        metric="correlation",
        test_statistic=r,
        p_value=p_value,
        is_significant=p_value < alpha,
        confidence_interval_95=(ci_lower, ci_upper),
        effect_size=r,
        sample_size=n
    )


def compute_treatment_effect_significance(
    df: pd.DataFrame,
    metric: str,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Test significance of treatment effects across experiments.
    
    Args:
        df: DataFrame with exp_id, treatment, and metric columns
        metric: Name of the metric to test
        alpha: Significance level
    
    Returns:
        DataFrame with significance test results per experiment
    """
    from proxima.models.baseline import compute_diff_in_means_effect
    
    results = []
    
    for exp_id in df['exp_id'].unique():
        exp_data = df[df['exp_id'] == exp_id]
        
        control = exp_data[exp_data['treatment'] == 0][metric].dropna()
        treatment = exp_data[exp_data['treatment'] == 1][metric].dropna()
        
        if len(control) < 2 or len(treatment) < 2:
            continue
        
        # Welch's t-test (doesn't assume equal variances)
        t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(control)-1)*control.var() + (len(treatment)-1)*treatment.var()) / (len(control)+len(treatment)-2))
        cohens_d = (treatment.mean() - control.mean()) / pooled_std if pooled_std > 0 else 0
        
        # Confidence interval for difference in means
        diff = treatment.mean() - control.mean()
        se_diff = np.sqrt(control.var()/len(control) + treatment.var()/len(treatment))
        v0, v1 = control.var()/len(control), treatment.var()/len(treatment)
        denominator = v0*v0/(len(control)-1) + v1*v1/(len(treatment)-1)
        dof = (v0+v1)**2/denominator if denominator > 0 else np.inf
        t_crit = stats.t.ppf(1 - alpha/2, dof)
        
        ci_lower = diff - t_crit * se_diff
        ci_upper = diff + t_crit * se_diff
        
        results.append({
            'exp_id': exp_id,
            'metric': metric,
            'effect': diff,
            't_statistic': t_stat,
            'p_value': p_value,
            'is_significant': p_value < alpha,
            'cohens_d': cohens_d,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'n_control': len(control),
            'n_treatment': len(treatment)
        })
    
    return pd.DataFrame(results)


def compute_proxy_reliability_confidence(
    df: pd.DataFrame, proxy_metric: str, long_metric: str = "long_retained",
    n_bootstrap: int = 1000, alpha: float = 0.05, seed: int = 42,
) -> Tuple[float, Tuple[float, float]]:
    """Seeded experiment-block bootstrap with unique identifiers for each draw."""
    from proxima.models.baseline import score_proxies
    if not 0 < alpha < 1 or n_bootstrap < 2 or df.exp_id.nunique() < 2:
        raise ValueError("Need two experiments, two resamples, and 0 < alpha < 1")
    def score(frame):
        details, _ = score_proxies(frame, proxy_metrics=[proxy_metric], long_metric=long_metric)
        return float(details.iloc[0].reliability)
    original = score(df)
    groups = [g for _, g in df.groupby("exp_id", sort=True)]
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(n_bootstrap):
        ids = rng.integers(0, len(groups), size=len(groups))
        sample = pd.concat([groups[i].assign(exp_id=j) for j, i in enumerate(ids)], ignore_index=True)
        values.append(score(sample))
    if not np.isfinite(values).all():
        raise ValueError("Undefined bootstrap scores: check segment sizes and missing data")
    return original, tuple(map(float, np.quantile(values, [alpha/2, 1-alpha/2])))


def test_proxy_superiority(
    df: pd.DataFrame,
    proxy1: str,
    proxy2: str,
    long_metric: str = "long_retained",
    alpha: float = 0.05
) -> dict:
    """
    Test if one proxy is significantly better than another.
    
    Uses McNemar's test for paired comparisons of directional accuracy.
    
    Args:
        df: DataFrame with experiment data
        proxy1: First proxy metric
        proxy2: Second proxy metric
        long_metric: Long-term metric
        alpha: Significance level
    
    Returns:
        Dictionary with test results
    """
    from proxima.models.baseline import compute_diff_in_means_effect
    
    # Compute effects
    long_eff = compute_diff_in_means_effect(df, long_metric).set_index("exp_id")
    proxy1_eff = compute_diff_in_means_effect(df, proxy1).set_index("exp_id")
    proxy2_eff = compute_diff_in_means_effect(df, proxy2).set_index("exp_id")
    
    # Align
    aligned = pd.concat([long_eff, proxy1_eff, proxy2_eff], axis=1, join="inner")
    aligned.columns = ['long', 'proxy1', 'proxy2']
    
    aligned = aligned.replace([np.inf, -np.inf], np.nan).dropna()
    if aligned.empty:
        raise ValueError("No finite paired effects for comparison")
    d1 = -1 if proxy1 == "rebuffer_rate" else 1
    d2 = -1 if proxy2 == "rebuffer_rate" else 1
    # The same positive-effect ship rule as the decision simulation.
    proxy1_correct = ((aligned['long'] > 0) == (d1 * aligned['proxy1'] > 0))
    proxy2_correct = ((aligned['long'] > 0) == (d2 * aligned['proxy2'] > 0))
    
    # McNemar's test
    # Contingency table: [both_correct, proxy1_only, proxy2_only, both_wrong]
    both_correct = (proxy1_correct & proxy2_correct).sum()
    proxy1_only = (proxy1_correct & ~proxy2_correct).sum()
    proxy2_only = (~proxy1_correct & proxy2_correct).sum()
    both_wrong = (~proxy1_correct & ~proxy2_correct).sum()
    
    # McNemar statistic
    if proxy1_only + proxy2_only > 0:
        mcnemar_stat = max(abs(proxy1_only - proxy2_only) - 1, 0)**2 / (proxy1_only + proxy2_only)
        p_value = 1 - stats.chi2.cdf(mcnemar_stat, df=1)
    else:
        mcnemar_stat = 0
        p_value = 1.0
    
    return {
        'proxy1': proxy1,
        'proxy2': proxy2,
        'proxy1_accuracy': proxy1_correct.mean(),
        'proxy2_accuracy': proxy2_correct.mean(),
        'mcnemar_statistic': mcnemar_stat,
        'p_value': p_value,
        'is_significant': p_value < alpha,
        'winner': None if proxy1_correct.mean() == proxy2_correct.mean() else (proxy1 if proxy1_correct.mean() > proxy2_correct.mean() else proxy2)
    }

