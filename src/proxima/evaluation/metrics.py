"""
Comprehensive Evaluation Metrics and Statistical Tests

This module provides:
- Confidence intervals for treatment effects
- Statistical significance tests
- Bootstrap-based uncertainty quantification
- Decision simulation metrics
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Tuple, Dict, List, Optional
from scipy import stats
from dataclasses import dataclass


@dataclass
class TreatmentEffectResult:
    """Container for treatment effect estimation with uncertainty."""
    effect: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float
    n_control: int
    n_treatment: int


def compute_effect_with_ci(
    df: pd.DataFrame,
    y_col: str,
    alpha: float = 0.05
) -> TreatmentEffectResult:
    """
    Compute treatment effect with confidence interval using t-test.
    
    Args:
        df: DataFrame with 'treatment' and y_col
        y_col: Outcome column name
        alpha: Significance level (default 0.05 for 95% CI)
    
    Returns:
        TreatmentEffectResult with effect estimate and statistics
    """
    control = df[df["treatment"] == 0][y_col].dropna()
    treatment = df[df["treatment"] == 1][y_col].dropna()
    
    effect = float(treatment.mean() - control.mean())
    
    # Welch's t-test (unequal variances)
    t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)
    
    # Standard error using Welch-Satterthwaite
    se_control = control.std() / np.sqrt(len(control))
    se_treatment = treatment.std() / np.sqrt(len(treatment))
    std_error = np.sqrt(se_control**2 + se_treatment**2)
    
    # Degrees of freedom (Welch-Satterthwaite)
    df_welch = (se_control**2 + se_treatment**2)**2 / (
        se_control**4 / (len(control) - 1) + se_treatment**4 / (len(treatment) - 1)
    )
    
    # Confidence interval
    t_crit = stats.t.ppf(1 - alpha/2, df_welch)
    ci_lower = effect - t_crit * std_error
    ci_upper = effect + t_crit * std_error
    
    return TreatmentEffectResult(
        effect=effect,
        std_error=std_error,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        p_value=float(p_value),
        n_control=len(control),
        n_treatment=len(treatment)
    )


def bootstrap_effect_ci(
    df: pd.DataFrame,
    y_col: str,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 42
) -> Tuple[float, float, float]:
    """
    Bootstrap confidence interval for treatment effect.
    
    Args:
        df: DataFrame with 'treatment' and y_col
        y_col: Outcome column name
        n_bootstrap: Number of bootstrap samples
        alpha: Significance level
        seed: Random seed
    
    Returns:
        Tuple of (effect, ci_lower, ci_upper)
    """
    rng = np.random.default_rng(seed)
    
    control = df[df["treatment"] == 0][y_col].values
    treatment = df[df["treatment"] == 1][y_col].values
    
    bootstrap_effects = []
    for _ in range(n_bootstrap):
        control_sample = rng.choice(control, size=len(control), replace=True)
        treatment_sample = rng.choice(treatment, size=len(treatment), replace=True)
        bootstrap_effects.append(treatment_sample.mean() - control_sample.mean())
    
    bootstrap_effects = np.array(bootstrap_effects)
    effect = float(treatment.mean() - control.mean())
    ci_lower = float(np.percentile(bootstrap_effects, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_effects, 100 * (1 - alpha / 2)))
    
    return effect, ci_lower, ci_upper


def compute_experiment_effects_with_ci(
    df: pd.DataFrame,
    y_col: str,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Compute per-experiment treatment effects with confidence intervals.
    
    Args:
        df: DataFrame with exp_id, treatment, and y_col
        y_col: Outcome column name
        alpha: Significance level
    
    Returns:
        DataFrame with columns [exp_id, effect, ci_lower, ci_upper, p_value, significant]
    """
    results = []
    
    for exp_id in df["exp_id"].unique():
        exp_df = df[df["exp_id"] == exp_id]
        result = compute_effect_with_ci(exp_df, y_col, alpha)
        
        results.append({
            "exp_id": exp_id,
            "effect": result.effect,
            "std_error": result.std_error,
            "ci_lower": result.ci_lower,
            "ci_upper": result.ci_upper,
            "p_value": result.p_value,
            "significant": result.p_value < alpha,
            "n_control": result.n_control,
            "n_treatment": result.n_treatment,
        })
    
    return pd.DataFrame(results)


def compute_proxy_correlation_with_ci(
    df: pd.DataFrame,
    proxy_col: str,
    long_col: str = "long_retained",
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 42
) -> Dict[str, float]:
    """
    Compute correlation between proxy and long-term effects with bootstrap CI.
    
    Args:
        df: DataFrame with experiment-level effects
        proxy_col: Proxy effect column name
        long_col: Long-term effect column name
        n_bootstrap: Number of bootstrap samples
        alpha: Significance level
        seed: Random seed
    
    Returns:
        Dictionary with correlation, ci_lower, ci_upper, p_value
    """
    from proxima.models.baseline import compute_diff_in_means_effect
    
    # Get experiment-level effects
    long_eff = compute_diff_in_means_effect(df, long_col).set_index("exp_id")[f"delta_{long_col}"]
    proxy_eff = compute_diff_in_means_effect(df, proxy_col).set_index("exp_id")[f"delta_{proxy_col}"]
    
    aligned = pd.concat([long_eff, proxy_eff], axis=1, join="inner").dropna()
    
    # Observed correlation
    corr = float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))
    
    # Bootstrap CI
    rng = np.random.default_rng(seed)
    bootstrap_corrs = []
    n = len(aligned)
    
    for _ in range(n_bootstrap):
        indices = rng.choice(n, size=n, replace=True)
        sample = aligned.iloc[indices]
        bootstrap_corrs.append(sample.iloc[:, 0].corr(sample.iloc[:, 1]))
    
    bootstrap_corrs = np.array(bootstrap_corrs)
    ci_lower = float(np.percentile(bootstrap_corrs, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_corrs, 100 * (1 - alpha / 2)))
    
    # Fisher's z-transformation for p-value
    z = 0.5 * np.log((1 + corr) / (1 - corr))
    se_z = 1 / np.sqrt(n - 3)
    p_value = 2 * (1 - stats.norm.cdf(abs(z) / se_z))
    
    return {
        "correlation": corr,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value": float(p_value),
        "n_experiments": n
    }

