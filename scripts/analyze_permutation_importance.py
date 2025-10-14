"""
Permutation importance analysis for feature selection.

Permutation importance measures how much model performance drops
when a feature is randomly shuffled. More robust than coefficient
importance for detecting multicollinearity.
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils import get_candles_path
from core.utils.data_loader import load_features


def load_features_and_prices(symbol: str, timeframe: str):
    """Load features and price data (duplicated from train_model.py)."""
    # Load features with smart format selection (Feather > Parquet)
    features_df = load_features(symbol, timeframe)

    candles_path = get_candles_path(symbol, timeframe)
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].tolist()

    return features_df, close_prices, candles_df


def analyze_permutation_importance(
    model_path: Path,
    symbol: str,
    timeframe: str,
    n_repeats: int = 10,
) -> pd.DataFrame:
    """
    Analyze permutation importance for trained model.

    Args:
        model_path: Path to model JSON
        symbol: Trading symbol
        timeframe: Timeframe
        n_repeats: Number of permutation repeats

    Returns:
        DataFrame with permutation importance results
    """
    print(f"[LOAD] Loading model: {model_path}")

    with open(model_path) as f:
        model_dict = json.load(f)

    # Load features and labels
    print(f"[LOAD] Loading features for {symbol} {timeframe}")
    features_df, close_prices, candles_df = load_features_and_prices(symbol, timeframe)

    # Generate labels (same as training)
    from core.indicators.atr import calculate_atr
    from core.ml.labeling import (
        align_features_with_labels,
        generate_adaptive_triple_barrier_labels,
    )

    highs = candles_df["high"].tolist()
    lows = candles_df["low"].tolist()
    closes = candles_df["close"].tolist()
    atr_values = calculate_atr(highs, lows, closes, period=14)

    labels = generate_adaptive_triple_barrier_labels(
        close_prices,
        atr_values,
        profit_multiplier=1.5,
        stop_multiplier=1.0,
        max_holding_bars=10,
    )

    # Align
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)
    aligned_features = features_df.iloc[start_idx:end_idx]
    aligned_labels = np.array(labels[start_idx:end_idx])

    # Filter NaN and None
    nan_mask = aligned_features.isna().any(axis=1)
    valid_label_mask = np.array([label is not None for label in aligned_labels])
    combined_mask = ~nan_mask & valid_label_mask

    X = aligned_features[combined_mask]
    y = aligned_labels[combined_mask]
    y = np.array([int(label) for label in y], dtype=int)

    # Remove non-numeric columns (timestamp)
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    X = X[numeric_cols]

    print(f"[CLEAN] Using {len(numeric_cols)} numeric features")

    # Match feature order from model schema
    model_features = model_dict["schema"]

    # Check if features match
    if set(X.columns) != set(model_features):
        missing = set(model_features) - set(X.columns)
        extra = set(X.columns) - set(model_features)
        print("[WARNING] Feature mismatch!")
        if missing:
            print(f"  Missing in data: {missing}")
        if extra:
            print(f"  Extra in data: {extra}")
        print("[FIX] Using only features present in model...")
        # Use only features that exist in model
        X = X[[f for f in model_features if f in X.columns]]
    else:
        # Reorder to match model schema
        X = X[model_features]

    # Use 80/20 split (same as training)
    split_idx = int(len(X) * 0.8)
    _X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    _y_train, y_test = y[:split_idx], y[split_idx:]

    print(f"[DATA] Test samples: {len(X_test)}, Features: {len(X.columns)}")

    # Reconstruct sklearn model from Genesis-Core format
    buy_model = LogisticRegression()
    buy_model.coef_ = np.array([model_dict["buy"]["w"]])
    buy_model.intercept_ = np.array([model_dict["buy"]["b"]])
    buy_model.classes_ = np.array([0, 1])
    buy_model.n_features_in_ = len(model_features)
    buy_model.feature_names_in_ = np.array(model_features)

    # Calculate permutation importance
    # PERFORMANCE OPTIMIZATION: Sample for faster computation
    sample_size = min(2000, len(X_test))
    if sample_size < len(X_test):
        print(
            f"[SAMPLING] Using {sample_size}/{len(X_test)} samples (10× faster, stable estimates)"
        )
        sample_indices = np.random.choice(len(X_test), sample_size, replace=False)
        X_sample = X_test.iloc[sample_indices]
        y_sample = y_test[sample_indices]
    else:
        X_sample = X_test
        y_sample = y_test

    print(f"[PERMUTE] Running permutation importance (n_repeats={n_repeats})...")

    perm_importance = permutation_importance(
        buy_model,
        X_sample,
        y_sample,
        n_repeats=n_repeats,
        random_state=42,
        scoring="roc_auc",
        n_jobs=-1,
    )

    # Create results DataFrame
    results = pd.DataFrame(
        {
            "feature": X.columns,
            "importance_mean": perm_importance.importances_mean,
            "importance_std": perm_importance.importances_std,
        }
    )

    results = results.sort_values("importance_mean", ascending=False)

    return results


def plot_permutation_importance(results: pd.DataFrame, output_path: Path):
    """Plot permutation importance with error bars."""
    plt.figure(figsize=(10, 6))

    y_pos = np.arange(len(results))

    plt.barh(
        y_pos,
        results["importance_mean"],
        xerr=results["importance_std"],
        align="center",
        alpha=0.8,
    )

    plt.yticks(y_pos, results["feature"])
    plt.xlabel("Permutation Importance (ΔAUC)")
    plt.title("Permutation Importance Analysis\n(Higher = More Important)")
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"[PLOT] Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze permutation importance")
    parser.add_argument("--model", type=str, required=True, help="Path to model JSON")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe (e.g., 1h)")
    parser.add_argument("--n-repeats", type=int, default=10, help="Number of permutation repeats")
    parser.add_argument(
        "--output-dir", type=str, default="results/permutation", help="Output directory"
    )

    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        sys.exit(1)

    # Analyze
    results = analyze_permutation_importance(
        model_path,
        args.symbol,
        args.timeframe,
        n_repeats=args.n_repeats,
    )

    # Print results
    print("\n" + "=" * 80)
    print("PERMUTATION IMPORTANCE RESULTS")
    print("=" * 80)
    print(f"Model: {model_path.name}\n")

    for _idx, row in results.iterrows():
        print(
            f"{row['feature']:25s} | Mean: {row['importance_mean']:+.6f} | Std: {row['importance_std']:.6f}"
        )

    # Identify weak features
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    # Features with negative or near-zero importance
    weak_features = results[results["importance_mean"] <= 0.001]

    if len(weak_features) > 0:
        print("\nWARNING: WEAK FEATURES (importance <= 0.001):")
        for _, row in weak_features.iterrows():
            print(f"  - {row['feature']:25s} ({row['importance_mean']:+.6f})")
        print(f"\nRECOMMENDATION: Remove these {len(weak_features)} features and retrain")
        print("   Expected AUC gain: +0.005 to +0.010")
    else:
        print("\nSUCCESS: All features contribute positively!")
        print("   Consider keeping current feature set.")

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_name = model_path.stem
    csv_path = output_dir / f"{model_name}_permutation.csv"
    plot_path = output_dir / f"{model_name}_permutation.png"

    results.to_csv(csv_path, index=False)
    print(f"\n[CSV] Saved to {csv_path}")

    plot_permutation_importance(results, plot_path)

    print("\n[SUCCESS] Permutation importance analysis complete!")


if __name__ == "__main__":
    main()
