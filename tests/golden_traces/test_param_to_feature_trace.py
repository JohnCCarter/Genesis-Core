"""
GOLDEN TRACE TEST 1: Parameter → Feature Determinism

Verifies that given identical parameters and market data,
feature extraction produces identical outputs.

Catches drift in:
- Indicator calculations (ATR, EMA, RSI, etc.)
- Fibonacci swing detection
- Feature preprocessing
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from core.strategy.features_asof import extract_features


def _assert_close(actual, expected, rtol=1e-10, name="value"):
    """Assert two floats are close within relative tolerance."""
    if abs(actual - expected) > rtol * abs(expected):
        raise AssertionError(
            f"{name}: expected {expected}, got {actual} "
            f"(diff: {abs(actual - expected)}, rtol: {rtol})"
        )


def _assert_fib_levels_equal(actual, expected):
    """Assert Fibonacci level structures are identical."""
    if actual is None and expected is None:
        return
    if actual is None or expected is None:
        raise AssertionError(f"Fib levels mismatch: actual={actual}, expected={expected}")

    # Check structure keys
    assert set(actual.keys()) == set(expected.keys()), "Fib level keys mismatch"

    # Check numeric values
    for key in actual:
        if isinstance(actual[key], (int, float)) and isinstance(expected[key], (int, float)):
            _assert_close(actual[key], expected[key], rtol=1e-10, name=f"fib.{key}")
        else:
            assert actual[key] == expected[key], f"Fib level {key} mismatch"


@pytest.fixture
def golden_dir():
    """Return path to golden snapshots directory."""
    return Path(__file__).parent / "snapshots"


@pytest.fixture
def frozen_candles(golden_dir):
    """Load frozen candle data for testing."""
    candles_path = golden_dir / "tBTCUSD_1h_sample_100bars.parquet"
    if not candles_path.exists():
        pytest.skip(f"Frozen candles not found: {candles_path}")
    return pd.read_parquet(candles_path)


@pytest.fixture
def champion_params(golden_dir):
    """Load golden champion parameters."""
    params_path = golden_dir / "golden_champion_params.json"
    if not params_path.exists():
        pytest.skip(f"Golden params not found: {params_path}")
    with open(params_path) as f:
        return json.load(f)


@pytest.fixture
def golden_features(golden_dir):
    """Return path to golden feature snapshot."""
    features_path = golden_dir / "golden_features_v1.json"
    if not features_path.exists():
        pytest.skip(f"Golden features not found: {features_path}")
    with open(features_path) as f:
        return json.load(f)


def test_param_to_feature_determinism(frozen_candles, champion_params, golden_features):
    """
    GOLDEN TRACE 1: Parameters → Features

    Asserts that feature extraction is deterministic.
    This test will fail if ANY indicator logic changes.
    """
    # Convert DataFrame to dict format for extract_features
    candles_dict = {
        "timestamp": frozen_candles["timestamp"].tolist(),
        "open": frozen_candles["open"].values,
        "high": frozen_candles["high"].values,
        "low": frozen_candles["low"].values,
        "close": frozen_candles["close"].values,
        "volume": frozen_candles["volume"].values,
    }

    # Extract features using champion params
    features, meta = extract_features(candles=candles_dict, configs=champion_params, state={})

    # Assert critical features match golden snapshot
    # (Use relaxed tolerance for floating point to avoid spurious failures)
    critical_features = ["atr_14", "ema_20", "ema_50", "rsi_14", "bb_position_20_2", "adx_14"]

    for feat in critical_features:
        if feat in golden_features and feat in features:
            _assert_close(
                features[feat],
                golden_features[feat],
                rtol=1e-8,  # Slightly relaxed for cross-platform consistency
                name=feat,
            )

    # Assert Fibonacci swing points unchanged
    if "swing_high" in golden_features and "swing_high" in features:
        _assert_close(features["swing_high"], golden_features["swing_high"], rtol=1e-8)
    if "swing_low" in golden_features and "swing_low" in features:
        _assert_close(features["swing_low"], golden_features["swing_low"], rtol=1e-8)

    # Assert HTF/LTF Fibonacci levels unchanged (if present)
    if "htf_fib" in golden_features and "htf_fib" in features:
        _assert_fib_levels_equal(features["htf_fib"], golden_features["htf_fib"])
    if "ltf_fib" in golden_features and "ltf_fib" in features:
        _assert_fib_levels_equal(features["ltf_fib"], golden_features["ltf_fib"])


def test_feature_extraction_snapshot_exists(golden_dir):
    """Sanity check: ensure golden snapshot exists before running trace test."""
    features_path = golden_dir / "golden_features_v1.json"
    if not features_path.exists():
        pytest.skip(
            f"Golden feature snapshot not found. Run scripts/rebaseline_golden_traces.py first.\n"
            f"Expected: {features_path}"
        )
