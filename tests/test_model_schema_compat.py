"""Regression tests for feature/schema compatibility.

Goal: prevent silent model drift where models expect feature keys that feature extraction no
longer produces (predict_proba defaults missing keys to 0.0).

This should stay fast and deterministic (synthetic candles, no network/data dependencies).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from core.strategy.features_asof import extract_features_backtest


def _synthetic_candles(*, n: int = 250) -> dict[str, list[float]]:
    rng = np.random.default_rng(0)
    closes = (10_000.0 + np.cumsum(rng.normal(0, 10, size=n))).tolist()
    opens = [closes[0]] + closes[:-1]
    highs = (np.maximum(opens, closes) + 5.0).tolist()
    lows = (np.minimum(opens, closes) - 5.0).tolist()
    volume = (np.ones(n) * 100.0).tolist()
    return {"open": opens, "high": highs, "low": lows, "close": closes, "volume": volume}


def _schema_union_from_config_models() -> set[str]:
    schemas: set[str] = set()
    for p in Path("config/models").glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("schema"), list):
            schemas.update(map(str, data["schema"]))
            continue

        # Support nested/newer structures (timeframe keys)
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, dict) and isinstance(v.get("schema"), list):
                    schemas.update(map(str, v["schema"]))

    return schemas


def test_feature_extraction_covers_all_model_schema_keys() -> None:
    candles = _synthetic_candles(n=260)
    feats, _meta = extract_features_backtest(
        candles,
        asof_bar=len(candles["close"]) - 1,
        timeframe="1h",
        symbol="tBTCUSD",
        config={"thresholds": {"signal_adaptation": {"atr_period": 14}}},
    )

    produced = set(feats.keys())
    schema_union = _schema_union_from_config_models()

    missing = sorted(schema_union - produced)
    assert missing == [], f"Missing schema keys in features: {missing}"
