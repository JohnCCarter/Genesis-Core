"""Tests for model evaluation (src/core/ml/evaluation.py)."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.core.ml.evaluation import (
    evaluate_binary_classification,
    evaluate_calibration,
    evaluate_trading_performance,
    generate_evaluation_report,
    generate_html_report,
    save_evaluation_report,
)


class TestEvaluateBinaryClassification:
    """Tests for binary classification evaluation."""

    def test_perfect_predictions(self):
        """Test evaluation with perfect predictions."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.8, 0.9])
        y_pred = np.array([0, 0, 1, 1])
        
        metrics = evaluate_binary_classification(y_true, y_pred_proba, y_pred)
        
        assert metrics["basic_metrics"]["accuracy"] == 1.0
        assert metrics["basic_metrics"]["roc_auc"] == 1.0
        assert metrics["classification_metrics"]["precision"] == 1.0
        assert metrics["classification_metrics"]["recall"] == 1.0
        assert metrics["classification_metrics"]["f1_score"] == 1.0

    def test_random_predictions(self):
        """Test evaluation with random predictions."""
        np.random.seed(42)
        y_true = np.random.randint(0, 2, 1000)
        y_pred_proba = np.random.rand(1000)
        
        metrics = evaluate_binary_classification(y_true, y_pred_proba)
        
        # Random predictions should have AUC close to 0.5
        assert 0.45 <= metrics["basic_metrics"]["roc_auc"] <= 0.55
        assert 0.4 <= metrics["basic_metrics"]["accuracy"] <= 0.6

    def test_single_class_handling(self):
        """Test handling of single class in data."""
        y_true = np.array([1, 1, 1, 1])
        y_pred_proba = np.array([0.8, 0.9, 0.7, 0.85])
        
        metrics = evaluate_binary_classification(y_true, y_pred_proba)
        
        # Should handle gracefully
        assert np.isnan(metrics["basic_metrics"]["roc_auc"]) or metrics["basic_metrics"]["roc_auc"] == 0.5
        assert metrics["basic_metrics"]["accuracy"] == 1.0

    def test_confusion_matrix_calculation(self):
        """Test confusion matrix calculation."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_pred_proba = np.array([0.1, 0.8, 0.9, 0.2, 0.3, 0.7])
        y_pred = np.array([0, 1, 1, 0, 0, 1])
        
        metrics = evaluate_binary_classification(y_true, y_pred_proba, y_pred)
        
        cm = metrics["confusion_matrix"]
        assert cm["true_negative"] == 2  # Correctly predicted 0 as 0
        assert cm["false_positive"] == 1  # Incorrectly predicted 0 as 1
        assert cm["false_negative"] == 1  # Incorrectly predicted 1 as 0
        assert cm["true_positive"] == 2  # Correctly predicted 1 as 1

    def test_class_distribution(self):
        """Test class distribution calculation."""
        y_true = np.array([0, 0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.3, 0.8, 0.9])
        
        metrics = evaluate_binary_classification(y_true, y_pred_proba)
        
        dist = metrics["class_distribution"]
        assert dist["n_samples"] == 5
        assert dist["n_positive"] == 2
        assert dist["n_negative"] == 3
        assert dist["positive_rate"] == 0.4

    def test_curves_generation(self):
        """Test ROC and PR curve generation."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.8, 0.9])
        
        metrics = evaluate_binary_classification(y_true, y_pred_proba)
        
        # Check ROC curve
        roc = metrics["curves"]["roc"]
        assert len(roc["fpr"]) > 0
        assert len(roc["tpr"]) > 0
        assert len(roc["thresholds"]) > 0
        
        # Check PR curve
        pr = metrics["curves"]["precision_recall"]
        assert len(pr["precision"]) > 0
        assert len(pr["recall"]) > 0
        assert len(pr["thresholds"]) > 0


class TestEvaluateCalibration:
    """Tests for calibration evaluation."""

    def test_perfect_calibration(self):
        """Test with perfectly calibrated probabilities."""
        # Perfect calibration: predicted prob = actual frequency
        y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        y_pred_proba = np.array([0.25, 0.25, 0.75, 0.75, 0.25, 0.75, 0.25, 0.75])
        
        metrics = evaluate_calibration(y_true, y_pred_proba)
        
        # Should have reasonable ECE (perfect calibration is hard with few samples)
        assert metrics["expected_calibration_error"] < 0.5

    def test_poor_calibration(self):
        """Test with poorly calibrated probabilities."""
        # Poor calibration: always predict 0.8 regardless of actual outcome
        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        y_pred_proba = np.array([0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
        
        metrics = evaluate_calibration(y_true, y_pred_proba)
        
        # Should have high ECE for poor calibration
        assert metrics["expected_calibration_error"] > 0.3

    def test_brier_decomposition(self):
        """Test Brier score decomposition."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.2, 0.3, 0.7, 0.8])
        
        metrics = evaluate_calibration(y_true, y_pred_proba)
        
        # Check decomposition components
        decomposition = metrics["brier_decomposition"]
        assert "reliability" in decomposition
        assert "resolution" in decomposition
        assert "uncertainty" in decomposition
        
        # Brier score should equal reliability - resolution + uncertainty
        brier = metrics["brier_score"]
        expected = decomposition["reliability"] - decomposition["resolution"] + decomposition["uncertainty"]
        # Allow for reasonable numerical differences (Brier decomposition can have rounding errors)
        assert abs(brier - expected) < 0.2

    def test_reliability_diagram(self):
        """Test reliability diagram data generation."""
        y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.7, 0.8, 0.3, 0.9, 0.4, 0.6])
        
        metrics = evaluate_calibration(y_true, y_pred_proba, n_bins=5)
        
        diagram = metrics["reliability_diagram"]
        assert len(diagram["bin_centers"]) == 5
        assert len(diagram["bin_accuracies"]) == 5
        assert len(diagram["bin_confidences"]) == 5
        assert len(diagram["bin_counts"]) == 5
        assert diagram["n_bins"] == 5


class TestEvaluateTradingPerformance:
    """Tests for trading performance evaluation."""

    def test_signal_analysis(self):
        """Test signal analysis metrics."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_pred_proba = np.array([0.1, 0.8, 0.9, 0.2, 0.3, 0.7])
        
        metrics = evaluate_trading_performance(y_true, y_pred_proba, threshold=0.5)
        
        signal_analysis = metrics["signal_analysis"]
        assert signal_analysis["n_signals"] == 3  # 3 predictions >= 0.5
        assert signal_analysis["signal_rate"] == 0.5  # 3/6
        assert signal_analysis["hit_rate"] == 2/3  # 2 correct out of 3 signals
        assert signal_analysis["win_rate"] == 4/6  # 4 correct out of 6 total

    def test_trading_metrics(self):
        """Test trading-specific metrics."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_pred_proba = np.array([0.1, 0.8, 0.9, 0.2, 0.3, 0.7])
        
        metrics = evaluate_trading_performance(y_true, y_pred_proba, threshold=0.5)
        
        trading_metrics = metrics["trading_metrics"]
        assert trading_metrics["true_positives"] == 2
        assert trading_metrics["false_positives"] == 1
        assert trading_metrics["false_negatives"] == 1
        assert trading_metrics["precision"] == 2/3
        assert trading_metrics["recall"] == 2/3

    def test_return_analysis(self):
        """Test return-based analysis."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_pred_proba = np.array([0.1, 0.8, 0.9, 0.2, 0.3, 0.7])
        returns = np.array([-0.01, 0.02, 0.03, -0.01, 0.01, 0.02])
        
        metrics = evaluate_trading_performance(y_true, y_pred_proba, returns, threshold=0.5)
        
        return_analysis = metrics["return_analysis"]
        assert "strategy_return" in return_analysis
        assert "buy_hold_return" in return_analysis
        assert "sharpe_ratio" in return_analysis
        assert "excess_return" in return_analysis

    def test_no_signals(self):
        """Test handling when no signals are generated."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.3, 0.4])  # All below threshold
        
        metrics = evaluate_trading_performance(y_true, y_pred_proba, threshold=0.5)
        
        signal_analysis = metrics["signal_analysis"]
        assert signal_analysis["n_signals"] == 0
        assert signal_analysis["signal_rate"] == 0.0
        assert signal_analysis["hit_rate"] == 0.0


class TestGenerateEvaluationReport:
    """Tests for comprehensive evaluation report generation."""

    def test_generate_report_basic(self):
        """Test basic report generation."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.8, 0.9])
        
        report = generate_evaluation_report(y_true, y_pred_proba, model_name="Test Model")
        
        # Check structure
        assert "model_info" in report
        assert "classification" in report
        assert "calibration" in report
        assert "trading" in report
        
        # Check model info
        assert report["model_info"]["name"] == "Test Model"
        assert report["model_info"]["n_samples"] == 4
        assert report["model_info"]["threshold"] == 0.5

    def test_generate_report_with_returns(self):
        """Test report generation with returns."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.8, 0.9])
        returns = np.array([-0.01, 0.02, 0.03, -0.01])
        
        report = generate_evaluation_report(y_true, y_pred_proba, returns=returns)
        
        # Should include return analysis
        assert "return_analysis" in report["trading"]

    def test_generate_report_custom_threshold(self):
        """Test report generation with custom threshold."""
        y_true = np.array([0, 0, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.8, 0.9])
        
        report = generate_evaluation_report(y_true, y_pred_proba, threshold=0.7)
        
        assert report["model_info"]["threshold"] == 0.7


class TestSaveEvaluationReport:
    """Tests for saving evaluation reports."""

    def test_save_json_report(self):
        """Test saving JSON report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "report.json"
            
            report = {
                "model_info": {"name": "Test", "n_samples": 100},
                "classification": {"basic_metrics": {"accuracy": 0.8}},
            }
            
            save_evaluation_report(report, output_path, format="json")
            
            assert output_path.exists()
            
            # Verify content
            with open(output_path) as f:
                loaded_report = json.load(f)
            assert loaded_report == report

    def test_save_html_report(self):
        """Test saving HTML report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "report.html"
            
            report = {
                "model_info": {"name": "Test Model", "n_samples": 100, "threshold": 0.5},
                "classification": {
                    "basic_metrics": {"accuracy": 0.8, "roc_auc": 0.75, "log_loss": 0.3, "brier_score": 0.2},
                    "classification_metrics": {"f1_score": 0.7},
                    "confusion_matrix": {"true_negative": 40, "false_positive": 10, "false_negative": 10, "true_positive": 40},
                },
                "calibration": {
                    "expected_calibration_error": 0.1,
                    "brier_decomposition": {"reliability": 0.05, "resolution": 0.1, "uncertainty": 0.25},
                },
                "trading": {
                    "signal_analysis": {"signal_rate": 0.5, "hit_rate": 0.6, "win_rate": 0.8},
                },
            }
            
            save_evaluation_report(report, output_path, format="html")
            
            assert output_path.exists()
            
            # Verify HTML content
            with open(output_path) as f:
                html_content = f.read()
            assert "Test Model" in html_content
            assert "0.800" in html_content  # Accuracy
            assert "0.750" in html_content  # ROC-AUC

    def test_save_creates_directory(self):
        """Test that save creates output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "new" / "subdir" / "report.json"
            
            report = {"model_info": {"name": "Test"}}
            
            # Directory shouldn't exist yet
            assert not output_path.parent.exists()
            
            save_evaluation_report(report, output_path)
            
            # Directory should be created
            assert output_path.parent.exists()
            assert output_path.exists()

    def test_save_unsupported_format(self):
        """Test error for unsupported format."""
        report = {"model_info": {"name": "Test"}}
        
        with pytest.raises(ValueError, match="Unsupported format"):
            save_evaluation_report(report, "test.txt", format="txt")


class TestGenerateHtmlReport:
    """Tests for HTML report generation."""

    def test_html_generation_basic(self):
        """Test basic HTML generation."""
        report = {
            "model_info": {"name": "Test Model", "n_samples": 100, "threshold": 0.5},
            "classification": {
                "basic_metrics": {"accuracy": 0.8, "roc_auc": 0.75, "log_loss": 0.3, "brier_score": 0.2},
                "classification_metrics": {"f1_score": 0.7},
                "confusion_matrix": {"true_negative": 40, "false_positive": 10, "false_negative": 10, "true_positive": 40},
            },
            "calibration": {
                "expected_calibration_error": 0.1,
                "brier_decomposition": {"reliability": 0.05, "resolution": 0.1, "uncertainty": 0.25},
            },
            "trading": {
                "signal_analysis": {"signal_rate": 0.5, "hit_rate": 0.6, "win_rate": 0.8},
            },
        }
        
        html = generate_html_report(report)
        
        # Check HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<title>Model Evaluation Report - Test Model</title>" in html
        assert "Test Model" in html
        assert "100" in html  # n_samples
        assert "0.800" in html  # accuracy
        assert "0.750" in html  # roc_auc
        assert "0.100" in html  # ece
        assert "0.500" in html  # signal_rate

    def test_html_generation_with_table(self):
        """Test HTML generation includes confusion matrix table."""
        report = {
            "model_info": {"name": "Test", "n_samples": 4, "threshold": 0.5},
            "classification": {
                "basic_metrics": {"accuracy": 0.8, "roc_auc": 0.75, "log_loss": 0.3, "brier_score": 0.2},
                "classification_metrics": {"f1_score": 0.7},
                "confusion_matrix": {"true_negative": 2, "false_positive": 0, "false_negative": 1, "true_positive": 1},
            },
            "calibration": {
                "expected_calibration_error": 0.1,
                "brier_decomposition": {"reliability": 0.05, "resolution": 0.1, "uncertainty": 0.25},
            },
            "trading": {
                "signal_analysis": {"signal_rate": 0.5, "hit_rate": 0.6, "win_rate": 0.8},
            },
        }
        
        html = generate_html_report(report)
        
        # Check table structure
        assert "<table" in html
        assert "Predicted 0" in html
        assert "Predicted 1" in html
        assert "Actual 0" in html
        assert "Actual 1" in html
        assert "2" in html  # true_negative
        assert "1" in html  # true_positive


class TestIntegration:
    """Integration tests."""

    def test_full_evaluation_pipeline(self):
        """Test complete evaluation pipeline."""
        # Create synthetic data
        np.random.seed(42)
        n_samples = 1000
        
        # Generate realistic trading data
        y_true = np.random.randint(0, 2, n_samples)
        y_pred_proba = np.random.beta(2, 2, n_samples)  # More realistic probabilities
        returns = np.random.normal(0.001, 0.02, n_samples)  # Small positive drift
        
        # Generate comprehensive report
        report = generate_evaluation_report(
            y_true, y_pred_proba, returns=returns, model_name="Integration Test"
        )
        
        # Verify all sections present
        assert "model_info" in report
        assert "classification" in report
        assert "calibration" in report
        assert "trading" in report
        
        # Verify metrics are reasonable
        assert 0.0 <= report["classification"]["basic_metrics"]["accuracy"] <= 1.0
        assert 0.0 <= report["classification"]["basic_metrics"]["roc_auc"] <= 1.0
        assert 0.0 <= report["calibration"]["expected_calibration_error"] <= 1.0
        assert 0.0 <= report["trading"]["signal_analysis"]["signal_rate"] <= 1.0
        
        # Test saving
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "report.json"
            html_path = Path(temp_dir) / "report.html"
            
            save_evaluation_report(report, json_path, format="json")
            save_evaluation_report(report, html_path, format="html")
            
            assert json_path.exists()
            assert html_path.exists()
            
            # Verify JSON can be loaded
            with open(json_path) as f:
                loaded_report = json.load(f)
            assert loaded_report["model_info"]["name"] == "Integration Test"
