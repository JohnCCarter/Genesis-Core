"""Tests for visualization utilities."""

import tempfile
from pathlib import Path

import matplotlib
import pandas as pd
import pytest

# Use non-interactive backend for testing
matplotlib.use("Agg")

from core.ml.visualization import (
    create_champion_summary,
    create_comparison_bars,
    create_metric_heatmap,
    create_radar_chart,
)


class TestRadarChart:
    """Tests for radar chart creation."""

    def test_create_radar_chart_basic(self):
        """Test basic radar chart creation."""
        models = {
            "model_a": {"auc": 0.8, "sharpe": 0.7, "profit": 0.9},
            "model_b": {"auc": 0.75, "sharpe": 0.6, "profit": 0.85},
        }
        metrics = ["auc", "sharpe", "profit"]

        fig = create_radar_chart(models, metrics)

        assert fig is not None
        assert len(fig.axes) == 1
        ax = fig.axes[0]
        assert len(ax.lines) == 2  # Two models

    def test_create_radar_chart_with_save(self):
        """Test radar chart with file save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "radar.png"

            models = {
                "model_a": {"auc": 0.8, "sharpe": 0.7, "profit": 0.9},
            }
            metrics = ["auc", "sharpe", "profit"]

            fig = create_radar_chart(models, metrics, output_path)

            assert fig is not None
            assert output_path.exists()

    def test_radar_chart_empty_models(self):
        """Test error with no models."""
        with pytest.raises(ValueError, match="No models"):
            create_radar_chart({}, ["auc", "sharpe", "profit"])

    def test_radar_chart_insufficient_metrics(self):
        """Test error with less than 3 metrics."""
        models = {"model_a": {"auc": 0.8, "sharpe": 0.7}}

        with pytest.raises(ValueError, match="at least 3 metrics"):
            create_radar_chart(models, ["auc", "sharpe"])


class TestComparisonBars:
    """Tests for comparison bar charts."""

    def test_create_comparison_bars(self):
        """Test comparison bar chart creation."""
        df = pd.DataFrame(
            {
                "model": ["model_a", "model_b"],
                "auc": [0.8, 0.75],
                "sharpe": [1.5, 1.3],
                "profit": [2.0, 1.8],
            }
        )

        fig = create_comparison_bars(df, ["auc", "sharpe", "profit"])

        assert fig is not None
        assert len(fig.axes) == 3  # Three metrics

    def test_comparison_bars_single_metric(self):
        """Test with single metric."""
        df = pd.DataFrame({"model": ["model_a", "model_b"], "auc": [0.8, 0.75]})

        fig = create_comparison_bars(df, ["auc"])

        assert fig is not None
        assert len(fig.axes) == 1

    def test_comparison_bars_empty_df(self):
        """Test error with empty DataFrame."""
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Empty"):
            create_comparison_bars(df, ["auc"])


class TestChampionSummary:
    """Tests for champion summary visualization."""

    def test_create_champion_summary(self):
        """Test champion summary creation."""
        df = pd.DataFrame(
            {
                "model": ["champion", "baseline"],
                "total_score": [8.5, 6.2],
                "auc": [0.85, 0.70],
                "sharpe_ratio": [1.8, 1.2],
                "profit_factor": [2.2, 1.5],
            }
        )

        weights = {"auc": 0.33, "sharpe_ratio": 0.33, "profit_factor": 0.34}

        fig = create_champion_summary(df, weights, "champion")

        assert fig is not None
        assert len(fig.axes) == 3  # Radar (polar), scores, weights

    def test_champion_summary_empty_df(self):
        """Test error with empty DataFrame."""
        df = pd.DataFrame()
        weights = {"auc": 1.0}

        with pytest.raises(ValueError, match="Empty"):
            create_champion_summary(df, weights, "champion")


class TestMetricHeatmap:
    """Tests for metric heatmap."""

    def test_create_metric_heatmap(self):
        """Test heatmap creation."""
        df = pd.DataFrame(
            {
                "model": ["model_a", "model_b", "model_c"],
                "auc": [0.8, 0.75, 0.85],
                "sharpe": [1.5, 1.3, 1.7],
                "profit": [2.0, 1.8, 2.1],
            }
        )

        fig = create_metric_heatmap(df, ["auc", "sharpe", "profit"])

        assert fig is not None
        assert len(fig.axes) == 2  # Main axis + colorbar

    def test_heatmap_with_save(self):
        """Test heatmap with file save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "heatmap.png"

            df = pd.DataFrame(
                {
                    "model": ["model_a"],
                    "auc": [0.8],
                    "sharpe": [1.5],
                    "profit": [2.0],
                }
            )

            fig = create_metric_heatmap(df, ["auc", "sharpe", "profit"], output_path)

            assert fig is not None
            assert output_path.exists()

    def test_heatmap_empty_df(self):
        """Test error with empty DataFrame."""
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Empty"):
            create_metric_heatmap(df, ["auc"])
