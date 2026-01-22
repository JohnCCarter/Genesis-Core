"""
Analyze model performance across different market regimes.

Evaluates if the model works better in bull/bear/ranging markets.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.ml.label_cache import load_cached_labels
from core.ml.labeling import align_features_with_labels
from core.strategy.regime import detect_regime_from_candles
from core.utils import get_candles_path


def load_model(model_path: Path) -> dict:
    """Load trained model."""
    with open(model_path) as f:
        return json.load(f)


def calculate_probabilities(X: np.ndarray, model: dict, side: str) -> np.ndarray:
    """Calculate probabilities from logistic regression weights."""
    weights = np.array(model[side]["w"])
    intercept = model[side]["b"]

    z = X @ weights + intercept
    proba = 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    return proba


def main():
    parser = argparse.ArgumentParser(description="Analyze model performance by regime")
    parser.add_argument("--model", type=str, required=True, help="Path to model JSON")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe")
    parser.add_argument("--k-profit", type=float, default=1.0, help="Profit multiplier for labels")
    parser.add_argument("--k-stop", type=float, default=0.6, help="Stop multiplier for labels")
    parser.add_argument("--max-holding", type=int, default=36, help="Max holding bars")

    args = parser.parse_args()

    print("=" * 80)
    print("REGIME-AWARE PERFORMANCE ANALYSIS")
    print("=" * 80)

    # Load model
    print(f"\n[LOAD] Model: {args.model}")
    model = load_model(Path(args.model))

    # Load features with smart format selection (Feather > Parquet)
    from core.utils.data_loader import load_features

    features_df = load_features(args.symbol, args.timeframe)
    print(f"[LOAD] Features: {len(features_df)} samples")

    # Load candles for regime detection
    try:
        candles_path = get_candles_path(args.symbol, args.timeframe)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1

    candles_df = pd.read_parquet(candles_path)

    # Detect regime for each bar
    print("\n[REGIME] Detecting market regimes...")
    regimes = []
    for i in range(len(candles_df)):
        # Need enough history for regime detection
        if i < 100:
            regimes.append("unknown")
            continue

        candles_window = {
            "open": candles_df["open"].iloc[: i + 1].tolist(),
            "high": candles_df["high"].iloc[: i + 1].tolist(),
            "low": candles_df["low"].iloc[: i + 1].tolist(),
            "close": candles_df["close"].iloc[: i + 1].tolist(),
            "volume": candles_df["volume"].iloc[: i + 1].tolist(),
        }

        regime = detect_regime_from_candles(candles_window)
        regimes.append(regime)

    candles_df["regime"] = regimes

    # Regime distribution
    regime_counts = candles_df["regime"].value_counts()
    print("\n[REGIME] Distribution:")
    for regime, count in regime_counts.items():
        pct = 100 * count / len(candles_df)
        print(f"  {regime:10s}: {count:4d} bars ({pct:5.1f}%)")

    # Load labels
    print("\n[LABELS] Loading from cache...")
    labels = load_cached_labels(
        args.symbol,
        args.timeframe,
        k_profit=args.k_profit,
        k_stop=args.k_stop,
        max_holding=args.max_holding,
        atr_period=14,
        version="v2",
    )

    if labels is None:
        print("[ERROR] Labels not found in cache. Run training first.")
        sys.exit(1)

    # Align
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)
    aligned_features = features_df.iloc[start_idx:end_idx]
    aligned_labels = labels[start_idx:end_idx]
    aligned_regimes = candles_df["regime"].iloc[start_idx:end_idx].values

    # Remove timestamp
    feature_cols = model["schema"]
    X = aligned_features[feature_cols].values

    # Filter None labels
    valid_mask = np.array([label is not None for label in aligned_labels])
    X = X[valid_mask]
    y_true = np.array([int(label) for label in aligned_labels if label is not None])
    regimes_valid = aligned_regimes[valid_mask]

    # Split train/val/test (same as training: 60/20/20)
    n = len(X)
    int(n * 0.6)
    val_end = int(n * 0.8)

    X_test = X[val_end:]
    y_test = y_true[val_end:]
    regimes_test = regimes_valid[val_end:]

    print(f"\n[SPLIT] Test set: {len(X_test)} samples")

    # Calculate predictions
    print("\n[PREDICT] Calculating probabilities...")
    proba_buy = calculate_probabilities(X_test, model, "buy")

    # Overall performance
    overall_auc = roc_auc_score(y_test, proba_buy)
    overall_acc = accuracy_score(y_test, (proba_buy > 0.5).astype(int))

    print("\n" + "=" * 80)
    print("OVERALL PERFORMANCE (Test Set)")
    print("=" * 80)
    print(f"AUC:      {overall_auc:.4f}")
    print(f"Accuracy: {overall_acc:.4f}")
    print(f"Samples:  {len(y_test)}")

    # Per-regime performance
    print("\n" + "=" * 80)
    print("PERFORMANCE BY REGIME")
    print("=" * 80)

    results = []

    for regime_type in ["bull", "bear", "ranging", "balanced"]:
        mask = regimes_test == regime_type
        n_samples = mask.sum()

        if n_samples < 30:
            print(f"\n{regime_type.upper():10s}: SKIPPED (only {n_samples} samples)")
            continue

        y_regime = y_test[mask]
        proba_regime = proba_buy[mask]

        # Calculate metrics
        try:
            auc = roc_auc_score(y_regime, proba_regime)
        except Exception:
            auc = 0.5  # Single class

        acc = accuracy_score(y_regime, (proba_regime > 0.5).astype(int))

        # Class distribution
        profit_rate = y_regime.mean()
        loss_rate = 1 - profit_rate

        print(f"\n{regime_type.upper():10s}:")
        print(f"  Samples:      {n_samples:4d} ({100*n_samples/len(y_test):5.1f}%)")
        print(f"  AUC:          {auc:.4f}")
        print(f"  Accuracy:     {acc:.4f}")
        print(f"  Profit rate:  {profit_rate:.1%}")
        print(f"  Loss rate:    {loss_rate:.1%}")

        # Performance vs overall
        delta_auc = auc - overall_auc
        status = "STRONG" if delta_auc > 0.05 else "WEAK" if delta_auc < -0.05 else "NORMAL"
        print(f"  vs Overall:   {delta_auc:+.4f} ({status})")

        results.append(
            {
                "regime": regime_type,
                "samples": n_samples,
                "auc": auc,
                "accuracy": acc,
                "profit_rate": profit_rate,
                "delta_auc": delta_auc,
            }
        )

    # Save results
    results_df = pd.DataFrame(results)
    output_path = Path("results/regime_analysis.csv")
    output_path.parent.mkdir(exist_ok=True, parents=True)
    results_df.to_csv(output_path, index=False)

    print("\n" + "=" * 80)
    print("INSIGHTS")
    print("=" * 80)

    if len(results) > 0:
        best_regime = results_df.loc[results_df["auc"].idxmax()]
        worst_regime = results_df.loc[results_df["auc"].idxmin()]

        print(f"\nBest regime:  {best_regime['regime'].upper()} (AUC {best_regime['auc']:.4f})")
        print(f"Worst regime: {worst_regime['regime'].upper()} (AUC {worst_regime['auc']:.4f})")
        print(f"Spread:       {best_regime['auc'] - worst_regime['auc']:.4f}")

        if best_regime["auc"] - worst_regime["auc"] > 0.10:
            print("\n[RECOMMENDATION] Large regime variance detected!")
            print("  Consider:")
            print("  1. Train regime-specific models")
            print("  2. Add regime as a feature")
            print("  3. Filter out weak regimes (only trade in best regime)")
        elif overall_auc < 0.52:
            print("\n[RECOMMENDATION] Low overall AUC across all regimes.")
            print("  Model has weak edge. Consider:")
            print("  1. More features (expand to 5-7)")
            print("  2. Different features (price action, patterns)")
            print("  3. Different strategy (mean-reversion vs momentum)")
        else:
            print("\n[RECOMMENDATION] Model shows consistent edge across regimes.")
            print("  Ready for deployment with confidence filtering.")

    print(f"\n[SUCCESS] Results saved to {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
