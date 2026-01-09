#!/usr/bin/env python3
"""
Test 1h timeframe med Trend-Favoring regime proba.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.timeframe_configs import get_timeframe_backtest_config, get_timeframe_config
from core.backtest.engine import BacktestEngine
from core.backtest.metrics import calculate_metrics


def test_1h_trend_favoring():
    """Test 1h timeframe med Trend-Favoring regime proba."""

    print("=" * 60)
    print("TESTING 1H - CONSERVATIVE REGIME PROBA")
    print("=" * 60)

    # Get configs
    backtest_config = get_timeframe_backtest_config("1h")
    strategy_config = get_timeframe_config("1h")

    print(f"Period: {backtest_config['start_date']} to {backtest_config['end_date']}")
    print(f"Entry Conf: {strategy_config['thresholds']['entry_conf_overall']}")
    print(f"Regime Proba: {strategy_config['thresholds']['regime_proba']}")
    print(f"Risk Map: {strategy_config['risk']['risk_map'][0]}")
    print(f"Partial 1: {strategy_config['htf_exit_config']['partial_1_pct']}")

    # Create backtest engine
    engine = BacktestEngine(**backtest_config)

    if not engine.load_data():
        print("[ERROR] Failed to load data for 1h")
        return None

    print(f"[OK] Loaded {len(engine.candles_df)} candles")

    # Run backtest
    try:
        results = engine.run(configs=strategy_config)

        if results and results.get("trades"):
            # Calculate metrics
            metrics = calculate_metrics(results["trades"], backtest_config["initial_capital"])

            print("\n=== 1H CONSERVATIVE RESULTS ===")
            print(f"Total Return: {metrics.get('total_return_pct', 0):.2f}%")
            print(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
            print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
            print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
            print(f"Total Trades: {metrics.get('num_trades', 0)}")
            print(f"Avg Trade Duration: {metrics.get('avg_trade_duration_hours', 0):.1f} hours")

            return {
                "return": metrics.get("total_return_pct", 0),
                "win_rate": metrics.get("win_rate", 0),
                "profit_factor": metrics.get("profit_factor", 0),
                "sharpe": metrics.get("sharpe_ratio", 0),
                "drawdown": metrics.get("max_drawdown_pct", 0),
                "trades": metrics.get("num_trades", 0),
                "duration": metrics.get("avg_trade_duration_hours", 0),
            }
        else:
            print("[WARN] No trades generated for 1h")
            return {
                "return": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "sharpe": 0.0,
                "drawdown": 0.0,
                "trades": 0,
                "duration": 0.0,
            }

    except Exception as e:
        print(f"[ERROR] Backtest failed for 1h: {e}")
        return None


if __name__ == "__main__":
    result = test_1h_trend_favoring()

    if result:
        print("\n=== COMPARISON ===")
        print("Previous (All 0.6): +3.36% return, 30.3% win rate, 33 trades")
        print(
            f"Current (Conservative): {result['return']:.2f}% return, {result['win_rate']:.1f}% win rate, {result['trades']} trades"
        )

        if result["return"] > 3.36:
            print("IMPROVEMENT: Higher return!")
        elif result["return"] < 3.36:
            print("DECLINE: Lower return")
        else:
            print("SAME: Similar return")
