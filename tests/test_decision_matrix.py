"""Tests for champion decision matrix."""

import pytest

from core.ml.decision_matrix import ChampionDecisionMatrix, ModelMetrics


class TestModelMetrics:
    """Tests for ModelMetrics dataclass."""

    def test_model_metrics_creation(self):
        """Test creating ModelMetrics instance."""
        metrics = ModelMetrics(
            auc=0.75,
            accuracy=0.72,
            log_loss=0.5,
            profit_factor=1.5,
            sharpe_ratio=1.2,
            max_drawdown=-0.15,
            win_rate=0.58,
            avg_trade_duration=12.5,
            num_trades=150,
            consistency=0.8,
        )

        assert metrics.auc == 0.75
        assert metrics.profit_factor == 1.5
        assert metrics.max_drawdown == -0.15


class TestChampionDecisionMatrix:
    """Tests for ChampionDecisionMatrix."""

    def test_weights_validation_valid(self):
        """Test that valid weights pass validation."""
        weights = {
            "auc": 0.25,
            "sharpe_ratio": 0.30,
            "profit_factor": 0.20,
            "max_drawdown": 0.15,
            "win_rate": 0.10,
        }

        matrix = ChampionDecisionMatrix(weights)
        assert matrix.weights == weights

    def test_weights_validation_invalid_sum(self):
        """Test that weights not summing to 1.0 raise error."""
        weights = {
            "auc": 0.25,
            "sharpe_ratio": 0.30,
            "profit_factor": 0.20,
        }  # Sum = 0.75, not 1.0

        with pytest.raises(ValueError, match="must sum to 1.0"):
            ChampionDecisionMatrix(weights)

    def test_weights_validation_invalid_metric(self):
        """Test that invalid metric names raise error."""
        weights = {
            "invalid_metric": 0.5,
            "auc": 0.5,
        }

        with pytest.raises(ValueError, match="Invalid metrics"):
            ChampionDecisionMatrix(weights)

    def test_normalize_metric_maximize(self):
        """Test normalization for metrics to maximize."""
        weights = {"auc": 1.0}
        matrix = ChampionDecisionMatrix(weights)

        # AUC: min=0.5, max=1.0
        assert matrix.normalize_metric(0.5, "auc") == 0.0  # At min
        assert matrix.normalize_metric(1.0, "auc") == 1.0  # At max
        assert matrix.normalize_metric(0.75, "auc") == 0.5  # Midpoint

    def test_normalize_metric_minimize(self):
        """Test normalization for metrics to minimize."""
        weights = {"log_loss": 1.0}
        matrix = ChampionDecisionMatrix(weights)

        # Log loss: min=0.0, max=2.0, direction=minimize
        # Lower is better, so normalized value is inverted
        assert matrix.normalize_metric(0.0, "log_loss") == 1.0  # Best (lowest)
        assert matrix.normalize_metric(2.0, "log_loss") == 0.0  # Worst (highest)
        assert matrix.normalize_metric(1.0, "log_loss") == 0.5  # Midpoint

    def test_normalize_metric_clipping(self):
        """Test that values outside range are clipped."""
        weights = {"auc": 1.0}
        matrix = ChampionDecisionMatrix(weights)

        # Values outside [0.5, 1.0] should be clipped
        assert matrix.normalize_metric(1.5, "auc") == 1.0  # Clipped to max
        assert matrix.normalize_metric(0.0, "auc") == 0.0  # Clipped to min

    def test_calculate_score(self):
        """Test score calculation with weighted metrics."""
        weights = {
            "auc": 0.50,  # 50%
            "sharpe_ratio": 0.50,  # 50%
        }
        matrix = ChampionDecisionMatrix(weights)

        metrics = ModelMetrics(
            auc=0.75,  # Normalized: 0.5 (midpoint between 0.5-1.0)
            accuracy=0.70,
            log_loss=0.5,
            profit_factor=1.5,
            sharpe_ratio=1.5,  # Normalized: 0.625 (midpoint between -1.0 - 3.0)
            max_drawdown=-0.15,
            win_rate=0.55,
            avg_trade_duration=10.0,
            num_trades=100,
            consistency=0.7,
        )

        score = matrix.calculate_score(metrics)

        # Expected: (0.5 * 0.5 + 0.625 * 0.5) * 10 = 5.625
        assert 5.6 <= score <= 5.7

    def test_calculate_score_dict_input(self):
        """Test that dict input works for calculate_score."""
        weights = {"auc": 0.5, "sharpe_ratio": 0.5}
        matrix = ChampionDecisionMatrix(weights)

        metrics_dict = {
            "auc": 0.75,
            "accuracy": 0.70,
            "log_loss": 0.5,
            "profit_factor": 1.5,
            "sharpe_ratio": 1.5,
            "max_drawdown": -0.15,
            "win_rate": 0.55,
            "avg_trade_duration": 10.0,
            "num_trades": 100,
            "consistency": 0.7,
        }

        score = matrix.calculate_score(metrics_dict)
        assert 5.0 <= score <= 6.0

    def test_rank_models(self):
        """Test ranking multiple models."""
        weights = {
            "auc": 0.40,
            "sharpe_ratio": 0.30,
            "profit_factor": 0.30,
        }
        matrix = ChampionDecisionMatrix(weights)

        models = {
            "model_a": ModelMetrics(
                auc=0.80,
                accuracy=0.75,
                log_loss=0.4,
                profit_factor=2.0,
                sharpe_ratio=1.5,
                max_drawdown=-0.10,
                win_rate=0.60,
                avg_trade_duration=10.0,
                num_trades=100,
                consistency=0.8,
            ),
            "model_b": ModelMetrics(
                auc=0.75,
                accuracy=0.72,
                log_loss=0.5,
                profit_factor=1.8,
                sharpe_ratio=1.3,
                max_drawdown=-0.15,
                win_rate=0.58,
                avg_trade_duration=12.0,
                num_trades=90,
                consistency=0.75,
            ),
            "model_c": ModelMetrics(
                auc=0.85,
                accuracy=0.78,
                log_loss=0.35,
                profit_factor=2.2,
                sharpe_ratio=1.8,
                max_drawdown=-0.08,
                win_rate=0.62,
                avg_trade_duration=9.0,
                num_trades=110,
                consistency=0.85,
            ),
        }

        ranking = matrix.rank_models(models)

        # model_c should win (best metrics)
        assert ranking.iloc[0]["model"] == "model_c"
        assert ranking.iloc[0]["rank"] == 1

        # Check all models are present
        assert len(ranking) == 3
        assert set(ranking["model"]) == {"model_a", "model_b", "model_c"}

        # Check scores are descending
        scores = ranking["total_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_get_champion(self):
        """Test champion selection."""
        weights = {
            "auc": 0.50,
            "profit_factor": 0.50,
        }
        matrix = ChampionDecisionMatrix(weights)

        models = {
            "baseline": ModelMetrics(
                auc=0.60,
                accuracy=0.55,
                log_loss=0.8,
                profit_factor=1.2,
                sharpe_ratio=0.5,
                max_drawdown=-0.20,
                win_rate=0.52,
                avg_trade_duration=15.0,
                num_trades=80,
                consistency=0.6,
            ),
            "champion": ModelMetrics(
                auc=0.85,
                accuracy=0.80,
                log_loss=0.3,
                profit_factor=2.5,
                sharpe_ratio=2.0,
                max_drawdown=-0.05,
                win_rate=0.65,
                avg_trade_duration=8.0,
                num_trades=120,
                consistency=0.9,
            ),
        }

        champion_name, champion_score, ranking = matrix.get_champion(models)

        assert champion_name == "champion"
        assert champion_score > 7.0  # Should be high score
        assert len(ranking) == 2

    def test_generate_report(self):
        """Test report generation."""
        weights = {
            "auc": 0.50,
            "profit_factor": 0.50,
        }
        matrix = ChampionDecisionMatrix(weights)

        models = {
            "model_a": ModelMetrics(
                auc=0.75,
                accuracy=0.70,
                log_loss=0.5,
                profit_factor=1.5,
                sharpe_ratio=1.2,
                max_drawdown=-0.15,
                win_rate=0.55,
                avg_trade_duration=10.0,
                num_trades=100,
                consistency=0.7,
            ),
        }

        ranking = matrix.rank_models(models)
        report = matrix.generate_report(ranking)

        # Check report contains key information
        assert "CHAMPION MODEL SELECTION REPORT" in report
        assert "CHAMPION: model_a" in report
        assert "Evaluation Weights" in report
        assert "auc" in report
        assert "profit_factor" in report


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_metric_in_calculate_score(self):
        """Test error when metric is missing from input."""
        weights = {"auc": 1.0}
        matrix = ChampionDecisionMatrix(weights)

        incomplete_metrics = {
            "sharpe_ratio": 1.5,  # Missing 'auc'
        }

        with pytest.raises(KeyError, match="auc"):
            matrix.calculate_score(incomplete_metrics)

    def test_empty_models_in_rank(self):
        """Test behavior with empty models dict."""
        weights = {"auc": 1.0}
        matrix = ChampionDecisionMatrix(weights)

        ranking = matrix.rank_models({})
        assert len(ranking) == 0

    def test_single_model_ranking(self):
        """Test ranking with only one model."""
        weights = {"auc": 1.0}
        matrix = ChampionDecisionMatrix(weights)

        models = {
            "only_model": ModelMetrics(
                auc=0.75,
                accuracy=0.70,
                log_loss=0.5,
                profit_factor=1.5,
                sharpe_ratio=1.2,
                max_drawdown=-0.15,
                win_rate=0.55,
                avg_trade_duration=10.0,
                num_trades=100,
                consistency=0.7,
            ),
        }

        ranking = matrix.rank_models(models)
        assert len(ranking) == 1
        assert ranking.iloc[0]["rank"] == 1
        assert ranking.iloc[0]["model"] == "only_model"
