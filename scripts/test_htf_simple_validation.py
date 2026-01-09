#!/usr/bin/env python3
"""Simple HTF Exit Validation for Genesis-Core.

Manual script (not a pytest test).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    # scripts/<this file> -> repo root is parents[1]
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.backtest.engine import BacktestEngine
from core.backtest.metrics import calculate_backtest_metrics
from core.config.authority import ConfigAuthority


def test_htf_vs_baseline() -> bool:
    """Simple test: HTF exits vs baseline fixed exits."""
    print("=== HTF Exit System Validation ===")

    test_config = {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "start_date": "2025-07-01",
        "end_date": "2025-10-13",
        "initial_capital": 10000.0,
        "commission_rate": 0.003,
        "slippage_rate": 0.0005,
        "warmup_bars": 200,
    }

    print(f"Testing {test_config['symbol']} {test_config['timeframe']}")
    print(f"Period: {test_config['start_date']} to {test_config['end_date']}")

    configs = {
        "BASELINE": {
            **test_config,
            "htf_exit_config": {
                "enable_partials": False,
                "enable_trailing": False,
                "enable_structure_breaks": False,
            },
        },
        "HTF_FULL": {
            **test_config,
            "htf_exit_config": {
                "enable_partials": True,
                "enable_trailing": True,
                "enable_structure_breaks": True,
                "partial_1_pct": 0.40,
                "partial_2_pct": 0.30,
                "fib_threshold_atr": 0.3,
                "trail_atr_multiplier": 1.3,
            },
        },
    }

    results: dict[str, dict] = {}

    for config_name, config in configs.items():
        print(f"\n--- Running {config_name} ---")

        try:
            engine = BacktestEngine(
                symbol=config["symbol"],
                timeframe=config["timeframe"],
                start_date=config["start_date"],
                end_date=config["end_date"],
                initial_capital=config["initial_capital"],
                commission_rate=config["commission_rate"],
                slippage_rate=config["slippage_rate"],
                warmup_bars=config["warmup_bars"],
                htf_exit_config=config["htf_exit_config"],
            )

            if not engine.load_data():
                print(f"[ERROR] Failed to load data for {config_name}")
                continue

            authority = ConfigAuthority()
            cfg_obj, _, _ = authority.get()
            strategy_config = cfg_obj.model_dump()

            policy = {"symbol": config["symbol"], "timeframe": config["timeframe"]}
            backtest_results = engine.run(policy=policy, configs=strategy_config, verbose=False)

            trades = backtest_results.get("trades", [])
            if trades:
                metrics = calculate_backtest_metrics(trades, config["initial_capital"])
                results[config_name] = metrics

                print(f"[OK] {config_name} Results:")
                print(f"   Return: {metrics['total_return']:.2f}%")
                print(f"   Trades: {metrics['total_trades']}")
                print(f"   Win Rate: {metrics['win_rate']:.1f}%")
                print(f"   Sharpe: {metrics['sharpe_ratio']:.3f}")
                print(f"   Max DD: {metrics['max_drawdown']:.2f}%")
            else:
                print(f"[WARN] {config_name}: No trades generated")
                results[config_name] = {"total_return": 0.0, "total_trades": 0}

        except Exception as e:
            print(f"[ERROR] {config_name} failed: {e}")
            results[config_name] = {"error": str(e)}

    print("\n=== COMPARISON ===")

    if "BASELINE" not in results or "HTF_FULL" not in results:
        print("[ERROR] Missing results for comparison")
        return False

    baseline = results["BASELINE"]
    htf_full = results["HTF_FULL"]

    if "error" in baseline or "error" in htf_full:
        print("[ERROR] Could not compare due to errors in backtests")
        return False

    improvement = htf_full["total_return"] - baseline["total_return"]
    trade_diff = htf_full["total_trades"] - baseline["total_trades"]

    print(f"Baseline Return: {baseline['total_return']:.2f}%")
    print(f"HTF Full Return: {htf_full['total_return']:.2f}%")

    if baseline["total_return"]:
        rel = improvement / baseline["total_return"] * 100
        print(f"Improvement: {improvement:+.2f}% ({rel:+.1f}%)")
    else:
        print(f"Improvement: {improvement:+.2f}%")

    print(
        f"Trade Count: {baseline['total_trades']} -> {htf_full['total_trades']} ({trade_diff:+d})"
    )

    if improvement > 2.0:
        print("\n[SUCCESS] HTF Exit System shows significant improvement!")
        print("RECOMMENDATION: Deploy HTF Exit System")
        return True
    if improvement > 0:
        print("\n[MARGINAL] HTF Exit System shows modest improvement")
        print("RECOMMENDATION: Consider deployment with further testing")
        return True

    print("\n[FAILURE] HTF Exit System does not improve performance")
    print("RECOMMENDATION: Do not deploy, investigate issues")
    return False


def test_partial_exit_functionality() -> bool:
    """Test that partial exits are actually working."""
    print("\n=== Testing Partial Exit Functionality ===")

    try:
        config = {
            "symbol": "tBTCUSD",
            "timeframe": "1h",
            "start_date": "2025-09-01",
            "end_date": "2025-10-13",
            "initial_capital": 10000.0,
            "htf_exit_config": {
                "enable_partials": True,
                "enable_trailing": False,
                "enable_structure_breaks": False,
                "partial_1_pct": 0.50,
                "fib_threshold_atr": 1.0,
            },
        }

        engine = BacktestEngine(**config)
        if not engine.load_data():
            print("[ERROR] Could not load data for partial exit test")
            return False

        strategy_config = {
            "cfg": {
                "thresholds": {"entry_conf_overall": 0.60},
                "exit": {"enabled": True},
                "risk": {"risk_map": [[0.55, 0.02]]},
                "ev": {"R_default": 1.8},
            }
        }

        results = engine.run(configs=strategy_config, verbose=False)
        trades = results.get("trades", [])

        partial_trades = [t for t in trades if t.get("is_partial", False)]
        full_trades = [t for t in trades if not t.get("is_partial", False)]

        print(f"Total trades: {len(trades)}")
        print(f"Partial exits: {len(partial_trades)}")
        print(f"Full exits: {len(full_trades)}")

        if partial_trades:
            print("[SUCCESS] Partial exits are working!")
            for i, trade in enumerate(partial_trades[:3]):
                print(
                    f"   Partial {i+1}: {trade.get('exit_reason', 'N/A')} - "
                    f"Size: {trade.get('size', 0):.3f} - "
                    f"PnL: ${trade.get('pnl', 0):.2f}"
                )
            return True

        print("[WARN] No partial exits detected - may need tuning")
        return False

    except Exception as e:
        print(f"[ERROR] Partial exit test failed: {e}")
        return False


def main() -> bool:
    print("HTF Exit System Simple Validation")
    print("=" * 40)

    comparison_success = test_htf_vs_baseline()
    partial_success = test_partial_exit_functionality()

    print("\n" + "=" * 40)
    print("VALIDATION SUMMARY")
    print("=" * 40)

    if comparison_success and partial_success:
        print("[SUCCESS] HTF Exit System is ready for deployment!")
        print("\nRECOMMENDATION: Deploy HTF Exit System to paper trading")
    elif comparison_success:
        print("[PARTIAL SUCCESS] HTF Exit System shows improvement")
        print("\nRECOMMENDATION: Deploy with monitoring")
    else:
        print("[NEEDS WORK] HTF Exit System requires further development")
        print("\nRECOMMENDATION: Debug and iterate before deployment")

    return comparison_success


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
