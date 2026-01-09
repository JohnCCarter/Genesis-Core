#!/usr/bin/env python3
"""
REAL BACKTEST: Fibonacci Fraktal Exits Comparison
Tests both STATIC FROZEN and DYNAMIC strategies with actual backtest engine.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine


def run_real_backtest_comparison():
    """Run real backtest comparison between static and dynamic exit strategies."""

    print("=" * 80)
    print("REAL BACKTEST: FIBONACCI FRAKTAL EXITS COMPARISON")
    print("Testing STATIC FROZEN vs DYNAMIC strategies")
    print("=" * 80)

    results = {
        "test_timestamp": datetime.now().isoformat(),
        "comparison_results": {},
        "performance_metrics": {},
    }

    # Test configuration
    config = {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "start_date": "2025-07-20",
        "end_date": "2025-10-08",
        "initial_capital": 10000.0,
        "warmup_bars": 120,
    }

    # Common strategy config
    base_configs = {
        "thresholds": {
            "entry_conf_overall": 0.35,  # Much lower threshold for signals
            "regime_proba": {"ranging": 0.5, "bull": 0.5, "bear": 0.5, "balanced": 0.5},
        },
        "risk": {
            "risk_map": [
                [0.5, 0.1],  # 0.5 confidence -> 0.1 size
                [0.6, 0.2],  # 0.6 confidence -> 0.2 size
                [0.7, 0.3],  # 0.7 confidence -> 0.3 size
            ]
        },
        "ev": {"R_default": 1.5},  # Reward ratio - CRITICAL for positive EV!
    }

    # Test STATIC FROZEN strategy
    print("\n[TEST 1] STATIC FROZEN EXITS")
    print("-" * 50)

    static_config = base_configs.copy()
    static_config.update(
        {
            "exit_strategy": {
                "enabled": True,
                "swing_update_strategy": "fixed",  # STATIC FROZEN
                "swing_update_params": {"strategy": "fixed", "log_updates": True},
                "enable_partials": True,
                "enable_trailing": True,
                "enable_structure_breaks": True,
            }
        }
    )

    static_results = run_single_backtest("STATIC_FROZEN", config, static_config)
    results["comparison_results"]["static_frozen"] = static_results

    # Test DYNAMIC strategy
    print("\n[TEST 2] DYNAMIC EXITS")
    print("-" * 50)

    dynamic_config = base_configs.copy()
    dynamic_config.update(
        {
            "exit_strategy": {
                "enabled": True,
                "swing_update_strategy": "dynamic",  # DYNAMIC
                "swing_update_params": {
                    "strategy": "dynamic",
                    "min_improvement_pct": 0.02,
                    "max_age_bars": 30,
                    "allow_worse_swing": True,
                    "log_updates": True,
                },
                "enable_partials": True,
                "enable_trailing": True,
                "enable_structure_breaks": True,
            }
        }
    )

    dynamic_results = run_single_backtest("DYNAMIC", config, dynamic_config)
    results["comparison_results"]["dynamic"] = dynamic_results

    # Test HYBRID strategy
    print("\n[TEST 3] HYBRID EXITS")
    print("-" * 50)

    hybrid_config = base_configs.copy()
    hybrid_config.update(
        {
            "exit_strategy": {
                "enabled": True,
                "swing_update_strategy": "hybrid",  # HYBRID
                "swing_update_params": {
                    "strategy": "hybrid",
                    "min_improvement_pct": 0.02,
                    "max_age_bars": 30,
                    "allow_worse_swing": False,
                    "log_updates": True,
                },
                "enable_partials": True,
                "enable_trailing": True,
                "enable_structure_breaks": True,
            }
        }
    )

    hybrid_results = run_single_backtest("HYBRID", config, hybrid_config)
    results["comparison_results"]["hybrid"] = hybrid_results

    # Analyze and compare results
    print("\n" + "=" * 80)
    print("BACKTEST COMPARISON ANALYSIS")
    print("=" * 80)

    analysis = analyze_backtest_results(results["comparison_results"])
    results["performance_metrics"] = analysis

    # Print summary
    print_comparison_summary(analysis)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/fibonacci_exits_real_backtest_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n[SAVE] Complete results saved to: {filename}")
    print("\n[COMPLETE] Real backtest comparison completed!")

    return results


def run_single_backtest(strategy_name: str, config: dict, strategy_configs: dict) -> dict:
    """Run a single backtest with given configuration."""

    print(f"Running {strategy_name} backtest...")

    try:
        # Initialize engine
        engine = BacktestEngine(
            symbol=config["symbol"],
            timeframe=config["timeframe"],
            start_date=config["start_date"],
            end_date=config["end_date"],
            initial_capital=config["initial_capital"],
            warmup_bars=config["warmup_bars"],
        )

        # Load data
        engine.load_data()

        # Run backtest
        backtest_results = engine.run(configs=strategy_configs)

        # Extract key metrics
        results = {
            "strategy": strategy_name,
            "total_trades": backtest_results.get("total_trades", 0),
            "total_return_pct": backtest_results.get("total_return_pct", 0.0),
            "win_rate": backtest_results.get("win_rate", 0.0),
            "profit_factor": backtest_results.get("profit_factor", 0.0),
            "max_drawdown_pct": backtest_results.get("max_drawdown_pct", 0.0),
            "sharpe_ratio": backtest_results.get("sharpe_ratio", 0.0),
            "partial_exits": backtest_results.get("partial_exits", 0),
            "exit_rate": 0.0,
            "swing_updates": 0,
            "raw_results": backtest_results,
        }

        # Calculate exit rate
        if results["total_trades"] > 0:
            results["exit_rate"] = results["partial_exits"] / results["total_trades"] * 100

        # Extract swing update info if available
        if "swing_updates" in backtest_results:
            results["swing_updates"] = backtest_results["swing_updates"]

        print(
            f"[{strategy_name}] Trades: {results['total_trades']}, "
            f"Return: {results['total_return_pct']:.2f}%, "
            f"Win Rate: {results['win_rate']:.1f}%, "
            f"Partial Exits: {results['partial_exits']}"
        )

        return results

    except Exception as e:
        print(f"[ERROR] {strategy_name} backtest failed: {e}")
        return {
            "strategy": strategy_name,
            "error": str(e),
            "total_trades": 0,
            "total_return_pct": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "partial_exits": 0,
            "exit_rate": 0.0,
            "swing_updates": 0,
        }


def analyze_backtest_results(comparison_results: dict) -> dict:
    """Analyze and compare backtest results."""

    analysis = {
        "strategies": list(comparison_results.keys()),
        "performance_ranking": {},
        "exit_analysis": {},
        "risk_analysis": {},
        "recommendations": [],
    }

    # Performance ranking
    strategies_by_return = sorted(
        comparison_results.items(), key=lambda x: x[1].get("total_return_pct", 0), reverse=True
    )

    analysis["performance_ranking"] = {
        "by_return": [
            {"strategy": k, "return": v.get("total_return_pct", 0)} for k, v in strategies_by_return
        ],
        "by_win_rate": sorted(
            comparison_results.items(), key=lambda x: x[1].get("win_rate", 0), reverse=True
        ),
        "by_sharpe": sorted(
            comparison_results.items(), key=lambda x: x[1].get("sharpe_ratio", 0), reverse=True
        ),
    }

    # Exit analysis
    analysis["exit_analysis"] = {
        strategy: {
            "total_trades": results.get("total_trades", 0),
            "partial_exits": results.get("partial_exits", 0),
            "exit_rate": results.get("exit_rate", 0),
            "swing_updates": results.get("swing_updates", 0),
        }
        for strategy, results in comparison_results.items()
    }

    # Risk analysis
    analysis["risk_analysis"] = {
        strategy: {
            "max_drawdown": results.get("max_drawdown_pct", 0),
            "profit_factor": results.get("profit_factor", 0),
            "sharpe_ratio": results.get("sharpe_ratio", 0),
        }
        for strategy, results in comparison_results.items()
    }

    # Generate recommendations
    best_return = max(comparison_results.values(), key=lambda x: x.get("total_return_pct", 0))
    best_return_strategy = [k for k, v in comparison_results.items() if v == best_return][0]

    analysis["recommendations"] = [
        f"Best return: {best_return_strategy} ({best_return.get('total_return_pct', 0):.2f}%)",
        f"Total trades generated: {sum(r.get('total_trades', 0) for r in comparison_results.values())}",
        f"Exit strategies tested: {len(comparison_results)}",
    ]

    return analysis


def print_comparison_summary(analysis: dict):
    """Print a summary of the comparison results."""

    print("\nPERFORMANCE RANKING (by Return %):")
    for i, entry in enumerate(analysis["performance_ranking"]["by_return"], 1):
        print(f"{i}. {entry['strategy']}: {entry['return']:.2f}%")

    print("\nEXIT ANALYSIS:")
    for strategy, exit_data in analysis["exit_analysis"].items():
        print(f"{strategy}:")
        print(f"  Trades: {exit_data['total_trades']}")
        print(f"  Partial Exits: {exit_data['partial_exits']}")
        print(f"  Exit Rate: {exit_data['exit_rate']:.1f}%")
        print(f"  Swing Updates: {exit_data['swing_updates']}")

    print("\nRISK METRICS:")
    for strategy, risk_data in analysis["risk_analysis"].items():
        print(f"{strategy}:")
        print(f"  Max Drawdown: {risk_data['max_drawdown']:.2f}%")
        print(f"  Profit Factor: {risk_data['profit_factor']:.2f}")
        print(f"  Sharpe Ratio: {risk_data['sharpe_ratio']:.2f}")

    print("\nRECOMMENDATIONS:")
    for rec in analysis["recommendations"]:
        print(f"• {rec}")


if __name__ == "__main__":
    run_real_backtest_comparison()
