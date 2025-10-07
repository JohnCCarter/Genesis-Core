"""Tests for backtest trade logger."""

import json
from pathlib import Path

import pandas as pd
import pytest

from core.backtest.trade_logger import TradeLogger


@pytest.fixture
def sample_backtest_results():
    """Create sample backtest results for testing."""
    return {
        "backtest_info": {
            "symbol": "tBTCUSD",
            "timeframe": "15m",
            "start_date": "2025-01-01",
            "end_date": "2025-01-10",
            "bars_total": 1000,
            "bars_processed": 950,
            "warmup_bars": 50,
        },
        "summary": {
            "initial_capital": 10000.0,
            "final_capital": 10500.0,
            "total_return": 5.0,
            "total_return_usd": 500.0,
            "total_commission": 15.0,
            "num_trades": 3,
            "winning_trades": 2,
            "losing_trades": 1,
            "win_rate": 66.67,
            "avg_win": 300.0,
            "avg_loss": -100.0,
            "profit_factor": 3.0,
        },
        "trades": [
            {
                "symbol": "tBTCUSD",
                "side": "LONG",
                "size": 0.1,
                "entry_price": 100.0,
                "entry_time": "2025-01-02T10:00:00",
                "exit_price": 105.0,
                "exit_time": "2025-01-02T14:00:00",
                "pnl": 0.5,
                "pnl_pct": 5.0,
                "commission": 0.01,
            },
            {
                "symbol": "tBTCUSD",
                "side": "SHORT",
                "size": 0.1,
                "entry_price": 105.0,
                "entry_time": "2025-01-03T10:00:00",
                "exit_price": 103.0,
                "exit_time": "2025-01-03T14:00:00",
                "pnl": 0.2,
                "pnl_pct": 2.0,
                "commission": 0.01,
            },
        ],
        "equity_curve": [
            {
                "timestamp": "2025-01-01T10:00:00",
                "capital": 10000.0,
                "unrealized_pnl": 0.0,
                "total_equity": 10000.0,
            },
            {
                "timestamp": "2025-01-02T14:00:00",
                "capital": 10500.0,
                "unrealized_pnl": 0.0,
                "total_equity": 10500.0,
            },
        ],
    }


def test_trade_logger_initialization(tmp_path):
    """Test TradeLogger initialization."""
    output_dir = tmp_path / "test_results"
    logger = TradeLogger(output_dir=output_dir)

    assert logger.output_dir == output_dir
    assert output_dir.exists()  # Should create directory


def test_save_results_json(tmp_path, sample_backtest_results):
    """Test saving results to JSON."""
    logger = TradeLogger(output_dir=tmp_path)

    saved_files = logger.save_results(sample_backtest_results)

    assert "json" in saved_files
    json_file = saved_files["json"]
    assert json_file.exists()
    assert json_file.suffix == ".json"

    # Verify content
    with open(json_file, "r") as f:
        loaded_data = json.load(f)

    assert loaded_data["backtest_info"]["symbol"] == "tBTCUSD"
    assert loaded_data["summary"]["num_trades"] == 3


def test_save_results_with_custom_prefix(tmp_path, sample_backtest_results):
    """Test saving results with custom filename prefix."""
    logger = TradeLogger(output_dir=tmp_path)

    saved_files = logger.save_results(
        sample_backtest_results, filename_prefix="custom_test"
    )

    json_file = saved_files["json"]
    assert "custom_test" in json_file.name


def test_save_results_filename_includes_timestamp(tmp_path, sample_backtest_results):
    """Test that saved filename includes timestamp."""
    logger = TradeLogger(output_dir=tmp_path)

    saved_files = logger.save_results(sample_backtest_results)

    json_file = saved_files["json"]
    # Filename should contain date/time (YYYYMMDD_HHMMSS format)
    assert len(json_file.stem.split("_")) >= 3  # symbol_timeframe_timestamp


def test_save_trades_csv(tmp_path, sample_backtest_results):
    """Test saving trades to CSV."""
    logger = TradeLogger(output_dir=tmp_path)

    csv_file = logger.save_trades_csv(sample_backtest_results)

    assert csv_file is not None
    assert csv_file.exists()
    assert csv_file.suffix == ".csv"

    # Verify content
    df = pd.read_csv(csv_file)
    assert len(df) == 2  # Two trades
    assert "symbol" in df.columns
    assert "pnl" in df.columns
    assert df["symbol"].iloc[0] == "tBTCUSD"


def test_save_trades_csv_no_trades(tmp_path):
    """Test saving trades CSV when there are no trades."""
    logger = TradeLogger(output_dir=tmp_path)

    results = {"trades": []}
    csv_file = logger.save_trades_csv(results)

    assert csv_file is None  # Should return None for empty trades


def test_save_equity_curve_csv(tmp_path, sample_backtest_results):
    """Test saving equity curve to CSV."""
    logger = TradeLogger(output_dir=tmp_path)

    csv_file = logger.save_equity_curve_csv(sample_backtest_results)

    assert csv_file is not None
    assert csv_file.exists()
    assert csv_file.suffix == ".csv"

    # Verify content
    df = pd.read_csv(csv_file)
    assert len(df) == 2  # Two equity points
    assert "timestamp" in df.columns
    assert "total_equity" in df.columns


def test_save_equity_curve_csv_no_data(tmp_path):
    """Test saving equity curve CSV when there is no data."""
    logger = TradeLogger(output_dir=tmp_path)

    results = {"equity_curve": []}
    csv_file = logger.save_equity_curve_csv(results)

    assert csv_file is None  # Should return None for empty curve


def test_save_all(tmp_path, sample_backtest_results):
    """Test saving all outputs (JSON + CSVs)."""
    logger = TradeLogger(output_dir=tmp_path)

    saved_files = logger.save_all(sample_backtest_results)

    assert "json" in saved_files
    assert "trades_csv" in saved_files
    assert "equity_csv" in saved_files

    # Verify all files exist
    assert saved_files["json"].exists()
    assert saved_files["trades_csv"].exists()
    assert saved_files["equity_csv"].exists()


def test_save_all_creates_trades_subdirectory(tmp_path, sample_backtest_results):
    """Test that trades CSV is saved in trades subdirectory."""
    logger = TradeLogger(output_dir=tmp_path / "backtests")

    saved_files = logger.save_all(sample_backtest_results)

    trades_file = saved_files["trades_csv"]
    # Should be in ../trades/ directory
    assert "trades" in str(trades_file.parent)


def test_multiple_saves_dont_overwrite(tmp_path, sample_backtest_results):
    """Test that multiple saves create different files (timestamp)."""
    logger = TradeLogger(output_dir=tmp_path)

    # Save twice
    saved_files_1 = logger.save_results(sample_backtest_results)
    
    import time
    time.sleep(1)  # Ensure different timestamp
    
    saved_files_2 = logger.save_results(sample_backtest_results)

    # Should be different files
    assert saved_files_1["json"] != saved_files_2["json"]
    assert saved_files_1["json"].exists()
    assert saved_files_2["json"].exists()


def test_directory_creation_on_init(tmp_path):
    """Test that TradeLogger creates output directory if it doesn't exist."""
    output_dir = tmp_path / "nonexistent" / "results"
    
    logger = TradeLogger(output_dir=output_dir)

    assert output_dir.exists()


def test_trades_csv_directory_creation(tmp_path, sample_backtest_results):
    """Test that trades subdirectory is created if it doesn't exist."""
    logger = TradeLogger(output_dir=tmp_path / "backtests")

    csv_file = logger.save_trades_csv(sample_backtest_results)

    trades_dir = csv_file.parent
    assert trades_dir.exists()
    assert "trades" in trades_dir.name
