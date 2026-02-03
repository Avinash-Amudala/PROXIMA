"""
PROXIMA: Proxy Metric Intelligence for Online Experiments

A system for automatically learning which early metrics are reliable proxies 
for long-term impact in A/B testing, with detection of proxy fragility under 
distribution shift.
"""

__version__ = "0.1.0"
__author__ = "Avinash Amudala"
__email__ = "aa9429@g.rit.edu"

from proxima.generator.simulate import generate_synthetic_experiments
from proxima.models.baseline import (
    score_proxies,
    train_long_term_model,
    compute_diff_in_means_effect,
    compute_segment_effects,
    find_top_fragility_segments,
)

__all__ = [
    "generate_synthetic_experiments",
    "score_proxies",
    "train_long_term_model",
    "compute_diff_in_means_effect",
    "compute_segment_effects",
    "find_top_fragility_segments",
]

