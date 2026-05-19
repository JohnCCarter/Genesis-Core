"""Tests for backtest engine."""

import builtins
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from core.backtest.engine import BacktestEngine
from core.backtest.position_tracker import Position
from core.strategy.champion_loader import ChampionConfig


@pytest.fixture
def sample_candles_data():
    """Create sample candles data for testing."""
    dates = pd.date_range("2025-01-01", periods=200, freq="15min")
    data = {
        "timestamp": dates,
        "open": [100 + i * 0.1 for i in range(200)],
        "high": [100 + i * 0.1 + 0.5 for i in range(200)],
        "low": [100 + i * 0.1 - 0.5 for i in range(200)],
        "close": [100 + i * 0.1 + 0.2 for i in range(200)],
        "volume": [1000 + i * 10 for i in range(200)],
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_data_file(tmp_path, sample_candles_data):
    """Create temporary parquet file with sample data."""
    data_dir = tmp_path / "data" / "candles"
    data_dir.mkdir(parents=True, exist_ok=True)

    file_path = data_dir / "tBTCUSD_15m.parquet"
    sample_candles_data.to_parquet(file_path, index=False)

    return tmp_path


def test_engine_initialization():
    """Test BacktestEngine initialization."""
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        initial_capital=10000.0,
        commission_rate=0.001,
        warmup_bars=120,
    )

    assert engine.symbol == "tBTCUSD"
    assert engine.timeframe == "15m"
    assert engine.warmup_bars == 120
    assert engine.data_source_policy == "frozen_first"
    assert engine.position_tracker.initial_capital == 10000.0
    assert engine.position_tracker.commission_rate == 0.001
    assert engine.candles_df is None


def test_engine_invalid_data_source_policy_raises():
    """Backtest data-source policy must reject unsupported values."""

    with pytest.raises(ValueError, match="Invalid data_source_policy"):
        BacktestEngine(symbol="tBTCUSD", timeframe="15m", data_source_policy="legacy_first")


def test_engine_precompute_without_fast_window_raises_when_mode_not_explicit(
    monkeypatch: pytest.MonkeyPatch,
):
    """A8: mixed mode must hard-fail unless explicit mode is acknowledged."""
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.delenv("GENESIS_MODE_EXPLICIT", raising=False)

    with pytest.raises(ValueError, match="GENESIS_MODE_EXPLICIT=1"):
        BacktestEngine(symbol="tBTCUSD", timeframe="15m", fast_window=False)


def test_engine_precompute_without_fast_window_allowed_in_explicit_mode(
    monkeypatch: pytest.MonkeyPatch,
):
    """A8: explicit mode keeps non-canonical path as opt-in with warning."""
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "1")

    with pytest.warns(UserWarning, match="explicit non-canonical mode"):
        engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", fast_window=False)

    assert engine.fast_window is False


def test_engine_load_data_missing_file():
    """Test engine fails gracefully when data file is missing."""
    engine = BacktestEngine(symbol="tNONEXISTENT", timeframe="1h")

    result = engine.load_data()

    assert result is False
    assert engine.candles_df is None


def test_engine_load_data_success(temp_data_file):
    """Test engine successfully loads data."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")

    # Manually load data from temp file (simulating load_data())
    data_file = temp_data_file / "data" / "candles" / "tBTCUSD_15m.parquet"
    engine.candles_df = pd.read_parquet(data_file)

    assert engine.candles_df is not None
    assert len(engine.candles_df) == 200
    assert "timestamp" in engine.candles_df.columns
    assert "close" in engine.candles_df.columns


def test_engine_load_data_with_date_filter(temp_data_file):
    """Test engine filters data by date range."""
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        start_date="2025-01-01",
        end_date="2025-01-02",
    )

    # Manually load and filter (simulating load_data() with date filter)
    data_file = temp_data_file / "data" / "candles" / "tBTCUSD_15m.parquet"
    df = pd.read_parquet(data_file)
    engine.candles_df = df[
        (df["timestamp"] >= pd.to_datetime("2025-01-01"))
        & (df["timestamp"] <= pd.to_datetime("2025-01-02"))
    ]

    assert engine.candles_df is not None
    assert len(engine.candles_df) < 200  # Filtered


def test_engine_load_data_date_filter_handles_tz_aware(monkeypatch):
    """Regression: load_data date filter must handle tz-aware candle timestamps."""

    # tz-aware candle timestamps (UTC)
    dates = pd.date_range("2025-01-01", periods=10, freq="15min", tz="UTC")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "open": [100.0] * 10,
            "high": [101.0] * 10,
            "low": [99.0] * 10,
            "close": [100.5] * 10,
            "volume": [1.0] * 10,
        }
    )

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        start_date="2025-01-01",
        end_date="2025-01-01",
    )

    # Pretend the frozen parquet exists so load_data takes that path.
    original_exists = Path.exists

    def _fake_exists(self: Path) -> bool:
        if self.name == "tBTCUSD_15m_frozen.parquet" and "raw" in self.parts:
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", _fake_exists)

    def _fake_read_parquet(_path, columns=None, **_kwargs):
        if columns is None:
            return df.copy()
        return df[columns].copy()

    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)

    assert engine.load_data() is True
    assert engine.candles_df is not None
    # end_date is inclusive at midnight; at least the first bar should remain.
    assert len(engine.candles_df) >= 1


def test_engine_load_data_default_policy_prefers_frozen(monkeypatch, sample_candles_data):
    """Default policy must preserve frozen-first behavior."""

    BacktestEngine._candles_cache.clear()

    frozen_df = sample_candles_data.copy()
    curated_df = sample_candles_data.copy()
    curated_df["close"] = curated_df["close"] + 500.0

    original_exists = Path.exists

    def _fake_exists(self: Path) -> bool:
        if self.name in {"tBTCUSD_15m_frozen.parquet", "tBTCUSD_15m.parquet"}:
            return True
        return original_exists(self)

    def _fake_read_parquet(path, columns=None, **_kwargs):
        df = frozen_df if str(path).endswith("_frozen.parquet") else curated_df
        if columns is None:
            return df.copy()
        return df[columns].copy()

    monkeypatch.setattr(Path, "exists", _fake_exists)
    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")

    assert engine.load_data() is True
    assert engine.candles_source is not None
    assert engine.candles_source.endswith("tBTCUSD_15m_frozen.parquet")
    assert engine.data_source_policy == "frozen_first"
    assert engine.candles_df is not None
    assert engine.candles_df["close"].iloc[0] == pytest.approx(frozen_df["close"].iloc[0])


def test_engine_load_data_curated_only_prefers_curated(monkeypatch, sample_candles_data):
    """Opt-in curated_only must select curated even when frozen exists."""

    BacktestEngine._candles_cache.clear()

    frozen_df = sample_candles_data.copy()
    curated_df = sample_candles_data.copy()
    curated_df["close"] = curated_df["close"] + 250.0
    read_paths: list[str] = []

    original_exists = Path.exists

    def _fake_exists(self: Path) -> bool:
        if self.name in {"tBTCUSD_15m_frozen.parquet", "tBTCUSD_15m.parquet"}:
            return True
        return original_exists(self)

    def _fake_read_parquet(path, columns=None, **_kwargs):
        read_paths.append(str(path))
        df = frozen_df if str(path).endswith("_frozen.parquet") else curated_df
        if columns is None:
            return df.copy()
        return df[columns].copy()

    monkeypatch.setattr(Path, "exists", _fake_exists)
    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        data_source_policy="curated_only",
    )

    assert engine.load_data() is True
    assert engine.candles_source is not None
    assert engine.candles_source.endswith("tBTCUSD_15m.parquet")
    assert engine.candles_df is not None
    assert engine.candles_df["close"].iloc[0] == pytest.approx(curated_df["close"].iloc[0])
    assert all("_frozen.parquet" not in path for path in read_paths)


def test_engine_load_data_curated_only_does_not_fallback_to_frozen(monkeypatch):
    """curated_only must fail closed instead of silently falling back to frozen."""

    BacktestEngine._candles_cache.clear()

    original_exists = Path.exists
    read_paths: list[str] = []

    def _fake_exists(self: Path) -> bool:
        if self.name == "tBTCUSD_15m_frozen.parquet":
            return True
        if self.name == "tBTCUSD_15m.parquet":
            return False
        return original_exists(self)

    def _fake_read_parquet(path, columns=None, **_kwargs):
        read_paths.append(str(path))
        raise FileNotFoundError(path)

    monkeypatch.setattr(Path, "exists", _fake_exists)
    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        data_source_policy="curated_only",
    )

    assert engine.load_data() is False
    assert engine.candles_source is None
    assert all("_frozen.parquet" not in path for path in read_paths)


def test_engine_load_data_cache_isolated_by_selected_source(monkeypatch, sample_candles_data):
    """Frozen and curated loads must not alias through the in-memory candle cache."""

    BacktestEngine._candles_cache.clear()

    frozen_df = sample_candles_data.copy()
    curated_df = sample_candles_data.copy()
    curated_df["close"] = curated_df["close"] + 777.0

    original_exists = Path.exists

    def _fake_exists(self: Path) -> bool:
        if self.name in {"tBTCUSD_15m_frozen.parquet", "tBTCUSD_15m.parquet"}:
            return True
        return original_exists(self)

    def _fake_read_parquet(path, columns=None, **_kwargs):
        df = frozen_df if str(path).endswith("_frozen.parquet") else curated_df
        if columns is None:
            return df.copy()
        return df[columns].copy()

    monkeypatch.setattr(Path, "exists", _fake_exists)
    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)

    frozen_engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    curated_engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        data_source_policy="curated_only",
    )

    assert frozen_engine.load_data() is True
    assert curated_engine.load_data() is True
    assert frozen_engine.candles_df is not None
    assert curated_engine.candles_df is not None
    assert frozen_engine.candles_df["close"].iloc[0] == pytest.approx(frozen_df["close"].iloc[0])
    assert curated_engine.candles_df["close"].iloc[0] == pytest.approx(curated_df["close"].iloc[0])


def test_engine_load_data_applies_policy_to_htf(monkeypatch, sample_candles_data):
    """HTF loading must follow the same data-source policy as the primary timeframe."""

    BacktestEngine._candles_cache.clear()

    ltf_frozen = sample_candles_data.copy()
    ltf_curated = sample_candles_data.copy()
    ltf_curated["close"] = ltf_curated["close"] + 300.0

    htf_dates = pd.date_range("2024-01-01", periods=40, freq="1D", tz="UTC")
    htf_frozen = pd.DataFrame(
        {
            "timestamp": htf_dates,
            "open": [100.0 + i for i in range(40)],
            "high": [101.0 + i for i in range(40)],
            "low": [99.0 + i for i in range(40)],
            "close": [100.5 + i for i in range(40)],
        }
    )
    htf_curated = htf_frozen.copy()
    htf_curated["close"] = htf_curated["close"] + 400.0

    original_exists = Path.exists

    def _fake_exists(self: Path) -> bool:
        if self.name in {
            "tBTCUSD_15m_frozen.parquet",
            "tBTCUSD_15m.parquet",
            "tBTCUSD_1D_frozen.parquet",
            "tBTCUSD_1D.parquet",
        }:
            return True
        return original_exists(self)

    def _fake_read_parquet(path, columns=None, **_kwargs):
        path_str = str(path)
        if path_str.endswith("tBTCUSD_15m_frozen.parquet"):
            df = ltf_frozen
        elif path_str.endswith("tBTCUSD_15m.parquet"):
            df = ltf_curated
        elif path_str.endswith("tBTCUSD_1D_frozen.parquet"):
            df = htf_frozen
        elif path_str.endswith("tBTCUSD_1D.parquet"):
            df = htf_curated
        else:
            raise AssertionError(f"Unexpected parquet read: {path_str}")

        if columns is None:
            return df.copy()
        return df[columns].copy()

    monkeypatch.setattr(Path, "exists", _fake_exists)
    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        data_source_policy="curated_only",
    )
    engine._use_new_exit_engine = True

    assert engine.load_data() is True
    assert engine.candles_source is not None
    assert engine.htf_candles_source is not None
    assert engine.candles_source.endswith("tBTCUSD_15m.parquet")
    assert engine.htf_candles_source.endswith("tBTCUSD_1D.parquet")


def test_precompute_cache_key_includes_candle_source(sample_candles_data):
    """Precompute cache keys must differ across frozen vs curated sources."""

    frozen_engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    curated_engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        data_source_policy="curated_only",
    )

    frozen_engine.candles_source = "data/raw/tBTCUSD_15m_frozen.parquet"
    curated_engine.candles_source = "data/curated/v1/candles/tBTCUSD_15m.parquet"

    assert frozen_engine._precompute_cache_key(
        sample_candles_data
    ) != curated_engine._precompute_cache_key(sample_candles_data)


def test_build_candles_window(sample_candles_data):
    """Test building candles window for pipeline."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.candles_df = sample_candles_data

    # Build window ending at index 100
    window = engine._build_candles_window(end_idx=100, window_size=50)

    assert isinstance(window, dict)
    assert "open" in window
    assert "close" in window
    assert "high" in window
    assert "low" in window
    assert "volume" in window
    assert "timestamp" in window
    assert len(window["close"]) == 50  # Correct window size
    assert len(window["timestamp"]) == 50


def test_build_candles_window_at_start(sample_candles_data):
    """Test building window at start of data (edge case)."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.candles_df = sample_candles_data

    # Build window at index 10 (less than window_size)
    window = engine._build_candles_window(end_idx=10, window_size=50)

    assert len(window["close"]) == 11  # 0 to 10 inclusive
    assert len(window["timestamp"]) == 11


@pytest.mark.parametrize(
    ("end_idx", "window_size"),
    [
        (10, 50),
        (100, 50),
        (199, 200),
    ],
)
def test_build_candles_window_fast_window_matches_numpy_path(
    monkeypatch: pytest.MonkeyPatch,
    sample_candles_data,
    end_idx: int,
    window_size: int,
):
    """Regression: fast-window slicing must match the normal prefix window exactly."""
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", fast_window=True)
    engine.candles_df = sample_candles_data
    engine._prepare_numpy_arrays()

    engine._col_open = sample_candles_data["open"].to_numpy(copy=False)
    engine._col_high = sample_candles_data["high"].to_numpy(copy=False)
    engine._col_low = sample_candles_data["low"].to_numpy(copy=False)
    engine._col_close = sample_candles_data["close"].to_numpy(copy=False)
    engine._col_volume = sample_candles_data["volume"].to_numpy(copy=False)
    engine._col_timestamp = sample_candles_data["timestamp"].tolist()

    def _normalize_window(window: dict) -> dict[str, list]:
        return {
            "open": [float(value) for value in window["open"]],
            "high": [float(value) for value in window["high"]],
            "low": [float(value) for value in window["low"]],
            "close": [float(value) for value in window["close"]],
            "volume": [float(value) for value in window["volume"]],
            "timestamp": [pd.Timestamp(value) for value in window["timestamp"]],
        }

    fast_window = _normalize_window(engine._build_candles_window(end_idx, window_size))

    engine.fast_window = False
    numpy_window = _normalize_window(engine._build_candles_window(end_idx, window_size))

    assert fast_window == numpy_window


def test_engine_run_no_data():
    """Test engine fails gracefully when no data is loaded."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")

    results = engine.run()

    assert "error" in results
    assert results["error"] == "no_data"


def test_engine_run_empty_dataframe():
    """Test engine fails gracefully when candles_df is empty (e.g. after date filtering)."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.candles_df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime([]),
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
        }
    )

    results = engine.run()

    assert "error" in results
    assert results["error"] == "no_data"


def test_engine_does_not_print_htf_unavailable_debug(monkeypatch):
    """Regression: HTF-unavailable should not spam stdout via print()."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.position_tracker.position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100.0,
        entry_time=datetime(2025, 1, 1),
    )

    def _fail_print(*_args, **_kwargs):
        raise AssertionError("print() should not be called for HTF debug")

    monkeypatch.setattr(builtins, "print", _fail_print)

    engine._initialize_position_exit_context(
        result={"features": {}},
        meta={
            "features": {"htf_fibonacci": {"available": False, "reason": "HTF_LEVELS_INCOMPLETE"}}
        },
        entry_price=100.0,
        timestamp=datetime(2025, 1, 1),
    )


def test_check_htf_exit_invalid_precomputed_context_forces_unavailable(sample_candles_data):
    """Regression: invalid precomputed HTF values must not be exposed as available context."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.candles_df = sample_candles_data
    engine._prepare_numpy_arrays()

    engine.position_tracker.position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100.0,
        entry_time=datetime(2025, 1, 1),
    )

    engine._precomputed_features = {
        "htf_fib_0382": [0.0],
        "htf_fib_05": [float("nan")],
        "htf_fib_0618": [101.0],
        "htf_swing_high": [0.0],
        "htf_swing_low": [99.0],
    }

    captured_context: dict = {}

    def _fake_check_exits(_position, _bar_data, htf_context, _indicators):
        captured_context["value"] = htf_context
        return []

    engine.htf_exit_engine.check_exits = _fake_check_exits

    reason = engine._check_htf_exit_conditions(
        current_price=100.0,
        timestamp=datetime(2025, 1, 1),
        bar_data={
            "timestamp": datetime(2025, 1, 1),
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0,
        },
        result={"features": {}, "confidence": 1.0, "regime": "NEUTRAL"},
        meta={"decision": {"state_out": {}}},
        configs={"exit": {"enabled": True}},
        bar_index=0,
    )

    assert reason is None
    assert captured_context["value"]["available"] is False
    assert engine._htf_context_seen is False


def test_check_htf_exit_out_of_range_precomputed_context_does_not_fallback_to_meta(
    sample_candles_data,
):
    """Regression: out-of-range precomputed HTF access must not silently fall back to meta."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.candles_df = sample_candles_data
    engine._prepare_numpy_arrays()

    engine.position_tracker.position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100.0,
        entry_time=datetime(2025, 1, 1),
    )

    engine._precomputed_features = {
        "htf_fib_0382": [99.5],
        "htf_fib_05": [100.0],
        "htf_fib_0618": [100.5],
        "htf_swing_high": [102.0],
        "htf_swing_low": [98.0],
    }

    captured_context: dict = {}

    def _fake_check_exits(_position, _bar_data, htf_context, _indicators):
        captured_context["value"] = htf_context
        return []

    engine.htf_exit_engine.check_exits = _fake_check_exits

    reason = engine._check_htf_exit_conditions(
        current_price=100.0,
        timestamp=datetime(2025, 1, 1, 0, 15),
        bar_data={
            "timestamp": datetime(2025, 1, 1, 0, 15),
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0,
        },
        result={"features": {}, "confidence": 1.0, "regime": "NEUTRAL"},
        meta={
            "decision": {"state_out": {}},
            "features": {
                "htf_fibonacci": {
                    "available": True,
                    "levels": {0.382: 111.0, 0.5: 112.0, 0.618: 113.0},
                    "swing_high": 120.0,
                    "swing_low": 90.0,
                }
            },
        },
        configs={"exit": {"enabled": True}},
        bar_index=1,
    )

    assert reason is None
    assert captured_context["value"] == {"available": False}
    assert engine._htf_context_seen is False


def test_check_htf_exit_valid_precomputed_context_remains_available(sample_candles_data):
    """Regression: valid precomputed HTF values should still be forwarded as available."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.candles_df = sample_candles_data
    engine._prepare_numpy_arrays()

    engine.position_tracker.position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100.0,
        entry_time=datetime(2025, 1, 1),
    )

    engine._precomputed_features = {
        "htf_fib_0382": [99.5],
        "htf_fib_05": [100.0],
        "htf_fib_0618": [100.5],
        "htf_swing_high": [102.0],
        "htf_swing_low": [98.0],
    }

    captured_context: dict = {}

    def _fake_check_exits(_position, _bar_data, htf_context, _indicators):
        captured_context["value"] = htf_context
        return []

    engine.htf_exit_engine.check_exits = _fake_check_exits

    reason = engine._check_htf_exit_conditions(
        current_price=100.0,
        timestamp=datetime(2025, 1, 1),
        bar_data={
            "timestamp": datetime(2025, 1, 1),
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0,
        },
        result={"features": {}, "confidence": 1.0, "regime": "NEUTRAL"},
        meta={"decision": {"state_out": {}}},
        configs={"exit": {"enabled": True}},
        bar_index=0,
    )

    assert reason is None
    assert captured_context["value"]["available"] is True
    assert captured_context["value"]["levels"][0.5] == pytest.approx(100.0)
    assert engine._htf_context_seen is True


def test_engine_run_with_minimal_data(sample_candles_data):
    """Test engine runs successfully with minimal data."""
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        warmup_bars=10,  # Low warmup for testing
        initial_capital=10000.0,
    )
    engine.candles_df = sample_candles_data

    policy = {"symbol": "tBTCUSD", "timeframe": "15m"}
    configs = {
        "thresholds": {"entry_conf_overall": 0.9},  # High threshold = no trades
        "risk": {"risk_map": [[0.7, 0.01]]},
    }

    results = engine.run(policy=policy, configs=configs, verbose=False)

    assert "error" not in results
    assert "backtest_info" in results
    assert "summary" in results
    assert "trades" in results
    assert "equity_curve" in results


def test_engine_run_skip_champion_merge_does_not_load_champion(monkeypatch, sample_candles_data):
    """Optimizer/backtest configs should be authoritative (no implicit champion merge)."""

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        warmup_bars=10,
        initial_capital=10000.0,
    )
    engine.candles_df = sample_candles_data

    def _fail_load_cached(*_args, **_kwargs):
        raise AssertionError(
            "ChampionLoader.load_cached should not be called when skip_champion_merge"
        )

    monkeypatch.setattr(engine.champion_loader, "load_cached", _fail_load_cached)

    results = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "15m"},
        configs={
            "meta": {"skip_champion_merge": True},
            "thresholds": {"entry_conf_overall": 0.9},
            "risk": {"risk_map": [[0.7, 0.01]]},
        },
        verbose=False,
    )

    assert "error" not in results
    assert results.get("backtest_info", {}).get("effective_config_fingerprint")


def test_engine_run_default_loads_champion_and_fingerprint_changes(
    monkeypatch, sample_candles_data
):
    """By default the engine merges champion; fingerprint must reflect the effective config."""

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        warmup_bars=10,
        initial_capital=10000.0,
    )
    engine.candles_df = sample_candles_data

    called = {"count": 0}

    def _fake_load_cached(_symbol: str, _timeframe: str) -> ChampionConfig:
        called["count"] += 1
        return ChampionConfig(
            config={"thresholds": {"entry_conf_overall": 0.01}},
            source="tests/fake_champion.json",
            version="test",
            checksum="deadbeef",
            loaded_at="2025-01-01T00:00:00Z",
        )

    monkeypatch.setattr(engine.champion_loader, "load_cached", _fake_load_cached)

    results_merged = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "15m"},
        configs={
            "thresholds": {"entry_conf_overall": 0.9},
            "risk": {"risk_map": [[0.7, 0.01]]},
        },
        verbose=False,
    )

    assert called["count"] == 1
    fp_merged = results_merged.get("backtest_info", {}).get("effective_config_fingerprint")
    assert fp_merged

    # Same base config, but skip champion merge should yield a different effective fingerprint.
    engine2 = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        warmup_bars=10,
        initial_capital=10000.0,
    )
    engine2.candles_df = sample_candles_data

    monkeypatch.setattr(engine2.champion_loader, "load_cached", _fake_load_cached)

    results_skip = engine2.run(
        policy={"symbol": "tBTCUSD", "timeframe": "15m"},
        configs={
            "meta": {"skip_champion_merge": True},
            "thresholds": {"entry_conf_overall": 0.9},
            "risk": {"risk_map": [[0.7, 0.01]]},
        },
        verbose=False,
    )
    fp_skip = results_skip.get("backtest_info", {}).get("effective_config_fingerprint")
    assert fp_skip
    assert fp_skip != fp_merged


@pytest.mark.parametrize(
    ("engine_policy", "expect_propagated"),
    [("frozen_first", False), ("curated_only", True)],
)
def test_engine_run_propagates_only_explicit_nondefault_data_source_policy(
    monkeypatch,
    sample_candles_data,
    engine_policy,
    expect_propagated,
):
    """Only explicit non-default policy should be injected into downstream eval configs."""

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        warmup_bars=10,
        data_source_policy=engine_policy,
    )
    engine.candles_df = sample_candles_data.head(30)

    captured_configs: list[dict] = []

    def _fake_evaluate_pipeline(*, candles, policy, configs, state):
        captured_configs.append(dict(configs))
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

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _fake_evaluate_pipeline)

    caller_configs = {
        "meta": {"skip_champion_merge": True},
        "thresholds": {"entry_conf_overall": 0.99},
        "risk": {"risk_map": [[0.7, 0.01]]},
    }

    results = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "15m"},
        configs=caller_configs,
        verbose=False,
    )

    assert "error" not in results
    assert captured_configs
    first_seen = captured_configs[0]
    if expect_propagated:
        assert first_seen.get("data_source_policy") == "curated_only"
    else:
        assert "data_source_policy" not in first_seen
    assert "data_source_policy" not in caller_configs


def test_engine_results_format(sample_candles_data):
    """Test that engine results have correct format."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data

    results = engine.run()

    # Check backtest_info
    assert "symbol" in results["backtest_info"]
    assert "timeframe" in results["backtest_info"]
    assert "data_source_policy" in results["backtest_info"]
    assert "ltf_candles_source" in results["backtest_info"]
    assert "bars_total" in results["backtest_info"]
    assert "bars_processed" in results["backtest_info"]
    assert "execution_mode" in results["backtest_info"]
    assert "htf" in results["backtest_info"]
    assert "htf_candles_loaded" in results["backtest_info"]["htf"]
    assert "use_new_exit_engine" in results["backtest_info"]["htf"]
    assert "env_htf_exits" in results["backtest_info"]["htf"]
    assert "htf_context_seen" in results["backtest_info"]["htf"]

    # Check summary
    assert "initial_capital" in results["summary"]
    assert "final_capital" in results["summary"]
    assert "total_return" in results["summary"]
    assert "num_trades" in results["summary"]

    # Check trades list
    assert isinstance(results["trades"], list)

    # Check equity_curve
    assert isinstance(results["equity_curve"], list)
    if results["equity_curve"]:
        assert "timestamp" in results["equity_curve"][0]
        assert "total_equity" in results["equity_curve"][0]


def test_engine_processes_correct_number_of_bars(sample_candles_data):
    """Test that engine processes correct number of bars (excluding warmup)."""
    warmup = 50
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=warmup)
    engine.candles_df = sample_candles_data

    results = engine.run()

    expected_processed = len(sample_candles_data) - warmup
    assert results["backtest_info"]["bars_processed"] == expected_processed


def test_engine_equity_curve_tracking(sample_candles_data):
    """Test that equity curve is tracked for each bar."""
    warmup = 50
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=warmup)
    engine.candles_df = sample_candles_data

    results = engine.run()

    expected_bars = len(sample_candles_data) - warmup
    assert len(results["equity_curve"]) == expected_bars


def test_engine_closes_positions_at_end(sample_candles_data):
    """Test that engine closes all open positions at end of backtest."""
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        warmup_bars=10,
        commission_rate=0.0,
    )
    engine.candles_df = sample_candles_data

    # Force a trade by using low thresholds
    configs = {
        "thresholds": {"entry_conf_overall": 0.1},
        "risk": {"risk_map": [[0.1, 0.01]]},
    }

    engine.run(configs=configs)

    # After backtest, no open position should remain
    assert engine.position_tracker.position is None


def test_engine_state_persistence(sample_candles_data):
    """Test that state persists between bars."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data.head(50)  # Small dataset

    engine.run()

    # State should be preserved (not empty after processing)
    # The engine's internal state should have been used
    assert engine.bar_count > 0


def test_engine_raises_on_pipeline_errors(sample_candles_data, monkeypatch):
    """Backtest must keep collecting per-bar failures and raise after loop completion."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data.head(20)
    calls = {"n": 0}

    def _raise_pipeline_error(*_args, **_kwargs):
        calls["n"] += 1
        raise ValueError("forced per-bar failure")

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _raise_pipeline_error)

    with pytest.raises(
        RuntimeError,
        match=r"count=10, first_at_bar=10, first_error=ValueError: forced per-bar failure",
    ):
        engine.run(configs={})

    assert calls["n"] == 10


def test_engine_error_policy_continues_loop_before_raising(sample_candles_data, monkeypatch):
    """A single per-bar failure must still let the engine finish replay before raising."""

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data.head(20)

    processed_bars: list[int] = []

    def _pipeline_with_single_failure(*_args, **_kwargs):
        bar_index = len(processed_bars) + engine.warmup_bars
        processed_bars.append(bar_index)
        if len(processed_bars) == 1:
            raise ValueError("first processed bar failed")
        return (
            {"action": "NONE", "confidence": 0.5, "regime": "BALANCED", "features": {}},
            {"decision": {"size": 0.0, "state_out": {}, "reasons": []}},
        )

    monkeypatch.setattr(
        "core.backtest.engine.evaluate_pipeline",
        _pipeline_with_single_failure,
    )

    with pytest.raises(
        RuntimeError,
        match=r"count=1, first_at_bar=10, first_error=ValueError: first processed bar failed",
    ):
        engine.run(configs={"exit": {"enabled": False}})

    assert processed_bars == list(range(10, 20))


def test_engine_error_policy_fail_fast_raises_on_first_processed_bar(
    sample_candles_data, monkeypatch
):
    """fail_fast must stop replay on the first processed-bar pipeline error."""

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data.head(20)

    processed_bars: list[int] = []

    def _pipeline_with_single_failure(*_args, **_kwargs):
        bar_index = len(processed_bars) + engine.warmup_bars
        processed_bars.append(bar_index)
        raise ValueError("first processed bar failed")

    monkeypatch.setattr(
        "core.backtest.engine.evaluate_pipeline",
        _pipeline_with_single_failure,
    )

    with pytest.raises(
        RuntimeError,
        match=r"count=1, first_at_bar=10, first_error=ValueError: first processed bar failed",
    ):
        engine.run(configs={"exit": {"enabled": False}}, error_policy="fail_fast")

    assert processed_bars == [10]


def test_engine_run_rejects_invalid_error_policy(sample_candles_data):
    """Invalid explicit error_policy values must fail before replay starts."""

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data.head(20)

    with pytest.raises(ValueError, match="Invalid error_policy"):
        engine.run(configs={"exit": {"enabled": False}}, error_policy="best_effort")


def test_engine_with_verbose_mode(sample_candles_data, capsys):
    """Test engine verbose mode emits some user-facing progress/log output."""
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="15m",
        warmup_bars=10,
        commission_rate=0.0,
    )
    engine.candles_df = sample_candles_data.head(50)

    # Low thresholds to force trades
    configs = {
        "thresholds": {"entry_conf_overall": 0.1},
        "risk": {"risk_map": [[0.1, 0.01]]},
    }

    engine.run(configs=configs, verbose=True)

    # Check if any output was emitted (tqdm writes to stderr; logging may also use stderr)
    captured = capsys.readouterr()
    assert (
        "Backtest" in captured.err
        or "Backtest" in captured.out
        or "Running" in captured.err
        or "Running" in captured.out
    )


def test_engine_precompute_cache_write_failure_logs_warning(monkeypatch, caplog):
    import numpy as np

    dates = pd.date_range("2025-01-01", periods=80, freq="15min", tz="UTC")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "open": [100.0 + i * 0.1 for i in range(80)],
            "high": [100.5 + i * 0.1 for i in range(80)],
            "low": [99.5 + i * 0.1 for i in range(80)],
            "close": [100.2 + i * 0.1 for i in range(80)],
            "volume": [1000.0 + i for i in range(80)],
        }
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", fast_window=True)

    original_exists = Path.exists

    def _fake_exists(self: Path) -> bool:
        if self.name == "tBTCUSD_15m_frozen.parquet" and "raw" in self.parts:
            return True
        return original_exists(self)

    def _fake_read_parquet(_path, columns=None, **_kwargs):
        if columns is None:
            return df.copy()
        return df[columns].copy()

    def _raise_savez(*_args, **_kwargs):
        raise RuntimeError("cache write failed")

    monkeypatch.setattr(Path, "exists", _fake_exists)
    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)
    monkeypatch.setattr(np, "savez_compressed", _raise_savez)

    with caplog.at_level("WARNING"):
        ok = engine.load_data()

    assert ok is True
    assert "Failed to write precompute cache" in caplog.text


def test_engine_precompute_cache_key_failure_remains_non_fatal(tmp_path, monkeypatch, caplog):
    import core.backtest.engine as engine_mod

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

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
    monkeypatch.setattr(
        engine,
        "_precompute_cache_key",
        lambda _df: (_ for _ in ()).throw(RuntimeError("key boom")),
    )

    with caplog.at_level("WARNING"):
        ok = engine.load_data()

    assert ok is True
    assert engine._precomputed_features is None
    assert "Precomputation failed (non-fatal): key boom" in caplog.text


def test_engine_precompute_cache_write_can_be_disabled_without_creating_cache_dir(
    tmp_path, monkeypatch
):
    import numpy as np

    import core.backtest.engine as engine_mod

    fake_engine_file = tmp_path / "src" / "core" / "backtest" / "engine.py"
    fake_engine_file.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(engine_mod, "__file__", str(fake_engine_file))

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)

    ltf_ts = pd.date_range("2025-01-01", periods=80, freq="15min", tz="UTC")
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

    save_calls = {"count": 0}

    def _fake_savez(*_args, **_kwargs):
        save_calls["count"] += 1

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_CACHE_WRITE", "0")
    monkeypatch.setattr(np, "savez_compressed", _fake_savez)

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
    cache_dir = tmp_path / "cache" / "precomputed"

    assert cache_dir.exists() is False
    assert engine.load_data() is True
    assert engine._precomputed_features is not None
    assert save_calls["count"] == 0
    assert cache_dir.exists() is False


def test_engine_precompute_cache_write_disabled_still_reads_existing_cache(tmp_path, monkeypatch):
    import numpy as np

    import core.backtest.engine as engine_mod

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

    cache_dir = tmp_path / "cache" / "precomputed"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = "pytest_precompute_read_only"
    np.savez_compressed(
        cache_dir / f"{key}.npz",
        atr_14=np.asarray([1.0, 1.0], dtype=float),
        atr_50=np.asarray([1.0, 1.0], dtype=float),
        ema_20=np.asarray([1.0, 1.0], dtype=float),
        ema_50=np.asarray([1.0, 1.0], dtype=float),
        rsi_14=np.asarray([50.0, 50.0], dtype=float),
        bb_position_20_2=np.asarray([0.0, 0.0], dtype=float),
        adx_14=np.asarray([20.0, 20.0], dtype=float),
        fib_high_idx=np.asarray([0], dtype=int),
        fib_low_idx=np.asarray([0], dtype=int),
        fib_high_px=np.asarray([100.0], dtype=float),
        fib_low_px=np.asarray([90.0], dtype=float),
    )

    save_calls = {"count": 0}

    def _fake_savez(*_args, **_kwargs):
        save_calls["count"] += 1

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_CACHE_WRITE", "0")
    monkeypatch.setattr(np, "savez_compressed", _fake_savez)

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
    monkeypatch.setattr(engine, "_precompute_cache_key", lambda _df: key)

    assert engine.load_data() is True
    assert engine._precomputed_features is not None
    assert engine._precomputed_features["atr_14"] == [1.0, 1.0]
    assert save_calls["count"] == 0


def test_engine_precompute_cache_metadata_payload_loads_when_valid(tmp_path, monkeypatch):
    import numpy as np

    import core.backtest.engine as engine_mod

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

    cache_dir = tmp_path / "cache" / "precomputed"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = "pytest_precompute_metadata_valid"
    candle_count = len(ltf_ts)
    metadata = json.dumps(
        {
            "schema_version": int(engine_mod.PRECOMPUTE_SCHEMA_VERSION),
            "material": engine_mod._precompute_cache_key_material(),
            "candle_count": candle_count,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    np.savez_compressed(
        cache_dir / f"{key}.npz",
        **{
            engine_mod._PRECOMPUTE_CACHE_METADATA_KEY: metadata,
            "atr_14": np.full(candle_count, 7.0, dtype=float),
            "atr_50": np.full(candle_count, 8.0, dtype=float),
            "ema_20": np.full(candle_count, 9.0, dtype=float),
            "ema_50": np.full(candle_count, 10.0, dtype=float),
            "rsi_14": np.full(candle_count, 11.0, dtype=float),
            "bb_position_20_2": np.full(candle_count, 12.0, dtype=float),
            "adx_14": np.full(candle_count, 13.0, dtype=float),
            "fib_high_idx": np.asarray([0, 16, 32], dtype=int),
            "fib_low_idx": np.asarray([8, 24, 40], dtype=int),
            "fib_high_px": np.asarray([101.0, 111.0, 121.0], dtype=float),
            "fib_low_px": np.asarray([99.0, 109.0, 119.0], dtype=float),
        },
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_CACHE_WRITE", "0")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
    monkeypatch.setattr(engine, "_precompute_cache_key", lambda _df: key)

    assert engine.load_data() is True
    assert engine._precomputed_features is not None
    assert len(engine._precomputed_features["atr_14"]) == candle_count
    assert engine._precomputed_features["atr_14"][0] == pytest.approx(7.0)
    assert engine._precomputed_features["fib_high_idx"] == [0, 16, 32]


def test_engine_precompute_cache_metadata_payload_recomputes_on_dense_length_mismatch(
    tmp_path, monkeypatch, caplog
):
    import numpy as np

    import core.backtest.engine as engine_mod

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

    cache_dir = tmp_path / "cache" / "precomputed"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = "pytest_precompute_metadata_invalid"
    candle_count = len(ltf_ts)
    metadata = json.dumps(
        {
            "schema_version": int(engine_mod.PRECOMPUTE_SCHEMA_VERSION),
            "material": engine_mod._precompute_cache_key_material(),
            "candle_count": candle_count,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    np.savez_compressed(
        cache_dir / f"{key}.npz",
        **{
            engine_mod._PRECOMPUTE_CACHE_METADATA_KEY: metadata,
            "atr_14": np.asarray([999.0, 999.0], dtype=float),
            "atr_50": np.asarray([999.0, 999.0], dtype=float),
            "ema_20": np.asarray([999.0, 999.0], dtype=float),
            "ema_50": np.asarray([999.0, 999.0], dtype=float),
            "rsi_14": np.asarray([999.0, 999.0], dtype=float),
            "bb_position_20_2": np.asarray([999.0, 999.0], dtype=float),
            "adx_14": np.asarray([999.0, 999.0], dtype=float),
            "fib_high_idx": np.asarray([0, 16, 32], dtype=int),
            "fib_low_idx": np.asarray([8, 24, 40], dtype=int),
            "fib_high_px": np.asarray([101.0, 111.0, 121.0], dtype=float),
            "fib_low_px": np.asarray([99.0, 109.0, 119.0], dtype=float),
        },
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_CACHE_WRITE", "0")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
    monkeypatch.setattr(engine, "_precompute_cache_key", lambda _df: key)

    with caplog.at_level("WARNING"):
        assert engine.load_data() is True

    assert engine._precomputed_features is not None
    assert len(engine._precomputed_features["atr_14"]) == candle_count
    assert engine._precomputed_features["atr_14"][0] != pytest.approx(999.0)
    assert "Ignoring precompute cache" in caplog.text


def test_engine_precompute_cache_metadata_payload_recomputes_on_material_mismatch(
    tmp_path, monkeypatch, caplog
):
    import numpy as np

    import core.backtest.engine as engine_mod

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

    cache_dir = tmp_path / "cache" / "precomputed"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = "pytest_precompute_metadata_material_mismatch"
    candle_count = len(ltf_ts)
    metadata = json.dumps(
        {
            "schema_version": int(engine_mod.PRECOMPUTE_SCHEMA_VERSION),
            "material": "v999_wrong_material",
            "candle_count": candle_count,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    np.savez_compressed(
        cache_dir / f"{key}.npz",
        **{
            engine_mod._PRECOMPUTE_CACHE_METADATA_KEY: metadata,
            "atr_14": np.full(candle_count, 777.0, dtype=float),
            "atr_50": np.full(candle_count, 778.0, dtype=float),
            "ema_20": np.full(candle_count, 779.0, dtype=float),
            "ema_50": np.full(candle_count, 780.0, dtype=float),
            "rsi_14": np.full(candle_count, 781.0, dtype=float),
            "bb_position_20_2": np.full(candle_count, 782.0, dtype=float),
            "adx_14": np.full(candle_count, 783.0, dtype=float),
            "fib_high_idx": np.asarray([0, 16, 32], dtype=int),
            "fib_low_idx": np.asarray([8, 24, 40], dtype=int),
            "fib_high_px": np.asarray([101.0, 111.0, 121.0], dtype=float),
            "fib_low_px": np.asarray([99.0, 109.0, 119.0], dtype=float),
        },
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_CACHE_WRITE", "0")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
    monkeypatch.setattr(engine, "_precompute_cache_key", lambda _df: key)

    with caplog.at_level("WARNING"):
        assert engine.load_data() is True

    assert engine._precomputed_features is not None
    assert len(engine._precomputed_features["atr_14"]) == candle_count
    assert engine._precomputed_features["atr_14"][0] != pytest.approx(777.0)
    assert "metadata_mismatch:material" in caplog.text


def test_engine_precompute_cache_metadata_payload_recomputes_on_swing_pair_misalignment(
    tmp_path, monkeypatch, caplog
):
    import numpy as np

    import core.backtest.engine as engine_mod

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

    cache_dir = tmp_path / "cache" / "precomputed"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = "pytest_precompute_metadata_swing_mismatch"
    candle_count = len(ltf_ts)
    metadata = json.dumps(
        {
            "schema_version": int(engine_mod.PRECOMPUTE_SCHEMA_VERSION),
            "material": engine_mod._precompute_cache_key_material(),
            "candle_count": candle_count,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    np.savez_compressed(
        cache_dir / f"{key}.npz",
        **{
            engine_mod._PRECOMPUTE_CACHE_METADATA_KEY: metadata,
            "atr_14": np.full(candle_count, 555.0, dtype=float),
            "atr_50": np.full(candle_count, 556.0, dtype=float),
            "ema_20": np.full(candle_count, 557.0, dtype=float),
            "ema_50": np.full(candle_count, 558.0, dtype=float),
            "rsi_14": np.full(candle_count, 559.0, dtype=float),
            "bb_position_20_2": np.full(candle_count, 560.0, dtype=float),
            "adx_14": np.full(candle_count, 561.0, dtype=float),
            "fib_high_idx": np.asarray([0, 16, 32], dtype=int),
            "fib_low_idx": np.asarray([8, 24, 40], dtype=int),
            "fib_high_px": np.asarray([101.0, 111.0], dtype=float),
            "fib_low_px": np.asarray([99.0, 109.0, 119.0], dtype=float),
        },
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_CACHE_WRITE", "0")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
    monkeypatch.setattr(engine, "_precompute_cache_key", lambda _df: key)

    with caplog.at_level("WARNING"):
        assert engine.load_data() is True

    assert engine._precomputed_features is not None
    assert len(engine._precomputed_features["atr_14"]) == candle_count
    assert engine._precomputed_features["atr_14"][0] != pytest.approx(555.0)
    assert "misaligned_swing_pair:fib_high_idx" in caplog.text


def test_engine_precompute_cache_write_disabled_preserves_cache_miss_runtime_parity(
    tmp_path, monkeypatch
):
    import shutil

    import core.backtest.engine as engine_mod

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

    cache_dir = tmp_path / "cache" / "precomputed"
    base_configs = {
        "meta": {"skip_champion_merge": True},
        "thresholds": {"entry_conf_overall": 0.99},
        "risk": {"risk_map": [[0.7, 0.01]]},
    }

    def _run_with(cache_write_flag: str | None):
        if cache_write_flag is None:
            monkeypatch.delenv("GENESIS_PRECOMPUTE_CACHE_WRITE", raising=False)
        else:
            monkeypatch.setenv("GENESIS_PRECOMPUTE_CACHE_WRITE", cache_write_flag)

        engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10, fast_window=True)
        assert engine.load_data() is True
        return engine.run(
            policy={"symbol": "tBTCUSD", "timeframe": "15m"},
            configs=base_configs,
            verbose=False,
        )

    default_results = _run_with(None)
    assert cache_dir.exists() is True

    shutil.rmtree(cache_dir)
    assert cache_dir.exists() is False

    suppressed_results = _run_with("0")

    assert suppressed_results["summary"] == default_results["summary"]
    assert suppressed_results["metrics"] == default_results["metrics"]
    assert suppressed_results["trades"] == default_results["trades"]
    assert len(suppressed_results["equity_curve"]) == len(default_results["equity_curve"])
    assert cache_dir.exists() is False


def test_engine_precompute_cache_hit_htf_mapping_does_not_require_local_fib_cfg(
    tmp_path, monkeypatch
):
    """Regression: HTF mapping should work even when precompute loads from cache.

    Previously, a cache-hit could skip the block that defines `fib_cfg`, causing
    UnboundLocalError when mapping HTF Fibonacci levels.
    """

    import numpy as np

    import core.backtest.engine as engine_mod

    # Create a minimal fake repo layout rooted at tmp_path.
    fake_engine_file = tmp_path / "src" / "core" / "backtest" / "engine.py"
    fake_engine_file.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(engine_mod, "__file__", str(fake_engine_file))

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)

    # LTF candles (1h)
    ltf_ts = pd.date_range("2025-01-01", periods=48, freq="1h", tz="UTC")
    ltf = pd.DataFrame(
        {
            "timestamp": ltf_ts,
            "open": np.linspace(100.0, 120.0, len(ltf_ts)),
            "high": np.linspace(101.0, 121.0, len(ltf_ts)),
            "low": np.linspace(99.0, 119.0, len(ltf_ts)),
            "close": np.linspace(100.5, 120.5, len(ltf_ts)),
            "volume": np.full(len(ltf_ts), 1000.0),
        }
    )
    ltf.to_parquet(data_raw / "tBTCUSD_1h_frozen.parquet", index=False)

    # HTF candles (1D)
    htf_ts = pd.date_range("2024-12-15", periods=40, freq="1D", tz="UTC")
    htf = pd.DataFrame(
        {
            "timestamp": htf_ts,
            "open": np.linspace(90.0, 110.0, len(htf_ts)),
            "high": np.linspace(91.0, 111.0, len(htf_ts)),
            "low": np.linspace(89.0, 109.0, len(htf_ts)),
            "close": np.linspace(90.5, 110.5, len(htf_ts)),
        }
    )
    htf.to_parquet(data_raw / "tBTCUSD_1D_frozen.parquet", index=False)

    # Create a precompute cache file so load_data takes the cache-hit path.
    cache_dir = tmp_path / "cache" / "precomputed"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = "pytest_precompute_cachehit"
    np.savez_compressed(
        cache_dir / f"{key}.npz",
        atr_14=np.asarray([1.0, 1.0], dtype=float),
        atr_50=np.asarray([1.0, 1.0], dtype=float),
        ema_20=np.asarray([1.0, 1.0], dtype=float),
        ema_50=np.asarray([1.0, 1.0], dtype=float),
        rsi_14=np.asarray([50.0, 50.0], dtype=float),
        bb_position_20_2=np.asarray([0.0, 0.0], dtype=float),
        adx_14=np.asarray([20.0, 20.0], dtype=float),
        fib_high_idx=np.asarray([0], dtype=int),
        fib_low_idx=np.asarray([0], dtype=int),
        fib_high_px=np.asarray([100.0], dtype=float),
        fib_low_px=np.asarray([90.0], dtype=float),
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    monkeypatch.setenv("GENESIS_HTF_EXITS", "1")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=10, fast_window=True)
    # Ensure the HTF loader path is active regardless of optional engine availability.
    engine._use_new_exit_engine = True
    monkeypatch.setattr(engine, "_precompute_cache_key", lambda _df: key)

    assert engine.load_data() is True
    assert engine._precomputed_features is not None
    # HTF mapping should have been added to precomputed features.
    assert "htf_fib_05" in engine._precomputed_features
    assert len(engine._precomputed_features["htf_fib_05"]) == len(engine.candles_df)
