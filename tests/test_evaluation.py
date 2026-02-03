"""
Unit tests for evaluation metrics and decision simulation
"""

import pytest
import pandas as pd
import numpy as np
from proxima.generator.simulate import generate_synthetic_experiments
from proxima.evaluation.metrics import (
    compute_effect_with_ci,
    bootstrap_effect_ci,
    compute_experiment_effects_with_ci,
    TreatmentEffectResult
)
from proxima.evaluation.decision_sim import (
    simulate_shipping_decisions,
    compare_decision_strategies,
    DecisionSimulationResult
)
from proxima.models.baseline import EARLY_METRICS


@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    return generate_synthetic_experiments(n_users=5000, n_experiments=10, seed=42)


class TestComputeEffectWithCI:
    """Test treatment effect with confidence interval."""
    
    def test_basic_computation(self, sample_data):
        """Test basic effect computation with CI."""
        result = compute_effect_with_ci(sample_data, "long_retained")
        
        assert isinstance(result, TreatmentEffectResult)
        assert isinstance(result.effect, float)
        assert isinstance(result.std_error, float)
        assert isinstance(result.p_value, float)
    
    def test_ci_bounds(self, sample_data):
        """Test confidence interval bounds."""
        result = compute_effect_with_ci(sample_data, "long_retained")
        
        # CI should contain the effect estimate
        assert result.ci_lower <= result.effect <= result.ci_upper
    
    def test_sample_sizes(self, sample_data):
        """Test sample sizes are reported."""
        result = compute_effect_with_ci(sample_data, "long_retained")
        
        assert result.n_control > 0
        assert result.n_treatment > 0
        assert result.n_control + result.n_treatment == len(sample_data)


class TestBootstrapEffectCI:
    """Test bootstrap confidence intervals."""
    
    def test_bootstrap_ci(self, sample_data):
        """Test bootstrap CI computation."""
        effect, ci_lower, ci_upper = bootstrap_effect_ci(
            sample_data, "long_retained", n_bootstrap=100, seed=42
        )
        
        assert isinstance(effect, float)
        assert ci_lower <= effect <= ci_upper
    
    def test_reproducibility(self, sample_data):
        """Test bootstrap is reproducible with same seed."""
        result1 = bootstrap_effect_ci(
            sample_data, "long_retained", n_bootstrap=100, seed=42
        )
        result2 = bootstrap_effect_ci(
            sample_data, "long_retained", n_bootstrap=100, seed=42
        )
        
        assert result1 == result2


class TestComputeExperimentEffectsWithCI:
    """Test per-experiment effects with CI."""
    
    def test_basic_computation(self, sample_data):
        """Test per-experiment effect computation."""
        result = compute_experiment_effects_with_ci(sample_data, "long_retained")
        
        assert isinstance(result, pd.DataFrame)
        assert "exp_id" in result.columns
        assert "effect" in result.columns
        assert "ci_lower" in result.columns
        assert "ci_upper" in result.columns
        assert "p_value" in result.columns
    
    def test_all_experiments_covered(self, sample_data):
        """Test all experiments are included."""
        result = compute_experiment_effects_with_ci(sample_data, "long_retained")
        
        assert len(result) == sample_data["exp_id"].nunique()


class TestSimulateShippingDecisions:
    """Test shipping decision simulation."""
    
    def test_basic_simulation(self, sample_data):
        """Test basic decision simulation."""
        result = simulate_shipping_decisions(sample_data, "early_watch_min")
        
        assert isinstance(result, DecisionSimulationResult)
        assert result.proxy_metric == "early_watch_min"
    
    def test_win_rate_bounds(self, sample_data):
        """Test win rate is bounded."""
        result = simulate_shipping_decisions(sample_data, "early_watch_min")
        
        assert 0.0 <= result.win_rate <= 1.0
    
    def test_error_rates_bounds(self, sample_data):
        """Test error rates are bounded."""
        result = simulate_shipping_decisions(sample_data, "early_watch_min")
        
        assert 0.0 <= result.false_positive_rate <= 1.0
        assert 0.0 <= result.false_negative_rate <= 1.0
    
    def test_decision_counts(self, sample_data):
        """Test decision counts are consistent."""
        result = simulate_shipping_decisions(sample_data, "early_watch_min")
        
        # Total shipped should equal correct + incorrect
        assert result.total_shipped == result.correct_ships + result.incorrect_ships
        assert result.total_shipped >= 0
        assert result.missed_opportunities >= 0


class TestCompareDecisionStrategies:
    """Test comparison of decision strategies."""
    
    def test_basic_comparison(self, sample_data):
        """Test basic strategy comparison."""
        result = compare_decision_strategies(sample_data, EARLY_METRICS)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(EARLY_METRICS) + 1  # +1 for Oracle
    
    def test_oracle_included(self, sample_data):
        """Test Oracle strategy is included."""
        result = compare_decision_strategies(sample_data, EARLY_METRICS)
        
        oracle_rows = result[result["proxy_metric"].str.contains("Oracle")]
        assert len(oracle_rows) == 1
    
    def test_sorted_by_win_rate(self, sample_data):
        """Test results are sorted by win rate."""
        result = compare_decision_strategies(sample_data, EARLY_METRICS)
        
        win_rates = result["win_rate"].tolist()
        assert win_rates == sorted(win_rates, reverse=True)
    
    def test_all_metrics_included(self, sample_data):
        """Test all proxy metrics are included."""
        result = compare_decision_strategies(sample_data, EARLY_METRICS)
        
        for metric in EARLY_METRICS:
            assert metric in result["proxy_metric"].values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

