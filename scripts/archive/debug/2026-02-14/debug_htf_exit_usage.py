#!/usr/bin/env python3
"""
Debug HTF Exit Usage

Check if HTF Fibonacci context is available and being used during backtest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.config.authority import ConfigAuthority


def debug_htf_context():
    """Debug HTF context availability during backtest."""

    print("=== Debugging HTF Exit Context ===\n")

    # Create baseline engine (HTF disabled)

    # Create HTF-enabled engine
    htf_config = {
        "enable_partials": True,
        "enable_trailing": True,
        "enable_structure_breaks": True,
        "partial_1_pct": 0.40,
        "partial_2_pct": 0.30,
        "fib_threshold_atr": 0.5,  # More lenient (50% ATR threshold instead of 30%)
        "trail_atr_multiplier": 1.3,
    }

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2025-08-01",  # Updated to match fresh data
        end_date="2025-10-13",
        initial_capital=10000.0,
        warmup_bars=200,
        htf_exit_config=htf_config,
    )

    if not engine.load_data():
        print("[ERROR] Could not load data")
        return

    print(f"[OK] Loaded {len(engine.candles_df)} candles")
    print("[OK] HTF Exit Engine configured:")
    print(f"   Partials enabled: {engine.htf_exit_engine.enable_partials}")
    print(f"   Trailing enabled: {engine.htf_exit_engine.enable_trailing}")
    print(f"   Structure breaks enabled: {engine.htf_exit_engine.enable_structure_breaks}")
    print(f"   Fib threshold: {engine.htf_exit_engine.fib_threshold_atr} ATR")
    print(f"   Partial 1%: {engine.htf_exit_engine.partial_1_pct:.0%}")
    print(f"   Partial 2%: {engine.htf_exit_engine.partial_2_pct:.0%}")

    # Load config
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    strategy_config = cfg_obj.model_dump()

    # Prepare policy
    policy = {"symbol": "tBTCUSD", "timeframe": "1h"}

    # Run backtest with verbose
    print("\n[STARTING BACKTEST]\n")
    results = engine.run(policy=policy, configs=strategy_config, verbose=True)

    # Analyze results
    trades = results.get("trades", [])
    partial_trades = [t for t in trades if t.get("is_partial", False)]
    full_trades = [t for t in trades if not t.get("is_partial", False)]

    print("\n[RESULTS]")
    print(f"Total trades: {len(trades)}")
    print(f"Partial exits: {len(partial_trades)}")
    print(f"Full exits: {len(full_trades)}")

    if len(partial_trades) > 0:
        print("\n[SUCCESS] HTF Exit System is working!")
        for i, trade in enumerate(partial_trades[:5], 1):
            print(
                f"   Partial {i}: {trade.get('exit_reason', 'N/A')} - "
                f"Size: {trade.get('size', 0):.3f} - "
                f"PnL: ${trade.get('pnl', 0):.2f}"
            )
    else:
        print("\n[ISSUE] No partial exits detected")
        print("Possible reasons:")
        print("- HTF Fibonacci context not available")
        print("- Price never near Fib levels")
        print("- Threshold too strict")
        print("- Integration bug")


if __name__ == "__main__":
    debug_htf_context()
