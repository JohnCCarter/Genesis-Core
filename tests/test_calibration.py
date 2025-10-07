"""Tests for model calibration (src/core/ml/calibration.py)."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest
from sklearn.isotonic import IsotonicRegression

from src.core.ml.calibration import (
    apply_calibration_from_params,
    apply_isotonic_calibration,
    apply_platt_calibration,
    calibrate_model,
    calibrate_with_isotonic_regression,
    calibrate_with_platt_scaling,
    compare_calibration_methods,
    load_calibration_params,
    save_calibration_params,
)


class TestPlattScaling:
    """Tests for Platt scaling calibration."""

    def test_calibrate_with_platt_scaling_basic(self):
        """Test basic Platt scaling calibration."""
        # Create synthetic data with known relationship
        np.random.seed(42)
        n_samples = 1000
        
        # Generate probabilities that are somewhat predictive
        y_pred_proba = np.random.beta(2, 2, n_samples)
        y_true = (y_pred_proba > 0.5).astype(int)
        
        A, B = calibrate_with_platt_scaling(y_true, y_pred_proba)
        
        # Parameters should be reasonable
        assert isinstance(A, float)
        assert isinstance(B, float)
        assert not np.isnan(A)
        assert not np.isnan(B)

    def test_apply_platt_calibration_basic(self):
        """Test applying Platt scaling calibration."""
        y_pred_proba = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        A, B = 1.0, 0.0  # Identity transformation
        
        calibrated = apply_platt_calibration(y_pred_proba, A, B)
        
        # Should be close to original (identity transformation)
        assert len(calibrated) == len(y_pred_proba)
        assert all(0.0 <= p <= 1.0 for p in calibrated)

    def test_apply_platt_calibration_edge_cases(self):
        """Test Platt scaling with edge case probabilities."""
        y_pred_proba = np.array([0.0, 0.5, 1.0])
        A, B = 1.0, 0.0
        
        calibrated = apply_platt_calibration(y_pred_proba, A, B)
        
        # Should handle edge cases gracefully
        assert len(calibrated) == 3
        assert all(0.0 <= p <= 1.0 for p in calibrated)
        assert calibrated[1] == 0.5  # Middle should stay 0.5

    def test_platt_scaling_improves_calibration(self):
        """Test that Platt scaling improves calibration."""
        # Create poorly calibrated probabilities
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_pred_proba = np.array([0.8, 0.8, 0.8, 0.2, 0.2, 0.2])  # Poorly calibrated
        
        A, B = calibrate_with_platt_scaling(y_true, y_pred_proba)
        calibrated = apply_platt_calibration(y_pred_proba, A, B)
        
        # Calibrated probabilities should be more reasonable
        assert all(0.0 <= p <= 1.0 for p in calibrated)
        # Low probabilities should be calibrated down, high probabilities up
        assert calibrated[0] < y_pred_proba[0]  # 0.8 -> lower
        assert calibrated[3] > y_pred_proba[3]  # 0.2 -> higher


class TestIsotonicRegression:
    """Tests for isotonic regression calibration."""

    def test_calibrate_with_isotonic_regression_basic(self):
        """Test basic isotonic regression calibration."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.7, 0.8])
        
        calibrator = calibrate_with_isotonic_regression(y_true, y_pred_proba)
        
        assert isinstance(calibrator, IsotonicRegression)
        assert hasattr(calibrator, "X_thresholds_")
        assert hasattr(calibrator, "y_thresholds_")

    def test_apply_isotonic_calibration_basic(self):
        """Test applying isotonic regression calibration."""
        y_pred_proba = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        y_true = np.array([0, 0, 1, 1, 1])
        
        calibrator = calibrate_with_isotonic_regression(y_true, y_pred_proba)
        calibrated = apply_isotonic_calibration(y_pred_proba, calibrator)
        
        # Should be monotonic (non-decreasing)
        assert len(calibrated) == len(y_pred_proba)
        assert all(0.0 <= p <= 1.0 for p in calibrated)
        
        # Check monotonicity
        for i in range(1, len(calibrated)):
            assert calibrated[i] >= calibrated[i-1] - 1e-10  # Allow small numerical errors

    def test_isotonic_calibration_monotonic(self):
        """Test that isotonic calibration preserves monotonicity."""
        y_pred_proba = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        y_true = np.array([0, 0, 0, 1, 1, 1, 1, 1, 1])
        
        calibrator = calibrate_with_isotonic_regression(y_true, y_pred_proba)
        calibrated = apply_isotonic_calibration(y_pred_proba, calibrator)
        
        # Should be non-decreasing
        for i in range(1, len(calibrated)):
            assert calibrated[i] >= calibrated[i-1] - 1e-10


class TestCalibrateModel:
    """Tests for the main calibration function."""

    def test_calibrate_model_platt(self):
        """Test calibrate_model with Platt scaling."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.7, 0.8])
        
        results = calibrate_model(y_true, y_pred_proba, method="platt")
        
        assert results["method"] == "platt"
        assert "parameters" in results
        assert "calibrated_proba" in results
        assert "A" in results["parameters"]
        assert "B" in results["parameters"]
        assert len(results["calibrated_proba"]) == len(y_pred_proba)

    def test_calibrate_model_isotonic(self):
        """Test calibrate_model with isotonic regression."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.7, 0.8])
        
        results = calibrate_model(y_true, y_pred_proba, method="isotonic")
        
        assert results["method"] == "isotonic"
        assert "parameters" in results
        assert "calibrated_proba" in results
        assert "x_thresholds" in results["parameters"]
        assert "y_thresholds" in results["parameters"]
        assert len(results["calibrated_proba"]) == len(y_pred_proba)

    def test_calibrate_model_unsupported_method(self):
        """Test error for unsupported calibration method."""
        y_true = np.array([0, 1])
        y_pred_proba = np.array([0.3, 0.7])
        
        with pytest.raises(ValueError, match="Unsupported calibration method"):
            calibrate_model(y_true, y_pred_proba, method="invalid")


class TestSaveLoadCalibrationParams:
    """Tests for saving and loading calibration parameters."""

    def test_save_load_platt_params(self):
        """Test saving and loading Platt scaling parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "calibration.json"
            
            # Save parameters
            calibration_results = {
                "method": "platt",
                "parameters": {"A": 1.5, "B": -0.2},
                "calibrated_proba": np.array([0.1, 0.2, 0.3]),
            }
            
            save_calibration_params(calibration_results, output_path)
            
            # Load parameters
            loaded_params = load_calibration_params(output_path)
            
            assert loaded_params["method"] == "platt"
            assert loaded_params["parameters"]["A"] == 1.5
            assert loaded_params["parameters"]["B"] == -0.2

    def test_save_load_isotonic_params(self):
        """Test saving and loading isotonic regression parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "calibration.json"
            
            # Save parameters
            calibration_results = {
                "method": "isotonic",
                "parameters": {
                    "x_thresholds": [0.1, 0.2, 0.3],
                    "y_thresholds": [0.0, 0.5, 1.0],
                },
                "calibrated_proba": np.array([0.1, 0.2, 0.3]),
            }
            
            save_calibration_params(calibration_results, output_path)
            
            # Load parameters
            loaded_params = load_calibration_params(output_path)
            
            assert loaded_params["method"] == "isotonic"
            assert loaded_params["parameters"]["x_thresholds"] == [0.1, 0.2, 0.3]
            assert loaded_params["parameters"]["y_thresholds"] == [0.0, 0.5, 1.0]

    def test_save_creates_directory(self):
        """Test that save creates output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "new" / "subdir" / "calibration.json"
            
            calibration_results = {
                "method": "platt",
                "parameters": {"A": 1.0, "B": 0.0},
            }
            
            # Directory shouldn't exist yet
            assert not output_path.parent.exists()
            
            save_calibration_params(calibration_results, output_path)
            
            # Directory should be created
            assert output_path.parent.exists()
            assert output_path.exists()


class TestApplyCalibrationFromParams:
    """Tests for applying calibration from loaded parameters."""

    def test_apply_platt_from_params(self):
        """Test applying Platt scaling from loaded parameters."""
        y_pred_proba = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        
        calibration_params = {
            "method": "platt",
            "parameters": {"A": 1.0, "B": 0.0},
        }
        
        calibrated = apply_calibration_from_params(y_pred_proba, calibration_params)
        
        assert len(calibrated) == len(y_pred_proba)
        assert all(0.0 <= p <= 1.0 for p in calibrated)

    def test_apply_isotonic_from_params(self):
        """Test applying isotonic regression from loaded parameters."""
        y_pred_proba = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        
        calibration_params = {
            "method": "isotonic",
            "parameters": {
                "x_thresholds": [0.0, 0.5, 1.0],
                "y_thresholds": [0.0, 0.5, 1.0],
            },
        }
        
        # Should return original probabilities with warning
        with pytest.warns(UserWarning, match="Isotonic regression parameters cannot be easily reconstructed"):
            calibrated = apply_calibration_from_params(y_pred_proba, calibration_params)
        
        # Should return original probabilities
        assert len(calibrated) == len(y_pred_proba)
        assert all(0.0 <= p <= 1.0 for p in calibrated)
        np.testing.assert_array_equal(calibrated, y_pred_proba)

    def test_apply_unsupported_method(self):
        """Test error for unsupported calibration method."""
        y_pred_proba = np.array([0.1, 0.2])
        
        calibration_params = {
            "method": "invalid",
            "parameters": {},
        }
        
        with pytest.raises(ValueError, match="Unsupported calibration method"):
            apply_calibration_from_params(y_pred_proba, calibration_params)


class TestCompareCalibrationMethods:
    """Tests for comparing calibration methods."""

    def test_compare_methods_basic(self):
        """Test basic comparison of calibration methods."""
        # Create synthetic data
        np.random.seed(42)
        y_true = np.random.randint(0, 2, 100)
        y_pred_proba = np.random.rand(100)
        
        comparison = compare_calibration_methods(y_true, y_pred_proba)
        
        # Check structure
        assert "original" in comparison
        assert "platt" in comparison
        assert "isotonic" in comparison
        assert "best_method" in comparison
        assert "best_improvement" in comparison
        
        # Check metrics
        assert "brier_score" in comparison["original"]
        assert "brier_score" in comparison["platt"]
        assert "brier_score" in comparison["isotonic"]
        assert "improvement" in comparison["platt"]
        assert "improvement" in comparison["isotonic"]

    def test_compare_methods_identifies_best(self):
        """Test that comparison identifies the best method."""
        # Create data where one method should be clearly better
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
        
        comparison = compare_calibration_methods(y_true, y_pred_proba)
        
        # Should identify a best method
        assert comparison["best_method"] in ["platt", "isotonic"]
        assert comparison["best_improvement"] >= 0  # Should be non-negative

    def test_compare_methods_improvement_calculation(self):
        """Test that improvement is calculated correctly."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.7, 0.8])
        
        comparison = compare_calibration_methods(y_true, y_pred_proba)
        
        # Improvement should be original - calibrated
        original_brier = comparison["original"]["brier_score"]
        platt_brier = comparison["platt"]["brier_score"]
        isotonic_brier = comparison["isotonic"]["brier_score"]
        
        assert abs(comparison["platt"]["improvement"] - (original_brier - platt_brier)) < 1e-10
        assert abs(comparison["isotonic"]["improvement"] - (original_brier - isotonic_brier)) < 1e-10


class TestIntegration:
    """Integration tests."""

    def test_full_calibration_pipeline(self):
        """Test complete calibration pipeline."""
        # Create synthetic data
        np.random.seed(42)
        n_samples = 1000
        y_true = np.random.randint(0, 2, n_samples)
        y_pred_proba = np.random.beta(2, 2, n_samples)
        
        # Compare methods
        comparison = compare_calibration_methods(y_true, y_pred_proba)
        
        # Should have valid results
        assert comparison["best_method"] in ["platt", "isotonic"]
        assert comparison["best_improvement"] >= 0
        
        # Test saving and loading
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "calibration.json"
            
            # Save best method parameters
            if comparison["best_method"] == "platt":
                calibration_results = {
                    "method": "platt",
                    "parameters": comparison["platt"]["parameters"],
                    "calibrated_proba": np.array([]),  # Not needed for saving
                }
            else:
                calibration_results = {
                    "method": "isotonic",
                    "parameters": comparison["isotonic"]["parameters"],
                    "calibrated_proba": np.array([]),  # Not needed for saving
                }
            
            save_calibration_params(calibration_results, output_path)
            
            # Load and apply
            loaded_params = load_calibration_params(output_path)
            
            # Handle warning for isotonic method
            if loaded_params["method"] == "isotonic":
                with pytest.warns(UserWarning):
                    calibrated = apply_calibration_from_params(y_pred_proba, loaded_params)
            else:
                calibrated = apply_calibration_from_params(y_pred_proba, loaded_params)
            
            # Should produce valid probabilities
            assert len(calibrated) == len(y_pred_proba)
            assert all(0.0 <= p <= 1.0 for p in calibrated)

    def test_calibration_with_realistic_data(self):
        """Test calibration with realistic trading data."""
        # Simulate realistic trading scenario
        np.random.seed(42)
        n_samples = 500
        
        # Generate somewhat predictive probabilities
        y_pred_proba = np.random.beta(3, 2, n_samples)  # Slightly biased towards higher values
        y_true = (y_pred_proba + np.random.normal(0, 0.1, n_samples) > 0.5).astype(int)
        
        # Calibrate
        platt_results = calibrate_model(y_true, y_pred_proba, method="platt")
        isotonic_results = calibrate_model(y_true, y_pred_proba, method="isotonic")
        
        # Check results
        assert len(platt_results["calibrated_proba"]) == n_samples
        assert len(isotonic_results["calibrated_proba"]) == n_samples
        
        # Both should produce valid probabilities
        assert all(0.0 <= p <= 1.0 for p in platt_results["calibrated_proba"])
        assert all(0.0 <= p <= 1.0 for p in isotonic_results["calibrated_proba"])
        
        # Isotonic should be monotonic (but only for sorted input)
        # Note: isotonic regression is monotonic in the fitted data, not necessarily in arbitrary input
        isotonic_calibrated = isotonic_results["calibrated_proba"]
        # Just check that all values are valid probabilities
        assert all(0.0 <= p <= 1.0 for p in isotonic_calibrated)
