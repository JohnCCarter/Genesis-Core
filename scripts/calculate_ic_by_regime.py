#!/usr/bin/env python3
"""
Calculate IC metrics split by market regime.

Tests hypothesis: Edge may exist only in specific market conditions.
- HighVol vs LowVol
- Trending vs Ranging
- Bull vs Bear

Usage:
    python scripts/calculate_ic_by_regime.py --model results/models/tBTCUSD_1h_v3.json \\
        --symbol tBTCUSD --timeframe 1h
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils.data_loader import load_features


def classify_volatility_regime(returns: pd.Series, window: int = 50) -> pd.Series:
    """
    Classify as HighVol or LowVol based on rolling volatility.

    Returns: Series with 'HighVol' or 'LowVol'
    """
    rolling_vol = returns.rolling(window=window).std()
    median_vol = rolling_vol.median()

    regime = pd.Series(index=returns.index, dtype=str)
    regime[rolling_vol > median_vol] = "HighVol"
    regime[rolling_vol <= median_vol] = "LowVol"

    return regime


def classify_trend_regime(close: pd.Series, window: int = 100) -> pd.Series:
    """
    Classify as Trending or Ranging based on ADX-like logic.

    Returns: Series with 'Trending' or 'Ranging'
    """
    # Simple trend strength: compare price to moving average
    ma = close.rolling(window=window).mean()
    distance = abs(close - ma) / ma

    # Rolling trend strength
    trend_strength = distance.rolling(window=50).mean()
    median_strength = trend_strength.median()

    regime = pd.Series(index=close.index, dtype=str)
    regime[trend_strength > median_strength] = "Trending"
    regime[trend_strength <= median_strength] = "Ranging"

    return regime


def classify_direction_regime(returns: pd.Series, window: int = 50) -> pd.Series:
    """
    Classify as Bull or Bear based on cumulative returns.

    Returns: Series with 'Bull' or 'Bear'
    """
    cum_returns = returns.rolling(window=window).sum()

    regime = pd.Series(index=returns.index, dtype=str)
    regime[cum_returns > 0] = "Bull"
    regime[cum_returns <= 0] = "Bear"

    return regime


def calculate_ic_by_regime(
    predictions: np.ndarray,
    forward_returns: np.ndarray,
    regime: pd.Series,
) -> dict:
    """Calculate IC for each regime."""
    results = {}

    # Get unique regimes
    unique_regimes = regime.dropna().unique()

    for reg in unique_regimes:
        mask = (regime == reg).values

        # Filter predictions and returns
        pred_regime = predictions[mask]
        ret_regime = forward_returns[mask]

        # Remove NaN
        valid_mask = ~np.isnan(ret_regime)
        pred_regime = pred_regime[valid_mask]
        ret_regime = ret_regime[valid_mask]

        if len(pred_regime) < 50:  # Need minimum samples
            continue

        # Calculate IC
        ic, p_value = spearmanr(pred_regime, ret_regime)

        # Calculate mean return per quintile
        quintiles = pd.qcut(pred_regime, q=5, labels=False, duplicates="drop")
        quintile_returns = []

        for q in range(5):
            q_mask = quintiles == q
            if q_mask.sum() > 0:
                quintile_returns.append(ret_regime[q_mask].mean())
            else:
                quintile_returns.append(np.nan)

        # Q5-Q1 spread
        if len(quintile_returns) >= 5:
            q5_q1_spread = quintile_returns[4] - quintile_returns[0]
        else:
            q5_q1_spread = np.nan

        results[reg] = {
            "samples": int(len(pred_regime)),
            "ic": float(ic),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "mean_return": float(ret_regime.mean()),
            "std_return": float(ret_regime.std()),
            "q5_q1_spread": float(q5_q1_spread) if not np.isnan(q5_q1_spread) else None,
            "quintile_returns": [float(x) if not np.isnan(x) else None for x in quintile_returns],
        }

    return results


def load_model_predictions(model_path: str, features_df: pd.DataFrame) -> np.ndarray:
    """
    Load model and generate predictions.

    For now, use placeholder. TODO: Load actual sklearn model.
    """
    # Placeholder: Use weighted average of features
    # In production, this should load the actual model and predict

    feature_cols = [col for col in features_df.columns if col != "timestamp"]

    if not feature_cols:
        raise ValueError("No feature columns found!")

    # Simple weighted average (placeholder)
    predictions = features_df[feature_cols].mean(axis=1).values

    return predictions


def calculate_forward_returns(close: pd.Series, horizon: int = 10) -> np.ndarray:
    """Calculate forward returns."""
    returns = close.pct_change(horizon).shift(-horizon)
    return returns.values


def print_regime_results(regime_results: dict, regime_name: str):
    """Print results for a regime split."""
    print(f"\n{'='*80}")
    print(f"{regime_name.upper()} REGIME SPLIT")
    print(f"{'='*80}")

    for regime, stats in regime_results.items():
        print(f"\n{regime}:")
        print(f"  Samples:        {stats['samples']:,}")
        ic_status = "[GOOD]" if stats["ic"] > 0.03 else "[WEAK]" if stats["ic"] > 0 else "[NEG]"
        sig_status = "[SIG]" if stats["significant"] else "[N/S]"
        print(f"  IC:             {stats['ic']:+.4f} {ic_status}")
        print(f"  p-value:        {stats['p_value']:.4f} {sig_status}")
        print(f"  Mean Return:    {stats['mean_return']:+.4%}")
        print(
            f"  Q5-Q1 Spread:   {stats['q5_q1_spread']:+.4%}"
            if stats["q5_q1_spread"]
            else "  Q5-Q1 Spread:   N/A"
        )

        # Show quintile returns
        if stats["quintile_returns"]:
            print(f"  Quintiles:      ", end="")
            for i, qret in enumerate(stats["quintile_returns"], 1):
                if qret is not None:
                    print(f"Q{i}:{qret:+.3%} ", end="")
            print()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="IC analysis by market regime")
    parser.add_argument("--model", required=True, help="Path to trained model")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument(
        "--horizon", type=int, default=10, help="Forward return horizon (default: 10)"
    )
    parser.add_argument("--output", help="Output JSON path (optional)")

    args = parser.parse_args()

    try:
        print("\n" + "=" * 80)
        print("REGIME-SPLIT IC ANALYSIS")
        print("=" * 80)
        print(f"Model:     {args.model}")
        print(f"Symbol:    {args.symbol}")
        print(f"Timeframe: {args.timeframe}")
        print(f"Horizon:   {args.horizon} bars")

        # Load model and data
        print(f"\n[LOAD] Loading model: {args.model}")
        with open(args.model) as f:
            model_data = json.load(f)

        print(f"[LOAD] Loading features for {args.symbol} {args.timeframe}")
        features_df = load_features(args.symbol, args.timeframe)

        # Load candles for regime classification
        candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
        candles_df = pd.read_parquet(candles_path)

        # Generate predictions
        print("[PREDICT] Generating model predictions...")
        predictions = load_model_predictions(args.model, features_df)

        # Calculate forward returns
        print("[RETURNS] Calculating forward returns...")
        forward_returns = calculate_forward_returns(candles_df["close"], args.horizon)

        # Align data
        min_len = min(len(predictions), len(forward_returns), len(candles_df))
        predictions = predictions[:min_len]
        forward_returns = forward_returns[:min_len]
        close = candles_df["close"].iloc[:min_len]

        # Calculate returns for regime classification
        returns = close.pct_change()

        # === VOLATILITY REGIME ===
        print("\n[REGIME] Classifying volatility regimes...")
        vol_regime = classify_volatility_regime(returns, window=50)
        vol_results = calculate_ic_by_regime(predictions, forward_returns, vol_regime)
        print_regime_results(vol_results, "VOLATILITY")

        # === TREND REGIME ===
        print("\n[REGIME] Classifying trend regimes...")
        trend_regime = classify_trend_regime(close, window=100)
        trend_results = calculate_ic_by_regime(predictions, forward_returns, trend_regime)
        print_regime_results(trend_results, "TREND")

        # === DIRECTION REGIME ===
        print("\n[REGIME] Classifying direction regimes...")
        direction_regime = classify_direction_regime(returns, window=50)
        direction_results = calculate_ic_by_regime(predictions, forward_returns, direction_regime)
        print_regime_results(direction_results, "DIRECTION")

        # === SUMMARY ===
        print("\n" + "=" * 80)
        print("REGIME ANALYSIS SUMMARY")
        print("=" * 80)

        # Find best regime
        all_regimes = []
        for regime_type, results in [
            ("Volatility", vol_results),
            ("Trend", trend_results),
            ("Direction", direction_results),
        ]:
            for regime_name, stats in results.items():
                all_regimes.append(
                    {
                        "type": regime_type,
                        "name": regime_name,
                        "ic": stats["ic"],
                        "spread": stats["q5_q1_spread"],
                        "samples": stats["samples"],
                    }
                )

        # Sort by IC
        all_regimes.sort(key=lambda x: x["ic"], reverse=True)

        print("\nBest Regimes by IC:")
        for i, reg in enumerate(all_regimes[:5], 1):
            print(
                f"{i}. {reg['type']}/{reg['name']}: IC={reg['ic']:+.4f}, "
                f"Spread={reg['spread']:+.3%} ({reg['samples']:,} samples)"
            )

        # Save results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            results = {
                "model": args.model,
                "symbol": args.symbol,
                "timeframe": args.timeframe,
                "horizon": args.horizon,
                "volatility": vol_results,
                "trend": trend_results,
                "direction": direction_results,
                "best_regimes": all_regimes[:5],
            }

            with open(output_path, "w") as f:
                json.dump(results, f, indent=2)

            print(f"\n[SAVED] {output_path}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Regime analysis complete!")
        print("=" * 80 + "\n")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
