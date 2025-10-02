from __future__ import annotations

from core.strategy.evaluate import evaluate_pipeline


def test_e2e_pipeline_stub():
    candles = {
        "open": [1, 2, 3, 4],
        "high": [2, 3, 4, 5],
        "low": [0.5, 1.5, 2.5, 3.5],
        "close": [1.5, 2.5, 3.5, 4.5],
        "volume": [10, 11, 12, 13],
    }
    policy = {"symbol": "tBTCUSD", "timeframe": "1m"}
    configs = {
        "features": {
            "percentiles": {"ema": [-10.0, 10.0], "rsi": [-10.0, 10.0]},
            "versions": {"feature_set": "v1"},
        },
        "thresholds": {"entry_conf_overall": 0.7, "regime_proba": {"balanced": 0.55}},
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},
        "ev": {"R_default": 1.5},
    }
    result, meta = evaluate_pipeline(candles, policy=policy, configs=configs, state={})
    assert isinstance(result, dict) and isinstance(meta, dict)
    assert set(result.keys()) >= {
        "features",
        "probas",
        "confidence",
        "regime",
        "action",
    }


def test_e2e_none_on_missing_data():
    # Saknad data => features fail-safe => beslut NONE
    result, meta = evaluate_pipeline({}, policy={}, configs={}, state={})
    assert result["action"] in ("NONE",)
