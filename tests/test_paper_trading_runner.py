"""
Tests for Paper Trading Runner

Tests candle-close detection and idempotency logic without network calls.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest
from paper_trading_runner import (
    RunnerState,
    _timeframe_to_ms,
    fetch_latest_candle,
    load_state,
    map_policy_symbol_to_test_symbol,
    save_state,
    submit_paper_order,
    validate_live_paper_guardrails,
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
        pipeline_state={"cooldown_remaining": 3, "last_action": "LONG"},
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
    assert loaded.pipeline_state == state.pipeline_state


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


def test_validate_live_paper_guardrails_requires_execution_mode(tmp_path, monkeypatch):
    from paper_trading_runner import RunnerConfig

    monkeypatch.delenv("GENESIS_EXECUTION_MODE", raising=False)

    config = RunnerConfig(
        host="localhost",
        port=8000,
        symbol="tBTCUSD",
        timeframe="1h",
        poll_interval=1,
        dry_run=False,
        live_paper=True,
        log_dir=tmp_path / "logs",
        state_file=tmp_path / "runner_state.json",
    )

    issues = validate_live_paper_guardrails(config)
    assert any("GENESIS_EXECUTION_MODE=paper_live" in issue for issue in issues)


def test_validate_live_paper_guardrails_blocks_forbidden_results_namespace(monkeypatch):
    from paper_trading_runner import RunnerConfig

    monkeypatch.setenv("GENESIS_EXECUTION_MODE", "paper_live")

    config = RunnerConfig(
        host="localhost",
        port=8000,
        symbol="tBTCUSD",
        timeframe="1h",
        poll_interval=1,
        dry_run=False,
        live_paper=True,
        log_dir=Path("results/hparam_search/paper_logs"),
        state_file=Path("results/paper_live/runner_state.json"),
    )

    issues = validate_live_paper_guardrails(config)
    assert any("forbidden root" in issue for issue in issues)


def test_validate_live_paper_guardrails_blocks_non_paperlive_results_namespace(monkeypatch):
    from paper_trading_runner import RunnerConfig

    monkeypatch.setenv("GENESIS_EXECUTION_MODE", "paper_live")

    config = RunnerConfig(
        host="localhost",
        port=8000,
        symbol="tBTCUSD",
        timeframe="1h",
        poll_interval=1,
        dry_run=False,
        live_paper=True,
        log_dir=Path("results/legacy_bucket/logs"),
        state_file=Path("results/legacy_bucket/runner_state.json"),
    )

    issues = validate_live_paper_guardrails(config)
    assert any("results/paper_live" in issue for issue in issues)


def test_validate_live_paper_guardrails_skips_dry_run(monkeypatch):
    from paper_trading_runner import RunnerConfig

    monkeypatch.delenv("GENESIS_EXECUTION_MODE", raising=False)

    config = RunnerConfig(
        host="localhost",
        port=8000,
        symbol="tBTCUSD",
        timeframe="1h",
        poll_interval=1,
        dry_run=True,
        live_paper=False,
        log_dir=Path("results/legacy_bucket/logs"),
        state_file=Path("results/legacy_bucket/runner_state.json"),
    )

    issues = validate_live_paper_guardrails(config)
    assert issues == []


# --- Bug #1 Test: Candle Data Consistency ---


@patch("paper_trading_runner.time.time")
def test_fetch_candle_uses_correct_ohlcv_when_forming(mock_time):
    """
    Bug #1 regression test: Verify that when latest is forming,
    previous candle's ts AND OHLCV are returned (not mixed data).
    """
    candle_ts = 1704067200000  # Latest candle start
    previous_ts = candle_ts - 3600000  # 1h before
    current_time = (candle_ts + 30 * 60 * 1000) / 1000  # 30 min into latest (forming)

    mock_time.return_value = current_time

    mock_response = Mock()
    mock_response.json.return_value = [
        [candle_ts, 50000.0, 50100.0, 50200.0, 49900.0, 100.5],  # Latest (forming)
        [previous_ts, 49000.0, 49500.0, 49800.0, 48900.0, 95.3],  # Previous (closed)
    ]
    mock_response.raise_for_status = Mock()

    mock_client = Mock(spec=httpx.Client)
    mock_client.get.return_value = mock_response
    logger = Mock()

    candle = fetch_latest_candle("tBTCUSD", "1h", mock_client, logger)

    # Should return previous candle (timestamp AND OHLCV must match)
    assert candle is not None
    assert candle["ts"] == previous_ts, "Timestamp should be from previous candle"
    assert candle["open"] == 49000.0, "Open should be from previous candle, NOT latest"
    assert candle["close"] == 49500.0, "Close should be from previous candle, NOT latest"
    assert candle["high"] == 49800.0, "High should be from previous candle"
    assert candle["low"] == 48900.0, "Low should be from previous candle"
    assert candle["volume"] == 95.3, "Volume should be from previous candle"
    assert candle["_source"] == "previous", "Source metadata should indicate 'previous'"

    # Verify audit logging was called
    logger.debug.assert_called()
    debug_call = logger.debug.call_args[0][0]
    assert "source=previous" in debug_call
    assert f"ts={previous_ts}" in debug_call


@patch("paper_trading_runner.time.time")
def test_fetch_candle_uses_correct_ohlcv_when_closed(mock_time):
    """
    Bug #1 regression test: Verify that when latest is closed,
    latest candle's ts AND OHLCV are returned.
    """
    candle_ts = 1704067200000  # Latest candle start
    previous_ts = candle_ts - 3600000  # 1h before
    candle_duration = 60 * 60 * 1000
    current_time = (candle_ts + candle_duration + 60 * 1000) / 1000  # 1 min after close

    mock_time.return_value = current_time

    mock_response = Mock()
    mock_response.json.return_value = [
        [candle_ts, 50000.0, 50100.0, 50200.0, 49900.0, 100.5],  # Latest (closed)
        [previous_ts, 49000.0, 49500.0, 49800.0, 48900.0, 95.3],  # Previous
    ]
    mock_response.raise_for_status = Mock()

    mock_client = Mock(spec=httpx.Client)
    mock_client.get.return_value = mock_response
    logger = Mock()

    candle = fetch_latest_candle("tBTCUSD", "1h", mock_client, logger)

    # Should return latest candle (timestamp AND OHLCV must match)
    assert candle is not None
    assert candle["ts"] == candle_ts, "Timestamp should be from latest candle"
    assert candle["open"] == 50000.0, "Open should be from latest candle"
    assert candle["close"] == 50100.0, "Close should be from latest candle"
    assert candle["high"] == 50200.0, "High should be from latest candle"
    assert candle["low"] == 49900.0, "Low should be from latest candle"
    assert candle["volume"] == 100.5, "Volume should be from latest candle"
    assert candle["_source"] == "latest", "Source metadata should indicate 'latest'"

    # Verify audit logging was called
    logger.debug.assert_called()
    debug_call = logger.debug.call_args[0][0]
    assert "source=latest" in debug_call
    assert f"ts={candle_ts}" in debug_call


# --- Bug #2 Test: Fail-Closed on Order Submission Failure ---


def test_order_submission_failure_causes_fail_closed_exit(tmp_path):
    """
    Bug #2 regression test: Verify that order submission failure in live-paper mode
    causes fail-closed exit (sys.exit(1)) and does NOT update last_processed_candle_ts.
    """
    from paper_trading_runner import RunnerConfig, RunnerState

    # Mock all dependencies
    with (
        patch("paper_trading_runner.httpx.Client") as mock_client_class,
        patch("paper_trading_runner.fetch_latest_candle") as mock_fetch,
        patch("paper_trading_runner.evaluate_strategy") as mock_eval,
        patch("paper_trading_runner.submit_paper_order") as mock_submit,
        patch("paper_trading_runner.save_state") as mock_save,
        patch.dict("os.environ", {"GENESIS_EXECUTION_MODE": "paper_live"}, clear=False),
    ):

        # Setup mocks
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        candle_ts = 1704067200000
        mock_fetch.return_value = {
            "ts": candle_ts,
            "open": 50000.0,
            "close": 50100.0,
            "high": 50200.0,
            "low": 49900.0,
            "volume": 100.5,
            "_source": "latest",
        }

        # Evaluation returns BUY signal
        mock_eval.return_value = {
            "result": {
                "action": "LONG",
                "signal": 1,
                "confidence": {"overall": 0.75},
            },
            "meta": {
                "champion": {"source": "config\\strategy\\champions\\tBTCUSD_1h.json"},
                "decision": {"size": 0.01},
            },
        }

        # Order submission FAILS (returns None)
        mock_submit.return_value = None

        # Setup config and state
        config = RunnerConfig(
            host="localhost",
            port=8000,
            symbol="tBTCUSD",
            timeframe="1h",
            poll_interval=1,
            dry_run=False,
            live_paper=True,  # LIVE-PAPER mode
            log_dir=tmp_path,
            state_file=tmp_path / "state.json",
        )

        state = RunnerState()
        logger = Mock()

        # Import run_loop
        from paper_trading_runner import run_loop

        # Run should exit with code 1 (fail-closed)
        with pytest.raises(SystemExit) as exc_info:
            run_loop(config, logger, state)

        # Verify exit code 1
        assert exc_info.value.code == 1, "Should exit with code 1 on order submission failure"

        # Verify that save_state was called (to persist state before exit)
        assert mock_save.called, "State should be saved before fail-closed exit"

        # Verify that last_processed_candle_ts was NOT updated
        # Check the state object passed to save_state
        save_calls = mock_save.call_args_list
        saved_state = save_calls[-1][0][0]  # First arg of last call
        assert (
            saved_state.last_processed_candle_ts != candle_ts
        ), "Candle should NOT be marked as processed on order submission failure"

        # Verify FATAL error was logged
        fatal_logged = any("FATAL" in str(call) for call in logger.error.call_args_list)
        assert fatal_logged, "FATAL error should be logged on order submission failure"


def test_order_submission_success_updates_candle_ts(tmp_path):
    """
    Bug #2 regression test: Verify that successful order submission
    updates last_processed_candle_ts correctly.
    """
    from paper_trading_runner import RunnerConfig, RunnerState

    with (
        patch("paper_trading_runner.httpx.Client") as mock_client_class,
        patch("paper_trading_runner.fetch_latest_candle") as mock_fetch,
        patch("paper_trading_runner.evaluate_strategy") as mock_eval,
        patch("paper_trading_runner.submit_paper_order") as mock_submit,
        patch("paper_trading_runner.save_state") as mock_save,
        patch("paper_trading_runner.time.sleep"),
        patch.dict("os.environ", {"GENESIS_EXECUTION_MODE": "paper_live"}, clear=False),
    ):  # Mock sleep to speed up test

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        candle_ts = 1704067200000

        # First fetch is used for startup verification, second for first loop iteration,
        # then None/StopIteration to exit.
        mock_fetch.side_effect = [
            {
                "ts": candle_ts,
                "open": 50000.0,
                "close": 50100.0,
                "high": 50200.0,
                "low": 49900.0,
                "volume": 100.5,
                "_source": "latest",
            },
            {
                "ts": candle_ts,
                "open": 50000.0,
                "close": 50100.0,
                "high": 50200.0,
                "low": 49900.0,
                "volume": 100.5,
                "_source": "latest",
            },
            None,  # Triggers exit
        ]

        mock_eval.return_value = {
            "result": {
                "action": "LONG",
                "signal": 1,
                "confidence": {"overall": 0.75},
            },
            "meta": {
                "champion": {"source": "config\\strategy\\champions\\tBTCUSD_1h.json"},
                "decision": {"size": 0.01},
            },
        }

        # Order submission SUCCEEDS
        mock_submit.return_value = {"ok": True, "order_id": "12345", "status": "accepted"}

        config = RunnerConfig(
            host="localhost",
            port=8000,
            symbol="tBTCUSD",
            timeframe="1h",
            poll_interval=1,
            dry_run=False,
            live_paper=True,
            log_dir=tmp_path,
            state_file=tmp_path / "state.json",
        )

        state = RunnerState()
        logger = Mock()

        from paper_trading_runner import run_loop

        # Run loop (will exit on second fetch returning None)
        run_loop(config, logger, state)

        # Verify that last_processed_candle_ts WAS updated
        save_calls = mock_save.call_args_list
        # Find the save call after order submission (not just heartbeat saves)
        saved_states = [call[0][0] for call in save_calls]
        final_state = saved_states[-1]

        assert (
            final_state.last_processed_candle_ts == candle_ts
        ), "Candle should be marked as processed after successful order submission"
        assert final_state.total_orders_submitted == 1, "Order counter should be incremented"


def test_map_policy_symbol_to_test_symbol():
    assert map_policy_symbol_to_test_symbol("tBTCUSD") == "tTESTBTC:TESTUSD"
    assert map_policy_symbol_to_test_symbol("tBTCUSDT") == "tTESTBTC:TESTUSDT"
    assert map_policy_symbol_to_test_symbol("tDOGE:USD") == "tTESTDOGE:TESTUSD"
    assert map_policy_symbol_to_test_symbol("tTESTETH:TESTUSD") == "tTESTETH:TESTUSD"


def test_submit_paper_order_uses_test_symbol_and_size_from_meta(tmp_path):
    from paper_trading_runner import RunnerConfig

    config = RunnerConfig(
        host="localhost",
        port=8000,
        symbol="tBTCUSD",
        timeframe="1h",
        poll_interval=1,
        dry_run=False,
        live_paper=True,
        log_dir=tmp_path,
        state_file=tmp_path / "state.json",
    )

    eval_resp = {
        "result": {"confidence": {"overall": 0.75}},
        "meta": {"decision": {"size": 0.005}},
    }

    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.json.return_value = {"ok": True, "response": {"status": "accepted"}}

    client = Mock(spec=httpx.Client)
    client.post.return_value = mock_resp

    logger = Mock()
    out = submit_paper_order(config, "LONG", eval_resp, client, logger)

    assert out is not None
    client.post.assert_called_once()
    _, kwargs = client.post.call_args
    assert kwargs["json"]["symbol"] == "tTESTBTC:TESTUSD"
    assert kwargs["json"]["side"] == "LONG"
    assert kwargs["json"]["size"] == 0.005


def test_submit_paper_order_ok_false_returns_none(tmp_path):
    from paper_trading_runner import RunnerConfig

    config = RunnerConfig(
        host="localhost",
        port=8000,
        symbol="tBTCUSD",
        timeframe="1h",
        poll_interval=1,
        dry_run=False,
        live_paper=True,
        log_dir=tmp_path,
        state_file=tmp_path / "state.json",
    )

    eval_resp = {"meta": {"decision": {"size": 0.005}}}

    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.json.return_value = {"ok": False, "error": "invalid_action_or_size"}

    client = Mock(spec=httpx.Client)
    client.post.return_value = mock_resp
    logger = Mock()

    out = submit_paper_order(config, "LONG", eval_resp, client, logger)
    assert out is None
    logger.error.assert_called()
