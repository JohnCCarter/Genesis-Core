from __future__ import annotations

import copy
import re

import pandas as pd

import core.backtest.engine as engine_mod
from core.backtest.engine import BacktestEngine


def _make_engine(monkeypatch) -> BacktestEngine:
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")
    return BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=0, fast_window=False)


def _sample_ohlcv(start: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(start, periods=10, freq="h"),
            "open": [1.0] * 10,
            "high": [1.0] * 10,
            "low": [1.0] * 10,
            "close": [1.0] * 10,
            "volume": [1.0] * 10,
        }
    )


def test_precompute_cache_key_changes_with_date_window(monkeypatch) -> None:
    engine = _make_engine(monkeypatch)

    df_a = _sample_ohlcv("2024-01-01")
    df_b = _sample_ohlcv("2024-02-01")

    key_a = engine._precompute_cache_key(df_a)
    key_b = engine._precompute_cache_key(df_b)
    expected_prefix = f"tBTCUSD_1h_{engine_mod._precompute_cache_key_material()}_"

    assert key_a != key_b
    assert key_a.startswith(expected_prefix)
    assert key_b.startswith(expected_prefix)


def test_precompute_cache_key_legacy_shape_when_config_hash_unset_or_empty(monkeypatch) -> None:
    engine = _make_engine(monkeypatch)
    df = _sample_ohlcv("2024-03-01")

    monkeypatch.delenv("GENESIS_PRECOMPUTE_CONFIG_HASH", raising=False)
    key_unset = engine._precompute_cache_key(df)
    material = re.escape(engine_mod._precompute_cache_key_material())

    assert "_cfg" not in key_unset
    assert re.fullmatch(rf"tBTCUSD_1h_{material}_\d+_-?\d+_-?\d+", key_unset)

    monkeypatch.setenv("GENESIS_PRECOMPUTE_CONFIG_HASH", "")
    key_empty = engine._precompute_cache_key(df)

    assert key_empty == key_unset


def test_precompute_cache_key_changes_with_non_empty_config_hash(monkeypatch) -> None:
    engine = _make_engine(monkeypatch)
    df = _sample_ohlcv("2024-03-01")

    monkeypatch.setenv("GENESIS_PRECOMPUTE_CONFIG_HASH", "cfg-A:atr=14")
    key_a = engine._precompute_cache_key(df)

    monkeypatch.setenv("GENESIS_PRECOMPUTE_CONFIG_HASH", "cfg-B:atr=21")
    key_b = engine._precompute_cache_key(df)

    assert key_a != key_b
    assert re.search(r"_cfg[0-9a-f]{12}_", key_a)
    assert re.search(r"_cfg[0-9a-f]{12}_", key_b)
    assert "cfg-A:atr=14" not in key_a
    assert "cfg-B:atr=21" not in key_b


def test_precompute_cache_key_material_changes_with_persisted_swing_threshold_subset(
    monkeypatch,
) -> None:
    material_a = engine_mod._precompute_cache_key_material()
    original_spec = engine_mod.get_persisted_precompute_spec()

    def _modified_spec() -> dict[str, object]:
        spec = copy.deepcopy(original_spec)
        spec["ltf_swing_detection"]["swing_threshold_min"] = 0.4
        return spec

    monkeypatch.setattr(engine_mod, "get_persisted_precompute_spec", _modified_spec)

    material_b = engine_mod._precompute_cache_key_material()
    material_c = engine_mod._precompute_cache_key_material()

    assert material_a != material_b
    assert material_b == material_c


def test_precompute_cache_cold_and_warm_paths_preserve_runtime_parity(
    tmp_path,
    monkeypatch,
) -> None:
    BacktestEngine._candles_cache.clear()

    fake_engine_file = tmp_path / "src" / "core" / "backtest" / "engine.py"
    fake_engine_file.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(engine_mod, "__file__", str(fake_engine_file))

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)

    ltf_ts = pd.date_range("2025-01-01", periods=48, freq="15min", tz="UTC")
    ltf = pd.DataFrame(
        {
            "timestamp": ltf_ts,
            "open": [100.0 + i * 0.1 for i in range(len(ltf_ts))],
            "high": [100.5 + i * 0.1 for i in range(len(ltf_ts))],
            "low": [99.5 + i * 0.1 for i in range(len(ltf_ts))],
            "close": [100.2 + i * 0.1 for i in range(len(ltf_ts))],
            "volume": [1000.0 + i for i in range(len(ltf_ts))],
        }
    )
    ltf.to_parquet(data_raw / "tBTCUSD_15m_frozen.parquet", index=False)

    def _fake_evaluate_pipeline(*, candles, policy, configs, state):
        return (
            {
                "action": "NONE",
                "confidence": 1.0,
                "regime": "NEUTRAL",
                "features": {},
            },
            {
                "decision": {"size": 0.0, "state_out": {}},
                "features": {},
            },
        )

    monkeypatch.setattr(engine_mod, "evaluate_pipeline", _fake_evaluate_pipeline)
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.delenv("GENESIS_MODE_EXPLICIT", raising=False)
    monkeypatch.delenv("GENESIS_PRECOMPUTE_CACHE_WRITE", raising=False)

    base_configs = {
        "meta": {"skip_champion_merge": True},
        "thresholds": {"entry_conf_overall": 0.99},
        "risk": {"risk_map": [[0.7, 0.01]]},
    }

    def _run_once():
        engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
        assert engine.load_data() is True
        return engine.run(
            policy={"symbol": "tBTCUSD", "timeframe": "15m"},
            configs=base_configs,
            verbose=False,
        )

    cold_results = _run_once()

    cache_dir = tmp_path / "cache" / "precomputed"
    cache_files = list(cache_dir.glob("*.npz"))

    assert cache_dir.exists() is True
    assert len(cache_files) == 1

    cache_path = cache_files[0]
    cache_mtime_before = cache_path.stat().st_mtime_ns

    warm_results = _run_once()

    assert cache_path.stat().st_mtime_ns == cache_mtime_before
    assert warm_results["summary"] == cold_results["summary"]
    assert warm_results["metrics"] == cold_results["metrics"]
    assert warm_results["trades"] == cold_results["trades"]
    assert len(warm_results["equity_curve"]) == len(cold_results["equity_curve"])
