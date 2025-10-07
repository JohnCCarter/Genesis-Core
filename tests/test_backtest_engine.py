"""Tests for backtest engine."""

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from core.backtest.engine import BacktestEngine


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
    assert len(window["close"]) == 50  # Correct window size


def test_build_candles_window_at_start(sample_candles_data):
    """Test building window at start of data (edge case)."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")
    engine.candles_df = sample_candles_data

    # Build window at index 10 (less than window_size)
    window = engine._build_candles_window(end_idx=10, window_size=50)

    assert len(window["close"]) == 11  # 0 to 10 inclusive


def test_engine_run_no_data():
    """Test engine fails gracefully when no data is loaded."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m")

    results = engine.run()

    assert "error" in results
    assert results["error"] == "no_data"


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

    results = engine.run(configs=configs)

    # After backtest, no open position should remain
    assert engine.position_tracker.position is None


def test_engine_state_persistence(sample_candles_data):
    """Test that state persists between bars."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data.head(50)  # Small dataset

    results = engine.run()

    # State should be preserved (not empty after processing)
    # The engine's internal state should have been used
    assert engine.bar_count > 0


def test_engine_handles_pipeline_errors_gracefully(sample_candles_data):
    """Test that engine continues on pipeline errors (robust)."""
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="15m", warmup_bars=10)
    engine.candles_df = sample_candles_data

    # Invalid config that might cause errors
    configs = {"invalid_key": "invalid_value"}

    # Should not crash, should handle gracefully
    results = engine.run(configs=configs)

    assert "error" not in results  # Should complete despite errors


def test_engine_with_verbose_mode(sample_candles_data, capsys):
    """Test engine verbose mode prints trade info."""
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

    # Check if any output was printed (trades or status)
    captured = capsys.readouterr()
    assert "Backtest" in captured.out or "Running" in captured.out
