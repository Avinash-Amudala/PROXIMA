"""
Unit tests for synthetic data generator
"""

import pytest
import pandas as pd
import numpy as np
from proxima.generator.simulate import generate_synthetic_experiments, sigmoid


class TestSigmoid:
    """Test sigmoid function."""
    
    def test_sigmoid_zero(self):
        """Test sigmoid at zero."""
        assert sigmoid(np.array([0.0]))[0] == pytest.approx(0.5, abs=1e-6)
    
    def test_sigmoid_positive(self):
        """Test sigmoid for positive values."""
        result = sigmoid(np.array([10.0]))[0]
        assert result > 0.5
        assert result < 1.0
    
    def test_sigmoid_negative(self):
        """Test sigmoid for negative values."""
        result = sigmoid(np.array([-10.0]))[0]
        assert result < 0.5
        assert result > 0.0
    
    def test_sigmoid_array(self):
        """Test sigmoid with array input."""
        x = np.array([-1.0, 0.0, 1.0])
        result = sigmoid(x)
        assert len(result) == 3
        assert result[1] == pytest.approx(0.5, abs=1e-6)


class TestGenerateSyntheticExperiments:
    """Test synthetic experiment generation."""
    
    def test_basic_generation(self):
        """Test basic data generation."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1000
        assert df["exp_id"].nunique() <= 5
    
    def test_required_columns(self):
        """Test that all required columns are present."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        required_cols = [
            "exp_id", "region", "device", "tenure", "treatment",
            "early_watch_min", "early_starts", "early_ctr", "rebuffer_rate",
            "long_retained", "failure_cohort"
        ]
        
        for col in required_cols:
            assert col in df.columns
    
    def test_treatment_assignment(self):
        """Test treatment assignment is binary."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        assert set(df["treatment"].unique()).issubset({0, 1})
    
    def test_segment_values(self):
        """Test segment values are from expected sets."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        assert set(df["region"].unique()).issubset({"NA", "LATAM", "EU", "IN"})
        assert set(df["device"].unique()).issubset({"TV", "Mobile", "Desktop"})
        assert set(df["tenure"].unique()).issubset({"New", "Existing"})
    
    def test_long_retained_binary(self):
        """Test long_retained is binary."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        assert set(df["long_retained"].unique()).issubset({0, 1})
    
    def test_failure_cohort_exists(self):
        """Test failure cohort is created."""
        df = generate_synthetic_experiments(n_users=10000, n_experiments=10, seed=42)
        
        # Should have some failure cohort members
        assert df["failure_cohort"].sum() > 0
        assert df["failure_cohort"].sum() < len(df)
    
    def test_early_metrics_positive(self):
        """Test early metrics are non-negative."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        assert (df["early_watch_min"] >= 0).all()
        assert (df["early_starts"] >= 0).all()
        assert (df["early_ctr"] >= 0).all()
        assert (df["rebuffer_rate"] >= 0).all()
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        df1 = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        df2 = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_different_seeds(self):
        """Test that different seeds produce different results."""
        df1 = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        df2 = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=43)
        
        # Should not be identical
        assert not df1.equals(df2)
    
    def test_experiment_distribution(self):
        """Test experiments are reasonably distributed."""
        df = generate_synthetic_experiments(n_users=10000, n_experiments=10, seed=42)
        
        exp_counts = df["exp_id"].value_counts()
        
        # Each experiment should have some users
        assert len(exp_counts) == 10
        # Distribution should be reasonably balanced (within 3x)
        assert exp_counts.max() / exp_counts.min() < 3.0
    
    def test_ctr_bounds(self):
        """Test CTR is bounded between 0 and 1."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        assert (df["early_ctr"] >= 0).all()
        assert (df["early_ctr"] <= 1).all()
    
    def test_rebuffer_bounds(self):
        """Test rebuffer rate is bounded between 0 and 1."""
        df = generate_synthetic_experiments(n_users=1000, n_experiments=5, seed=42)
        
        assert (df["rebuffer_rate"] >= 0).all()
        assert (df["rebuffer_rate"] <= 1).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

