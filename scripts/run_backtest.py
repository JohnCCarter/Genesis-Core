#!/usr/bin/env python3
"""
Run backtest on historical data.

Usage:
    python scripts/run_backtest.py --symbol tBTCUSD --timeframe 15m
    python scripts/run_backtest.py --symbol tETHUSD --timeframe 1h --capital 20000
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.backtest.engine import BacktestEngine
from core.backtest.metrics import calculate_metrics, print_metrics_report
from core.backtest.trade_logger import TradeLogger
from core.config.authority import ConfigAuthority


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run backtest on historical data")
    parser.add_argument(
        "--symbol", type=str, required=True, help="Trading symbol (e.g., tBTCUSD)"
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        required=True,
        help="Candle timeframe (e.g., 15m, 1h)",
    )
    parser.add_argument(
        "--start", type=str, help="Start date (YYYY-MM-DD)", default=None
    )
    parser.add_argument(
        "--end", type=str, help="End date (YYYY-MM-DD)", default=None
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=10000.0,
        help="Initial capital (default: 10000)",
    )
    parser.add_argument(
        "--commission",
        type=float,
        default=0.001,
        help="Commission rate (default: 0.001 = 0.1%%)",
    )
    parser.add_argument(
        "--slippage",
        type=float,
        default=0.0005,
        help="Slippage rate (default: 0.0005 = 0.05%%)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=120,
        help="Warmup bars for indicators (default: 120)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print trade details"
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save results to files"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Genesis-Core Backtest Runner")
    print("=" * 70)

    try:
        # Initialize engine
        engine = BacktestEngine(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=args.start,
            end_date=args.end,
            initial_capital=args.capital,
            commission_rate=args.commission,
            slippage_rate=args.slippage,
            warmup_bars=args.warmup,
        )

        # Load data
        if not engine.load_data():
            return 1

        # Load runtime config
        authority = ConfigAuthority()
        cfg_obj, _, _ = authority.get()
        cfg = cfg_obj.model_dump()

        # Prepare policy
        policy = {"symbol": args.symbol, "timeframe": args.timeframe}

        # Run backtest
        results = engine.run(policy=policy, configs=cfg, verbose=args.verbose)

        if "error" in results:
            print(f"\n[ERROR] Backtest failed: {results['error']}")
            return 1

        # Calculate metrics
        metrics = calculate_metrics(results)

        # Print report
        print_metrics_report(metrics, results.get("backtest_info"))

        # Save results
        if not args.no_save:
            logger = TradeLogger()
            saved_files = logger.save_all(results)
            print(f"\n[OK] Results saved:")
            for key, path in saved_files.items():
                print(f"  {key}: {path}")

        print("\n[SUCCESS] Backtest complete!")
        return 0

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Backtest interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[FAILED] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
