#!/usr/bin/env python3
"""
Quick test: Compare uniform vs regime-specific thresholds.

Usage:
    python scripts/test_regime_thresholds.py --model results/models/tBTCUSD_1h_v3.json
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.strategy.prob_model import predict_proba
from core.utils.data_loader import load_features


def classify_trend_regime_simple(closes: pd.Series, window: int = 50) -> pd.Series:
    """Classify trend regime (matching analyze_calibration_by_regime.py)."""
    ema = closes.ewm(span=window, adjust=False).mean()
    trend = (closes - ema) / ema

    regimes = []
    for t in trend:
        if t > 0.02:
            regimes.append("bull")
        elif t < -0.02:
            regimes.append("bear")
        else:
            regimes.append("ranging")
    return pd.Series(regimes, index=closes.index)


def backtest_with_thresholds(
    predictions: np.ndarray,
    returns: np.ndarray,
    regimes: pd.Series,
    thresholds: dict,
    uniform_threshold: float = 0.6,
) -> dict:
    """
    Simulate trading with threshold rules.

    Returns metrics for comparison.
    """
    # Scenario A: Uniform threshold
    uniform_signals = predictions >= uniform_threshold
    uniform_trades = uniform_signals.sum()
    uniform_returns = returns[uniform_signals]
    uniform_mean_return = uniform_returns.mean() if len(uniform_returns) > 0 else 0.0
    uniform_win_rate = (uniform_returns > 0).mean() if len(uniform_returns) > 0 else 0.0

    # Scenario B: Regime-specific thresholds
    regime_signals = np.zeros(len(predictions), dtype=bool)
    for i, regime in enumerate(regimes):
        thr = thresholds.get(regime, uniform_threshold)
        if predictions[i] >= thr:
            regime_signals[i] = True

    regime_trades = regime_signals.sum()
    regime_returns = returns[regime_signals]
    regime_mean_return = regime_returns.mean() if len(regime_returns) > 0 else 0.0
    regime_win_rate = (regime_returns > 0).mean() if len(regime_returns) > 0 else 0.0

    # Calculate metrics
    def calc_sharpe(rets):
        if len(rets) == 0:
            return 0.0
        return rets.mean() / rets.std() if rets.std() > 0 else 0.0

    def calc_max_dd(rets):
        if len(rets) == 0:
            return 0.0
        cumulative = np.cumprod(1 + rets)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return float(drawdown.min())

    uniform_sharpe = calc_sharpe(uniform_returns)
    uniform_max_dd = calc_max_dd(uniform_returns)

    regime_sharpe = calc_sharpe(regime_returns)
    regime_max_dd = calc_max_dd(regime_returns)

    return {
        "uniform": {
            "trades": int(uniform_trades),
            "mean_return": float(uniform_mean_return),
            "win_rate": float(uniform_win_rate),
            "sharpe": float(uniform_sharpe),
            "max_dd": float(uniform_max_dd),
            "annual_return": float(uniform_mean_return * uniform_trades),  # Approximation
        },
        "regime_specific": {
            "trades": int(regime_trades),
            "mean_return": float(regime_mean_return),
            "win_rate": float(regime_win_rate),
            "sharpe": float(regime_sharpe),
            "max_dd": float(regime_max_dd),
            "annual_return": float(regime_mean_return * regime_trades),  # Approximation
        },
        "improvement": {
            "trades_delta": int(regime_trades - uniform_trades),
            "trades_pct": (
                float((regime_trades - uniform_trades) / uniform_trades * 100)
                if uniform_trades > 0
                else 0.0
            ),
            "mean_return_delta": float(regime_mean_return - uniform_mean_return),
            "win_rate_delta": float(regime_win_rate - uniform_win_rate),
            "sharpe_delta": float(regime_sharpe - uniform_sharpe),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Test regime-specific thresholds")
    parser.add_argument("--model", required=True, help="Path to model JSON")

    args = parser.parse_args()

    model_path = Path(args.model)

    print("=" * 80)
    print("REGIME-SPECIFIC THRESHOLD BACKTEST")
    print("=" * 80)

    # Extract symbol/timeframe from filename
    parts = model_path.stem.split("_")
    symbol = parts[0] if len(parts) >= 2 else "tBTCUSD"
    timeframe = parts[1] if len(parts) >= 2 else "1h"

    print(f"Model: {model_path.name}")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")

    # Load model
    import json

    with open(model_path) as f:
        model_config = json.load(f)

    # Load features
    print("\n[LOAD] Loading features and candles...")
    features_df = load_features(symbol, timeframe)
    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path)

    # Get predictions
    print("[PREDICT] Generating predictions...")
    feature_cols = [col for col in features_df.columns if col != "timestamp"]
    X = features_df[feature_cols].values

    schema = model_config.get("schema", feature_cols)
    buy_w = model_config.get("buy", {}).get("w")
    buy_b = model_config.get("buy", {}).get("b", 0.0)
    calib_buy = (
        model_config.get("buy", {}).get("calib", {}).get("a", 1.0),
        model_config.get("buy", {}).get("calib", {}).get("b", 0.0),
    )

    predictions = []
    for i in range(len(X)):
        feats_dict = {col: X[i, j] for j, col in enumerate(feature_cols)}
        probas = predict_proba(
            feats_dict, schema=schema, buy_w=buy_w, buy_b=buy_b, calib_buy=calib_buy
        )
        predictions.append(probas["buy"])

    predictions = np.array(predictions)

    # Calculate returns
    print("[CALC] Calculating forward returns and regimes...")
    close_prices = candles_df["close"]
    forward_returns = close_prices.pct_change(10).shift(-10)

    # Classify regimes
    regimes = classify_trend_regime_simple(close_prices, window=50)

    # Align data
    min_len = min(len(predictions), len(forward_returns), len(regimes))
    predictions = predictions[:min_len]
    returns = forward_returns.iloc[:min_len].values
    regimes = regimes.iloc[:min_len]

    # Remove NaN
    valid_mask = ~np.isnan(returns)
    predictions = predictions[valid_mask]
    returns = returns[valid_mask]
    regimes = regimes[valid_mask]

    # Define thresholds
    regime_thresholds = {
        "bear": 0.30,
        "bull": 0.90,
        "ranging": 0.50,
        "balanced": 0.60,
    }

    # Run backtest
    print("\n[BACKTEST] Comparing strategies...")
    results = backtest_with_thresholds(
        predictions, returns, regimes, regime_thresholds, uniform_threshold=0.6
    )

    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print("\nUNIFORM THRESHOLD (0.60 for all regimes):")
    u = results["uniform"]
    print(f"  Trades:        {u['trades']}")
    print(f"  Mean Return:   {u['mean_return']:+.4%}")
    print(f"  Win Rate:      {u['win_rate']:.1%}")
    print(f"  Sharpe Ratio:  {u['sharpe']:.3f}")
    print(f"  Max Drawdown:  {u['max_dd']:.1%}")

    print("\nREGIME-SPECIFIC THRESHOLDS:")
    print("  Bear: 0.30, Bull: 0.90, Ranging: 0.50")
    r = results["regime_specific"]
    print(f"  Trades:        {r['trades']}")
    print(f"  Mean Return:   {r['mean_return']:+.4%}")
    print(f"  Win Rate:      {r['win_rate']:.1%}")
    print(f"  Sharpe Ratio:  {r['sharpe']:.3f}")
    print(f"  Max Drawdown:  {r['max_dd']:.1%}")

    print("\nIMPROVEMENT:")
    imp = results["improvement"]
    print(f"  Trades:        {imp['trades_delta']:+d} ({imp['trades_pct']:+.1f}%)")
    print(f"  Mean Return:   {imp['mean_return_delta']:+.4%}")
    print(f"  Win Rate:      {imp['win_rate_delta']:+.1%}")
    print(f"  Sharpe Ratio:  {imp['sharpe_delta']:+.3f}")

    # Assessment
    print("\n" + "=" * 80)
    print("ASSESSMENT")
    print("=" * 80)

    if imp["sharpe_delta"] > 0.3:
        print("[EXCELLENT] Regime thresholds provide SIGNIFICANT improvement!")
        print("Recommendation: DEPLOY with these thresholds")
    elif imp["sharpe_delta"] > 0.1:
        print("[GOOD] Regime thresholds provide moderate improvement")
        print("Recommendation: DEPLOY or further optimize")
    elif imp["sharpe_delta"] > 0:
        print("[MARGINAL] Slight improvement")
        print("Recommendation: Consider Option C (regime-aware calibration)")
    else:
        print("[NEGATIVE] No improvement or worse!")
        print("Recommendation: Use Option C (regime-aware calibration) instead")

    print("=" * 80)


if __name__ == "__main__":
    main()
