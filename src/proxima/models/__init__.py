"""Models and scoring algorithms for proxy metric evaluation."""

from proxima.models.baseline import (
    ProxyScore,
    compute_diff_in_means_effect,
    compute_segment_effects,
    train_long_term_model,
    score_proxies,
    find_top_fragility_segments,
)

__all__ = [
    "ProxyScore",
    "compute_diff_in_means_effect",
    "compute_segment_effects",
    "train_long_term_model",
    "score_proxies",
    "find_top_fragility_segments",
]

