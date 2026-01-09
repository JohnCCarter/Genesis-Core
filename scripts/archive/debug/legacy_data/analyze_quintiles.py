"""
Quintile Analysis for model predictions.

Quintile analysis sorts predictions into 5 buckets (quintiles) and compares
average returns. Industry standard for evaluating predictive power.

Q5 = Top 20% predictions (should have highest returns)
Q1 = Bottom 20% predictions (should have lowest returns)
Q5-Q1 spread = Direct measure of predictive edge

Usage:
    # Test model predictions
    python scripts/analyze_quintiles.py \
      --model results/models/tBTCUSD_1h_v11_robust.json \
      --symbol tBTCUSD --timeframe 1h

    # Test individual features
    python scripts/analyze_quintiles.py \
      --symbol tBTCUSD --timeframe 1h \
      --test-features
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils.data_loader import load_features


def calculate_forward_returns(close_prices, horizon=10):
    """Calculate forward returns."""
    returns = []
    for i in range(len(close_prices) - horizon):
        ret = (close_prices[i + horizon] - close_prices[i]) / close_prices[i]
        returns.append(ret)

    # Pad with None
    returns.extend([None] * horizon)
    return returns


def quintile_analysis(predictions, returns):
    """
    Perform quintile analysis on predictions vs returns.

    Args:
        predictions: Array of predictions or feature values
        returns: Array of forward returns

    Returns:
        Dict with quintile metrics
    """
    # Remove None values
    valid_mask = np.array([r is not None for r in returns])
    valid_mask &= ~np.isnan(predictions)

    pred_valid = np.array(predictions)[valid_mask]
    ret_valid = np.array([r for r in returns if r is not None])[: len(pred_valid)]

    if len(pred_valid) < 100:
        return {"status": "INSUFFICIENT_DATA", "n_samples": len(pred_valid)}

    # Sort by predictions
    sorted_indices = np.argsort(pred_valid)
    sorted_returns = ret_valid[sorted_indices]

    # Split into quintiles
    n = len(sorted_returns)
    quintile_size = n // 5

    quintiles = {}
    for i in range(5):
        start = i * quintile_size
        end = (i + 1) * quintile_size if i < 4 else n

        q_returns = sorted_returns[start:end]

        quintiles[f"Q{i+1}"] = {
            "mean_return": float(np.mean(q_returns)),
            "median_return": float(np.median(q_returns)),
            "std_return": float(np.std(q_returns)),
            "n_samples": int(len(q_returns)),
            "pct_positive": float((q_returns > 0).mean() * 100),
        }

    # Calculate spreads
    q5_mean = quintiles["Q5"]["mean_return"]
    q1_mean = quintiles["Q1"]["mean_return"]
    spread = q5_mean - q1_mean

    # Monotonicity check (Q5 > Q4 > Q3 > Q2 > Q1)
    means = [quintiles[f"Q{i+1}"]["mean_return"] for i in range(5)]
    is_monotonic = all(means[i] >= means[i - 1] for i in range(1, 5))

    # Rank correlation (Spearman-like, but simpler)
    # Perfect would be 1.0, worst would be -1.0
    expected_ranks = [1, 2, 3, 4, 5]
    actual_ranks = np.argsort(np.argsort(means)) + 1
    rank_corr = np.corrcoef(expected_ranks, actual_ranks)[0, 1]

    # Statistical test: Is Q5 significantly different from Q1?
    from scipy.stats import ttest_ind

    q5_returns = sorted_returns[4 * quintile_size :]
    q1_returns = sorted_returns[:quintile_size]
    t_stat, p_value = ttest_ind(q5_returns, q1_returns)

    return {
        "quintiles": quintiles,
        "spread": {
            "q5_minus_q1": float(spread),
            "q5_minus_q1_annualized": float(spread * 252),  # Assuming daily-like
            "statistical_significance": {
                "t_stat": float(t_stat),
                "p_value": float(p_value),
                "significant": bool(p_value < 0.05),
            },
        },
        "monotonicity": {"is_monotonic": bool(is_monotonic), "rank_correlation": float(rank_corr)},
        "status": "OK",
        "n_samples": int(n),
    }


def test_model_predictions(model_path, symbol, timeframe, horizon=10):
    """Test quintile analysis on model predictions."""
    print(f"[LOAD] Loading model: {model_path}")
    with open(model_path) as f:
        model_json = json.load(f)

    print(f"[LOAD] Loading features for {symbol} {timeframe}")
    features_df = load_features(symbol, timeframe)

    # Load candles for returns
    candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].values

    # Get features
    feature_cols = model_json["schema"]
    X = features_df[feature_cols].values

    # Remove NaN
    nan_mask = ~np.isnan(X).any(axis=1)
    X = X[nan_mask]
    close_prices_aligned = close_prices[nan_mask]

    # Recreate model
    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression()
    model.coef_ = np.array([model_json["buy"]["w"]])
    model.intercept_ = np.array([model_json["buy"]["b"]])
    model.classes_ = np.array([0, 1])

    # Get predictions
    predictions = model.predict_proba(X)[:, 1]

    # Calculate returns
    forward_returns = calculate_forward_returns(close_prices_aligned, horizon)

    # Adjust for length
    min_len = min(len(predictions), len(forward_returns))
    predictions = predictions[:min_len]
    forward_returns = forward_returns[:min_len]

    print(f"[QUINTILE] Analyzing {min_len} samples...")
    results = quintile_analysis(predictions, forward_returns)

    return results


def test_individual_features(symbol, timeframe, horizon=10):
    """Test quintile analysis on individual features."""
    print(f"[LOAD] Loading features for {symbol} {timeframe}")
    features_df = load_features(symbol, timeframe)

    # Load candles
    candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].values

    feature_cols = [c for c in features_df.columns if c != "timestamp"]

    print(f"[QUINTILE] Testing {len(feature_cols)} features...")
    results = {}

    for feature in feature_cols:
        feature_values = features_df[feature].values

        # Remove NaN
        nan_mask = ~np.isnan(feature_values)
        feature_valid = feature_values[nan_mask]
        close_valid = close_prices[nan_mask]

        # Calculate returns
        forward_returns = calculate_forward_returns(close_valid, horizon)

        # Adjust for length
        min_len = min(len(feature_valid), len(forward_returns))
        feature_valid = feature_valid[:min_len]
        forward_returns = forward_returns[:min_len]

        # Analyze
        result = quintile_analysis(feature_valid, forward_returns)
        results[feature] = result

    return results


def plot_quintile_returns(quintile_data, title, output_path):
    """Plot quintile returns as bar chart."""
    quintiles = quintile_data["quintiles"]

    labels = [f"Q{i+1}" for i in range(5)]
    means = [quintiles[f"Q{i+1}"]["mean_return"] * 100 for i in range(5)]  # Convert to %
    stds = [quintiles[f"Q{i+1}"]["std_return"] * 100 for i in range(5)]

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["red" if m < 0 else "green" for m in means]
    bars = ax.bar(labels, means, yerr=stds, capsize=5, color=colors, alpha=0.7, edgecolor="black")

    ax.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax.set_xlabel("Quintile (Q1=lowest predictions, Q5=highest predictions)")
    ax.set_ylabel("Mean Forward Return (%)")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.2f}%",
            ha="center",
            va="bottom" if height > 0 else "top",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Quintile analysis for model predictions")
    parser.add_argument("--model", type=str, help="Path to model JSON")
    parser.add_argument("--symbol", required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", required=True, help="Timeframe (e.g., 1h)")
    parser.add_argument(
        "--horizon", type=int, default=10, help="Forward return horizon in bars (default: 10)"
    )
    parser.add_argument(
        "--test-features", action="store_true", help="Test individual features instead of model"
    )
    parser.add_argument("--output", default="results/quintile_analysis", help="Output directory")

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("QUINTILE ANALYSIS")
    print("=" * 80)
    print(f"Forward horizon: {args.horizon} bars")

    if args.test_features:
        # Test individual features
        results = test_individual_features(args.symbol, args.timeframe, args.horizon)

        print("\n" + "=" * 80)
        print("FEATURE QUINTILE RANKING")
        print("=" * 80)

        # Rank features by Q5-Q1 spread
        feature_spreads = []
        for feature, data in results.items():
            if data["status"] != "OK":
                continue
            spread = data["spread"]["q5_minus_q1"]
            is_monotonic = data["monotonicity"]["is_monotonic"]
            is_significant = data["spread"]["statistical_significance"]["significant"]
            feature_spreads.append((feature, spread, is_monotonic, is_significant))

        # Sort by absolute spread
        feature_spreads.sort(key=lambda x: abs(x[1]), reverse=True)

        print("\nFeatures ranked by Q5-Q1 spread:\n")
        for i, (feature, spread, monotonic, significant) in enumerate(feature_spreads, 1):
            mono_mark = "[MONO]" if monotonic else "[----]"
            sig_mark = "[SIG]" if significant else "[---]"
            print(f"{i:2d}. {feature:25s} | Spread: {spread*100:+6.2f}% | {mono_mark} {sig_mark}")

        # Detailed breakdown for top feature
        if len(feature_spreads) > 0:
            top_feature = feature_spreads[0][0]
            print("\n" + "=" * 80)
            print(f"DETAILED BREAKDOWN: {top_feature}")
            print("=" * 80)

            data = results[top_feature]
            quintiles = data["quintiles"]

            print("\nQuintile Returns:")
            for i in range(5):
                q = quintiles[f"Q{i+1}"]
                print(
                    f"  Q{i+1}: {q['mean_return']*100:+6.2f}% ± {q['std_return']*100:5.2f}% "
                    f"(n={q['n_samples']}, {q['pct_positive']:.1f}% positive)"
                )

            print(f"\nQ5-Q1 Spread: {data['spread']['q5_minus_q1']*100:+.2f}%")
            print(f"Monotonic: {data['monotonicity']['is_monotonic']}")
            print(f"Rank Correlation: {data['monotonicity']['rank_correlation']:.3f}")
            print(
                f"Statistical Significance: p={data['spread']['statistical_significance']['p_value']:.4f}"
            )

            # Plot
            plot_path = output_dir / f"{args.symbol}_{args.timeframe}_{top_feature}_quintiles.png"
            plot_quintile_returns(
                data, f"{top_feature} Quintile Returns ({args.symbol} {args.timeframe})", plot_path
            )
            print(f"\n[PLOT] {plot_path}")

        # Save detailed results
        output_path = output_dir / f"{args.symbol}_{args.timeframe}_feature_quintiles.json"

        # Remove large arrays for JSON
        results_clean = {}
        for feature, data in results.items():
            if data["status"] == "OK":
                results_clean[feature] = data

        with open(output_path, "w") as f:
            json.dump(results_clean, f, indent=2)

        print(f"\n[SAVED] {output_path}")

    else:
        # Test model predictions
        if not args.model:
            print("Error: --model required when not using --test-features")
            sys.exit(1)

        results = test_model_predictions(
            Path(args.model), args.symbol, args.timeframe, args.horizon
        )

        if results["status"] != "OK":
            print(f"\n[ERROR] {results['status']}")
            sys.exit(1)

        print("\n" + "=" * 80)
        print("MODEL QUINTILE ANALYSIS")
        print("=" * 80)

        quintiles = results["quintiles"]

        print(f"\nQuintile Returns ({args.horizon}-bar forward):\n")
        for i in range(5):
            q = quintiles[f"Q{i+1}"]
            print(
                f"  Q{i+1}: {q['mean_return']*100:+6.2f}% ± {q['std_return']*100:5.2f}% "
                f"(n={q['n_samples']}, {q['pct_positive']:.1f}% positive)"
            )

        spread = results["spread"]["q5_minus_q1"]
        is_monotonic = results["monotonicity"]["is_monotonic"]
        rank_corr = results["monotonicity"]["rank_correlation"]
        p_value = results["spread"]["statistical_significance"]["p_value"]

        print("\n" + "-" * 80)
        print(f"Q5-Q1 Spread:     {spread*100:+.2f}% per {args.horizon} bars")
        print(f"Annualized:       {results['spread']['q5_minus_q1_annualized']*100:+.2f}%")
        print(f"Monotonic:        {is_monotonic}")
        print(f"Rank Correlation: {rank_corr:.3f}")
        print(f"p-value:          {p_value:.4f}")

        print("\n" + "=" * 80)
        print("ASSESSMENT")
        print("=" * 80)

        if spread > 0.005:  # 0.5% spread
            print(f"  [+] GOOD SPREAD (> 0.5% per {args.horizon} bars)")
        elif spread > 0.002:
            print("  [!] WEAK SPREAD (> 0.2%)")
        else:
            print("  [-] VERY WEAK SPREAD (< 0.2%)")

        if is_monotonic:
            print("  [+] MONOTONIC (Q5 > Q4 > Q3 > Q2 > Q1)")
        else:
            print("  [-] NOT MONOTONIC (inconsistent ranking)")

        if rank_corr > 0.9:
            print("  [+] EXCELLENT RANK CORRELATION (> 0.9)")
        elif rank_corr > 0.7:
            print("  [!] MODERATE RANK CORRELATION (> 0.7)")
        else:
            print("  [-] POOR RANK CORRELATION (< 0.7)")

        if p_value < 0.05:
            print("  [+] STATISTICALLY SIGNIFICANT (p < 0.05)")
        else:
            print("  [-] NOT SIGNIFICANT (p > 0.05)")

        # Plot
        plot_path = output_dir / f"{args.symbol}_{args.timeframe}_model_quintiles.png"
        plot_quintile_returns(
            results, f"Model Quintile Returns ({args.symbol} {args.timeframe})", plot_path
        )
        print(f"\n[PLOT] {plot_path}")

        # Save results
        output_path = output_dir / f"{args.symbol}_{args.timeframe}_model_quintiles.json"
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"[SAVED] {output_path}")

    print("\n" + "=" * 80)
    print("[SUCCESS] Quintile analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
