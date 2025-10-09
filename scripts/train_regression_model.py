#!/usr/bin/env python3
"""
Train regression model with ATR-scaled targets.

Instead of binary classification (profit/loss), predicts continuous returns
scaled by ATR for better risk-adjusted predictions.

Usage:
    python scripts/train_regression_model.py --symbol tBTCUSD --timeframe 1h \\
        --use-holdout --save-provenance
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.atr import calculate_atr
from core.utils.data_loader import load_features


def calculate_atr_scaled_targets(candles_df, horizon: int = 10, atr_period: int = 14) -> np.ndarray:
    """
    Calculate ATR-scaled forward returns as regression target.

    Target = forward_return / ATR

    This normalizes returns by volatility, making predictions more stable.
    """
    # Calculate ATR
    highs = candles_df["high"].tolist()
    lows = candles_df["low"].tolist()
    closes = candles_df["close"].tolist()

    # Calculate ATR for full series
    atr_list = calculate_atr(highs, lows, closes, period=atr_period)
    atr_values = np.array(atr_list)

    # Calculate forward returns
    close_series = candles_df["close"]
    forward_returns = close_series.pct_change(horizon).shift(-horizon).values

    # ATR percentage (ATR / price)
    close_array = candles_df["close"].values
    atr_pct = atr_values / close_array

    # Scale returns by ATR (target = how many ATRs did price move?)
    atr_scaled_targets = forward_returns / np.where(atr_pct > 0, atr_pct, np.nan)

    # Clip extreme values
    atr_scaled_targets = np.clip(atr_scaled_targets, -5, 5)

    return atr_scaled_targets


def split_data_chronological(
    features: np.ndarray,
    targets: np.ndarray,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    use_holdout: bool = False,
):
    """Split data chronologically with optional holdout."""
    n = len(features)

    if use_holdout:
        # Reserve 20% for holdout
        holdout_size = int(n * 0.2)
        holdout_idx = list(range(n - holdout_size, n))

        # Split remaining 80% into 60/20/20 (train/val/test)
        trainable_size = n - holdout_size
        train_end = int(trainable_size * 0.6)
        val_end = int(trainable_size * 0.8)

        X_train = features[:train_end]
        y_train = targets[:train_end]
        X_val = features[train_end:val_end]
        y_val = targets[train_end:val_end]
        X_test = features[val_end:trainable_size]
        y_test = targets[val_end:trainable_size]

        return X_train, X_val, X_test, y_train, y_val, y_test, holdout_idx
    else:
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        X_train = features[:train_end]
        y_train = targets[:train_end]
        X_val = features[train_end:val_end]
        y_val = targets[train_end:val_end]
        X_test = features[val_end:]
        y_test = targets[val_end:]

        return X_train, X_val, X_test, y_train, y_val, y_test, None


def train_regression_model(X_train, y_train, X_val, y_val):
    """Train regression model with hyperparameter tuning."""
    print("[TRAIN] Training regression model with GridSearchCV...")

    # Ridge regression (L2 regularization)
    param_grid = {
        "alpha": [0.1, 1.0, 10.0, 100.0],
    }

    ridge = Ridge()
    grid_search = GridSearchCV(
        ridge,
        param_grid,
        cv=5,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
    )

    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_

    # Evaluate
    train_pred = best_model.predict(X_train)
    val_pred = best_model.predict(X_val)

    train_mse = mean_squared_error(y_train, train_pred)
    val_mse = mean_squared_error(y_val, val_pred)

    train_mae = mean_absolute_error(y_train, train_pred)
    val_mae = mean_absolute_error(y_val, val_pred)

    train_r2 = r2_score(y_train, train_pred)
    val_r2 = r2_score(y_val, val_pred)

    return best_model, {
        "train_mse": float(train_mse),
        "val_mse": float(val_mse),
        "train_mae": float(train_mae),
        "val_mae": float(val_mae),
        "train_r2": float(train_r2),
        "val_r2": float(val_r2),
        "best_params": grid_search.best_params_,
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Train regression model with ATR-scaled targets")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument("--use-holdout", action="store_true", help="Reserve 20%% holdout")
    parser.add_argument("--save-provenance", action="store_true", help="Save provenance record")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    parser.add_argument("--atr-period", type=int, default=14, help="ATR period")

    args = parser.parse_args()

    try:
        print(f"\n[LOAD] Loading features and candles for {args.symbol} {args.timeframe}")

        # Load features
        features_df = load_features(args.symbol, args.timeframe)
        feature_cols = [col for col in features_df.columns if col != "timestamp"]

        print(f"[DATA] Loaded {len(features_df)} samples with {len(feature_cols)} features")

        # Load candles
        candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
        candles_df = pd.read_parquet(candles_path)

        # Calculate ATR-scaled targets
        print(
            f"[TARGETS] Generating ATR-scaled targets (horizon={args.horizon}, ATR={args.atr_period})"
        )
        targets = calculate_atr_scaled_targets(candles_df, args.horizon, args.atr_period)

        # Align features and targets
        min_len = min(len(features_df), len(targets))
        X = features_df[feature_cols].iloc[:min_len].values
        y = targets[:min_len]

        # Remove NaN
        valid_mask = ~np.isnan(y) & ~np.isnan(X).any(axis=1)
        X = X[valid_mask]
        y = y[valid_mask]

        print(f"[ALIGN] Using {len(X)} samples after removing NaN")

        # Split data
        print(f"[SPLIT] Splitting with {'holdout + ' if args.use_holdout else ''}train/val/test")
        X_train, X_val, X_test, y_train, y_val, y_test, holdout_idx = split_data_chronological(
            X, y, use_holdout=args.use_holdout
        )

        print(f"[SPLIT] Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        if holdout_idx:
            print(f"[SPLIT] Holdout: {len(holdout_idx)} samples (reserved for final validation)")

        # Train model
        model, metrics = train_regression_model(X_train, y_train, X_val, y_val)

        # Print results
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE - REGRESSION MODEL")
        print("=" * 60)
        print(f"Symbol: {args.symbol}")
        print(f"Timeframe: {args.timeframe}")
        print(f"Target: ATR-scaled returns (horizon={args.horizon})")
        print(
            f"Features: {len(feature_cols)} ({', '.join(feature_cols[:3])}... +{len(feature_cols)-3} more)"
        )
        print(f"Training samples: {len(X_train)}")

        print("\nRegression Metrics:")
        print(f"  Train R²:  {metrics['train_r2']:.4f}")
        print(f"  Val R²:    {metrics['val_r2']:.4f}")
        print(f"  Train MAE: {metrics['train_mae']:.4f} ATR")
        print(f"  Val MAE:   {metrics['val_mae']:.4f} ATR")
        print(f"  Best params: {metrics['best_params']}")

        # Save model
        output_dir = Path("results/models_regression")
        output_dir.mkdir(parents=True, exist_ok=True)

        model_path = output_dir / f"{args.symbol}_{args.timeframe}_regression.json"

        model_data = {
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "type": "regression",
            "target": "atr_scaled_returns",
            "horizon": args.horizon,
            "atr_period": args.atr_period,
            "feature_names": feature_cols,
            "coefficients": model.coef_.tolist(),
            "intercept": float(model.intercept_),
            "metrics": metrics,
            "trained_at": datetime.now().isoformat(),
        }

        with open(model_path, "w") as f:
            json.dump(model_data, f, indent=2)

        print(f"\nModel saved: {model_path}")
        print("=" * 60 + "\n")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
