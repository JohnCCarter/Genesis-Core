"""
Test model loading for backtest_with_fees.py and calculate_ic_by_regime.py scripts.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from backtest_with_fees import simulate_predictions
from calculate_ic_by_regime import load_model_predictions


@pytest.fixture
def sample_model_data():
    """Sample model data in Genesis-Core format."""
    return {
        "version": "v3",
        "schema": ["feature1", "feature2", "feature3"],
        "buy": {
            "w": [0.5, -0.3, 0.2],
            "b": 0.1,
            "calib": {"a": 1.0, "b": 0.0},
        },
        "sell": {
            "w": [-0.5, 0.3, -0.2],
            "b": -0.1,
            "calib": {"a": 1.0, "b": 0.0},
        },
    }


@pytest.fixture
def sample_features_df():
    """Sample features DataFrame."""
    return pd.DataFrame(
        {
            "feature1": [0.1, 0.2, 0.3, 0.4, 0.5],
            "feature2": [0.5, 0.4, 0.3, 0.2, 0.1],
            "feature3": [0.2, 0.2, 0.2, 0.2, 0.2],
        }
    )


def test_simulate_predictions_basic(sample_model_data, sample_features_df):
    """Test that simulate_predictions works with valid inputs."""
    predictions = simulate_predictions(sample_features_df, sample_model_data)

    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == len(sample_features_df)
    assert np.all((predictions >= 0) & (predictions <= 1))


def test_simulate_predictions_missing_schema(sample_features_df):
    """Test that simulate_predictions raises error when schema is missing."""
    model_data = {"buy": {"w": [0.1, 0.2], "b": 0.0}}

    with pytest.raises(ValueError, match="Model missing schema"):
        simulate_predictions(sample_features_df, model_data)


def test_simulate_predictions_missing_weights(sample_features_df):
    """Test that simulate_predictions raises error when weights are missing."""
    model_data = {"schema": ["feature1", "feature2"], "buy": {"b": 0.0}}

    with pytest.raises(ValueError, match="Model missing buy weights"):
        simulate_predictions(sample_features_df, model_data)


def test_simulate_predictions_with_calibration(sample_model_data, sample_features_df):
    """Test predictions with calibration applied."""
    # Add calibration
    sample_model_data["buy"]["calib"] = {"a": 2.0, "b": 0.5}

    predictions = simulate_predictions(sample_features_df, sample_model_data)

    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == len(sample_features_df)
    assert np.all((predictions >= 0) & (predictions <= 1))


def test_load_model_predictions_from_file(tmp_path, sample_model_data, sample_features_df):
    """Test load_model_predictions loads from JSON file."""
    # Create temporary model file
    model_path = tmp_path / "test_model.json"
    with open(model_path, "w") as f:
        json.dump(sample_model_data, f)

    # Load predictions
    predictions = load_model_predictions(str(model_path), sample_features_df)

    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == len(sample_features_df)
    assert np.all((predictions >= 0) & (predictions <= 1))


def test_load_model_predictions_missing_file(sample_features_df):
    """Test that load_model_predictions raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        load_model_predictions("/nonexistent/model.json", sample_features_df)


def test_predictions_consistency(tmp_path, sample_model_data, sample_features_df):
    """Test that both functions produce consistent results."""
    # Save model to file
    model_path = tmp_path / "test_model.json"
    with open(model_path, "w") as f:
        json.dump(sample_model_data, f)

    # Get predictions from both functions
    pred1 = simulate_predictions(sample_features_df, sample_model_data)
    pred2 = load_model_predictions(str(model_path), sample_features_df)

    # Should be identical
    np.testing.assert_array_almost_equal(pred1, pred2)


def test_predictions_with_missing_features(sample_model_data):
    """Test handling of missing features in DataFrame."""
    # Create DataFrame with only subset of features
    incomplete_df = pd.DataFrame(
        {
            "feature1": [0.1, 0.2, 0.3],
            # feature2 and feature3 are missing
        }
    )

    # Should still work, using zeros for missing features
    predictions = simulate_predictions(incomplete_df, sample_model_data)

    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == len(incomplete_df)
    assert np.all((predictions >= 0) & (predictions <= 1))
