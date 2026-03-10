from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from core.strategy.features_asof import extract_features_backtest


def _load_schema_keys() -> list[str]:
    model_path = Path("config/models/tBTCUSD_1h.json")
    payload = json.loads(model_path.read_text(encoding="utf-8"))
    schema = payload.get("schema")
    if not isinstance(schema, list) or not schema:
        raise AssertionError("Expected non-empty list at config/models/tBTCUSD_1h.json:schema")

    keys: list[str] = []
    for item in schema:
        if not isinstance(item, str) or not item:
            raise AssertionError("Schema entries must be non-empty strings")
        keys.append(item)
    return keys


def _make_synthetic_candles(n: int = 320, seed: int = 42) -> dict[str, list[float]]:
    """Deterministiska candles med lagom variation för att trigga alla indikatorer."""

    rng = np.random.default_rng(seed)
    # Random walk + mild sinus för att undvika platt regime
    steps = rng.normal(loc=0.0, scale=15.0, size=n)
    base = 50_000.0 + np.cumsum(steps) + 200.0 * np.sin(np.linspace(0, 6.0 * np.pi, n))

    close = base
    open_ = np.roll(close, 1)
    open_[0] = close[0]

    spread = np.abs(rng.normal(loc=0.0, scale=20.0, size=n)) + 10.0
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread

    volume = 100.0 + np.abs(rng.normal(loc=0.0, scale=5.0, size=n))

    return {
        "open": open_.astype(float).tolist(),
        "high": high.astype(float).tolist(),
        "low": low.astype(float).tolist(),
        "close": close.astype(float).tolist(),
        "volume": volume.astype(float).tolist(),
    }


def test_tBTCUSD_1h_schema_contract_keys_present_and_finite(monkeypatch) -> None:
    """Kontrakts-test: SSOT ska alltid producera modellens schema-keys (finite values)."""

    # Make the test independent of any precompute setup.
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    schema_keys = _load_schema_keys()
    candles = _make_synthetic_candles()

    asof_bar = 250
    feats, meta = extract_features_backtest(
        candles,
        asof_bar,
        timeframe="1h",
        symbol="tBTCUSD",
        config={
            "thresholds": {
                "signal_adaptation": {
                    "atr_period": 14,
                }
            }
        },
    )

    assert isinstance(meta, dict)
    missing = [k for k in schema_keys if k not in feats]
    assert not missing, f"Missing schema keys: {missing}"

    non_finite: list[tuple[str, float]] = []
    for k in schema_keys:
        v = feats[k]
        if not isinstance(v, int | float):
            raise AssertionError(f"Feature {k} is not numeric: {type(v)}")
        fv = float(v)
        if not math.isfinite(fv):
            non_finite.append((k, fv))

    assert not non_finite, f"Non-finite feature values: {non_finite}"
