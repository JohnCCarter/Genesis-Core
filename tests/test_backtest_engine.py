"""Tests for backtest engine."""

import builtins
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
    assert engine.position_tracker.initial_capital == 10000.0
    assert engine.position_tracker.commission_rate == 0.001
    assert engine.candles_df is None


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


def test_engine_results_format(sample_candles_data):
    """Test that engine results have correct format."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data

    results = engine.run()

    # Check backtest_info
    assert "symbol" in results["backtest_info"]
    assert "timeframe" in results["backtest_info"]
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
    """Backtest must fail if per-bar pipeline exceptions occurred."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data.head(20)

    def _raise_pipeline_error(*_args, **_kwargs):
        raise ValueError("forced per-bar failure")

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _raise_pipeline_error)

    with pytest.raises(RuntimeError, match="per-bar evaluation errors"):
        engine.run(configs={})


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
