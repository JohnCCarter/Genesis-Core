from __future__ import annotations

import pandas as pd
import pytest

import core.indicators.htf_fibonacci as htf
import core.indicators.htf_fibonacci_data as htf_data


def _set_cached_fib_df(fib_df: pd.DataFrame) -> None:
    cache_key = "tBTCUSD_1D_frozen_first_default"
    htf._htf_context_cache[cache_key] = {"fib_df": fib_df}


@pytest.mark.parametrize(
    "case",
    [
        {
            "name": "timeframe missing",
            "timeframe": None,
            "ltf": {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
                {
                    "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                    "htf_fib_0382": [100.0],
                    "htf_fib_05": [95.0],
                    "htf_fib_0618": [90.0],
                    "htf_fib_0786": [85.0],
                    "htf_swing_high": [110.0],
                    "htf_swing_low": [80.0],
                    "htf_swing_age_bars": [3],
                }
            ),
            "reason": "HTF_TIMEFRAME_MISSING",
        },
        {
            "name": "timeframe not applicable",
            "timeframe": "4h",
            "ltf": {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
                {
                    "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                    "htf_fib_0382": [100.0],
                    "htf_fib_05": [95.0],
                    "htf_fib_0618": [90.0],
                    "htf_fib_0786": [85.0],
                    "htf_swing_high": [110.0],
                    "htf_swing_low": [80.0],
                    "htf_swing_age_bars": [3],
                }
            ),
            "reason": "HTF_NOT_APPLICABLE",
        },
        {
            "name": "missing reference timestamp (lookahead prevention)",
            "timeframe": "1h",
            "ltf": {"open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0], "volume": [1.0]},
            "fib_df": pd.DataFrame(
                {
                    "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                    "htf_fib_0382": [100.0],
                    "htf_fib_05": [95.0],
                    "htf_fib_0618": [90.0],
                    "htf_fib_0786": [85.0],
                    "htf_swing_high": [110.0],
                    "htf_swing_low": [80.0],
                    "htf_swing_age_bars": [3],
                }
            ),
            "reason": "HTF_MISSING_REFERENCE_TS",
        },
        {
            "name": "stale HTF data",
            "timeframe": "1h",
            "ltf": {"timestamp": [pd.Timestamp("2025-02-10T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
                {
                    "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                    "htf_fib_0382": [100.0],
                    "htf_fib_05": [95.0],
                    "htf_fib_0618": [90.0],
                    "htf_fib_0786": [85.0],
                    "htf_swing_high": [110.0],
                    "htf_swing_low": [80.0],
                    "htf_swing_age_bars": [3],
                }
            ),
            "reason": "HTF_DATA_STALE",
        },
        {
            "name": "levels out of bounds",
            "timeframe": "1h",
            "ltf": {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
                {
                    "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                    "htf_fib_0382": [999.0],
                    "htf_fib_05": [95.0],
                    "htf_fib_0618": [90.0],
                    "htf_fib_0786": [85.0],
                    "htf_swing_high": [110.0],
                    "htf_swing_low": [80.0],
                    "htf_swing_age_bars": [3],
                }
            ),
            "reason": "HTF_LEVELS_OUT_OF_BOUNDS",
        },
    ],
    ids=lambda c: c["name"],
)
def test_get_htf_fibonacci_context_edge_cases_table(case) -> None:
    _set_cached_fib_df(case["fib_df"])

    ctx = htf.get_htf_fibonacci_context(
        case["ltf"],
        timeframe=case["timeframe"],
        symbol="tBTCUSD",
        htf_timeframe="1D",
    )

    assert ctx.get("available") is False
    assert ctx.get("reason") == case["reason"]


def test_get_htf_fibonacci_context_accepts_3h_when_cached_levels_are_valid() -> None:
    _set_cached_fib_df(
        pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                "htf_fib_0382": [100.0],
                "htf_fib_05": [95.0],
                "htf_fib_0618": [90.0],
                "htf_fib_0786": [85.0],
                "htf_swing_high": [110.0],
                "htf_swing_low": [80.0],
                "htf_swing_age_bars": [3],
            }
        )
    )

    ctx = htf.get_htf_fibonacci_context(
        {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
        timeframe="3h",
        symbol="tBTCUSD",
        htf_timeframe="1D",
    )

    assert ctx.get("available") is True
    assert ctx.get("htf_timeframe") == "1D"
    assert ctx.get("swing_high") == 110.0
    assert ctx.get("swing_low") == 80.0
    assert ctx.get("levels") == {0.382: 100.0, 0.5: 95.0, 0.618: 90.0, 0.786: 85.0}


def test_get_htf_fibonacci_context_forwards_data_source_policy_to_loader(monkeypatch) -> None:
    htf._htf_context_cache.clear()

    calls: list[dict[str, str]] = []

    def _fake_loader(symbol: str, timeframe: str, *, data_source_policy: str = "frozen_first"):
        calls.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "data_source_policy": data_source_policy,
            }
        )
        return pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                "close": [100.0],
            }
        )

    def _fake_compute(_candles, _config):
        return pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                "htf_fib_0382": [100.0],
                "htf_fib_05": [95.0],
                "htf_fib_0618": [90.0],
                "htf_fib_0786": [85.0],
                "htf_swing_high": [110.0],
                "htf_swing_low": [80.0],
                "htf_swing_age_bars": [3],
            }
        )

    monkeypatch.setattr(htf, "load_candles_data", _fake_loader)
    monkeypatch.setattr(htf, "compute_htf_fibonacci_levels", _fake_compute)

    ctx = htf.get_htf_fibonacci_context(
        {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
        timeframe="3h",
        symbol="tBTCUSD",
        htf_timeframe="1D",
        data_source_policy="curated_only",
    )

    assert ctx.get("available") is True
    assert calls == [
        {
            "symbol": "tBTCUSD",
            "timeframe": "1D",
            "data_source_policy": "curated_only",
        }
    ]


def test_get_htf_fibonacci_context_cache_is_isolated_by_data_source_policy(monkeypatch) -> None:
    htf._htf_context_cache.clear()

    calls: list[str] = []

    def _fake_loader(symbol: str, timeframe: str, *, data_source_policy: str = "frozen_first"):
        calls.append(data_source_policy)
        return pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                "close": [100.0],
            }
        )

    def _fake_compute(_candles, _config):
        return pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                "htf_fib_0382": [100.0],
                "htf_fib_05": [95.0],
                "htf_fib_0618": [90.0],
                "htf_fib_0786": [85.0],
                "htf_swing_high": [110.0],
                "htf_swing_low": [80.0],
                "htf_swing_age_bars": [3],
            }
        )

    monkeypatch.setattr(htf, "load_candles_data", _fake_loader)
    monkeypatch.setattr(htf, "compute_htf_fibonacci_levels", _fake_compute)

    ltf = {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]}
    ctx_default = htf.get_htf_fibonacci_context(ltf, timeframe="3h", symbol="tBTCUSD")
    ctx_curated = htf.get_htf_fibonacci_context(
        ltf,
        timeframe="3h",
        symbol="tBTCUSD",
        data_source_policy="curated_only",
    )

    assert ctx_default.get("available") is True
    assert ctx_curated.get("available") is True
    assert calls == ["frozen_first", "curated_only"]
    assert "tBTCUSD_1D_frozen_first_default" in htf._htf_context_cache
    assert "tBTCUSD_1D_curated_only_default" in htf._htf_context_cache


def test_load_candles_data_curated_only_does_not_fallback_to_frozen(monkeypatch) -> None:
    htf_data._candles_cache.clear()

    original_exists = htf_data.Path.exists
    read_paths: list[str] = []

    def _fake_exists(self: htf_data.Path) -> bool:
        if self.name == "tBTCUSD_1D_frozen.parquet":
            return True
        if self.name == "tBTCUSD_1D.parquet":
            return False
        return original_exists(self)

    def _fake_read_parquet(path, engine="pyarrow"):
        read_paths.append(str(path))
        raise FileNotFoundError(path)

    monkeypatch.setattr(htf_data.Path, "exists", _fake_exists)
    monkeypatch.setattr(htf_data.pd, "read_parquet", _fake_read_parquet)

    with pytest.raises(FileNotFoundError):
        htf_data.load_candles_data(
            "tBTCUSD",
            "1D",
            data_source_policy="curated_only",
        )

    assert all("_frozen.parquet" not in path for path in read_paths)


def test_load_candles_data_cache_is_isolated_by_policy(monkeypatch) -> None:
    htf_data._candles_cache.clear()

    frozen_df = pd.DataFrame(
        {"timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")], "close": [100.0]}
    )
    curated_df = pd.DataFrame(
        {"timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")], "close": [200.0]}
    )
    original_exists = htf_data.Path.exists

    def _fake_exists(self: htf_data.Path) -> bool:
        if self.name in {"tBTCUSD_1D_frozen.parquet", "tBTCUSD_1D.parquet"}:
            return True
        return original_exists(self)

    def _fake_read_parquet(path, engine="pyarrow"):
        path_str = str(path)
        if path_str.endswith("_frozen.parquet"):
            return frozen_df.copy()
        return curated_df.copy()

    monkeypatch.setattr(htf_data.Path, "exists", _fake_exists)
    monkeypatch.setattr(htf_data.pd, "read_parquet", _fake_read_parquet)

    default_df = htf_data.load_candles_data("tBTCUSD", "1D")
    curated_only_df = htf_data.load_candles_data(
        "tBTCUSD",
        "1D",
        data_source_policy="curated_only",
    )

    assert float(default_df["close"].iloc[0]) == 100.0
    assert float(curated_only_df["close"].iloc[0]) == 200.0
    assert len(htf_data._candles_cache) == 2
