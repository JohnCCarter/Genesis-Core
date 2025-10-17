#!/usr/bin/env python3
"""
Test ytterligare optimerade timeframe-specific configurations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.timeframe_configs import get_timeframe_backtest_config, get_timeframe_config
from core.backtest.engine import BacktestEngine
from core.backtest.metrics import calculate_metrics


def test_timeframe_optimized_v2(timeframe):
    """Test en specifik timeframe med ytterligare optimerad config."""

    print(f"\n{'='*60}")
    print(f"TESTING {timeframe.upper()} - OPTIMIZED V2 CONFIG")
    print(f"{'='*60}")

    # Get optimized configs
    backtest_config = get_timeframe_backtest_config(timeframe)
    strategy_config = get_timeframe_config(timeframe)

    print(f"Period: {backtest_config['start_date']} to {backtest_config['end_date']}")
    print(f"Entry Conf: {strategy_config['thresholds']['entry_conf_overall']}")
    print(f"Max Hold: {strategy_config['exit']['max_hold_bars']}")
    print(f"Risk Map: {strategy_config['risk']['risk_map'][0]}")
    print(f"Partial 1: {strategy_config['htf_exit_config']['partial_1_pct']}")
    print(f"Cooldown: {strategy_config['gates']['cooldown_bars']}")

    # Create backtest engine
    engine = BacktestEngine(**backtest_config)

    if not engine.load_data():
        print(f"[ERROR] Failed to load data for {timeframe}")
        return None

    print(f"[OK] Loaded {len(engine.candles_df)} candles")

    # Run backtest
    try:
        results = engine.run(configs=strategy_config)

        if results and results.get("trades"):
            # Calculate metrics
            metrics = calculate_metrics(results["trades"], backtest_config["initial_capital"])

            print(f"\n=== {timeframe.upper()} OPTIMIZED V2 RESULTS ===")
            print(f"Total Return: {metrics.get('total_return_pct', 0):.2f}%")
            print(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
            print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
            print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
            print(f"Total Trades: {metrics.get('num_trades', 0)}")
            print(f"Avg Trade Duration: {metrics.get('avg_trade_duration_hours', 0):.1f} hours")

            return {
                "timeframe": timeframe,
                "return": metrics.get("total_return_pct", 0),
                "win_rate": metrics.get("win_rate", 0),
                "profit_factor": metrics.get("profit_factor", 0),
                "sharpe": metrics.get("sharpe_ratio", 0),
                "drawdown": metrics.get("max_drawdown_pct", 0),
                "trades": metrics.get("num_trades", 0),
                "duration": metrics.get("avg_trade_duration_hours", 0),
            }
        else:
            print(f"[WARN] No trades generated for {timeframe}")
            return {
                "timeframe": timeframe,
                "return": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "sharpe": 0.0,
                "drawdown": 0.0,
                "trades": 0,
                "duration": 0.0,
            }

    except Exception as e:
        print(f"[ERROR] Backtest failed for {timeframe}: {e}")
        return None


def test_optimized_configs_v2():
    """Test alla timeframes med ytterligare optimerade configs."""

    print("=" * 80)
    print("TIMEFRAME-SPECIFIC OPTIMIZED CONFIGS V2 TEST")
    print("=" * 80)

    timeframes = ["1D", "1h"]  # Fokusera på de som behöver optimering
    results = []

    # Test varje timeframe
    for timeframe in timeframes:
        result = test_timeframe_optimized_v2(timeframe)
        if result:
            results.append(result)

    # Sammanfattning
    print(f"\n{'='*80}")
    print("OPTIMIZED CONFIGS V2 RESULTS SUMMARY")
    print(f"{'='*80}")

    if results:
        # Sortera efter return
        results.sort(key=lambda x: x["return"], reverse=True)

        print(
            f"{'Timeframe':<10} {'Return':<10} {'Win Rate':<10} {'Trades':<8} {'PF':<8} {'Sharpe':<8} {'DD':<8}"
        )
        print("-" * 80)

        for result in results:
            print(
                f"{result['timeframe']:<10} "
                f"{result['return']:>8.2f}% "
                f"{result['win_rate']:>8.1f}% "
                f"{result['trades']:>6} "
                f"{result['profit_factor']:>6.2f} "
                f"{result['sharpe']:>6.2f} "
                f"{result['drawdown']:>6.2f}%"
            )

        # Bästa timeframe
        best = results[0]
        print(f"\nBEST OPTIMIZED V2 TIMEFRAME: {best['timeframe']}")
        print(f"   Return: {best['return']:.2f}%")
        print(f"   Win Rate: {best['win_rate']:.1f}%")
        print(f"   Trades: {best['trades']}")

        # Analys
        print("\nANALYSIS:")
        positive_returns = [r for r in results if r["return"] > 0]
        print(f"   Positive Returns: {len(positive_returns)}/{len(results)} timeframes")

        if len(positive_returns) > 0:
            avg_positive = sum(r["return"] for r in positive_returns) / len(positive_returns)
            print(f"   Average Positive Return: {avg_positive:.2f}%")

        high_winrate = [r for r in results if r["win_rate"] > 50]
        print(f"   High Win Rate (>50%): {len(high_winrate)}/{len(results)} timeframes")

        # Jämför med tidigare resultat
        print("\nCOMPARISON WITH PREVIOUS RESULTS:")
        print(
            f"   1D: Previous 0.00% vs Optimized V2 {next((r['return'] for r in results if r['timeframe'] == '1D'), 'N/A')}%"
        )
        print(
            f"   1h: Previous +0.68% vs Optimized V2 {next((r['return'] for r in results if r['timeframe'] == '1h'), 'N/A')}%"
        )

    else:
        print("No results to display")


if __name__ == "__main__":
    test_optimized_configs_v2()
