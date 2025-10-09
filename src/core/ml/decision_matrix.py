"""
Champion model selection using weighted decision matrix.

This module provides a systematic, data-driven approach to select the best
trading model by evaluating multiple performance metrics with configurable weights.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class ModelMetrics:
    """Container for all model evaluation metrics."""

    # Classification metrics
    auc: float  # ROC AUC score (0.5-1.0)
    accuracy: float  # Accuracy (0-1.0)
    log_loss: float  # Log loss (lower is better)

    # Trading metrics
    profit_factor: float  # Total profit / Total loss
    sharpe_ratio: float  # Risk-adjusted returns
    max_drawdown: float  # Maximum peak-to-trough decline (negative)
    win_rate: float  # Percentage of winning trades (0-1.0)

    # Stability metrics
    avg_trade_duration: float  # Average bars held
    num_trades: int  # Total number of trades
    consistency: float  # Win rate stability across time periods (0-1.0)


class ChampionDecisionMatrix:
    """
    Systematic model selection using weighted multi-criteria decision matrix.

    Evaluates models across multiple dimensions and calculates a weighted score
    to select the champion model objectively.

    Example:
        >>> weights = {
        ...     "auc": 0.25,
        ...     "sharpe_ratio": 0.30,
        ...     "profit_factor": 0.20,
        ...     "max_drawdown": 0.15,
        ...     "win_rate": 0.10
        ... }
        >>> matrix = ChampionDecisionMatrix(weights)
        >>> score = matrix.calculate_score(metrics)
    """

    def __init__(self, weights: dict[str, float], config: dict[str, Any] | None = None):
        """
        Initialize decision matrix with weights and normalization config.

        Args:
            weights: Dict mapping metric names to their weights (must sum to 1.0)
            config: Optional normalization config with min/max ranges per metric

        Raises:
            ValueError: If weights don't sum to 1.0 or contain invalid metrics
        """
        self.weights = weights
        self.config = config or self._default_config()
        self._validate_weights()

    def _default_config(self) -> dict[str, dict[str, float]]:
        """Default normalization ranges for metrics."""
        return {
            "auc": {"min": 0.5, "max": 1.0, "direction": "maximize"},
            "accuracy": {"min": 0.5, "max": 1.0, "direction": "maximize"},
            "log_loss": {"min": 0.0, "max": 2.0, "direction": "minimize"},
            "profit_factor": {"min": 0.5, "max": 3.0, "direction": "maximize"},
            "sharpe_ratio": {"min": -1.0, "max": 3.0, "direction": "maximize"},
            "max_drawdown": {"min": -0.5, "max": 0.0, "direction": "maximize"},
            "win_rate": {"min": 0.3, "max": 0.7, "direction": "maximize"},
            "consistency": {"min": 0.0, "max": 1.0, "direction": "maximize"},
            "avg_trade_duration": {"min": 5, "max": 100, "direction": "neutral"},
        }

    def _validate_weights(self):
        """Validate that weights sum to 1.0 and contain valid metrics."""
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0, atol=1e-6):
            raise ValueError(f"Weights must sum to 1.0, got {total:.4f}")

        valid_metrics = set(self.config.keys())
        invalid = set(self.weights.keys()) - valid_metrics
        if invalid:
            raise ValueError(f"Invalid metrics in weights: {invalid}")

    def normalize_metric(self, value: float, metric_name: str) -> float:
        """
        Normalize a metric value to 0-1 scale.

        Args:
            value: Raw metric value
            metric_name: Name of the metric for lookup in config

        Returns:
            Normalized value in [0, 1] range
        """
        cfg = self.config[metric_name]
        min_val = cfg["min"]
        max_val = cfg["max"]
        direction = cfg["direction"]

        # Clip to range
        clipped = np.clip(value, min_val, max_val)

        # Normalize to 0-1
        if max_val == min_val:
            normalized = 0.5
        else:
            normalized = (clipped - min_val) / (max_val - min_val)

        # Invert if we want to minimize
        if direction == "minimize":
            normalized = 1.0 - normalized

        return float(normalized)

    def calculate_score(self, metrics: ModelMetrics | dict) -> float:
        """
        Calculate weighted score for a model.

        Args:
            metrics: ModelMetrics instance or dict with metric values

        Returns:
            Total weighted score in [0, 10] scale
        """
        if isinstance(metrics, ModelMetrics):
            metrics = metrics.__dict__

        score = 0.0

        for metric_name, weight in self.weights.items():
            if metric_name not in metrics:
                raise KeyError(f"Metric '{metric_name}' not found in model metrics")

            raw_value = metrics[metric_name]
            normalized = self.normalize_metric(raw_value, metric_name)
            score += weight * normalized

        # Scale to 0-10 for easier interpretation
        return score * 10.0

    def rank_models(self, models: dict[str, ModelMetrics | dict]) -> pd.DataFrame:
        """
        Rank multiple models and return sorted DataFrame.

        Args:
            models: Dict mapping model names to their metrics

        Returns:
            DataFrame with models ranked by score (best first)
        """
        # Handle empty models
        if not models:
            return pd.DataFrame()

        results = []

        for model_name, metrics in models.items():
            if isinstance(metrics, ModelMetrics):
                metrics_dict = metrics.__dict__.copy()
            else:
                metrics_dict = metrics.copy()

            score = self.calculate_score(metrics)

            results.append(
                {
                    "model": model_name,
                    "total_score": score,
                    **metrics_dict,
                }
            )

        df = pd.DataFrame(results)
        df = df.sort_values("total_score", ascending=False).reset_index(drop=True)

        # Add rank column
        df.insert(0, "rank", range(1, len(df) + 1))

        return df

    def get_champion(
        self, models: dict[str, ModelMetrics | dict]
    ) -> tuple[str, float, pd.DataFrame]:
        """
        Select champion model and return name, score, and full ranking.

        Args:
            models: Dict mapping model names to their metrics

        Returns:
            Tuple of (champion_name, champion_score, ranking_dataframe)
        """
        ranking = self.rank_models(models)
        champion_name = ranking.iloc[0]["model"]
        champion_score = ranking.iloc[0]["total_score"]

        return champion_name, champion_score, ranking

    def generate_report(self, ranking: pd.DataFrame, output_path: Path | None = None) -> str:
        """
        Generate human-readable report of model ranking.

        Args:
            ranking: DataFrame from rank_models()
            output_path: Optional path to save report

        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("CHAMPION MODEL SELECTION REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Champion
        champion = ranking.iloc[0]
        report_lines.append(f"🏆 CHAMPION: {champion['model']}")
        report_lines.append(f"   Total Score: {champion['total_score']:.2f}/10.0")
        report_lines.append("")

        # Weights used
        report_lines.append("📊 Evaluation Weights:")
        for metric, weight in sorted(self.weights.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"   {metric:20s}: {weight:5.1%}")
        report_lines.append("")

        # Full ranking
        report_lines.append("📈 Model Rankings:")
        report_lines.append("-" * 80)

        for _, row in ranking.iterrows():
            rank = int(row["rank"])
            model = row["model"]
            score = row["total_score"]

            report_lines.append(f"{rank}. {model:30s} Score: {score:5.2f}/10.0")

            # Show key metrics
            if "auc" in row:
                report_lines.append(f"   AUC: {row['auc']:.3f}")
            if "sharpe_ratio" in row:
                report_lines.append(f"   Sharpe: {row['sharpe_ratio']:.2f}")
            if "profit_factor" in row:
                report_lines.append(f"   Profit Factor: {row['profit_factor']:.2f}")
            if "max_drawdown" in row:
                report_lines.append(f"   Max DD: {row['max_drawdown']:.1%}")
            report_lines.append("")

        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)

        return report


def load_weights_from_config(config_path: Path) -> dict[str, float]:
    """
    Load weights from JSON config file.

    Args:
        config_path: Path to JSON config file

    Returns:
        Dict of metric weights
    """
    import json

    with open(config_path) as f:
        config = json.load(f)

    return config.get("weights", {})
