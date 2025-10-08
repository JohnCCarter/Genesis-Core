"""
Train ML models for Genesis-Core trading strategy.

Usage:
    python scripts/train_model.py --symbol tBTCUSD --timeframe 15m
    python scripts/train_model.py --symbol tBTCUSD --timeframe 15m --lookahead 20 --version 2
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import GridSearchCV

from core.ml.label_cache import load_cached_labels, save_labels_to_cache
from core.ml.labeling import (
    align_features_with_labels,
    generate_adaptive_triple_barrier_labels,
    generate_labels,
    generate_triple_barrier_labels,
)

# Try to use fast Numba implementation if available
try:
    from core.ml.labeling_fast import generate_adaptive_triple_barrier_labels_fast

    USE_NUMBA = True
except ImportError:
    USE_NUMBA = False


def load_features_and_prices(
    symbol: str, timeframe: str
) -> tuple[pd.DataFrame, list[float], pd.DataFrame]:
    """
    Load features, close prices, and full candles for labeling.

    Args:
        symbol: Symbol (e.g., 'tBTCUSD')
        timeframe: Timeframe (e.g., '15m')

    Returns:
        Tuple of (features_df, close_prices, candles_df)
    """
    # Try Feather first (2-5× faster), fall back to Parquet
    feather_path = Path("data/features") / f"{symbol}_{timeframe}_features.feather"
    parquet_path = Path("data/features") / f"{symbol}_{timeframe}_features.parquet"

    if feather_path.exists():
        features_df = pd.read_feather(feather_path)
    elif parquet_path.exists():
        features_df = pd.read_parquet(parquet_path)
    else:
        raise FileNotFoundError(f"Features file not found: {feather_path} or {parquet_path}")

    if features_df.empty:
        raise ValueError("Features dataframe is empty")

    # Extract close prices from candles (needed for labeling)
    candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"
    if not candles_path.exists():
        raise FileNotFoundError(f"Candles file not found: {candles_path}")

    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].tolist()

    # Verify alignment
    if len(features_df) != len(close_prices):
        raise ValueError(
            f"Features ({len(features_df)}) and candles ({len(close_prices)}) length mismatch"
        )

    return features_df, close_prices, candles_df


def generate_training_labels(
    close_prices: list[float],
    lookahead_bars: int = 10,
    threshold_pct: float = 0.0,
) -> list[int | None]:
    """
    Generate binary labels for training.

    Args:
        close_prices: List of close prices
        lookahead_bars: Number of bars to look ahead
        threshold_pct: Minimum price change % to label as "up"

    Returns:
        List of labels (1, 0, or None)
    """

    return generate_labels(close_prices, lookahead_bars, threshold_pct)


def split_data_chronological(
    features: np.ndarray,
    labels: np.ndarray,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data chronologically (no random shuffling for time series).

    Args:
        features: Feature matrix
        labels: Label array
        train_ratio: Training set ratio
        val_ratio: Validation set ratio (test = 1 - train - val)

    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    n_samples = len(features)

    train_end = int(n_samples * train_ratio)
    val_end = int(n_samples * (train_ratio + val_ratio))

    X_train = features[:train_end]
    X_val = features[train_end:val_end]
    X_test = features[val_end:]

    y_train = labels[:train_end]
    y_val = labels[train_end:val_end]
    y_test = labels[val_end:]

    return X_train, X_val, X_test, y_train, y_val, y_test


def train_buy_sell_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: list[str],
) -> tuple[LogisticRegression, LogisticRegression, dict]:
    """
    Train separate models for buy and sell decisions.

    Args:
        X_train: Training features
        y_train: Training labels (1=up, 0=down)
        X_val: Validation features
        y_val: Validation labels
        feature_names: List of feature names

    Returns:
        Tuple of (buy_model, sell_model, training_metrics)
    """
    # For buy model: predict when price goes up (y=1)
    buy_y_train = y_train
    buy_y_val = y_val

    # For sell model: predict when price goes down (y=0 becomes 1)
    sell_y_train = 1 - y_train  # Invert labels
    sell_y_val = 1 - y_val

    # Hyperparameter grid
    param_grid = {
        "C": [0.1, 1.0, 10.0],
        "penalty": ["l2"],
        "solver": ["lbfgs"],
        "max_iter": [1000],
    }

    # Train buy model
    print("Training buy model...")
    buy_model = GridSearchCV(
        LogisticRegression(random_state=42),
        param_grid,
        cv=3,
        scoring="neg_log_loss",
        n_jobs=-1,
    )
    buy_model.fit(X_train, buy_y_train)

    # Train sell model
    print("Training sell model...")
    sell_model = GridSearchCV(
        LogisticRegression(random_state=42),
        param_grid,
        cv=3,
        scoring="neg_log_loss",
        n_jobs=-1,
    )
    sell_model.fit(X_train, sell_y_train)

    # Calculate metrics
    buy_pred_proba = buy_model.predict_proba(X_val)[:, 1]
    sell_pred_proba = sell_model.predict_proba(X_val)[:, 1]

    buy_log_loss = log_loss(buy_y_val, buy_pred_proba)
    sell_log_loss = log_loss(sell_y_val, sell_pred_proba)

    buy_auc = roc_auc_score(buy_y_val, buy_pred_proba)
    sell_auc = roc_auc_score(sell_y_val, sell_pred_proba)

    metrics = {
        "buy_model": {
            "best_params": buy_model.best_params_,
            "best_score": buy_model.best_score_,
            "val_log_loss": buy_log_loss,
            "val_auc": buy_auc,
        },
        "sell_model": {
            "best_params": sell_model.best_params_,
            "best_score": sell_model.best_score_,
            "val_log_loss": sell_log_loss,
            "val_auc": sell_auc,
        },
        "feature_names": feature_names,
        "n_features": len(feature_names),
        "n_train": len(X_train),
        "n_val": len(X_val),
    }

    return buy_model.best_estimator_, sell_model.best_estimator_, metrics


def convert_to_model_json(
    buy_model: LogisticRegression,
    sell_model: LogisticRegression,
    feature_names: list[str],
    version: str = "v2",
) -> dict:
    """
    Convert trained models to Genesis-Core JSON format.

    Args:
        buy_model: Trained buy model
        sell_model: Trained sell model
        feature_names: List of feature names
        version: Model version

    Returns:
        Model dictionary in Genesis-Core format
    """
    # Extract weights and biases
    buy_weights = buy_model.coef_[0].tolist()
    buy_bias = float(buy_model.intercept_[0])

    sell_weights = sell_model.coef_[0].tolist()
    sell_bias = float(sell_model.intercept_[0])

    # Create model structure
    model_json = {
        "version": version,
        "schema": feature_names,
        "buy": {
            "w": buy_weights,
            "b": buy_bias,
            "calib": {"a": 1.0, "b": 0.0},  # Will be calibrated later
        },
        "sell": {
            "w": sell_weights,
            "b": sell_bias,
            "calib": {"a": 1.0, "b": 0.0},  # Will be calibrated later
        },
    }

    return model_json


def save_model_and_metrics(
    model_json: dict,
    metrics: dict,
    symbol: str,
    timeframe: str,
    version: str,
    output_dir: Path,
) -> dict:
    """
    Save model and training metrics.

    Args:
        model_json: Model in JSON format
        metrics: Training metrics
        symbol: Symbol
        timeframe: Timeframe
        version: Model version
        output_dir: Output directory

    Returns:
        Dictionary with file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    model_filename = f"{symbol}_{timeframe}_{version}.json"
    model_path = output_dir / model_filename

    with open(model_path, "w") as f:
        json.dump(model_json, f, indent=2)

    # Save metrics
    metrics_filename = f"{symbol}_{timeframe}_{version}_metrics.json"
    metrics_path = output_dir / metrics_filename

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    return {
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
        "model_filename": model_filename,
        "metrics_filename": metrics_filename,
    }


def main():
    parser = argparse.ArgumentParser(description="Train ML models for trading strategy")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe (e.g., 15m)")
    parser.add_argument("--lookahead", type=int, default=10, help="Lookahead bars for labeling")
    parser.add_argument("--threshold", type=float, default=0.0, help="Price change threshold %")
    parser.add_argument(
        "--use-triple-barrier",
        action="store_true",
        help="Use triple-barrier labeling instead of simple binary",
    )
    parser.add_argument(
        "--use-adaptive-triple-barrier",
        action="store_true",
        help="Use ATR-adaptive triple-barrier labeling (volatility-aware)",
    )
    parser.add_argument(
        "--profit-pct", type=float, default=0.3, help="Profit target % for triple-barrier"
    )
    parser.add_argument(
        "--stop-pct", type=float, default=0.2, help="Stop loss % for triple-barrier"
    )
    parser.add_argument(
        "--profit-multiplier",
        type=float,
        default=1.5,
        help="ATR multiplier for profit (adaptive mode)",
    )
    parser.add_argument(
        "--stop-multiplier",
        type=float,
        default=1.0,
        help="ATR multiplier for stop loss (adaptive mode)",
    )
    parser.add_argument(
        "--max-holding", type=int, default=5, help="Max holding bars for triple-barrier"
    )
    parser.add_argument("--version", type=str, default="v3", help="Model version")
    parser.add_argument("--output-dir", type=str, default="results/models", help="Output directory")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    try:
        # Load data
        if not args.quiet:
            print(f"[LOAD] Loading features and candles for {args.symbol} {args.timeframe}")

        features_df, close_prices, candles_df = load_features_and_prices(
            args.symbol, args.timeframe
        )

        if not args.quiet:
            print(
                f"[DATA] Loaded {len(features_df)} samples with {len(features_df.columns)-1} features"
            )

        # Generate labels
        if args.use_adaptive_triple_barrier:
            # Try to load from cache first
            labels = load_cached_labels(
                args.symbol,
                args.timeframe,
                k_profit=args.profit_multiplier,
                k_stop=args.stop_multiplier,
                max_holding=args.max_holding,
                atr_period=14,
                version="v2",  # Point-in-time ATR version
            )

            if labels is not None:
                if not args.quiet:
                    print("[CACHE HIT] Loaded labels from cache")
            else:
                # Cache miss - generate labels
                implementation = "Numba (JIT)" if USE_NUMBA else "Pure Python"
                if not args.quiet:
                    print(
                        f"[LABELS] Generating ADAPTIVE TRIPLE-BARRIER labels ({implementation}) (profit_mult={args.profit_multiplier}x ATR, stop_mult={args.stop_multiplier}x ATR, holding={args.max_holding} bars)"
                    )

                # Extract OHLC data for adaptive barriers (NO LOOKAHEAD)
                highs = candles_df["high"].tolist()
                lows = candles_df["low"].tolist()
                closes = candles_df["close"].tolist()

                # Use Numba if available (2000× faster!)
                if USE_NUMBA:
                    labels = generate_adaptive_triple_barrier_labels_fast(
                        closes,
                        highs,
                        lows,
                        profit_multiplier=args.profit_multiplier,
                        stop_multiplier=args.stop_multiplier,
                        max_holding_bars=args.max_holding,
                        atr_period=14,
                    )
                else:
                    labels = generate_adaptive_triple_barrier_labels(
                        closes,
                        highs,
                        lows,
                        profit_multiplier=args.profit_multiplier,
                        stop_multiplier=args.stop_multiplier,
                        max_holding_bars=args.max_holding,
                        atr_period=14,
                    )

                # Save to cache for future runs
                save_labels_to_cache(
                    labels,
                    args.symbol,
                    args.timeframe,
                    k_profit=args.profit_multiplier,
                    k_stop=args.stop_multiplier,
                    max_holding=args.max_holding,
                    atr_period=14,
                    version="v2",
                )
        elif args.use_triple_barrier:
            if not args.quiet:
                print(
                    f"[LABELS] Generating TRIPLE-BARRIER labels (profit={args.profit_pct}%, stop={args.stop_pct}%, holding={args.max_holding} bars)"
                )
            labels = generate_triple_barrier_labels(
                close_prices,
                profit_threshold_pct=args.profit_pct,
                stop_threshold_pct=args.stop_pct,
                max_holding_bars=args.max_holding,
            )
        else:
            if not args.quiet:
                print(
                    f"[LABELS] Generating simple binary labels (lookahead={args.lookahead}, threshold={args.threshold}%)"
                )
            labels = generate_training_labels(close_prices, args.lookahead, args.threshold)

        # Align features and labels
        start_idx, end_idx = align_features_with_labels(len(features_df), labels)

        if end_idx <= start_idx:
            raise ValueError("No valid labels found after alignment")

        # Extract aligned data
        aligned_features = features_df.iloc[start_idx:end_idx]
        aligned_labels = np.array(labels[start_idx:end_idx])

        # Report label statistics
        if not args.quiet:
            total_labels = len(labels)
            none_count = sum(1 for label in labels if label is None)
            profitable_count = sum(1 for label in labels if label == 1)
            loss_count = sum(1 for label in labels if label == 0)

            print(f"[LABELS] Total: {total_labels}")
            print(f"[LABELS] None (filtered): {none_count} ({100*none_count/total_labels:.1f}%)")
            print(
                f"[LABELS] Profitable (1): {profitable_count} ({100*profitable_count/total_labels:.1f}%)"
            )
            print(f"[LABELS] Loss (0): {loss_count} ({100*loss_count/total_labels:.1f}%)")
            print(f"[LABELS] Training on: {len(aligned_labels)} samples (after alignment)")

        # Remove timestamp column for training
        feature_columns = [col for col in aligned_features.columns if col != "timestamp"]
        X = aligned_features[feature_columns].values
        feature_names = feature_columns

        # Handle NaN values (drop rows with any NaN)
        nan_mask = np.isnan(X).any(axis=1)
        if nan_mask.any():
            print(f"[CLEAN] Removing {nan_mask.sum()} rows with NaN values")
            X = X[~nan_mask]
            aligned_labels = aligned_labels[~nan_mask]

        # Filter None labels (from triple-barrier filtering)
        valid_label_mask = np.array([label is not None for label in aligned_labels])
        if not valid_label_mask.all():
            none_in_aligned = (~valid_label_mask).sum()
            if not args.quiet:
                print(f"[CLEAN] Removing {none_in_aligned} rows with None labels (filtered trades)")
            X = X[valid_label_mask]
            aligned_labels = aligned_labels[valid_label_mask]

        # Convert labels to int (might be mixed type after filtering)
        aligned_labels = np.array([int(label) for label in aligned_labels], dtype=int)

        if not args.quiet:
            print(
                f"[ALIGN] Using {len(X)} samples (removed {len(features_df) - len(X)} with invalid/filtered labels)"
            )

        # Split data
        if not args.quiet:
            print("[SPLIT] Splitting data chronologically (60/20/20)")

        X_train, X_val, X_test, y_train, y_val, y_test = split_data_chronological(X, aligned_labels)

        if not args.quiet:
            print(f"[SPLIT] Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

        # Train models
        if not args.quiet:
            print("[TRAIN] Training buy/sell models with GridSearchCV")

        buy_model, sell_model, metrics = train_buy_sell_models(
            X_train, y_train, X_val, y_val, feature_names
        )

        # Convert to JSON format
        if not args.quiet:
            print("[CONVERT] Converting to Genesis-Core model format")

        model_json = convert_to_model_json(buy_model, sell_model, feature_names, args.version)

        # Save results
        output_dir = Path(args.output_dir)
        file_paths = save_model_and_metrics(
            model_json, metrics, args.symbol, args.timeframe, args.version, output_dir
        )

        # Print summary
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)
        print(f"Symbol: {args.symbol}")
        print(f"Timeframe: {args.timeframe}")
        print(f"Version: {args.version}")
        if args.use_adaptive_triple_barrier:
            print(
                f"Labeling: Adaptive Triple-Barrier (profit={args.profit_multiplier}x ATR, stop={args.stop_multiplier}x ATR, holding={args.max_holding})"
            )
        elif args.use_triple_barrier:
            print(
                f"Labeling: Triple-Barrier (profit={args.profit_pct}%, stop={args.stop_pct}%, holding={args.max_holding})"
            )
        else:
            print(
                f"Labeling: Simple Binary (lookahead={args.lookahead}, threshold={args.threshold}%)"
            )
        print(
            f"Features: {len(feature_names)} ({', '.join(feature_names[:3])}... +{len(feature_names)-3} more)"
        )
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Test samples: {len(X_test)}")
        print(
            f"\nBuy Model - Val Log Loss: {metrics['buy_model']['val_log_loss']:.4f}, AUC: {metrics['buy_model']['val_auc']:.4f}"
        )
        print(
            f"Sell Model - Val Log Loss: {metrics['sell_model']['val_log_loss']:.4f}, AUC: {metrics['sell_model']['val_auc']:.4f}"
        )
        print(f"\nModel saved: {file_paths['model_path']}")
        print(f"Metrics saved: {file_paths['metrics_path']}")

    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
