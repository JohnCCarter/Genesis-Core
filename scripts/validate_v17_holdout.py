#!/usr/bin/env python3
"""
Holdout validation for features v17.
Train on 70% data, test on 30% holdout to verify out-of-sample edge.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def calculate_forward_returns(close_prices: pd.Series, horizon: int = 10) -> pd.Series:
    """Calculate forward returns for IC calculation."""
    return close_prices.pct_change(horizon).shift(-horizon)


def calculate_ic(feature_values: np.ndarray, returns: np.ndarray) -> tuple[float, float]:
    """Calculate Information Coefficient (Spearman correlation)."""
    mask = ~(np.isnan(feature_values) | np.isnan(returns) | np.isinf(feature_values))
    if mask.sum() < 30:
        return np.nan, np.nan

    ic, p_val = spearmanr(feature_values[mask], returns[mask])
    return ic, p_val


def calculate_quintile_spread(predictions: np.ndarray, returns: np.ndarray) -> float:
    """Calculate Q5-Q1 spread (mean return difference)."""
    mask = ~(np.isnan(predictions) | np.isnan(returns))
    if mask.sum() < 50:
        return np.nan

    pred_masked = predictions[mask]
    ret_masked = returns[mask]

    # Split into 5 quintiles
    quintiles = pd.qcut(pred_masked, q=5, labels=False, duplicates="drop")

    q5_returns = ret_masked[quintiles == 4]
    q1_returns = ret_masked[quintiles == 0]

    if len(q5_returns) < 5 or len(q1_returns) < 5:
        return np.nan

    return np.mean(q5_returns) - np.mean(q1_returns)


def main():
    parser = argparse.ArgumentParser(description="Holdout validation for features v17")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    parser.add_argument("--train-ratio", type=float, default=0.7, help="Train/test split")
    args = parser.parse_args()

    print("=" * 80)
    print("FEATURES V17 HOLDOUT VALIDATION")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Horizon: {args.horizon} bars")
    print(f"Train/Holdout Split: {args.train_ratio:.0%} / {(1-args.train_ratio):.0%}")
    print("=" * 80)
    print()

    # Load features v17
    features_path = Path(f"data/features/{args.symbol}_{args.timeframe}_features_v17.feather")
    if not features_path.exists():
        print(f"[ERROR] Features v17 not found: {features_path}")
        return 1

    features_df = pd.read_feather(features_path)
    print(f"[LOAD] Loaded {len(features_df):,} samples with {len(features_df.columns)-1} features")

    # Load candles for returns and labels
    candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path)

    # Calculate forward returns
    returns = calculate_forward_returns(candles_df["close"], horizon=args.horizon)

    # Create binary labels (1 = positive return, 0 = negative)
    labels = (returns > 0).astype(int)

    # Drop rows with NaN
    valid_mask = ~(features_df.isna().any(axis=1) | returns.isna() | labels.isna())
    features_clean = features_df[valid_mask].drop(columns=["timestamp"])
    returns_clean = returns[valid_mask]
    labels_clean = labels[valid_mask]

    print(f"[CLEAN] {len(features_clean):,} valid samples after NaN removal")

    # Split train/holdout
    split_idx = int(len(features_clean) * args.train_ratio)

    X_train = features_clean.iloc[:split_idx]
    y_train = labels_clean.iloc[:split_idx]
    returns_train = returns_clean.iloc[:split_idx]

    X_holdout = features_clean.iloc[split_idx:]
    y_holdout = labels_clean.iloc[split_idx:]
    returns_holdout = returns_clean.iloc[split_idx:]

    print(f"[SPLIT] Train: {len(X_train):,} samples | Holdout: {len(X_holdout):,} samples")
    print()

    # === TRAIN LOGISTIC REGRESSION MODEL ===
    print("=" * 80)
    print("TRAINING LOGISTIC REGRESSION MODEL")
    print("=" * 80)

    model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    print("[TRAINED] Logistic Regression with all 14 features")
    print()

    # === EVALUATE ON TRAIN SET ===
    print("=" * 80)
    print("TRAIN SET PERFORMANCE")
    print("=" * 80)

    train_proba = model.predict_proba(X_train)[:, 1]

    train_ic, train_p = calculate_ic(train_proba, returns_train.values)
    train_auc = roc_auc_score(y_train, train_proba)
    train_q_spread = calculate_quintile_spread(train_proba, returns_train.values)

    print(f"IC:        {train_ic:+.4f} (p={train_p:.4f})")
    print(f"AUC:       {train_auc:.4f}")
    print(
        f"Q5-Q1 Spread: {train_q_spread:+.4%}"
        if not np.isnan(train_q_spread)
        else "Q5-Q1 Spread: NaN"
    )
    print()

    # === EVALUATE ON HOLDOUT SET ===
    print("=" * 80)
    print("HOLDOUT SET PERFORMANCE (OUT-OF-SAMPLE)")
    print("=" * 80)

    holdout_proba = model.predict_proba(X_holdout)[:, 1]

    holdout_ic, holdout_p = calculate_ic(holdout_proba, returns_holdout.values)
    holdout_auc = roc_auc_score(y_holdout, holdout_proba)
    holdout_q_spread = calculate_quintile_spread(holdout_proba, returns_holdout.values)

    print(f"IC:        {holdout_ic:+.4f} (p={holdout_p:.4f})")
    print(f"AUC:       {holdout_auc:.4f}")
    print(
        f"Q5-Q1 Spread: {holdout_q_spread:+.4%}"
        if not np.isnan(holdout_q_spread)
        else "Q5-Q1 Spread: NaN"
    )
    print()

    # === COMPARE TRAIN VS HOLDOUT ===
    print("=" * 80)
    print("OVERFITTING ANALYSIS")
    print("=" * 80)

    ic_degradation = (
        ((abs(train_ic) - abs(holdout_ic)) / abs(train_ic) * 100) if train_ic != 0 else 0
    )
    auc_degradation = ((train_auc - holdout_auc) / train_auc * 100) if train_auc != 0 else 0

    print(f"IC Degradation:  {ic_degradation:+.1f}%")
    print(f"AUC Degradation: {auc_degradation:+.1f}%")
    print()

    if ic_degradation < 20 and auc_degradation < 10:
        print("[EXCELLENT] Low degradation - model generalizes well!")
    elif ic_degradation < 40 and auc_degradation < 20:
        print("[GOOD] Moderate degradation - acceptable generalization")
    else:
        print("[WARNING] High degradation - possible overfitting!")

    print()

    # === FEATURE IMPORTANCE ===
    print("=" * 80)
    print("TOP 5 FEATURES (by coefficient magnitude)")
    print("=" * 80)

    feature_importance = pd.DataFrame(
        {
            "feature": X_train.columns,
            "coefficient": model.coef_[0],
            "abs_coef": np.abs(model.coef_[0]),
        }
    )

    feature_importance = feature_importance.sort_values("abs_coef", ascending=False)

    for _idx, row in feature_importance.head(5).iterrows():
        print(f"{row['feature']:30s} Coef: {row['coefficient']:+.4f}")

    print()

    # === FINAL VERDICT ===
    print("=" * 80)
    print("VALIDATION VERDICT")
    print("=" * 80)

    holdout_sig = holdout_p < 0.05
    low_degradation = ic_degradation < 30 and auc_degradation < 15
    positive_edge = abs(holdout_ic) > 0.03 or holdout_auc > 0.52

    if holdout_sig and low_degradation and positive_edge:
        print("[SUCCESS] Features v17 VALIDATED for production!")
        print(f"  - Holdout IC: {holdout_ic:+.4f} (p<0.05)")
        print("  - Low degradation (<30%)")
        print("  - Positive out-of-sample edge")
    elif holdout_sig and positive_edge:
        print("[CAUTION] Features show edge but higher degradation")
        print("  - Monitor for overfitting in live trading")
    else:
        print("[FAIL] Features do not validate on holdout")
        print("  - Re-evaluate feature selection or parameters")

    return 0


if __name__ == "__main__":
    sys.exit(main())
