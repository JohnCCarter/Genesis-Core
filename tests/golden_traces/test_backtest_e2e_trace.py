"""
GOLDEN TRACE TEST 3: End-to-End Backtest Determinism

Verifies that given identical parameters and market data,
a complete backtest produces identical trade outcomes and metrics.

Catches drift in:
- Entire execution pipeline
- Fill simulation (slippage, commission)
- PnL calculation
- Metrics calculation
- Any semantic changes to strategy logic
"""

import json
from pathlib import Path

import pytest

from core.backtest.metrics import calculate_metrics
from core.pipeline import GenesisPipeline
from core.utils.optuna_helpers import set_global_seeds


def _assert_close(actual, expected, rtol=1e-10, name="value"):
    """Assert two floats are close within relative tolerance."""
    if expected == 0:
        # Absolute tolerance for zero values
        if abs(actual - expected) > rtol:
            raise AssertionError(
                f"{name}: expected {expected}, got {actual} (diff: {abs(actual - expected)})"
            )
    else:
        if abs(actual - expected) > rtol * abs(expected):
            raise AssertionError(
                f"{name}: expected {expected}, got {actual} "
                f"(diff: {abs(actual - expected)}, rtol: {rtol})"
            )


@pytest.fixture
def golden_dir():
    """Return path to golden snapshots directory."""
    return Path(__file__).parent / "snapshots"


@pytest.fixture
def champion_params(golden_dir):
    """Load golden champion parameters."""
    params_path = golden_dir / "golden_champion_params.json"
    if not params_path.exists():
        pytest.skip(f"Golden params not found: {params_path}")
    with open(params_path) as f:
        return json.load(f)


@pytest.fixture
def golden_backtest(golden_dir):
    """Load golden backtest results."""
    backtest_path = golden_dir / "golden_backtest_v1.json"
    if not backtest_path.exists():
        pytest.skip(f"Golden backtest not found: {backtest_path}")
    with open(backtest_path) as f:
        return json.load(f)


def test_backtest_e2e_determinism(champion_params, golden_backtest):
    """
    GOLDEN TRACE 3: Full Backtest (Param → PnL)

    Asserts that the entire backtest pipeline is deterministic.
    This is the ultimate integration test - ANY change to strategy logic will fail this.
    """
    # Fixed seed for determinism
    set_global_seeds(42)

    # Create pipeline and engine
    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)

    engine = pipeline.create_engine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2024-06-01",
        end_date="2024-08-01",
        capital=10000.0,
        commission=0.002,
        slippage=0.0005,
        warmup_bars=150,
        fast_window=True,
    )

    # Load data (should use frozen file)
    engine.load_data()

    # Run backtest
    results = engine.run(policy="backtest", configs=champion_params, verbose=False)

    # Assert trade count matches
    num_trades = len(results["trades"])
    num_golden_trades = len(golden_backtest["trades"])
    assert (
        num_trades == num_golden_trades
    ), f"Trade count mismatch: {num_trades} != {num_golden_trades}"

    # Assert trade-level determinism (strict)
    for i, (trade, golden_trade) in enumerate(zip(results["trades"], golden_backtest["trades"])):
        assert (
            trade["side"] == golden_trade["side"]
        ), f"Trade {i} side mismatch: {trade['side']} != {golden_trade['side']}"

        _assert_close(
            trade["entry_price"], golden_trade["entry_price"], rtol=1e-8, name=f"trade_{i}_entry_price"
        )
        _assert_close(
            trade["exit_price"], golden_trade["exit_price"], rtol=1e-8, name=f"trade_{i}_exit_price"
        )
        _assert_close(trade["pnl"], golden_trade["pnl"], rtol=1e-8, name=f"trade_{i}_pnl")

        assert (
            trade["exit_reason"] == golden_trade["exit_reason"]
        ), f"Trade {i} exit_reason mismatch: {trade['exit_reason']} != {golden_trade['exit_reason']}"

    # Calculate metrics
    metrics = calculate_metrics(results)
    golden_metrics = golden_backtest["metrics"]

    # Assert metrics determinism (tighter tolerances for aggregates)
    assert (
        metrics["total_trades"] == golden_metrics["total_trades"]
    ), f"total_trades mismatch: {metrics['total_trades']} != {golden_metrics['total_trades']}"

    _assert_close(
        metrics["total_return"], golden_metrics["total_return"], rtol=1e-10, name="total_return"
    )
    _assert_close(
        metrics["profit_factor"], golden_metrics["profit_factor"], rtol=1e-10, name="profit_factor"
    )
    _assert_close(
        metrics["max_drawdown"], golden_metrics["max_drawdown"], rtol=1e-10, name="max_drawdown"
    )
    _assert_close(metrics["sharpe_ratio"], golden_metrics["sharpe_ratio"], rtol=1e-10, name="sharpe_ratio")

    # Assert final equity determinism (ultimate sanity check)
    final_equity = results["summary"]["final_capital"]
    golden_final_equity = golden_backtest["summary"]["final_capital"]
    _assert_close(final_equity, golden_final_equity, rtol=1e-12, name="final_equity")


def test_backtest_snapshot_exists(golden_dir):
    """Sanity check: ensure golden backtest snapshot exists."""
    backtest_path = golden_dir / "golden_backtest_v1.json"
    if not backtest_path.exists():
        pytest.skip(
            f"Golden backtest snapshot not found. Run scripts/rebaseline_golden_traces.py first.\n"
            f"Expected: {backtest_path}"
        )
