#!/usr/bin/env python3
"""
Run composable strategy backtest with real BacktestEngine (Phase 2).

Usage:
    python scripts/run_composable_backtest_phase2.py \\
        --config config/strategy/composable/phase2/v0_ml_smoke.yaml \\
        --symbol tBTCUSD \\
        --timeframe 1h \\
        --start 2024-06-01 \\
        --end 2024-08-01
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from core.backtest.composable_engine import ComposableBacktestEngine
from core.strategy.components.ml_confidence import MLConfidenceComponent
from core.strategy.components.regime_filter import RegimeFilterComponent
from core.strategy.components.ev_gate import EVGateComponent
from core.strategy.components.cooldown import CooldownComponent
from core.strategy.components.strategy import ComposableStrategy


def load_composable_config(config_path: Path) -> dict:
    """Load composable strategy config from YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def build_strategy_from_config(config: dict) -> ComposableStrategy:
    """Build ComposableStrategy from config dict."""
    components = []

    for comp_cfg in config.get("components", []):
        comp_type = comp_cfg["type"]
        params = comp_cfg.get("params", {})

        if comp_type == "ml_confidence":
            components.append(MLConfidenceComponent(**params))
        elif comp_type == "regime_filter":
            components.append(RegimeFilterComponent(**params))
        elif comp_type == "ev_gate":
            components.append(EVGateComponent(**params))
        elif comp_type == "cooldown":
            components.append(CooldownComponent(params))
        # Add more component types as we expand
        else:
            raise ValueError(f"Unknown component type: {comp_type}")

    return ComposableStrategy(components=components)


def main():
    parser = argparse.ArgumentParser(description="Run composable backtest (Phase 2)")
    parser.add_argument("--config", required=True, help="Path to composable strategy config")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", default="1h", help="Candle timeframe")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set canonical mode (required for deterministic results)
    os.environ["GENESIS_FAST_WINDOW"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    config = load_composable_config(config_path)
    print(f"Loaded config: {config_path}")
    print(f"Components: {[c['type'] for c in config.get('components', [])]}")

    # Build strategy
    strategy = build_strategy_from_config(config)
    print(f"Strategy built with {len(strategy.components)} component(s)")

    # Create engine
    engine = ComposableBacktestEngine(
        symbol=args.symbol,
        timeframe=args.timeframe,
        strategy=strategy,
        start_date=args.start,
        end_date=args.end,
        fast_window=True,
    )

    # Load data
    print(f"\nLoading data: {args.symbol} {args.timeframe} ({args.start} to {args.end})")
    if not engine.load_data():
        print("ERROR: Failed to load data")
        sys.exit(1)

    print("Data loaded successfully")

    # Run backtest
    print("\nRunning backtest...")
    results = engine.run(verbose=args.verbose)

    # Add composable config identity for traceability (helps avoid overwrite confusion)
    bt_info = results.setdefault("backtest_info", {})
    bt_info.setdefault("composable_config_id", config_path.stem)
    bt_info.setdefault("composable_config_path", str(config_path))
    bt_info.setdefault("composable_components", [c["type"] for c in config.get("components", [])])

    # Check for errors
    if "error" in results:
        print(f"\nERROR: Backtest failed: {results['error']}")
        sys.exit(1)

    # Print summary
    print("\n" + "=" * 70)
    print("BACKTEST RESULTS")
    print("=" * 70)

    summary = results.get("summary", {})
    print(f"Total Trades: {summary.get('total_trades', 0)}")
    print(f"Profit Factor: {summary.get('profit_factor', 0.0):.2f}")
    print(f"Win Rate: {summary.get('win_rate', 0.0):.1f}%")
    print(f"Total Return: {summary.get('total_return', 0.0):.2f}%")
    print(f"Max Drawdown: {summary.get('max_drawdown', 0.0):.2f}%")

    # Print attribution
    print("\n" + "=" * 70)
    print("COMPONENT ATTRIBUTION")
    print("=" * 70)

    attribution = results.get("attribution", {})
    print(f"Total Decisions: {attribution.get('total_decisions', 0)}")
    allow_rate = attribution.get("allow_rate", 0.0) * 100
    print(f"Allowed: {attribution.get('allowed', 0)} ({allow_rate:.1f}%)")
    print(f"Vetoed: {attribution.get('vetoed', 0)}")

    veto_counts = attribution.get("veto_counts", {})
    if veto_counts:
        print("\nVeto Counts by Component:")
        for comp_name, count in veto_counts.items():
            print(f"  {comp_name}: {count}")

    component_confidence = attribution.get("component_confidence", {})
    if component_confidence:
        print("\nComponent Confidence:")
        for comp_name, conf in component_confidence.items():
            avg, min_c, max_c = conf["avg"], conf["min"], conf["max"]
            print(f"  {comp_name}: avg={avg:.3f}, min={min_c:.3f}, max={max_c:.3f}")

    # Save results
    output_dir = repo_root / "results" / "composable_backtest_phase2"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = (
        output_dir
        / f"{args.symbol}_{args.timeframe}_{config_path.stem}_{args.start}_{args.end}.json"
    )
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
