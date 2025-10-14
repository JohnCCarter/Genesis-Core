#!/usr/bin/env python3
"""
Comprehensive feature IC analysis - ALL possible features.

Tests:
1. Current v15 features (inverted)
2. Non-inverted versions (directional)
3. ALL available indicators
4. Regime-split analysis

Goal: Find features with STRONG directional signal (IC > 0.08)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.adx import calculate_adx
from core.indicators.atr import calculate_atr
from core.indicators.bollinger import bollinger_bands
from core.indicators.derived_features import (
    calculate_volatility_shift,
)
from core.indicators.ema import calculate_ema
from core.indicators.fibonacci import FibonacciConfig, calculate_fibonacci_features_vectorized
from core.indicators.macd import calculate_macd
from core.indicators.rsi import calculate_rsi
from core.indicators.volume import calculate_volume_sma


def calculate_all_possible_features(candles_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ALL possible features (inverted and non-inverted).

    This gives us the full universe to test.
    """
    df = candles_df.copy()

    # Extract series
    closes = df["close"].tolist()
    highs = df["high"].tolist()
    lows = df["low"].tolist()
    volumes = df["volume"].tolist()

    # Calculate base indicators
    ema20 = calculate_ema(closes, period=20)
    ema50 = calculate_ema(closes, period=50)
    ema100 = calculate_ema(closes, period=100)
    rsi = calculate_rsi(closes, period=14)
    atr14 = calculate_atr(highs, lows, closes, period=14)
    atr50 = calculate_atr(highs, lows, closes, period=50)
    adx = calculate_adx(highs, lows, closes, period=14)
    bb = bollinger_bands(closes, period=20, std_dev=2.0)
    macd_data = calculate_macd(closes, fast_period=12, slow_period=26, signal_period=9)
    vol_sma = calculate_volume_sma(volumes, period=20)
    vol_shift = calculate_volatility_shift(atr14, atr50)

    # Convert to arrays
    def to_array(lst):
        return np.array(lst if lst else [np.nan] * len(df))

    ema20_arr = to_array(ema20)
    ema50_arr = to_array(ema50)
    ema100_arr = to_array(ema100)
    rsi_arr = to_array(rsi)
    atr14_arr = to_array(atr14)
    adx_arr = to_array(adx)
    bb_pos_arr = to_array(bb["position"])
    bb_width_arr = to_array(bb["width"])
    macd_hist_arr = to_array(macd_data["histogram"])
    vol_sma_arr = to_array(vol_sma)
    vol_shift_arr = to_array(vol_shift)

    close_arr = df["close"].values

    # Build comprehensive feature set
    features = pd.DataFrame(index=df.index)

    # === TREND FEATURES (Directional) ===
    features["ema_slope_20"] = pd.Series(ema20_arr).pct_change(5)  # 5-bar EMA slope
    features["ema_slope_50"] = pd.Series(ema50_arr).pct_change(5)
    features["price_vs_ema20"] = (close_arr - ema20_arr) / ema20_arr  # % above/below
    features["price_vs_ema50"] = (close_arr - ema50_arr) / ema50_arr
    features["ema20_vs_ema100"] = (ema20_arr - ema100_arr) / ema100_arr  # EMA cross
    features["adx"] = adx_arr / 100.0  # Normalize to [0, 1]

    # === MOMENTUM FEATURES (Directional) ===
    features["rsi"] = (rsi_arr - 50.0) / 50.0  # Centered at 0
    features["rsi_inv"] = -features["rsi"]  # INVERTED (mean reversion)
    features["rsi_lag1"] = features["rsi"].shift(1)
    features["rsi_inv_lag1"] = -features["rsi_lag1"]
    features["macd_histogram"] = macd_hist_arr / close_arr  # Normalized

    # === VOLATILITY FEATURES ===
    features["atr_pct"] = atr14_arr / close_arr  # ATR as % of price
    features["bb_position"] = bb_pos_arr  # 0 = lower, 1 = upper
    features["bb_position_inv"] = 1.0 - bb_pos_arr  # INVERTED
    features["bb_width"] = bb_width_arr
    features["volatility_shift"] = vol_shift_arr
    features["vol_regime"] = (vol_shift_arr > 1.0).astype(float)

    # === SMOOTHED VERSIONS (3-bar MA) ===
    features["rsi_ma3"] = features["rsi"].rolling(3, min_periods=1).mean()
    features["rsi_inv_ma3"] = -features["rsi_ma3"]
    features["bb_position_ma3"] = features["bb_position"].rolling(3, min_periods=1).mean()
    features["bb_position_inv_ma3"] = 1.0 - features["bb_position_ma3"]
    features["volatility_shift_ma3"] = features["volatility_shift"].rolling(3, min_periods=1).mean()

    # === INTERACTION FEATURES ===
    features["rsi_vol_interaction"] = features["rsi_inv"] * features["volatility_shift"]
    features["rsi_vol_directional"] = (
        features["rsi"] * features["volatility_shift"]
    )  # NON-inverted!

    # === VOLUME FEATURES ===
    features["volume_ratio"] = df["volume"].values / vol_sma_arr

    # === FIBONACCI FEATURES ===
    # Calculate Fibonacci features using vectorized approach
    fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
    fib_features_df = calculate_fibonacci_features_vectorized(df, fib_config)

    # Add Fibonacci features to main features DataFrame
    for col in fib_features_df.columns:
        features[col] = fib_features_df[col]

    # Add timestamp
    features.insert(0, "timestamp", df["timestamp"])

    return features


def test_feature_ic_by_regime(
    feature_values: pd.Series,
    returns: pd.Series,
    regimes: pd.Series,
    feature_name: str,
) -> dict:
    """Test IC for a feature overall and per regime."""
    results = {"feature": feature_name, "overall": {}, "by_regime": {}}

    # Overall IC
    mask = ~feature_values.isna() & ~returns.isna()
    if mask.sum() > 20:
        ic, p_val = spearmanr(feature_values[mask], returns[mask])
        results["overall"] = {
            "ic": float(ic),
            "p_value": float(p_val),
            "n_samples": int(mask.sum()),
        }

    # Per regime
    for regime in ["bear", "bull", "ranging"]:
        regime_mask = (regimes == regime) & ~feature_values.isna() & ~returns.isna()
        if regime_mask.sum() > 20:
            ic, p_val = spearmanr(feature_values[regime_mask], returns[regime_mask])
            results["by_regime"][regime] = {
                "ic": float(ic),
                "p_value": float(p_val),
                "n_samples": int(regime_mask.sum()),
            }

    return results


def main():
    parser = argparse.ArgumentParser(description="Comprehensive feature IC analysis")
    parser.add_argument("--symbol", default="tBTCUSD", help="Symbol")
    parser.add_argument("--timeframe", default="1h", help="Timeframe")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    parser.add_argument("--output", help="Output JSON path")

    args = parser.parse_args()

    print("=" * 80)
    print("COMPREHENSIVE FEATURE IC ANALYSIS")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Horizon: {args.horizon} bars")
    print("=" * 80)

    # Load candles
    candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path)

    print(f"\n[LOAD] Loaded {len(candles_df)} candles")

    # Calculate ALL possible features
    print("[COMPUTE] Calculating ALL possible features...")
    features_df = calculate_all_possible_features(candles_df)

    feature_cols = [col for col in features_df.columns if col != "timestamp"]
    print(f"[COMPUTED] {len(feature_cols)} features")

    # Calculate forward returns
    print(f"[RETURNS] Calculating {args.horizon}-bar forward returns...")
    close_prices = candles_df["close"]
    forward_returns = close_prices.pct_change(args.horizon).shift(-args.horizon)

    # Classify regimes
    print("[REGIMES] Classifying market regimes...")

    def classify_trend(closes, window=50):
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

    regimes = classify_trend(candles_df["close"])

    # Test all features
    print("\n" + "=" * 80)
    print("TESTING ALL FEATURES")
    print("=" * 80)

    all_results = []

    for feat in feature_cols:
        result = test_feature_ic_by_regime(features_df[feat], forward_returns, regimes, feat)
        all_results.append(result)

        # Print summary
        overall_ic = result["overall"].get("ic", 0.0)
        overall_p = result["overall"].get("p_value", 1.0)
        sig = "[SIG]" if overall_p < 0.05 else ""

        print(f"\n{feat:<30} Overall IC: {overall_ic:+.4f} (p={overall_p:.4f}) {sig}")

        # Per regime
        for regime in ["bear", "bull", "ranging"]:
            if regime in result["by_regime"]:
                r = result["by_regime"][regime]
                ic = r["ic"]
                p = r["p_value"]
                sig = "[SIG]" if p < 0.05 else ""
                print(f"  {regime:>8}: IC {ic:+.4f} (p={p:.4f}) {sig}")

    # Sort by overall IC (absolute value)
    all_results_sorted = sorted(
        all_results, key=lambda x: abs(x["overall"].get("ic", 0)), reverse=True
    )

    print("\n" + "=" * 80)
    print("TOP 20 FEATURES (by absolute IC)")
    print("=" * 80)

    for i, result in enumerate(all_results_sorted[:20], 1):
        overall = result["overall"]
        ic = overall.get("ic", 0)
        p = overall.get("p_value", 1)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""

        print(f"{i:2}. {result['feature']:<30} IC: {ic:+.4f} {sig}")

        # Show regime breakdown
        by_reg = result["by_regime"]
        bear_ic = by_reg.get("bear", {}).get("ic", 0)
        bull_ic = by_reg.get("bull", {}).get("ic", 0)
        rang_ic = by_reg.get("ranging", {}).get("ic", 0)

        print(f"    Bear: {bear_ic:+.4f}, Bull: {bull_ic:+.4f}, Ranging: {rang_ic:+.4f}")

    # Identify directional vs mean reversion
    print("\n" + "=" * 80)
    print("FEATURE CLASSIFICATION")
    print("=" * 80)

    directional = []
    mean_reversion = []

    for result in all_results:
        feat = result["feature"]
        overall_ic = result["overall"].get("ic", 0)
        by_reg = result["by_regime"]

        # Check if IC signs match expected directional behavior
        bear_ic = by_reg.get("bear", {}).get("ic", 0)
        bull_ic = by_reg.get("bull", {}).get("ic", 0)

        # Directional: Negative IC in bear (SHORT profitable), Positive in bull (LONG profitable)
        # Mean reversion: Positive IC in bear (BUY dips), Negative in bull (SELL rallies)

        if abs(overall_ic) > 0.03:
            if bear_ic < -0.03 and bull_ic > 0.03:
                directional.append((feat, overall_ic, bear_ic, bull_ic))
            elif bear_ic > 0.03 or (bear_ic > 0 and bull_ic < 0):
                mean_reversion.append((feat, overall_ic, bear_ic, bull_ic))

    print("\nDIRECTIONAL FEATURES (Short in bear, Long in bull):")
    for feat, overall, bear, bull in sorted(directional, key=lambda x: abs(x[1]), reverse=True):
        print(f"  {feat:<30} Overall: {overall:+.4f}, Bear: {bear:+.4f}, Bull: {bull:+.4f}")

    print("\nMEAN REVERSION FEATURES (Buy dips in bear, Sell rallies in bull):")
    for feat, overall, bear, bull in sorted(mean_reversion, key=lambda x: abs(x[1]), reverse=True):
        print(f"  {feat:<30} Overall: {overall:+.4f}, Bear: {bear:+.4f}, Bull: {bull:+.4f}")

    # Save results
    if args.output:
        output_data = {
            "all_features": all_results,
            "top_20": [r["feature"] for r in all_results_sorted[:20]],
            "directional_features": [
                {"feature": f[0], "overall_ic": f[1], "bear_ic": f[2], "bull_ic": f[3]}
                for f in directional
            ],
            "mean_reversion_features": [
                {"feature": f[0], "overall_ic": f[1], "bear_ic": f[2], "bull_ic": f[3]}
                for f in mean_reversion
            ],
        }

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n[SAVED] Results: {output_path}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if directional:
        print(f"\n[EXCELLENT] Found {len(directional)} directional features!")
        print("Recommendation: Build TREND-FOLLOWING model with these features")
    else:
        print("\n[WARNING] No strong directional features found!")
        print("Current features are biased toward MEAN REVERSION")

    if mean_reversion:
        print(f"\nFound {len(mean_reversion)} mean reversion features")
        print("These can be used for counter-trend strategy in ranging markets")

    print("=" * 80)


if __name__ == "__main__":
    main()
