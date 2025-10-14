#!/usr/bin/env python3
"""
Fees-aware backtest with realistic transaction costs.

Validates if model has profitable edge after accounting for:
- Trading fees (0.1% maker/taker)
- Slippage (0.1% average)
- Round-trip cost = 0.2% total

Usage:
    python scripts/backtest_with_fees.py --model results/models/tBTCUSD_1h_v3.json \\
        --symbol tBTCUSD --timeframe 1h --fees 0.001 --slippage 0.001
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils.data_loader import load_features
from src.core.utils import get_candles_path


def load_model_and_data(model_path: str, symbol: str, timeframe: str):
    """Load trained model and feature data."""
    print(f"[LOAD] Loading model: {model_path}")
    with open(model_path) as f:
        model_data = json.load(f)

    print(f"[LOAD] Loading features for {symbol} {timeframe}")
    features_df = load_features(symbol, timeframe)

    return model_data, features_df


def simulate_predictions(features_df: pd.DataFrame, model_data: dict) -> np.ndarray:
    """
    Simulate model predictions.
    For now, use simple heuristic based on feature values.
    TODO: Load actual sklearn model and predict.
    """
    # Get feature names
    feature_names = model_data.get("feature_names", [])

    if not feature_names:
        raise ValueError("Model missing feature_names!")

    # Simple heuristic: predict based on first feature
    # In reality, this should load the actual model and predict
    # For now, we'll use a placeholder
    print("[WARNING] Using placeholder predictions! Implement actual model loading.")

    # Placeholder: return random probabilities
    n_samples = len(features_df)
    predictions = np.random.random(n_samples)

    return predictions


def calculate_forward_returns(close_prices: pd.Series, horizon: int = 10) -> np.ndarray:
    """Calculate forward returns for given horizon."""
    returns = close_prices.pct_change(horizon).shift(-horizon)
    return returns.values


def backtest_with_fees(
    predictions: np.ndarray,
    forward_returns: np.ndarray,
    fees_pct: float = 0.001,
    slippage_pct: float = 0.001,
    threshold: float = 0.5,
) -> dict:
    """
    Backtest model predictions with realistic transaction costs.

    Args:
        predictions: Model probability predictions [0-1]
        forward_returns: Actual forward returns
        fees_pct: Trading fees as decimal (0.001 = 0.1%)
        slippage_pct: Slippage as decimal (0.001 = 0.1%)
        threshold: Prediction threshold for taking trades

    Returns:
        Dictionary with backtest results
    """
    round_trip_cost = 2 * (fees_pct + slippage_pct)  # Entry + exit

    # Filter out NaN returns
    valid_mask = ~np.isnan(forward_returns)
    predictions = predictions[valid_mask]
    forward_returns = forward_returns[valid_mask]

    # Generate signals (1 = long, 0 = no trade)
    signals = (predictions > threshold).astype(int)

    # Calculate gross returns (before costs)
    gross_returns = signals * forward_returns

    # Calculate net returns (after costs)
    # Cost is applied only when we trade
    costs = signals * round_trip_cost
    net_returns = gross_returns - costs

    # Calculate cumulative returns
    cum_gross_returns = np.cumsum(gross_returns)
    cum_net_returns = np.cumsum(net_returns)

    # Calculate metrics
    n_trades = int(signals.sum())
    n_total = len(signals)

    gross_mean = gross_returns.mean()
    net_mean = net_returns.mean()

    gross_sharpe = gross_mean / gross_returns.std() * np.sqrt(252) if gross_returns.std() > 0 else 0
    net_sharpe = net_mean / net_returns.std() * np.sqrt(252) if net_returns.std() > 0 else 0

    gross_cum_ret = cum_gross_returns[-1]
    net_cum_ret = cum_net_returns[-1]

    # Quintile analysis (fees-aware)
    quintiles = pd.qcut(predictions, q=5, labels=False, duplicates="drop")
    quintile_stats = []

    for q in range(5):
        q_mask = quintiles == q
        if q_mask.sum() == 0:
            continue

        q_gross_ret = forward_returns[q_mask].mean()
        q_net_ret = q_gross_ret - round_trip_cost  # Assume all trades executed
        q_count = q_mask.sum()

        quintile_stats.append(
            {
                "quintile": q + 1,
                "count": int(q_count),
                "gross_return": float(q_gross_ret),
                "net_return": float(q_net_ret),
                "profitable": q_net_ret > 0,
            }
        )

    # Q5-Q1 spread (fees-aware)
    if len(quintile_stats) >= 5:
        q5_net = quintile_stats[4]["net_return"]
        q1_net = quintile_stats[0]["net_return"]
        q5_q1_spread_net = q5_net - q1_net
    else:
        q5_q1_spread_net = 0.0

    results = {
        "total_samples": int(n_total),
        "trades_taken": n_trades,
        "trade_rate": float(n_trades / n_total),
        "costs": {
            "fees_pct": float(fees_pct * 100),
            "slippage_pct": float(slippage_pct * 100),
            "round_trip_pct": float(round_trip_cost * 100),
            "total_cost": float(n_trades * round_trip_cost),
        },
        "gross": {
            "mean_return": float(gross_mean),
            "cum_return": float(gross_cum_ret),
            "sharpe": float(gross_sharpe),
        },
        "net": {
            "mean_return": float(net_mean),
            "cum_return": float(net_cum_ret),
            "sharpe": float(net_sharpe),
        },
        "impact": {
            "cost_per_trade": float(round_trip_cost),
            "total_drag": float(gross_cum_ret - net_cum_ret),
            "drag_pct": (
                float((gross_cum_ret - net_cum_ret) / gross_cum_ret * 100)
                if gross_cum_ret != 0
                else 0
            ),
        },
        "quintiles": quintile_stats,
        "q5_q1_spread_net": float(q5_q1_spread_net),
        "profitable_after_fees": net_sharpe > 0 and q5_q1_spread_net > 0,
    }

    return results


def print_results(results: dict):
    """Print backtest results in readable format."""
    print("\n" + "=" * 80)
    print("FEES-AWARE BACKTEST RESULTS")
    print("=" * 80)

    print("\n📊 OVERVIEW:")
    print(f"  Total Samples:    {results['total_samples']:,}")
    print(f"  Trades Taken:     {results['trades_taken']:,} ({results['trade_rate']:.1%})")

    print("\n💸 TRANSACTION COSTS:")
    costs = results["costs"]
    print(f"  Fees:             {costs['fees_pct']:.2f}%")
    print(f"  Slippage:         {costs['slippage_pct']:.2f}%")
    print(f"  Round-trip:       {costs['round_trip_pct']:.2f}%")
    print(f"  Total Cost:       {costs['total_cost']:.4f}")

    print("\n📈 GROSS PERFORMANCE (before fees):")
    gross = results["gross"]
    print(f"  Mean Return:      {gross['mean_return']:.4%}")
    print(f"  Cum Return:       {gross['cum_return']:.4%}")
    print(f"  Sharpe Ratio:     {gross['sharpe']:.2f}")

    print("\n💰 NET PERFORMANCE (after fees):")
    net = results["net"]
    print(f"  Mean Return:      {net['mean_return']:.4%}")
    print(f"  Cum Return:       {net['cum_return']:.4%}")
    print(f"  Sharpe Ratio:     {net['sharpe']:.2f}")

    print("\n⚡ COST IMPACT:")
    impact = results["impact"]
    print(f"  Cost per Trade:   {impact['cost_per_trade']:.2%}")
    print(f"  Total Drag:       {impact['total_drag']:.4%}")
    print(f"  Drag %:           {impact['drag_pct']:.1f}%")

    print("\n📊 QUINTILE ANALYSIS (fees-aware):")
    print(f"  {'Q':>3} | {'Count':>6} | {'Gross':>8} | {'Net':>8} | {'Profit?'}")
    print(f"  {'-'*3}-+-{'-'*6}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}")
    for q_stat in results["quintiles"]:
        q_num = q_stat["quintile"]
        count = q_stat["count"]
        gross_ret = q_stat["gross_return"]
        net_ret = q_stat["net_return"]
        profitable = "✅ YES" if q_stat["profitable"] else "❌ NO"
        print(f"  Q{q_num} | {count:>6,} | {gross_ret:>7.3%} | {net_ret:>7.3%} | {profitable}")

    print(f"\n🎯 Q5-Q1 SPREAD (NET): {results['q5_q1_spread_net']:+.3%}")
    print(f"\n{'='*80}")

    if results["profitable_after_fees"]:
        print("✅ PROFITABLE AFTER FEES")
    else:
        print("❌ NOT PROFITABLE AFTER FEES")

    print("=" * 80 + "\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Fees-aware backtest")
    parser.add_argument("--model", required=True, help="Path to trained model JSON")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument(
        "--fees",
        type=float,
        default=0.001,
        help="Trading fees as decimal (default: 0.001 = 0.1%%)",
    )
    parser.add_argument(
        "--slippage",
        type=float,
        default=0.001,
        help="Slippage as decimal (default: 0.001 = 0.1%%)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Prediction threshold for trades (default: 0.5)",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=10,
        help="Forward return horizon in bars (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON path (optional)",
    )

    args = parser.parse_args()

    try:
        # Load model and data
        model_data, features_df = load_model_and_data(args.model, args.symbol, args.timeframe)

        # Get predictions
        predictions = simulate_predictions(features_df, model_data)

        # Calculate forward returns
        # Need close prices - assume they're in the candles file
        try:
            candles_path = get_candles_path(args.symbol, args.timeframe)
        except FileNotFoundError as e:
            print(f"[ERROR] {e}")
            return 1

        candles = pd.read_parquet(candles_path)
        forward_returns = calculate_forward_returns(candles["close"], args.horizon)

        # Align predictions and returns
        min_len = min(len(predictions), len(forward_returns))
        predictions = predictions[:min_len]
        forward_returns = forward_returns[:min_len]

        # Run backtest
        results = backtest_with_fees(
            predictions,
            forward_returns,
            fees_pct=args.fees,
            slippage_pct=args.slippage,
            threshold=args.threshold,
        )

        # Print results
        print_results(results)

        # Save results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"[SAVED] {output_path}")

        # Return exit code based on profitability
        return 0 if results["profitable_after_fees"] else 1

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
