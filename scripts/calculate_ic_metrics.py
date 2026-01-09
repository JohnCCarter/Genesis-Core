"""
Calculate Information Coefficient (IC) metrics for model validation.

IC = Spearman correlation between predictions and forward returns
ICIR = IC Information Ratio = Mean(IC) / Std(IC)

Industry standard for quantitative trading model validation.

Usage:
    # Test model predictions
    python scripts/calculate_ic_metrics.py \
      --model results/models/tBTCUSD_1h_v11_robust.json \
      --symbol tBTCUSD --timeframe 1h

    # Test individual features
    python scripts/calculate_ic_metrics.py \
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
from scipy.stats import spearmanr

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils import get_candles_path
from core.utils.data_loader import load_features


def calculate_forward_returns(close_prices, horizons=None):
    """
    Calculate forward returns at multiple horizons.

    Args:
        close_prices: Array of close prices
        horizons: List of forward periods (bars)

    Returns:
        Dict of {horizon: returns_array}
    """
    if horizons is None:
        horizons = [1, 5, 10, 20]

    forward_returns = {}

    for h in horizons:
        returns = []
        for i in range(len(close_prices) - h):
            ret = (close_prices[i + h] - close_prices[i]) / close_prices[i]
            returns.append(ret)

        # Pad with None for last h bars
        returns.extend([None] * h)
        forward_returns[h] = returns

    return forward_returns


def calculate_ic(predictions, returns):
    """
    Calculate Information Coefficient (Spearman correlation).

    Args:
        predictions: Model predictions or feature values
        returns: Forward returns

    Returns:
        Dict with IC, t-stat, p-value
    """
    # Remove None values
    valid_mask = np.array([r is not None for r in returns])
    valid_mask &= ~np.isnan(predictions)

    pred_valid = np.array(predictions)[valid_mask]
    ret_valid = np.array([r for r in returns if r is not None])[: len(pred_valid)]

    if len(pred_valid) < 30:
        return {
            "ic": 0.0,
            "t_stat": 0.0,
            "p_value": 1.0,
            "n_samples": len(pred_valid),
            "status": "INSUFFICIENT_DATA",
        }

    # Spearman correlation
    ic, p_value = spearmanr(pred_valid, ret_valid)

    # T-statistic
    n = len(pred_valid)
    t_stat = ic * np.sqrt(n - 2) / np.sqrt(1 - ic**2 + 1e-10)

    # Significance (t-stat > 2.0 is roughly p < 0.05)
    status = "SIGNIFICANT" if abs(t_stat) > 2.0 else "NOT_SIGNIFICANT"

    return {
        "ic": float(ic),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "n_samples": int(n),
        "status": status,
    }


def calculate_rolling_ic(predictions, returns, window=252):
    """
    Calculate rolling IC for stability analysis.

    Args:
        predictions: Model predictions
        returns: Forward returns
        window: Rolling window size (252 = 1 year for daily, adjust for timeframe)

    Returns:
        Array of rolling IC values
    """
    # Remove None values first
    valid_indices = [
        i for i, r in enumerate(returns) if r is not None and not np.isnan(predictions[i])
    ]
    pred_valid = predictions[valid_indices]
    ret_valid = [returns[i] for i in valid_indices]

    if len(pred_valid) < window + 50:
        return []

    rolling_ic = []
    for i in range(window, len(pred_valid)):
        ic = spearmanr(pred_valid[i - window : i], ret_valid[i - window : i])[0]
        rolling_ic.append(ic)

    return rolling_ic


def calculate_ic_metrics(predictions, returns, window=252):
    """
    Calculate comprehensive IC metrics.

    Returns:
        Dict with IC, ICIR, stability metrics
    """
    # Overall IC
    overall_ic = calculate_ic(predictions, returns)

    # Rolling IC
    rolling_ic = calculate_rolling_ic(predictions, returns, window)

    if len(rolling_ic) == 0:
        return {
            "overall": overall_ic,
            "icir": 0.0,
            "rolling_mean": 0.0,
            "rolling_std": 0.0,
            "worst_case": 0.0,
            "best_case": 0.0,
            "pct_positive": 0.0,
            "status": "INSUFFICIENT_DATA_FOR_ROLLING",
        }

    # ICIR = Mean(IC) / Std(IC)
    mean_ic = np.mean(rolling_ic)
    std_ic = np.std(rolling_ic)
    icir = mean_ic / (std_ic + 1e-10)

    # Stability metrics
    pct_positive = (np.array(rolling_ic) > 0).mean() * 100
    worst_case = np.min(rolling_ic)
    best_case = np.max(rolling_ic)

    return {
        "overall": overall_ic,
        "icir": float(icir),
        "rolling_mean": float(mean_ic),
        "rolling_std": float(std_ic),
        "worst_case": float(worst_case),
        "best_case": float(best_case),
        "pct_positive": float(pct_positive),
        "rolling_ic": rolling_ic,
        "status": "OK",
    }


def test_model_predictions(model_path, symbol, timeframe, horizons=None):
    """
    Test IC metrics for trained model predictions.
    """
    if horizons is None:
        horizons = [10]

    print(f"[LOAD] Loading model: {model_path}")
    with open(model_path) as f:
        model_json = json.load(f)

    print(f"[LOAD] Loading features for {symbol} {timeframe}")
    features_df = load_features(symbol, timeframe)

    # Load candles for returns
    candles_path = get_candles_path(symbol, timeframe)
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].values

    # Get feature columns
    feature_cols = model_json["schema"]
    X = features_df[feature_cols].values

    # Remove NaN rows
    nan_mask = ~np.isnan(X).any(axis=1)
    X = X[nan_mask]
    close_prices_aligned = close_prices[nan_mask]

    # Recreate model
    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression()
    model.coef_ = np.array([model_json["buy"]["w"]])
    model.intercept_ = np.array([model_json["buy"]["b"]])
    model.classes_ = np.array([0, 1])

    # Get predictions (probability of class 1)
    predictions = model.predict_proba(X)[:, 1]

    print("[IC] Calculating IC metrics...")
    results = {}

    for horizon in horizons:
        forward_returns = calculate_forward_returns(close_prices_aligned, [horizon])[horizon]

        # Adjust for length mismatch
        min_len = min(len(predictions), len(forward_returns))
        pred_adj = predictions[:min_len]
        ret_adj = forward_returns[:min_len]

        # Calculate metrics
        window = min(252, min_len // 3)  # Adjust for data size
        metrics = calculate_ic_metrics(pred_adj, ret_adj, window)

        results[f"{horizon}bar"] = metrics

    return results


def test_individual_features(symbol, timeframe, horizons=None):
    """
    Test IC metrics for each feature individually.
    """
    if horizons is None:
        horizons = [10]

    print(f"[LOAD] Loading features for {symbol} {timeframe}")
    features_df = load_features(symbol, timeframe)

    # Load candles for returns
    candles_path = get_candles_path(symbol, timeframe)
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].values

    feature_cols = [c for c in features_df.columns if c != "timestamp"]

    print(f"[IC] Testing {len(feature_cols)} features...")
    results = {}

    for feature in feature_cols:
        feature_values = features_df[feature].values

        # Remove NaN
        nan_mask = ~np.isnan(feature_values)
        feature_valid = feature_values[nan_mask]
        close_valid = close_prices[nan_mask]

        feature_results = {}

        for horizon in horizons:
            forward_returns = calculate_forward_returns(close_valid, [horizon])[horizon]

            # Adjust for length
            min_len = min(len(feature_valid), len(forward_returns))
            feat_adj = feature_valid[:min_len]
            ret_adj = forward_returns[:min_len]

            # Calculate metrics
            window = min(252, min_len // 3)
            metrics = calculate_ic_metrics(feat_adj, ret_adj, window)

            feature_results[f"{horizon}bar"] = metrics

        results[feature] = feature_results

    return results


def plot_rolling_ic(rolling_ic, title, output_path):
    """Plot rolling IC over time."""
    plt.figure(figsize=(12, 6))
    plt.plot(rolling_ic, linewidth=1, alpha=0.7)
    plt.axhline(y=0, color="black", linestyle="--", linewidth=1)
    plt.axhline(y=0.03, color="green", linestyle="--", linewidth=1, label="Target IC (0.03)")
    plt.axhline(y=-0.03, color="red", linestyle="--", linewidth=1)

    plt.title(title)
    plt.xlabel("Time Window")
    plt.ylabel("IC (Spearman Correlation)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Calculate Information Coefficient metrics")
    parser.add_argument("--model", type=str, help="Path to model JSON")
    parser.add_argument("--symbol", required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", required=True, help="Timeframe (e.g., 1h)")
    parser.add_argument(
        "--horizons",
        nargs="+",
        type=int,
        default=[10],
        help="Forward return horizons in bars (default: 10)",
    )
    parser.add_argument(
        "--test-features", action="store_true", help="Test individual features instead of model"
    )
    parser.add_argument("--window", type=int, default=252, help="Rolling window size")
    parser.add_argument("--output", default="results/ic_metrics", help="Output directory")

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("INFORMATION COEFFICIENT (IC) ANALYSIS")
    print("=" * 80)

    if args.test_features:
        # Test individual features
        results = test_individual_features(args.symbol, args.timeframe, args.horizons)

        print("\n" + "=" * 80)
        print("FEATURE IC RANKING")
        print("=" * 80)

        # Rank features by IC
        horizon_key = f"{args.horizons[0]}bar"
        feature_ics = []

        for feature, metrics in results.items():
            ic = metrics[horizon_key]["overall"]["ic"]
            t_stat = metrics[horizon_key]["overall"]["t_stat"]
            status = metrics[horizon_key]["overall"]["status"]
            feature_ics.append((feature, ic, t_stat, status))

        # Sort by absolute IC
        feature_ics.sort(key=lambda x: abs(x[1]), reverse=True)

        print(f"\nFeatures ranked by IC ({horizon_key} forward returns):\n")
        for i, (feature, ic, t_stat, status) in enumerate(feature_ics, 1):
            significance = "[SIG]" if status == "SIGNIFICANT" else "[---]"
            print(f"{i:2d}. {feature:25s} | IC: {ic:+.4f} | t-stat: {t_stat:+.2f} | {significance}")

        # Save detailed results
        output_path = output_dir / f"{args.symbol}_{args.timeframe}_feature_ic.json"
        with open(output_path, "w") as f:
            # Convert numpy arrays to lists for JSON
            results_serializable = {}
            for feature, metrics in results.items():
                results_serializable[feature] = {}
                for horizon, m in metrics.items():
                    results_serializable[feature][horizon] = {
                        k: (v.tolist() if isinstance(v, np.ndarray) else v)
                        for k, v in m.items()
                        if k != "rolling_ic"  # Skip large arrays
                    }
            json.dump(results_serializable, f, indent=2)

        print(f"\n[SAVED] Detailed results: {output_path}")

        # Plot best feature
        if len(feature_ics) > 0:
            best_feature = feature_ics[0][0]
            rolling_ic = results[best_feature][horizon_key].get("rolling_ic", [])

            if len(rolling_ic) > 0:
                plot_path = (
                    output_dir / f"{args.symbol}_{args.timeframe}_{best_feature}_rolling_ic.png"
                )
                plot_rolling_ic(
                    rolling_ic,
                    f"{best_feature} Rolling IC ({args.symbol} {args.timeframe})",
                    plot_path,
                )
                print(f"[PLOT] Rolling IC: {plot_path}")

    else:
        # Test model predictions
        if not args.model:
            print("Error: --model required when not using --test-features")
            sys.exit(1)

        results = test_model_predictions(
            Path(args.model), args.symbol, args.timeframe, args.horizons
        )

        print("\n" + "=" * 80)
        print("MODEL IC METRICS")
        print("=" * 80)

        for horizon_key, metrics in results.items():
            print(f"\n{horizon_key.upper()} Forward Returns:")
            print(f"  Overall IC:      {metrics['overall']['ic']:+.4f}")
            print(f"  t-statistic:     {metrics['overall']['t_stat']:+.2f}")
            print(f"  p-value:         {metrics['overall']['p_value']:.4f}")
            print(f"  Status:          {metrics['overall']['status']}")
            print(f"\n  ICIR:            {metrics['icir']:+.4f}")
            print(f"  Rolling mean IC: {metrics['rolling_mean']:+.4f}")
            print(f"  Rolling std IC:  {metrics['rolling_std']:.4f}")
            print(f"  Worst-case IC:   {metrics['worst_case']:+.4f}")
            print(f"  Best-case IC:    {metrics['best_case']:+.4f}")
            print(f"  % Positive:      {metrics['pct_positive']:.1f}%")

            # Assessment
            ic = metrics["overall"]["ic"]
            icir = metrics["icir"]

            print("\n  ASSESSMENT:")
            if ic > 0.05:
                print("    [+] EXCELLENT IC (> 0.05)")
            elif ic > 0.03:
                print("    [+] GOOD IC (> 0.03)")
            elif ic > 0.01:
                print("    [!] WEAK IC (> 0.01)")
            else:
                print("    [-] VERY WEAK IC (< 0.01)")

            if icir > 1.0:
                print("    [+] EXCELLENT ICIR (> 1.0)")
            elif icir > 0.5:
                print("    [+] GOOD ICIR (> 0.5)")
            else:
                print("    [-] POOR ICIR (< 0.5)")

        # Save results
        output_path = output_dir / f"{args.symbol}_{args.timeframe}_model_ic.json"

        # Convert for JSON serialization
        results_serializable = {}
        for horizon, metrics in results.items():
            results_serializable[horizon] = {
                k: (v.tolist() if isinstance(v, np.ndarray) else v)
                for k, v in metrics.items()
                if k != "rolling_ic"
            }

        with open(output_path, "w") as f:
            json.dump(results_serializable, f, indent=2)

        print(f"\n[SAVED] {output_path}")

        # Plot rolling IC
        horizon_key = list(results.keys())[0]
        rolling_ic = results[horizon_key].get("rolling_ic", [])

        if len(rolling_ic) > 0:
            plot_path = output_dir / f"{args.symbol}_{args.timeframe}_model_rolling_ic.png"
            plot_rolling_ic(
                rolling_ic, f"Model Rolling IC ({args.symbol} {args.timeframe})", plot_path
            )
            print(f"[PLOT] {plot_path}")

    print("\n" + "=" * 80)
    print("[SUCCESS] IC analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
