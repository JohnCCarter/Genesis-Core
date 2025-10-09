#!/usr/bin/env python3
"""
Test individual feature IC within specific regime (HighVol).

Tests each feature separately to find best performers in target regime.

Usage:
    python scripts/test_features_by_regime.py --symbol tBTCUSD --timeframe 1h --regime HighVol
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
    """Classify as HighVol or LowVol."""
    rolling_vol = returns.rolling(window=window).std()
    median_vol = rolling_vol.median()

    regime = pd.Series(index=returns.index, dtype=str)
    regime[rolling_vol > median_vol] = "HighVol"
    regime[rolling_vol <= median_vol] = "LowVol"

    return regime


def calculate_forward_returns(close: pd.Series, horizon: int = 10) -> np.ndarray:
    """Calculate forward returns."""
    returns = close.pct_change(horizon).shift(-horizon)
    return returns.values


def test_feature_ic(
    feature_values: np.ndarray,
    forward_returns: np.ndarray,
    regime_mask: np.ndarray,
) -> dict:
    """Test IC for a single feature in specific regime."""
    # Filter by regime
    feat_regime = feature_values[regime_mask]
    ret_regime = forward_returns[regime_mask]

    # Remove NaN
    valid_mask = ~np.isnan(ret_regime) & ~np.isnan(feat_regime)
    feat_regime = feat_regime[valid_mask]
    ret_regime = ret_regime[valid_mask]

    if len(feat_regime) < 50:
        return None

    # Calculate IC
    ic, p_value = spearmanr(feat_regime, ret_regime)

    # Quintile analysis
    quintiles = pd.qcut(feat_regime, q=5, labels=False, duplicates="drop")
    quintile_returns = []

    for q in range(5):
        q_mask = quintiles == q
        if q_mask.sum() > 0:
            quintile_returns.append(ret_regime[q_mask].mean())
        else:
            quintile_returns.append(np.nan)

    # Q5-Q1 spread
    if (
        len(quintile_returns) >= 5
        and not np.isnan(quintile_returns[4])
        and not np.isnan(quintile_returns[0])
    ):
        q5_q1_spread = quintile_returns[4] - quintile_returns[0]
    else:
        q5_q1_spread = np.nan

    return {
        "samples": int(len(feat_regime)),
        "ic": float(ic),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
        "q5_q1_spread": float(q5_q1_spread) if not np.isnan(q5_q1_spread) else None,
        "quintile_returns": [float(x) if not np.isnan(x) else None for x in quintile_returns],
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Test features by regime")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument("--regime", default="HighVol", help="Target regime (default: HighVol)")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    parser.add_argument("--output", help="Output JSON path")

    args = parser.parse_args()

    try:
        print("\n" + "=" * 80)
        print(f"FEATURE IC TESTING - {args.regime.upper()} REGIME")
        print("=" * 80)
        print(f"Symbol:    {args.symbol}")
        print(f"Timeframe: {args.timeframe}")
        print(f"Regime:    {args.regime}")
        print(f"Horizon:   {args.horizon} bars")

        # Load features
        print(f"\n[LOAD] Loading features for {args.symbol} {args.timeframe}")
        features_df = load_features(args.symbol, args.timeframe)

        # Load candles
        candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
        candles_df = pd.read_parquet(candles_path)

        # Calculate forward returns
        print("[RETURNS] Calculating forward returns...")
        forward_returns = calculate_forward_returns(candles_df["close"], args.horizon)

        # Classify regime
        print("[REGIME] Classifying volatility regimes...")
        returns = candles_df["close"].pct_change()
        regime = classify_volatility_regime(returns, window=50)
        regime_mask = (regime == args.regime).values

        print(
            f"[REGIME] {args.regime} samples: {regime_mask.sum():,}/{len(regime_mask):,} ({regime_mask.mean():.1%})"
        )

        # Test each feature
        print(f"\n[TEST] Testing {len(features_df.columns)-1} features...")

        results = {}
        feature_cols = [col for col in features_df.columns if col != "timestamp"]

        for feat_name in feature_cols:
            feat_values = features_df[feat_name].values

            # Align lengths
            min_len = min(len(feat_values), len(forward_returns), len(regime_mask))
            feat_values = feat_values[:min_len]
            fwd_ret = forward_returns[:min_len]
            reg_mask = regime_mask[:min_len]

            result = test_feature_ic(feat_values, fwd_ret, reg_mask)

            if result:
                results[feat_name] = result

        # Sort by IC
        sorted_results = sorted(results.items(), key=lambda x: x[1]["ic"], reverse=True)

        # Print results
        print("\n" + "=" * 80)
        print(f"FEATURE RANKING - {args.regime.upper()} REGIME")
        print("=" * 80)
        print(f"\n{'Rank':<5} | {'Feature':<30} | {'IC':<8} | {'Spread':<8} | {'Sig?':<5}")
        print("-" * 80)

        for rank, (feat_name, stats) in enumerate(sorted_results, 1):
            ic_str = f"{stats['ic']:+.4f}"
            spread_str = f"{stats['q5_q1_spread']:+.3%}" if stats["q5_q1_spread"] else "N/A"
            sig_str = "[SIG]" if stats["significant"] else ""

            ic_rating = ""
            if stats["ic"] > 0.05:
                ic_rating = "[EXCELLENT]"
            elif stats["ic"] > 0.03:
                ic_rating = "[GOOD]"
            elif stats["ic"] > 0:
                ic_rating = "[WEAK]"
            else:
                ic_rating = "[NEG]"

            print(
                f"{rank:<5} | {feat_name:<30} | {ic_str:<8} {ic_rating:<12} | {spread_str:<8} | {sig_str}"
            )

        # Top performers summary
        print("\n" + "=" * 80)
        print("TOP 10 FEATURES")
        print("=" * 80)

        for rank, (feat_name, stats) in enumerate(sorted_results[:10], 1):
            print(f"\n{rank}. {feat_name}")
            print(f"   IC:       {stats['ic']:+.4f}")
            print(
                f"   Spread:   {stats['q5_q1_spread']:+.3%}"
                if stats["q5_q1_spread"]
                else "   Spread:   N/A"
            )
            print(f"   p-value:  {stats['p_value']:.4f}")
            print(f"   Samples:  {stats['samples']:,}")

        # Save results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            output = {
                "symbol": args.symbol,
                "timeframe": args.timeframe,
                "regime": args.regime,
                "horizon": args.horizon,
                "total_features": len(results),
                "features": dict(sorted_results),
            }

            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)

            print(f"\n[SAVED] {output_path}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Feature testing complete!")
        print("=" * 80 + "\n")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
