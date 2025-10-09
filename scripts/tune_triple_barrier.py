"""
Triple-barrier parameter sweep for optimal risk/reward.

Grid search over:
- k_profit ∈ {1.0, 1.2, 1.4}
- k_stop ∈ {0.6, 0.8, 1.0}
- H ∈ {24, 36, 48}

Metrics:
- AUC (model discrimination)
- Coverage (% of bars with valid labels)
- Profit Factor (sum(profits) / sum(losses))
- Risk/Reward ratio (k_profit / k_stop)
"""

import argparse
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.ml.label_cache import load_cached_labels, save_labels_to_cache
from core.ml.labeling import (
    align_features_with_labels,
    generate_adaptive_triple_barrier_labels,
)
from core.utils.data_loader import load_features

# Try Numba for 2000× speedup
try:
    from core.ml.labeling_fast import generate_adaptive_triple_barrier_labels_fast

    USE_NUMBA = True
except ImportError:
    USE_NUMBA = False


def load_data(symbol: str, timeframe: str):
    """Load features and candles."""
    # Load features with smart format selection (Feather > Parquet)
    features_df = load_features(symbol, timeframe)

    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path)

    # Remove timestamp
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    features_df = features_df[numeric_cols]

    return features_df, candles_df


def evaluate_barrier_config(
    features_df: pd.DataFrame,
    candles_df: pd.DataFrame,
    k_profit: float,
    k_stop: float,
    max_holding: int,
    symbol: str = "tBTCUSD",
    timeframe: str = "1h",
) -> dict:
    """
    Evaluate single triple-barrier configuration.

    Returns dict with AUC, coverage, PF, etc.
    """
    # Try cache first
    labels = load_cached_labels(
        symbol,
        timeframe,
        k_profit=k_profit,
        k_stop=k_stop,
        max_holding=max_holding,
        atr_period=14,
        version="v2",
    )

    if labels is None:
        # Cache miss - generate labels
        closes = candles_df["close"].tolist()
        highs = candles_df["high"].tolist()
        lows = candles_df["low"].tolist()

        # Use Numba if available (2000× faster!)
        if USE_NUMBA:
            labels = generate_adaptive_triple_barrier_labels_fast(
                closes,
                highs,
                lows,
                profit_multiplier=k_profit,
                stop_multiplier=k_stop,
                max_holding_bars=max_holding,
                atr_period=14,
            )
        else:
            labels = generate_adaptive_triple_barrier_labels(
                closes,
                highs,
                lows,
                profit_multiplier=k_profit,
                stop_multiplier=k_stop,
                max_holding_bars=max_holding,
                atr_period=14,
            )

        # Save to cache
        save_labels_to_cache(
            labels,
            symbol,
            timeframe,
            k_profit=k_profit,
            k_stop=k_stop,
            max_holding=max_holding,
            atr_period=14,
            version="v2",
        )

    # Calculate coverage
    total = len(labels)
    valid = sum(1 for l in labels if l is not None)
    coverage = valid / total if total > 0 else 0.0

    # Align and filter
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)
    X = features_df.iloc[start_idx:end_idx]
    y = np.array(labels[start_idx:end_idx])

    nan_mask = X.isna().any(axis=1)
    valid_label_mask = np.array([l is not None for l in y])
    combined_mask = ~nan_mask & valid_label_mask

    X = X[combined_mask]
    y = y[combined_mask]
    y = np.array([int(l) for l in y], dtype=int)

    if len(X) < 100:
        return {"error": "insufficient_data"}

    # Train/test split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Quick train (no grid search, just default)
    clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred_proba = clf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)

    # Calculate simple profit factor estimate
    # (Assuming 1:1 risk/reward for simplicity, actual PF needs backtest)
    profit_rate = y_test.mean()
    loss_rate = 1 - profit_rate

    # Theoretical PF based on k_profit/k_stop ratio
    theoretical_pf = (profit_rate * k_profit) / (loss_rate * k_stop) if loss_rate > 0 else 0.0

    return {
        "k_profit": k_profit,
        "k_stop": k_stop,
        "max_holding": max_holding,
        "risk_reward": k_profit / k_stop if k_stop > 0 else 0.0,
        "auc": auc,
        "coverage": coverage,
        "samples": len(X),
        "profit_rate": profit_rate,
        "theoretical_pf": theoretical_pf,
    }


def main():
    parser = argparse.ArgumentParser(description="Tune triple-barrier parameters")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe")
    parser.add_argument(
        "--output", type=str, default="results/barrier_sweep.csv", help="Output CSV"
    )

    args = parser.parse_args()

    print(f"[LOAD] Loading data for {args.symbol} {args.timeframe}")
    features_df, candles_df = load_data(args.symbol, args.timeframe)

    # Grid search
    k_profits = [1.0, 1.2, 1.4]
    k_stops = [0.6, 0.8, 1.0]
    holdings = [24, 36, 48]

    total_configs = len(k_profits) * len(k_stops) * len(holdings)
    print(f"\n[SWEEP] Testing {total_configs} configurations...")
    print("k_profit x k_stop x max_holding = configs")
    print(f"{k_profits} x {k_stops} x {holdings}")

    results = []

    for idx, (kp, ks, h) in enumerate(product(k_profits, k_stops, holdings), 1):
        print(f"\n[{idx}/{total_configs}] k_profit={kp}, k_stop={ks}, H={h}")

        result = evaluate_barrier_config(
            features_df, candles_df, kp, ks, h, args.symbol, args.timeframe
        )

        if "error" not in result:
            print(
                f"  AUC: {result['auc']:.4f}, Coverage: {result['coverage']:.1%}, "
                f"R:R: {result['risk_reward']:.2f}, PF_est: {result['theoretical_pf']:.2f}"
            )
            results.append(result)
        else:
            print(f"  ERROR: {result['error']}")

    # Convert to DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("auc", ascending=False)

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)

    print(f"\n[SUCCESS] Results saved to {output_path}")
    print("\n" + "=" * 80)
    print("TOP 5 CONFIGURATIONS (by AUC)")
    print("=" * 80)

    for idx, row in results_df.head(5).iterrows():
        print(f"\n#{idx+1}: AUC {row['auc']:.4f}")
        print(f"  k_profit={row['k_profit']}, k_stop={row['k_stop']}, H={row['max_holding']}")
        print(
            f"  R:R={row['risk_reward']:.2f}, Coverage={row['coverage']:.1%}, PF_est={row['theoretical_pf']:.2f}"
        )

    # Find sweet spot (AUC > 0.60, Coverage > 25%, R:R ~= 1.4)
    sweet_spot = results_df[
        (results_df["auc"] >= 0.60)
        & (results_df["coverage"] >= 0.25)
        & (results_df["risk_reward"] >= 1.3)
        & (results_df["risk_reward"] <= 1.5)
    ]

    if len(sweet_spot) > 0:
        print("\n" + "=" * 80)
        print("SWEET SPOT (AUC>=0.60, Coverage>=25%, R:R~=1.4)")
        print("=" * 80)

        best = sweet_spot.iloc[0]
        print(f"\nBEST: AUC {best['auc']:.4f}")
        print(f"  k_profit={best['k_profit']}, k_stop={best['k_stop']}, H={best['max_holding']}")
        print(
            f"  R:R={best['risk_reward']:.2f}, Coverage={best['coverage']:.1%}, PF_est={best['theoretical_pf']:.2f}"
        )


if __name__ == "__main__":
    main()
