"""
Purged Walk-Forward Cross-Validation med embargo period.

Eliminerar data leakage genom:
- Embargo period mellan train och test
- Purging av overlappande samples
- Temporal splits med korrekt separation

Usage:
    python scripts/validate_purged_wfcv.py --symbol tBTCUSD --timeframe 1h
    python scripts/validate_purged_wfcv.py --symbol tBTCUSD --timeframe 1h --n-splits 6
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score

from core.ml.labeling import align_features_with_labels, generate_labels
from core.utils.data_loader import load_features


def create_purged_splits(
    n_samples: int, n_splits: int = 5, train_ratio: float = 0.6, embargo_pct: float = 0.02
):
    """
    Purged Walk-Forward CV med embargo period.

    Args:
        n_samples: Total samples
        n_splits: Number of splits
        train_ratio: Training window size
        embargo_pct: Embargo as % of total data

    Returns:
        List of dicts with train/test/embargo indices
    """
    window_size = n_samples // n_splits
    embargo_size = int(n_samples * embargo_pct)

    print(f"[PURGED WFCV] Window size: {window_size}, Embargo: {embargo_size} bars")

    splits = []
    for i in range(n_splits):
        start = i * (window_size // 2)
        end = start + window_size

        if end > n_samples:
            break

        train_size = int(window_size * train_ratio)
        train_end = start + train_size

        embargo_start = train_end
        embargo_end = train_end + embargo_size

        test_start = embargo_end
        test_end = min(end, n_samples)

        if test_start >= test_end:
            continue

        splits.append(
            {
                "train": list(range(start, train_end)),
                "test": list(range(test_start, test_end)),
                "embargo": list(range(embargo_start, embargo_end)),
                "embargo_size": embargo_size,
            }
        )

    return splits


def purge_overlapping_labels(train_indices, test_indices, label_dependency_window):
    """Purge train samples vars labels beror på test data."""
    min_test_idx = min(test_indices)
    purge_threshold = min_test_idx - label_dependency_window
    purged_train = [idx for idx in train_indices if idx < purge_threshold]

    n_purged = len(train_indices) - len(purged_train)
    if n_purged > 0:
        print(f"    [PURGE] Removed {n_purged} overlapping samples")

    return purged_train


def train_and_evaluate_split(X, y, split_info, feature_names, lookahead):
    """Träna och evaluera på en purged split."""
    purged_train = purge_overlapping_labels(split_info["train"], split_info["test"], lookahead)

    X_train = X[purged_train]
    y_train = y[purged_train]
    X_test = X[split_info["test"]]
    y_test = y[split_info["test"]]

    # Clean data
    train_valid = ~np.isnan(X_train).any(axis=1) & ~np.isnan(y_train) & (y_train != -1)
    test_valid = ~np.isnan(X_test).any(axis=1) & ~np.isnan(y_test) & (y_test != -1)

    X_train = X_train[train_valid]
    y_train = y_train[train_valid]
    X_test = X_test[test_valid]
    y_test = y_test[test_valid]

    if len(X_train) < 50 or len(X_test) < 20:
        return None

    if len(np.unique(y_train)) < 2 or len(np.unique(y_test)) < 2:
        return None

    # Train
    model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    # Evaluate
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    try:
        auc = roc_auc_score(y_test, y_pred_proba)
    except Exception:
        auc = 0.5

    return {
        "auc": auc,
        "accuracy": accuracy_score(y_test, (y_pred_proba > 0.5).astype(int)),
        "log_loss": log_loss(y_test, y_pred_proba),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_purged": len(split_info["train"]) - len(purged_train),
    }


def calculate_stability_metrics(results):
    """Beräkna stability metrics."""
    if not results:
        return None

    aucs = [r["auc"] for r in results]
    mean_auc = np.mean(aucs)
    std_auc = np.std(aucs)

    return {
        "mean_auc": mean_auc,
        "std_auc": std_auc,
        "min_auc": np.min(aucs),
        "max_auc": np.max(aucs),
        "stability_score": 1.0 - (std_auc / (mean_auc + 1e-6)),
        "worst_case_auc": np.min(aucs),
    }


def main():
    parser = argparse.ArgumentParser(description="Purged WFCV")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--embargo-pct", type=float, default=0.02)
    parser.add_argument("--lookahead", type=int, default=10)
    parser.add_argument("--output", default="results/validation")

    args = parser.parse_args()

    print("=" * 80)
    print("PURGED WALK-FORWARD CROSS-VALIDATION")
    print("=" * 80)

    # Load data
    features_df = load_features(args.symbol, args.timeframe)
    candles_path = Path("data/candles") / f"{args.symbol}_{args.timeframe}.parquet"
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].tolist()

    # Generate labels
    labels = generate_labels(close_prices, args.lookahead, threshold_pct=0.0)

    # Align
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)
    features_aligned = features_df.iloc[start_idx:end_idx]
    labels_aligned = labels[start_idx:end_idx]

    # Extract features
    feature_cols = [c for c in features_aligned.columns if c != "timestamp"]
    X = features_aligned[feature_cols].values
    y = np.array([label if label is not None else -1 for label in labels_aligned])

    # Create splits
    splits = create_purged_splits(len(X), args.n_splits, 0.6, args.embargo_pct)

    # Validate
    results = []
    for i, split in enumerate(splits, 1):
        print(f"\n[SPLIT {i}/{len(splits)}]")
        result = train_and_evaluate_split(X, y, split, feature_cols, args.lookahead)
        if result:
            print(f"  AUC: {result['auc']:.4f}, Purged: {result['n_purged']}")
            results.append(result)

    # Results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    if not results:
        print("✗ No valid results")
        sys.exit(1)

    stability = calculate_stability_metrics(results)
    print(f"\nMean AUC: {stability['mean_auc']:.4f}")
    print(f"Stability: {stability['stability_score']:.4f}")

    production_ready = stability["stability_score"] > 0.70 and stability["worst_case_auc"] > 0.60

    # Save
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.symbol}_{args.timeframe}_purged_wfcv.json"

    with open(output_path, "w") as f:
        json.dump(
            {
                "symbol": args.symbol,
                "stability_metrics": stability,
                "results": results,
                "production_ready": production_ready,
            },
            f,
            indent=2,
        )

    print(f"\n[SAVED] {output_path}")
    print(f"Production ready: {production_ready}")

    sys.exit(0 if production_ready else 1)


if __name__ == "__main__":
    main()
