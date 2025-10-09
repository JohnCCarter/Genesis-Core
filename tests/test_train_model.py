"""Tests for ML training script (scripts/train_model.py)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from scripts.train_model import (
    align_features_with_labels,
    convert_to_model_json,
    generate_training_labels,
    load_features_and_prices,
    save_model_and_metrics,
    split_data_chronological,
    train_buy_sell_models,
)


class TestLoadFeaturesAndPrices:
    """Tests for loading features and prices."""

    def test_load_features_and_prices_success(self):
        """Test successful loading of features and prices."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock features file
            features_data = {
                "timestamp": pd.date_range("2024-01-01", periods=10, freq="15min"),
                "ema_delta_pct": np.random.randn(10),
                "rsi": np.random.randn(10),
            }
            features_df = pd.DataFrame(features_data)
            features_path = temp_path / "tBTCUSD_15m_features.parquet"
            features_df.to_parquet(features_path)

            # Create mock candles file
            candles_data = {
                "timestamp": pd.date_range("2024-01-01", periods=10, freq="15min"),
                "open": np.random.randn(10) + 50000,
                "high": np.random.randn(10) + 50100,
                "low": np.random.randn(10) + 49900,
                "close": np.random.randn(10) + 50000,
                "volume": np.random.rand(10) * 1000,
            }
            candles_df = pd.DataFrame(candles_data)
            candles_path = temp_path / "tBTCUSD_15m.parquet"
            candles_df.to_parquet(candles_path)

            # Create data directory structure
            data_dir = temp_path / "data" / "features"
            data_dir.mkdir(parents=True)
            candles_dir = temp_path / "data" / "candles"
            candles_dir.mkdir(parents=True)

            # Move files to correct locations
            features_path = data_dir / "tBTCUSD_15m_features.parquet"
            features_df.to_parquet(features_path)
            candles_path = candles_dir / "tBTCUSD_15m.parquet"
            candles_df.to_parquet(candles_path)

            # Mock the data directory for both modules
            def path_side_effect(x):
                if isinstance(x, str):
                    if x.startswith("data/"):
                        return temp_path / x
                    return Path(x)
                return Path(x)

            with patch("scripts.train_model.Path", side_effect=path_side_effect):
                with patch("core.utils.data_loader.Path", side_effect=path_side_effect):
                    features, prices, candles = load_features_and_prices("tBTCUSD", "15m")

                    assert len(features) == 10
                    assert len(prices) == 10
                    assert len(candles) == 10
                    assert "ema_delta_pct" in features.columns
                    assert "rsi" in features.columns
                    assert all(isinstance(p, int | float) for p in prices)

    def test_load_features_file_not_found(self):
        """Test error when features file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            def path_side_effect(x):
                if isinstance(x, str):
                    if x.startswith("data/"):
                        return temp_path / x
                    return Path(x)
                return Path(x)

            with patch("scripts.train_model.Path", side_effect=path_side_effect):
                with patch("core.utils.data_loader.Path", side_effect=path_side_effect):
                    with pytest.raises(FileNotFoundError, match="Features not found"):
                        load_features_and_prices("tBTCUSD", "15m")

    def test_load_candles_file_not_found(self):
        """Test error when candles file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create only features file (no candles file)
            features_data = {
                "timestamp": pd.date_range("2024-01-01", periods=10, freq="15min"),
                "ema_delta_pct": np.random.randn(10),
                "rsi": np.random.randn(10),
            }
            features_df = pd.DataFrame(features_data)

            # Create data directory structure
            data_dir = temp_path / "data" / "features"
            data_dir.mkdir(parents=True)
            features_path = data_dir / "tBTCUSD_15m_features.parquet"
            features_df.to_parquet(features_path)

            def path_side_effect(x):
                if isinstance(x, str):
                    if x.startswith("data/"):
                        return temp_path / x
                    return Path(x)
                return Path(x)

            with patch("scripts.train_model.Path", side_effect=path_side_effect):
                with patch("core.utils.data_loader.Path", side_effect=path_side_effect):
                    with pytest.raises(FileNotFoundError, match="Candles file not found"):
                        load_features_and_prices("tBTCUSD", "15m")

    def test_load_length_mismatch(self):
        """Test error when features and candles have different lengths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create features file (10 rows)
            features_data = {
                "timestamp": pd.date_range("2024-01-01", periods=10, freq="15min"),
                "ema_delta_pct": np.random.randn(10),
                "rsi": np.random.randn(10),
            }
            features_df = pd.DataFrame(features_data)
            features_path = temp_path / "tBTCUSD_15m_features.parquet"
            features_df.to_parquet(features_path)

            # Create candles file (8 rows - mismatch!)
            candles_data = {
                "timestamp": pd.date_range("2024-01-01", periods=8, freq="15min"),
                "open": np.random.randn(8) + 50000,
                "high": np.random.randn(8) + 50100,
                "low": np.random.randn(8) + 49900,
                "close": np.random.randn(8) + 50000,
                "volume": np.random.rand(8) * 1000,
            }
            candles_df = pd.DataFrame(candles_data)
            candles_path = temp_path / "tBTCUSD_15m.parquet"
            candles_df.to_parquet(candles_path)

            # Create data directory structure
            data_dir = temp_path / "data"
            features_dir = data_dir / "features"
            candles_dir = data_dir / "candles"
            features_dir.mkdir(parents=True)
            candles_dir.mkdir(parents=True)

            # Move files to correct locations
            features_path = features_dir / "tBTCUSD_15m_features.parquet"
            candles_path = candles_dir / "tBTCUSD_15m.parquet"
            features_df.to_parquet(features_path)
            candles_df.to_parquet(candles_path)

            def path_side_effect(x):
                if isinstance(x, str):
                    if x.startswith("data/"):
                        return temp_path / x
                    return Path(x)
                return Path(x)

            with patch("scripts.train_model.Path", side_effect=path_side_effect):
                with patch("core.utils.data_loader.Path", side_effect=path_side_effect):
                    with pytest.raises(ValueError, match="length mismatch"):
                        load_features_and_prices("tBTCUSD", "15m")


class TestGenerateTrainingLabels:
    """Tests for generating training labels."""

    def test_generate_training_labels_basic(self):
        """Test basic label generation."""
        prices = [100, 102, 105, 103, 101, 99]
        labels = generate_training_labels(prices, lookahead_bars=2)

        # Should match generate_labels behavior
        assert len(labels) == 6
        assert labels[0] == 1  # 100 -> 105: +5%
        assert labels[1] == 1  # 102 -> 103: +0.98%
        assert labels[2] == 0  # 105 -> 101: -3.8%
        assert labels[3] == 0  # 103 -> 99: -3.9%
        assert labels[4] is None  # No future data
        assert labels[5] is None  # No future data

    def test_generate_training_labels_with_threshold(self):
        """Test label generation with threshold filtering."""
        prices = [100, 100.1, 99.9, 101, 99]
        labels = generate_training_labels(prices, lookahead_bars=1, threshold_pct=0.5)

        assert labels[0] == 0  # +0.1% < 0.5%
        assert labels[1] == 0  # -0.2% < 0.5%
        assert labels[2] == 1  # +1.1% > 0.5%
        assert labels[3] == 0  # -2% < 0.5%
        assert labels[4] is None


class TestSplitDataChronological:
    """Tests for chronological data splitting."""

    def test_split_data_basic(self):
        """Test basic chronological split."""
        features = np.random.randn(100, 2)
        labels = np.random.randint(0, 2, 100)

        X_train, X_val, X_test, y_train, y_val, y_test, holdout_indices = split_data_chronological(
            features, labels
        )

        # Check sizes (60/20/20 split)
        assert len(X_train) == 60
        assert len(X_val) == 20
        assert len(X_test) == 20

        assert len(y_train) == 60
        assert len(y_val) == 20
        assert len(y_test) == 20

        # No holdout when use_holdout=False (default)
        assert holdout_indices is None

        # Check chronological order (no shuffling)
        assert np.array_equal(X_train, features[:60])
        assert np.array_equal(X_val, features[60:80])
        assert np.array_equal(X_test, features[80:])

        assert np.array_equal(y_train, labels[:60])
        assert np.array_equal(y_val, labels[60:80])
        assert np.array_equal(y_test, labels[80:])

    def test_split_data_custom_ratios(self):
        """Test split with custom ratios."""
        features = np.random.randn(100, 2)
        labels = np.random.randint(0, 2, 100)

        X_train, X_val, X_test, y_train, y_val, y_test, holdout_indices = split_data_chronological(
            features, labels, train_ratio=0.5, val_ratio=0.3
        )

        # Check sizes (50/30/20 split)
        assert len(X_train) == 50
        assert len(X_val) == 30
        assert len(X_test) == 20

    def test_split_data_small_dataset(self):
        """Test split with small dataset."""
        features = np.random.randn(10, 2)
        labels = np.random.randint(0, 2, 10)

        X_train, X_val, X_test, y_train, y_val, y_test, holdout_indices = split_data_chronological(
            features, labels
        )

        # Should still work with small data
        assert len(X_train) == 6
        assert len(X_val) == 2
        assert len(X_test) == 2
        assert holdout_indices is None


class TestTrainBuySellModels:
    """Tests for training buy/sell models."""

    def test_train_buy_sell_models_basic(self):
        """Test basic buy/sell model training."""
        # Create synthetic data
        np.random.seed(42)
        X_train = np.random.randn(100, 2)
        y_train = np.random.randint(0, 2, 100)
        X_val = np.random.randn(50, 2)
        y_val = np.random.randint(0, 2, 50)
        feature_names = ["ema_delta_pct", "rsi"]

        buy_model, sell_model, metrics = train_buy_sell_models(
            X_train, y_train, X_val, y_val, feature_names
        )

        # Check models are trained
        assert isinstance(buy_model, LogisticRegression)
        assert isinstance(sell_model, LogisticRegression)

        # Check metrics structure
        assert "buy_model" in metrics
        assert "sell_model" in metrics
        assert "feature_names" in metrics
        assert "n_features" in metrics
        assert "n_train" in metrics
        assert "n_val" in metrics

        # Check metric values
        assert "val_log_loss" in metrics["buy_model"]
        assert "val_auc" in metrics["buy_model"]
        assert "best_params" in metrics["buy_model"]

        assert "val_log_loss" in metrics["sell_model"]
        assert "val_auc" in metrics["sell_model"]
        assert "best_params" in metrics["sell_model"]

        # Check feature info
        assert metrics["feature_names"] == feature_names
        assert metrics["n_features"] == 2
        assert metrics["n_train"] == 100
        assert metrics["n_val"] == 50

    def test_train_buy_sell_models_label_inversion(self):
        """Test that sell model uses inverted labels."""
        # Create data with both classes for training
        X_train = np.array([[1.0], [1.0], [1.0], [-1.0], [-1.0]])  # Mixed features
        y_train = np.array([1, 1, 1, 0, 0])  # Mixed labels
        X_val = np.array([[1.0], [-1.0]])
        y_val = np.array([1, 0])
        feature_names = ["feature1"]

        buy_model, sell_model, metrics = train_buy_sell_models(
            X_train, y_train, X_val, y_val, feature_names
        )

        # Buy model should predict high probability for positive features
        buy_pred = buy_model.predict_proba(X_val)[0, 1]
        assert buy_pred > 0.5

        # Sell model should predict high probability for negative features (inverted labels)
        sell_pred = sell_model.predict_proba(X_val)[1, 1]  # Second sample (negative feature)
        assert sell_pred > 0.4  # Lower threshold for test data


class TestConvertToModelJson:
    """Tests for converting models to JSON format."""

    def test_convert_to_model_json_basic(self):
        """Test basic model conversion to JSON."""
        # Create mock models
        buy_model = LogisticRegression()
        buy_model.coef_ = np.array([[0.5, -0.3]])
        buy_model.intercept_ = np.array([0.1])

        sell_model = LogisticRegression()
        sell_model.coef_ = np.array([[-0.2, 0.4]])
        sell_model.intercept_ = np.array([-0.05])

        feature_names = ["ema_delta_pct", "rsi"]
        version = "v2"

        model_json = convert_to_model_json(buy_model, sell_model, feature_names, version)

        # Check structure
        assert model_json["version"] == version
        assert model_json["schema"] == feature_names

        # Check buy model
        assert model_json["buy"]["w"] == [0.5, -0.3]
        assert model_json["buy"]["b"] == 0.1
        assert model_json["buy"]["calib"] == {"a": 1.0, "b": 0.0}

        # Check sell model
        assert model_json["sell"]["w"] == [-0.2, 0.4]
        assert model_json["sell"]["b"] == -0.05
        assert model_json["sell"]["calib"] == {"a": 1.0, "b": 0.0}

    def test_convert_to_model_json_single_feature(self):
        """Test conversion with single feature."""
        buy_model = LogisticRegression()
        buy_model.coef_ = np.array([[0.8]])
        buy_model.intercept_ = np.array([0.2])

        sell_model = LogisticRegression()
        sell_model.coef_ = np.array([[-0.6]])
        sell_model.intercept_ = np.array([-0.1])

        feature_names = ["ema_delta_pct"]
        version = "v1"

        model_json = convert_to_model_json(buy_model, sell_model, feature_names, version)

        assert model_json["buy"]["w"] == [0.8]
        assert model_json["sell"]["w"] == [-0.6]
        assert model_json["version"] == "v1"


class TestSaveModelAndMetrics:
    """Tests for saving model and metrics."""

    def test_save_model_and_metrics_success(self):
        """Test successful saving of model and metrics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            model_json = {
                "version": "v2",
                "schema": ["ema_delta_pct", "rsi"],
                "buy": {"w": [0.5, -0.3], "b": 0.1, "calib": {"a": 1.0, "b": 0.0}},
                "sell": {"w": [-0.2, 0.4], "b": -0.05, "calib": {"a": 1.0, "b": 0.0}},
            }

            metrics = {
                "buy_model": {"val_log_loss": 0.5, "val_auc": 0.7},
                "sell_model": {"val_log_loss": 0.6, "val_auc": 0.65},
                "feature_names": ["ema_delta_pct", "rsi"],
                "n_features": 2,
                "n_train": 100,
                "n_val": 50,
            }

            file_paths = save_model_and_metrics(
                model_json, metrics, "tBTCUSD", "15m", "v2", output_dir
            )

            # Check file paths
            assert "model_path" in file_paths
            assert "metrics_path" in file_paths
            assert "model_filename" in file_paths
            assert "metrics_filename" in file_paths

            # Check files exist
            model_path = Path(file_paths["model_path"])
            metrics_path = Path(file_paths["metrics_path"])

            assert model_path.exists()
            assert metrics_path.exists()

            # Check file contents
            with open(model_path) as f:
                saved_model = json.load(f)
            assert saved_model == model_json

            with open(metrics_path) as f:
                saved_metrics = json.load(f)
            assert saved_metrics == metrics

    def test_save_model_and_metrics_creates_directory(self):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "new" / "subdirectory"

            model_json = {"version": "v1", "schema": ["feature1"]}
            metrics = {"buy_model": {}, "sell_model": {}}

            # Directory shouldn't exist yet
            assert not output_dir.exists()

            save_model_and_metrics(model_json, metrics, "tBTCUSD", "15m", "v1", output_dir)

            # Directory should be created
            assert output_dir.exists()


class TestAlignFeaturesWithLabels:
    """Tests for aligning features with labels."""

    def test_align_features_with_labels_basic(self):
        """Test basic alignment."""
        labels = [1, 0, 1, 0, None, None]
        start, end = align_features_with_labels(6, labels)

        assert start == 0
        assert end == 4

    def test_align_features_with_labels_all_none(self):
        """Test alignment when all labels are None."""
        labels = [None, None, None]
        start, end = align_features_with_labels(3, labels)

        assert start == 0
        assert end == 0

    def test_align_features_with_labels_mismatch_raises(self):
        """Test that mismatched counts raise ValueError."""
        labels = [1, 0, None]
        with pytest.raises(ValueError, match="must match"):
            align_features_with_labels(5, labels)


class TestIntegration:
    """Integration tests."""

    def test_full_training_pipeline_mock(self):
        """Test full training pipeline with mocked data loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock data files
            features_data = {
                "timestamp": pd.date_range("2024-01-01", periods=100, freq="15min"),
                "ema_delta_pct": np.random.randn(100),
                "rsi": np.random.randn(100),
            }
            features_df = pd.DataFrame(features_data)
            features_path = temp_path / "tBTCUSD_15m_features.parquet"
            features_df.to_parquet(features_path)

            candles_data = {
                "timestamp": pd.date_range("2024-01-01", periods=100, freq="15min"),
                "open": np.random.randn(100) + 50000,
                "high": np.random.randn(100) + 50100,
                "low": np.random.randn(100) + 49900,
                "close": np.random.randn(100) + 50000,
                "volume": np.random.rand(100) * 1000,
            }
            candles_df = pd.DataFrame(candles_data)
            candles_path = temp_path / "tBTCUSD_15m.parquet"
            candles_df.to_parquet(candles_path)

            # Create data directory structure
            data_dir = temp_path / "data" / "features"
            data_dir.mkdir(parents=True)
            candles_dir = temp_path / "data" / "candles"
            candles_dir.mkdir(parents=True)

            # Move files to correct locations
            features_path = data_dir / "tBTCUSD_15m_features.parquet"
            features_df.to_parquet(features_path)
            candles_path = candles_dir / "tBTCUSD_15m.parquet"
            candles_df.to_parquet(candles_path)

            # Mock the data directory for both modules
            def path_side_effect(x):
                if isinstance(x, str):
                    if x.startswith("data/"):
                        return temp_path / x
                    return Path(x)
                return Path(x)

            with patch("scripts.train_model.Path", side_effect=path_side_effect):
                with patch("core.utils.data_loader.Path", side_effect=path_side_effect):
                    # Load data
                    features_df, close_prices, candles_df = load_features_and_prices(
                        "tBTCUSD", "15m"
                    )

                    # Generate labels
                    labels = generate_training_labels(close_prices, lookahead_bars=5)

                    # Align data
                    start_idx, end_idx = align_features_with_labels(len(features_df), labels)

                    # Extract features
                    aligned_features = features_df.iloc[start_idx:end_idx]
                    aligned_labels = np.array(labels[start_idx:end_idx])

                    feature_columns = [
                        col for col in aligned_features.columns if col != "timestamp"
                    ]
                    X = aligned_features[feature_columns].values

                    # Split data
                    X_train, X_val, X_test, y_train, y_val, y_test, holdout_indices = (
                        split_data_chronological(X, aligned_labels)
                    )

                    # Train models
                    buy_model, sell_model, metrics = train_buy_sell_models(
                        X_train, y_train, X_val, y_val, feature_columns
                    )

                    # Convert to JSON
                    model_json = convert_to_model_json(buy_model, sell_model, feature_columns, "v2")

                    # Save results
                    output_dir = Path(temp_dir) / "results"
                    file_paths = save_model_and_metrics(
                        model_json, metrics, "tBTCUSD", "15m", "v2", output_dir
                    )

                    # Verify results
                    assert len(X_train) > 0
                    assert len(X_val) > 0
                    assert len(X_test) > 0
                    assert isinstance(buy_model, LogisticRegression)
                    assert isinstance(sell_model, LogisticRegression)
                    assert "buy_model" in metrics
                    assert "sell_model" in metrics
                    assert model_json["version"] == "v2"
                    assert model_json["schema"] == feature_columns
                    assert Path(file_paths["model_path"]).exists()
                    assert Path(file_paths["metrics_path"]).exists()
