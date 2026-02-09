from __future__ import annotations

from core.backtest.engine import BacktestEngine
from core.utils.diffing.canonical import scrub_volatile


def test_scrub_volatile_removes_nested_timestamp_and_run_id() -> None:
    payload = {
        "meta": {
            "run_id": "run_123",
            "nested": {"timestamp": "2026-02-09T00:00:00", "keep": 1},
        },
        "keep": {"created_at": "x", "value": 2},
    }

    out = scrub_volatile(payload)

    assert "run_id" not in (out.get("meta") or {})
    assert "timestamp" not in ((out.get("meta") or {}).get("nested") or {})
    assert "created_at" not in (out.get("keep") or {})
    assert (out.get("meta") or {}).get("nested", {}).get("keep") == 1
    assert (out.get("keep") or {}).get("value") == 2


def test_effective_config_fingerprint_ignores_volatile_fields() -> None:
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h")

    cfg1 = {
        "thresholds": {"entry_conf_overall": 0.35},
        "meta": {
            "champion_loaded_at": "2026-02-09T00:00:00",
            "run_id": "run_a",
            "nested": {"timestamp": "2026-02-09T00:00:01"},
        },
        "_global_index": [1, 2, 3],
        "precomputed_features": {"atr_14": [0.1, 0.2, 0.3]},
    }
    cfg2 = {
        "thresholds": {"entry_conf_overall": 0.35},
        "meta": {
            "champion_loaded_at": "2026-02-09T12:34:56",
            "run_id": "run_b",
            "nested": {"timestamp": "2026-02-09T12:34:57"},
        },
        "_global_index": [999],
        "precomputed_features": {"atr_14": [9.9]},
    }

    fp1 = engine._config_fingerprint(cfg1)
    fp2 = engine._config_fingerprint(cfg2)

    assert fp1 == fp2


def test_effective_config_fingerprint_changes_when_semantic_config_changes() -> None:
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h")

    cfg1 = {"thresholds": {"entry_conf_overall": 0.35}}
    cfg2 = {"thresholds": {"entry_conf_overall": 0.36}}

    assert engine._config_fingerprint(cfg1) != engine._config_fingerprint(cfg2)
