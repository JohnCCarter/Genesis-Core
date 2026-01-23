"""Minimal E2E-smoke för strategy pipeline.

Viktigt: Denna modul ska vara *import-säker* (inga sidoeffekter vid import).
Kör den som script när du vill smoke-testa pipeline lokalt.
"""

from core.strategy.evaluate import evaluate_pipeline


def main() -> int:
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
            "percentiles": {"ema": [-10, 10], "rsi": [-10, 10]},
            "versions": {"feature_set": "v1"},
        },
        "thresholds": {"entry_conf_overall": 0.7, "regime_proba": {"balanced": 0.55}},
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},
        "ev": {"R_default": 1.5},
    }
    res, _meta = evaluate_pipeline(candles, policy=policy, configs=configs, state={})
    print(res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
