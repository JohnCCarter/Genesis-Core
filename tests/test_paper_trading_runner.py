"""
Tests for Paper Trading Runner

Tests candle-close detection and idempotency logic without network calls.
"""

# Import from scripts (add to path if needed)
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from paper_trading_runner import (
    RunnerState,
    _timeframe_to_ms,
    fetch_latest_candle,
    load_state,
    save_state,
)

# --- Timeframe Conversion Tests ---


def test_timeframe_to_ms():
    """Test timeframe string to milliseconds conversion."""
    assert _timeframe_to_ms("1m") == 60 * 1000
    assert _timeframe_to_ms("5m") == 5 * 60 * 1000
    assert _timeframe_to_ms("15m") == 15 * 60 * 1000
    assert _timeframe_to_ms("1h") == 60 * 60 * 1000
    assert _timeframe_to_ms("4h") == 4 * 60 * 60 * 1000
    assert _timeframe_to_ms("1D") == 24 * 60 * 60 * 1000
    assert _timeframe_to_ms("unknown") == 60 * 60 * 1000  # Default 1h


# --- State Persistence Tests ---


def test_state_roundtrip(tmp_path):
    """Test state serialization and deserialization."""
    state_file = tmp_path / "test_state.json"

    # Create state
    state = RunnerState(
        last_processed_candle_ts=1234567890000,
        total_evaluations=42,
        total_orders_submitted=10,
        last_heartbeat="2026-02-04T10:00:00Z",
    )

    # Save
    logger = Mock()
    save_state(state, state_file, logger)

    # Load
    loaded = load_state(state_file, logger)

    assert loaded.last_processed_candle_ts == state.last_processed_candle_ts
    assert loaded.total_evaluations == state.total_evaluations
    assert loaded.total_orders_submitted == state.total_orders_submitted
    assert loaded.last_heartbeat == state.last_heartbeat


def test_load_state_missing_file(tmp_path):
    """Test loading state when file doesn't exist."""
    state_file = tmp_path / "nonexistent.json"
    logger = Mock()

    state = load_state(state_file, logger)

    assert state.last_processed_candle_ts is None
    assert state.total_evaluations == 0
    assert state.total_orders_submitted == 0


def test_load_state_corrupt_file_fails(tmp_path):
    """Test that corrupt state file causes fail-closed exit."""
    state_file = tmp_path / "corrupt.json"
    state_file.write_text("not valid json {{{")

    logger = Mock()

    with pytest.raises(SystemExit) as exc:
        load_state(state_file, logger)

    assert exc.value.code == 1
    logger.error.assert_called()


# --- Candle-Close Detection Tests ---


@patch("paper_trading_runner.time.time")
def test_fetch_latest_candle_closed(mock_time):
    """Test fetching latest candle when it's closed."""
    # Mock current time: 2 hours after candle start
    candle_ts = 1704067200000  # 2024-01-01 00:00:00 UTC
    candle_duration = 60 * 60 * 1000  # 1h
    current_time = (candle_ts + candle_duration + 60 * 1000) / 1000  # 1 min after close

    mock_time.return_value = current_time

    # Mock Bitfinex response (2 candles)
    mock_response = Mock()
    mock_response.json.return_value = [
        [candle_ts, 50000.0, 50100.0, 50200.0, 49900.0, 100.5],  # Latest
        [candle_ts - candle_duration, 49900.0, 50000.0, 50100.0, 49800.0, 95.3],  # Previous
    ]
    mock_response.raise_for_status = Mock()

    mock_client = Mock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    logger = Mock()

    candle = fetch_latest_candle("tBTCUSD", "1h", mock_client, logger)

    assert candle is not None
    assert candle["ts"] == candle_ts
    assert candle["open"] == 50000.0
    assert candle["close"] == 50100.0
    assert candle["high"] == 50200.0
    assert candle["low"] == 49900.0
    assert candle["volume"] == 100.5


@patch("paper_trading_runner.time.time")
def test_fetch_latest_candle_forming(mock_time):
    """Test fetching candle when latest is still forming."""
    # Mock current time: BEFORE latest candle closes
    candle_ts = 1704067200000  # 2024-01-01 00:00:00 UTC
    candle_duration = 60 * 60 * 1000  # 1h
    current_time = (candle_ts + 30 * 60 * 1000) / 1000  # 30 min into candle (still forming)

    mock_time.return_value = current_time

    # Mock Bitfinex response
    previous_ts = candle_ts - candle_duration
    mock_response = Mock()
    mock_response.json.return_value = [
        [candle_ts, 50000.0, 50100.0, 50200.0, 49900.0, 50.0],  # Latest (forming)
        [previous_ts, 49900.0, 50000.0, 50100.0, 49800.0, 95.3],  # Previous (closed)
    ]
    mock_response.raise_for_status = Mock()

    mock_client = Mock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    logger = Mock()

    candle = fetch_latest_candle("tBTCUSD", "1h", mock_client, logger)

    assert candle is not None
    # Should return previous candle since latest is still forming
    assert candle["ts"] == previous_ts


def test_fetch_latest_candle_http_error():
    """Test handling of HTTP errors during candle fetch."""
    mock_client = Mock(spec=httpx.Client)
    mock_client.get.side_effect = httpx.HTTPError("Connection failed")

    logger = Mock()

    candle = fetch_latest_candle("tBTCUSD", "1h", mock_client, logger)

    assert candle is None
    logger.error.assert_called()


# --- Idempotency Tests ---


def test_idempotency_skips_processed_candles(tmp_path):
    """Test that already-processed candles are skipped."""
    state_file = tmp_path / "state.json"

    # State: candle 1000 already processed
    state = RunnerState(last_processed_candle_ts=1000)
    logger = Mock()
    save_state(state, state_file, logger)

    # Load state
    loaded = load_state(state_file, logger)

    # Try to process candle 900 (older than last processed)
    assert loaded.last_processed_candle_ts == 1000
    should_skip = 900 <= loaded.last_processed_candle_ts
    assert should_skip is True

    # Try to process candle 1100 (newer than last processed)
    should_skip = 1100 <= loaded.last_processed_candle_ts
    assert should_skip is False


def test_idempotency_processes_new_candles(tmp_path):
    """Test that new candles are processed after restart."""
    state_file = tmp_path / "state.json"

    # Initial state: candle 1000 processed
    state = RunnerState(last_processed_candle_ts=1000, total_evaluations=5)
    logger = Mock()
    save_state(state, state_file, logger)

    # Simulate restart: load state
    loaded = load_state(state_file, logger)

    assert loaded.last_processed_candle_ts == 1000
    assert loaded.total_evaluations == 5

    # Process new candle 2000
    new_candle_ts = 2000
    should_skip = new_candle_ts <= loaded.last_processed_candle_ts
    assert should_skip is False

    # Update state
    loaded.last_processed_candle_ts = new_candle_ts
    loaded.total_evaluations += 1
    save_state(loaded, state_file, logger)

    # Verify persistence
    reloaded = load_state(state_file, logger)
    assert reloaded.last_processed_candle_ts == 2000
    assert reloaded.total_evaluations == 6


# --- Champion Verification Tests ---


def test_champion_verification():
    """Test champion verification from eval response."""
    from paper_trading_runner import verify_champion_loaded

    logger = Mock()

    # Champion loaded
    eval_resp = {"meta": {"champion": {"source": "config\\strategy\\champions\\tBTCUSD_1h.json"}}}
    assert verify_champion_loaded(eval_resp, logger) is True

    # Baseline fallback
    eval_resp = {"meta": {"champion": {"source": "baseline:fallback_1h"}}}
    assert verify_champion_loaded(eval_resp, logger) is False
    logger.error.assert_called()
