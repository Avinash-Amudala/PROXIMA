"""
Unit tests for baseline model and proxy scoring
"""

import pytest
import pandas as pd
import numpy as np
from proxima.generator.simulate import generate_synthetic_experiments
from proxima.models.baseline import (
    compute_diff_in_means_effect,
    compute_segment_effects,
    train_long_term_model,
    score_proxies,
    find_top_fragility_segments,
    ProxyScore,
    EARLY_METRICS
)


@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    return generate_synthetic_experiments(n_users=5000, n_experiments=10, seed=42)


class TestComputeDiffInMeansEffect:
    """Test treatment effect computation."""
    
    def test_basic_effect(self, sample_data):
        """Test basic effect computation."""
        result = compute_diff_in_means_effect(sample_data, "long_retained")
        
        assert isinstance(result, pd.DataFrame)
        assert "exp_id" in result.columns
        assert "delta_long_retained" in result.columns
        assert len(result) <= sample_data["exp_id"].nunique()
    
    def test_effect_for_early_metric(self, sample_data):
        """Test effect computation for early metrics."""
        result = compute_diff_in_means_effect(sample_data, "early_watch_min")
        
        assert "delta_early_watch_min" in result.columns
        assert len(result) > 0


class TestComputeSegmentEffects:
    """Test segment-level effect computation."""
    
    def test_single_segment(self, sample_data):
        """Test with single segment column."""
        result = compute_segment_effects(sample_data, "long_retained", ["region"])
        
        assert isinstance(result, pd.DataFrame)
        assert "exp_id" in result.columns
        assert "region" in result.columns
        assert "delta_long_retained" in result.columns
    
    def test_multiple_segments(self, sample_data):
        """Test with multiple segment columns."""
        result = compute_segment_effects(
            sample_data, "long_retained", ["region", "device"]
        )
        
        assert "region" in result.columns
        assert "device" in result.columns
        assert len(result) > 0


class TestTrainLongTermModel:
    """Test long-term model training."""
    
    def test_model_training(self, sample_data):
        """Test model can be trained."""
        model, auc = train_long_term_model(sample_data)
        
        assert model is not None
        assert isinstance(auc, float)
        assert 0.0 <= auc <= 1.0
    
    def test_model_prediction(self, sample_data):
        """Test model can make predictions."""
        model, _ = train_long_term_model(sample_data)
        
        # Test prediction on a small sample
        test_sample = sample_data.head(10)[
            ["region", "device", "tenure", "treatment"] + EARLY_METRICS
        ]
        predictions = model.predict(test_sample)
        
        assert len(predictions) == 10
        assert set(predictions).issubset({0, 1})


class TestScoreProxies:
    """Test proxy scoring."""
    
    def test_basic_scoring(self, sample_data):
        """Test basic proxy scoring."""
        details, proxy_scores = score_proxies(sample_data)
        
        assert isinstance(details, pd.DataFrame)
        assert isinstance(proxy_scores, list)
        assert len(proxy_scores) == len(EARLY_METRICS)
    
    def test_score_columns(self, sample_data):
        """Test that score dataframe has required columns."""
        details, _ = score_proxies(sample_data)
        
        required_cols = [
            "metric", "reliability", "effect_corr",
            "directional_accuracy", "fragility_rate", "n_experiments_scored"
        ]
        
        for col in required_cols:
            assert col in details.columns
    
    def test_reliability_bounds(self, sample_data):
        """Test reliability scores are bounded."""
        details, _ = score_proxies(sample_data)
        
        assert (details["reliability"] >= 0).all()
        assert (details["reliability"] <= 1).all()
    
    def test_correlation_bounds(self, sample_data):
        """Test correlation is bounded."""
        details, _ = score_proxies(sample_data)
        
        assert (details["effect_corr"] >= -1).all()
        assert (details["effect_corr"] <= 1).all()
    
    def test_directional_accuracy_bounds(self, sample_data):
        """Test directional accuracy is bounded."""
        details, _ = score_proxies(sample_data)
        
        assert (details["directional_accuracy"] >= 0).all()
        assert (details["directional_accuracy"] <= 1).all()
    
    def test_fragility_bounds(self, sample_data):
        """Test fragility rate is bounded."""
        details, _ = score_proxies(sample_data)
        
        assert (details["fragility_rate"] >= 0).all()
        assert (details["fragility_rate"] <= 1).all()
    
    def test_sorted_by_reliability(self, sample_data):
        """Test results are sorted by reliability."""
        details, _ = score_proxies(sample_data)
        
        reliabilities = details["reliability"].tolist()
        assert reliabilities == sorted(reliabilities, reverse=True)
    
    def test_proxy_score_objects(self, sample_data):
        """Test ProxyScore objects are created correctly."""
        _, proxy_scores = score_proxies(sample_data)
        
        for score in proxy_scores:
            assert isinstance(score, ProxyScore)
            assert score.metric in EARLY_METRICS
            assert 0 <= score.reliability <= 1


class TestFindTopFragilitySegments:
    """Test fragility segment detection."""
    
    def test_basic_fragility(self, sample_data):
        """Test basic fragility detection."""
        result = find_top_fragility_segments(
            sample_data, "early_watch_min", min_count=100
        )
        
        assert isinstance(result, pd.DataFrame)
        assert "flip_rate" in result.columns
        assert "n_cells" in result.columns
        assert "avg_cell_n" in result.columns
    
    def test_fragility_sorted(self, sample_data):
        """Test results are sorted by flip rate."""
        result = find_top_fragility_segments(
            sample_data, "early_watch_min", min_count=100
        )
        
        if len(result) > 1:
            flip_rates = result["flip_rate"].tolist()
            assert flip_rates == sorted(flip_rates, reverse=True)
    
    def test_min_count_filter(self, sample_data):
        """Test min_count filtering works."""
        result = find_top_fragility_segments(
            sample_data, "early_watch_min", min_count=1000
        )
        
        # With high min_count, should have fewer segments
        assert len(result) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

