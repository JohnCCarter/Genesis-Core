#!/usr/bin/env python3
"""
Calculate Partial Information Coefficient (Partial-IC).

Tests if Feature B adds incremental value AFTER controlling for Feature A.
Used to find non-redundant features with unique predictive power.

Partial-IC(B | A) = IC(residual(B, A), returns)

Where residual(B, A) is what remains of B after removing correlation with A.

Usage:
    python scripts/calculate_partial_ic.py --symbol tBTCUSD --timeframe 1h \\
        --regime HighVol --output results/partial_ic/highvol_partial_ic.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression

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


def calculate_ic(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Calculate IC and p-value."""
    # Remove NaN
    valid_mask = ~np.isnan(x) & ~np.isnan(y)
    x_clean = x[valid_mask]
    y_clean = y[valid_mask]

    if len(x_clean) < 50:
        return np.nan, np.nan

    ic, p_value = spearmanr(x_clean, y_clean)
    return ic, p_value


def calculate_partial_ic(
    feature_a: np.ndarray,
    feature_b: np.ndarray,
    returns: np.ndarray,
) -> dict:
    """
    Calculate Partial-IC(B | A).

    Steps:
    1. Calculate IC(B, returns) - baseline IC of B
    2. Regress B on A to get residuals (what B has that A doesn't)
    3. Calculate IC(residuals, returns) - incremental IC of B after A
    4. Partial-IC = IC from step 3
    """
    # Remove NaN
    valid_mask = ~np.isnan(feature_a) & ~np.isnan(feature_b) & ~np.isnan(returns)
    feat_a = feature_a[valid_mask]
    feat_b = feature_b[valid_mask]
    ret = returns[valid_mask]

    if len(feat_a) < 50:
        return None

    # Step 1: Baseline IC of B
    ic_b, p_b = calculate_ic(feat_b, ret)

    # Step 2: Regress B on A to get residuals
    reg = LinearRegression()
    reg.fit(feat_a.reshape(-1, 1), feat_b)
    predicted_b = reg.predict(feat_a.reshape(-1, 1))
    residuals_b = feat_b - predicted_b

    # Step 3: IC of residuals (incremental IC)
    partial_ic, partial_p = calculate_ic(residuals_b, ret)

    # Additional: Calculate correlation between A and B
    corr_ab, _ = spearmanr(feat_a, feat_b)

    # Incremental value: Partial-IC vs baseline IC
    incremental_ic = (
        partial_ic - ic_b if not np.isnan(partial_ic) and not np.isnan(ic_b) else np.nan
    )

    return {
        "baseline_ic": float(ic_b) if not np.isnan(ic_b) else None,
        "baseline_p": float(p_b) if not np.isnan(p_b) else None,
        "partial_ic": float(partial_ic) if not np.isnan(partial_ic) else None,
        "partial_p": float(partial_p) if not np.isnan(partial_p) else None,
        "incremental_ic": float(incremental_ic) if not np.isnan(incremental_ic) else None,
        "correlation_ab": float(corr_ab) if not np.isnan(corr_ab) else None,
        "samples": int(len(feat_a)),
    }


def analyze_feature_pairs(
    features_df: pd.DataFrame,
    forward_returns: np.ndarray,
    regime_mask: np.ndarray,
) -> dict:
    """Analyze all feature pairs for Partial-IC."""
    feature_cols = [col for col in features_df.columns if col != "timestamp"]

    results = {}

    for feat_a_name in feature_cols:
        results[feat_a_name] = {}

        for feat_b_name in feature_cols:
            if feat_a_name == feat_b_name:
                continue

            # Get feature values
            feat_a = features_df[feat_a_name].values
            feat_b = features_df[feat_b_name].values

            # Align lengths and filter by regime
            min_len = min(len(feat_a), len(feat_b), len(forward_returns), len(regime_mask))
            feat_a = feat_a[:min_len][regime_mask[:min_len]]
            feat_b = feat_b[:min_len][regime_mask[:min_len]]
            ret = forward_returns[:min_len][regime_mask[:min_len]]

            # Calculate Partial-IC
            partial_result = calculate_partial_ic(feat_a, feat_b, ret)

            if partial_result:
                results[feat_a_name][feat_b_name] = partial_result

    return results


def find_best_feature_set(partial_ic_results: dict, max_features: int = 7) -> list:
    """
    Find best non-redundant feature set using greedy selection.

    Strategy:
    1. Start with feature with highest individual IC
    2. Add features that maximize Partial-IC (after controlling for already selected)
    3. Stop at max_features or when Partial-IC < threshold
    """
    # Get individual ICs (baseline)
    individual_ics = {}
    for feat_a, pairs in partial_ic_results.items():
        # Use any pair to get baseline_ic (should be same for all)
        for _feat_b, stats in pairs.items():
            if stats.get("baseline_ic"):
                individual_ics[feat_a] = stats["baseline_ic"]
                break

    # Sort by IC
    sorted_features = sorted(individual_ics.items(), key=lambda x: x[1], reverse=True)

    # Greedy selection
    selected = []

    for feat, ic in sorted_features:
        if len(selected) == 0:
            # First feature: highest IC
            selected.append(
                {
                    "feature": feat,
                    "baseline_ic": ic,
                    "partial_ic": ic,  # First feature has no conditioning
                    "incremental_value": ic,
                }
            )
        elif len(selected) < max_features:
            # Check Partial-IC after controlling for already selected features
            # For simplicity, use Partial-IC after conditioning on first selected feature
            # (More sophisticated: chain conditioning)
            base_feature = selected[0]["feature"]

            if feat in partial_ic_results[base_feature]:
                stats = partial_ic_results[base_feature][feat]
                partial_ic = stats.get("partial_ic", 0)

                # Only add if Partial-IC > 0.02 (meaningful contribution)
                if partial_ic and partial_ic > 0.02:
                    selected.append(
                        {
                            "feature": feat,
                            "baseline_ic": ic,
                            "partial_ic": partial_ic,
                            "incremental_value": partial_ic - ic if ic else partial_ic,
                            "conditioned_on": base_feature,
                        }
                    )

    return selected


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Partial-IC analysis")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument("--regime", default="HighVol", help="Target regime")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    parser.add_argument("--max-features", type=int, default=7, help="Max features in optimal set")
    parser.add_argument("--output", help="Output JSON path")

    args = parser.parse_args()

    try:
        print("\n" + "=" * 80)
        print("PARTIAL-IC ANALYSIS")
        print("=" * 80)
        print(f"Symbol:       {args.symbol}")
        print(f"Timeframe:    {args.timeframe}")
        print(f"Regime:       {args.regime}")
        print(f"Horizon:      {args.horizon} bars")
        print(f"Max Features: {args.max_features}")

        # Load data
        print("\n[LOAD] Loading features...")
        features_df = load_features(args.symbol, args.timeframe)

        candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
        candles_df = pd.read_parquet(candles_path)

        # Calculate forward returns
        print("[RETURNS] Calculating forward returns...")
        forward_returns = calculate_forward_returns(candles_df["close"], args.horizon)

        # Classify regime
        print(f"[REGIME] Classifying {args.regime} regime...")
        returns = candles_df["close"].pct_change()
        regime = classify_volatility_regime(returns, window=50)
        regime_mask = (regime == args.regime).values

        print(f"[REGIME] {args.regime} samples: {regime_mask.sum():,}/{len(regime_mask):,}")

        # Analyze feature pairs
        print("\n[ANALYZE] Calculating Partial-IC for all feature pairs...")
        feature_cols = [col for col in features_df.columns if col != "timestamp"]
        total_pairs = len(feature_cols) * (len(feature_cols) - 1)
        print(f"[ANALYZE] Testing {total_pairs} feature pairs...")

        partial_ic_results = analyze_feature_pairs(features_df, forward_returns, regime_mask)

        # Find best feature set
        print(f"\n[OPTIMIZE] Finding best {args.max_features}-feature set...")
        best_set = find_best_feature_set(partial_ic_results, args.max_features)

        # Print results
        print("\n" + "=" * 80)
        print("OPTIMAL FEATURE SET")
        print("=" * 80)

        for rank, feat_info in enumerate(best_set, 1):
            print(f"\n{rank}. {feat_info['feature']}")
            print(f"   Baseline IC:  {feat_info['baseline_ic']:+.4f}")
            print(f"   Partial-IC:   {feat_info['partial_ic']:+.4f}")
            if "conditioned_on" in feat_info:
                print(f"   After controlling for: {feat_info['conditioned_on']}")
                print(f"   Incremental value: {feat_info.get('incremental_value', 0):+.4f}")

        # Show redundancy matrix
        print("\n" + "=" * 80)
        print("FEATURE REDUNDANCY MATRIX (correlation)")
        print("=" * 80)

        selected_features = [f["feature"] for f in best_set]

        print(f"\n{'':<30}", end="")
        for feat in selected_features[:5]:  # Show first 5
            print(f" | {feat[:8]:<8}", end="")
        print()
        print("-" * 80)

        for feat_a in selected_features[:5]:
            print(f"{feat_a:<30}", end="")
            for feat_b in selected_features[:5]:
                if feat_a == feat_b:
                    corr_str = "1.000"
                elif feat_b in partial_ic_results.get(feat_a, {}):
                    corr = partial_ic_results[feat_a][feat_b].get("correlation_ab", 0)
                    corr_str = f"{corr:+.3f}" if corr else "N/A"
                else:
                    corr_str = "N/A"
                print(f" | {corr_str:>8}", end="")
            print()

        # Summary statistics
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        total_ic = sum(f["partial_ic"] for f in best_set)
        avg_correlation = []

        for i, feat_i in enumerate(selected_features):
            for feat_j in selected_features[i + 1 :]:
                if feat_j in partial_ic_results.get(feat_i, {}):
                    corr = partial_ic_results[feat_i][feat_j].get("correlation_ab")
                    if corr is not None:
                        avg_correlation.append(abs(corr))

        avg_corr = np.mean(avg_correlation) if avg_correlation else 0

        print(f"\nSelected features:      {len(best_set)}")
        print(f"Total IC (sum):         {total_ic:+.4f}")
        print(f"Average IC per feature: {total_ic/len(best_set):+.4f}")
        print(f"Avg |correlation|:      {avg_corr:.3f}")

        if avg_corr < 0.5:
            print("\n[OK] LOW REDUNDANCY - Features are complementary!")
        elif avg_corr < 0.7:
            print("\n[WARNING] MODERATE REDUNDANCY - Some overlap exists")
        else:
            print("\n[ALERT] HIGH REDUNDANCY - Features are highly correlated!")

        # Save results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            output = {
                "symbol": args.symbol,
                "timeframe": args.timeframe,
                "regime": args.regime,
                "horizon": args.horizon,
                "max_features": args.max_features,
                "optimal_set": best_set,
                "partial_ic_matrix": partial_ic_results,
                "summary": {
                    "total_ic": float(total_ic),
                    "avg_ic": float(total_ic / len(best_set)),
                    "avg_correlation": float(avg_corr),
                },
            }

            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)

            print(f"\n[SAVED] {output_path}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Partial-IC analysis complete!")
        print("=" * 80 + "\n")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
