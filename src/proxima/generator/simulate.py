"""
Synthetic Data Generator for A/B Experiments

This generator intentionally creates:
- "good proxies" (early metrics tightly linked to long-term)
- "bad proxies" (early metrics confounded, noisy, or segment-inverted)
- segment-level sign flips (proxy positive but long-term negative in specific cohorts)
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid function."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def generate_synthetic_experiments(
    n_users: int = 200_000,
    n_experiments: int = 40,
    seed: int = 7,
) -> pd.DataFrame:
    """
    Generates user-level rows across multiple experiments with:
      - segments (region, device, tenure)
      - randomized treatment assignment
      - early metrics (candidate proxies)
      - long-term outcome (binary retention-like)
    
    Also bakes in failure modes:
      - segment-level sign flips where early metric uplift disagrees with long-term uplift.
    
    Args:
        n_users: Total number of user observations to generate
        n_experiments: Number of distinct experiments
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with columns:
            - exp_id: experiment identifier
            - region, device, tenure: segment attributes
            - treatment: binary treatment assignment (0=control, 1=treatment)
            - early_watch_min, early_starts, early_ctr, rebuffer_rate: early metrics
            - long_retained: long-term binary outcome
            - failure_cohort: indicator for intentionally problematic segment
    """
    rng = np.random.default_rng(seed)

    # Define segment spaces
    regions = np.array(["NA", "LATAM", "EU", "IN"])
    devices = np.array(["TV", "Mobile", "Desktop"])
    tenures = np.array(["New", "Existing"])

    # Sample experiment ids
    exp_id = rng.integers(0, n_experiments, size=n_users)

    # Sample segments
    region = rng.choice(regions, size=n_users, p=[0.35, 0.20, 0.25, 0.20])
    device = rng.choice(devices, size=n_users, p=[0.45, 0.45, 0.10])
    tenure = rng.choice(tenures, size=n_users, p=[0.30, 0.70])

    # Treatment assignment (50/50 randomized within each experiment)
    treatment = rng.integers(0, 2, size=n_users)

    # Build segment embeddings (simple numeric encodings)
    region_w = pd.Series(region).map({"NA": 0.2, "LATAM": -0.1, "EU": 0.05, "IN": -0.15}).to_numpy()
    device_w = pd.Series(device).map({"TV": 0.25, "Mobile": -0.05, "Desktop": 0.0}).to_numpy()
    tenure_w = pd.Series(tenure).map({"New": -0.1, "Existing": 0.1}).to_numpy()

    # Experiment-level base treatment effect (heterogeneous across experiments)
    exp_tau = rng.normal(0.0, 0.12, size=n_experiments)  # long-term uplift tendency
    exp_bias = rng.normal(0.0, 0.08, size=n_experiments)  # baseline shift per experiment

    # Segment interaction with treatment (heterogeneous treatment effects)
    seg_tau = (
        0.06 * (device == "TV").astype(float)
        - 0.05 * (device == "Mobile").astype(float)
        - 0.03 * (region == "IN").astype(float)
        + 0.03 * (tenure == "Existing").astype(float)
    )

    # Inject a "proxy failure" cohort:
    # For Mobile + IN + New, treatment increases early engagement but hurts long-term retention.
    failure_cohort = ((device == "Mobile") & (region == "IN") & (tenure == "New"))
    failure_long_penalty = -0.25

    # Latent user "satisfaction" and "engagement propensity"
    user_sat = rng.normal(0.0, 1.0, size=n_users) + region_w + device_w + tenure_w
    user_eng = rng.normal(0.0, 1.0, size=n_users) + 0.5 * device_w - 0.2 * tenure_w

    # Construct long-term log-odds
    base_logit = (
        -0.3
        + 0.7 * user_sat
        + 0.15 * user_eng
        + exp_bias[exp_id]
    )

    # True long-term treatment effect in log-odds
    tau_long = exp_tau[exp_id] + seg_tau
    tau_long = tau_long + failure_long_penalty * failure_cohort.astype(float)

    long_logit = base_logit + treatment * tau_long
    long_prob = sigmoid(long_logit)
    long_retained = rng.binomial(1, long_prob, size=n_users)

    # Early metrics: watch_time_1d, starts_1d, ctr_1d, rebuffer_rate_1d
    noise = rng.normal(0.0, 1.0, size=n_users)

    # Good-ish proxy: early_watch_min correlates with satisfaction and engagement
    early_watch_min = (
        25
        + 10 * user_eng
        + 6 * user_sat
        + 8 * treatment * (exp_tau[exp_id] + 0.3 * seg_tau)
        + 6 * treatment * failure_cohort.astype(float)  # boosts early in failure cohort
        + 5 * noise
    )
    early_watch_min = np.clip(early_watch_min, 0, None)

    # Another proxy: early_starts (weaker)
    early_starts = (
        1.8
        + 0.7 * sigmoid(user_eng)
        + 0.2 * sigmoid(user_sat)
        + 0.4 * treatment * (exp_tau[exp_id] + 0.2 * seg_tau)
        + 0.6 * treatment * failure_cohort.astype(float)
        + 0.3 * rng.normal(0, 1, size=n_users)
    )
    early_starts = np.clip(early_starts, 0, None)

    # CTR proxy: can be "gamed"
    ctr_base = sigmoid(0.3 * user_eng - 0.35 * user_sat + 0.1 * rng.normal(0, 1, size=n_users))
    early_ctr = ctr_base + 0.06 * treatment + 0.04 * (device == "Mobile").astype(float) * treatment
    early_ctr = np.clip(early_ctr, 0, 1)

    # Rebuffer rate: negative QoE metric
    rebuffer_rate = sigmoid(
        -0.2 * user_sat 
        + 0.25 * (region == "IN").astype(float) 
        + 0.15 * (device == "Mobile").astype(float) 
        + 0.1 * rng.normal(0, 1, size=n_users)
    )
    rebuffer_rate = np.clip(rebuffer_rate - 0.03 * treatment * (device == "TV").astype(float), 0, 1)

    df = pd.DataFrame({
        "exp_id": exp_id,
        "region": region,
        "device": device,
        "tenure": tenure,
        "treatment": treatment,
        "early_watch_min": early_watch_min,
        "early_starts": early_starts,
        "early_ctr": early_ctr,
        "rebuffer_rate": rebuffer_rate,
        "long_retained": long_retained,
        "failure_cohort": failure_cohort.astype(int),
    })

    return df

