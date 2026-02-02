#!/usr/bin/env python3
"""
Run composable strategy backtest with HTF/LTF Fibonacci gates DISABLED.

Usage:
    python scripts/run_composable_backtest_no_fib.py \\
        --config config/strategy/composable/phase2/v0_ml_smoke.yaml \\
        --symbol tBTCUSD \\
        --timeframe 1h \\
        --start 2024-01-01 \\
        --end 2024-03-31
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
        else:
            raise ValueError(f"Unknown component type: {comp_type}")

    return ComposableStrategy(components=components)


def main():
    parser = argparse.ArgumentParser(description="Run composable backtest WITHOUT Fibonacci gates")
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

    # CRITICAL: Override configs to DISABLE HTF/LTF Fibonacci gates
    override_configs = {
        "htf_fibonacci": {
            "enabled": False,
            "missing_policy": "allow",  # Allow entries when HTF data unavailable
        },
        "ltf_fibonacci": {
            "enabled": False,
            "missing_policy": "allow",  # Allow entries when LTF data unavailable
        },
    }

    print("\nWARNING: HTF/LTF Fibonacci gates DISABLED for validation")
    print(f"Override configs: {override_configs}")

    # Run backtest WITH config overrides
    print("\nRunning backtest...")
    results = engine.run(configs=override_configs, verbose=args.verbose)

    # Add composable config identity + gate override info
    bt_info = results.setdefault("backtest_info", {})
    bt_info.setdefault("composable_config_id", config_path.stem)
    bt_info.setdefault("composable_config_path", str(config_path))
    bt_info.setdefault("composable_components", [c["type"] for c in config.get("components", [])])
    bt_info["fib_gates_disabled"] = True
    bt_info["override_configs"] = override_configs

    # Check for errors
    if "error" in results:
        print(f"\nERROR: Backtest failed: {results['error']}")
        sys.exit(1)

    # Print summary
    print("\n" + "=" * 70)
    print("BACKTEST RESULTS (NO FIB GATES)")
    print("=" * 70)

    summary = results.get("summary", {})
    print(f"Total Trades: {summary.get('num_trades', 0)}")
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
    print(
        f"Allowed: {attribution.get('allowed', 0)} ({attribution.get('allow_rate', 0.0) * 100:.1f}%)"
    )
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
            print(
                f"  {comp_name}: avg={conf['avg']:.3f}, min={conf['min']:.3f}, max={conf['max']:.3f}"
            )

    # Save results with unique filename (include config name to avoid overwrites)
    output_dir = repo_root / "results" / "composable_no_fib"
    output_dir.mkdir(parents=True, exist_ok=True)

    config_id = config_path.stem
    output_file = output_dir / f"{config_id}_{args.symbol}_{args.timeframe}_{args.start}_{args.end}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
