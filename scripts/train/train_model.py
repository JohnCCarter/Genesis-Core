from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import GridSearchCV

from core.ml.labeling import align_features_with_labels, generate_labels
from core.utils import timeframe_filename_suffix
from core.utils.data_loader import load_features

__all__ = [
    "align_features_with_labels",
    "convert_to_model_json",
    "generate_training_labels",
    "load_features_and_prices",
    "save_model_and_metrics",
    "split_data_chronological",
    "train_buy_sell_models",
]


def load_features_and_prices(
    symbol: str, timeframe: str, feature_version: str = "v17"
) -> tuple[pd.DataFrame, list[float], pd.DataFrame]:
    """Load features and aligned close prices for model training."""

    features_df = load_features(symbol, timeframe, version=feature_version)
    suffix = timeframe_filename_suffix(timeframe)

    search_paths = [
        Path("data/curated/v1/candles") / f"{symbol}_{suffix}.parquet",
        Path("data/candles") / f"{symbol}_{suffix}.parquet",
    ]
    candles_path = next((path for path in search_paths if path.exists()), None)

    if candles_path is None:
        missing_path = Path("data/candles") / f"{symbol}_{suffix}.parquet"
        raise FileNotFoundError(f"Candles file not found: {missing_path}")

    candles_df = pd.read_parquet(candles_path)

    if "timestamp" in candles_df.columns and "timestamp" in features_df.columns:
        candles_df = (
            candles_df.set_index("timestamp").reindex(features_df["timestamp"]).reset_index()
        )

    close_prices = candles_df["close"].tolist()
    if len(features_df) != len(close_prices) or pd.isna(close_prices).any():
        raise ValueError(
            f"Features ({len(features_df)}) and candles ({len(close_prices)}) length mismatch"
        )

    return features_df, [float(price) for price in close_prices], candles_df


def generate_training_labels(
    close_prices: list[float],
    lookahead_bars: int = 10,
    threshold_pct: float = 0.0,
) -> list[int | None]:
    """Generate binary training labels using the shared labeling helper."""

    return generate_labels(close_prices, lookahead_bars, threshold_pct)


def split_data_chronological(
    features: np.ndarray,
    labels: np.ndarray,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    use_holdout: bool = False,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    list[int] | None,
]:
    """Split data chronologically without shuffling (optionally with holdout tail)."""

    n_samples = len(features)
    holdout_indices = None

    if use_holdout:
        holdout_size = int(n_samples * 0.2)
        holdout_start = n_samples - holdout_size
        holdout_indices = list(range(holdout_start, n_samples))

        n_samples -= holdout_size
        features = features[:n_samples]
        labels = labels[:n_samples]

    train_end = int(n_samples * train_ratio)
    val_end = int(n_samples * (train_ratio + val_ratio))

    X_train = features[:train_end]
    X_val = features[train_end:val_end]
    X_test = features[val_end:]

    y_train = labels[:train_end]
    y_val = labels[train_end:val_end]
    y_test = labels[val_end:]

    return X_train, X_val, X_test, y_train, y_val, y_test, holdout_indices


def train_buy_sell_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: list[str],
    fast_mode: bool = False,
) -> tuple[LogisticRegression, LogisticRegression, dict]:
    """Train separate buy/sell logistic models with optional fast path."""

    buy_y_train = y_train
    buy_y_val = y_val

    sell_y_train = 1 - y_train
    sell_y_val = 1 - y_val

    if fast_mode:
        buy_model = LogisticRegression(
            C=1.0,
            penalty="l2",
            solver="lbfgs",
            max_iter=1000,
            random_state=42,
        )
        buy_model.fit(X_train, buy_y_train)

        sell_model = LogisticRegression(
            C=1.0,
            penalty="l2",
            solver="lbfgs",
            max_iter=1000,
            random_state=42,
        )
        sell_model.fit(X_train, sell_y_train)

        buy_pred_proba = buy_model.predict_proba(X_val)[:, 1]
        sell_pred_proba = sell_model.predict_proba(X_val)[:, 1]
        buy_log_loss_val = log_loss(buy_y_val, buy_pred_proba)
        sell_log_loss_val = log_loss(sell_y_val, sell_pred_proba)
        buy_auc = roc_auc_score(buy_y_val, buy_pred_proba)
        sell_auc = roc_auc_score(sell_y_val, sell_pred_proba)

        metrics = {
            "buy_model": {
                "best_params": {
                    "C": 1.0,
                    "penalty": "l2",
                    "solver": "lbfgs",
                    "max_iter": 1000,
                },
                "best_score": -buy_log_loss_val,
                "val_log_loss": buy_log_loss_val,
                "val_auc": buy_auc,
            },
            "sell_model": {
                "best_params": {
                    "C": 1.0,
                    "penalty": "l2",
                    "solver": "lbfgs",
                    "max_iter": 1000,
                },
                "best_score": -sell_log_loss_val,
                "val_log_loss": sell_log_loss_val,
                "val_auc": sell_auc,
            },
            "feature_names": feature_names,
            "n_features": len(feature_names),
            "n_train": len(X_train),
            "n_val": len(X_val),
        }
        return buy_model, sell_model, metrics

    param_grid = {
        "C": [0.1, 1.0, 10.0],
        "penalty": ["l2"],
        "solver": ["lbfgs"],
        "max_iter": [1000],
    }

    buy_model = GridSearchCV(
        LogisticRegression(random_state=42),
        param_grid,
        cv=3,
        scoring="neg_log_loss",
        n_jobs=-1,
    )
    buy_model.fit(X_train, buy_y_train)

    sell_model = GridSearchCV(
        LogisticRegression(random_state=42),
        param_grid,
        cv=3,
        scoring="neg_log_loss",
        n_jobs=-1,
    )
    sell_model.fit(X_train, sell_y_train)

    buy_pred_proba = buy_model.predict_proba(X_val)[:, 1]
    sell_pred_proba = sell_model.predict_proba(X_val)[:, 1]
    buy_log_loss_val = log_loss(buy_y_val, buy_pred_proba)
    sell_log_loss_val = log_loss(sell_y_val, sell_pred_proba)
    buy_auc = roc_auc_score(buy_y_val, buy_pred_proba)
    sell_auc = roc_auc_score(sell_y_val, sell_pred_proba)

    metrics = {
        "buy_model": {
            "best_params": buy_model.best_params_,
            "best_score": buy_model.best_score_,
            "val_log_loss": buy_log_loss_val,
            "val_auc": buy_auc,
        },
        "sell_model": {
            "best_params": sell_model.best_params_,
            "best_score": sell_model.best_score_,
            "val_log_loss": sell_log_loss_val,
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
    """Convert trained models to Genesis-Core JSON model format."""

    return {
        "version": version,
        "schema": feature_names,
        "buy": {
            "w": buy_model.coef_[0].tolist(),
            "b": float(buy_model.intercept_[0]),
            "calib": {"a": 1.0, "b": 0.0},
        },
        "sell": {
            "w": sell_model.coef_[0].tolist(),
            "b": float(sell_model.intercept_[0]),
            "calib": {"a": 1.0, "b": 0.0},
        },
    }


def save_model_and_metrics(
    model_json: dict,
    metrics: dict,
    symbol: str,
    timeframe: str,
    version: str,
    output_dir: Path,
) -> dict:
    """Save model and metrics payloads to disk."""

    output_dir.mkdir(parents=True, exist_ok=True)
    model_filename = f"{symbol}_{timeframe}_{version}.json"
    metrics_filename = f"{symbol}_{timeframe}_{version}_metrics.json"
    model_path = output_dir / model_filename
    metrics_path = output_dir / metrics_filename

    with open(model_path, "w", encoding="utf-8") as file_obj:
        json.dump(model_json, file_obj, indent=2)
    with open(metrics_path, "w", encoding="utf-8") as file_obj:
        json.dump(metrics, file_obj, indent=2)

    return {
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
        "model_filename": model_filename,
        "metrics_filename": metrics_filename,
    }


def _run_deprecated_cli() -> int:
    print(
        "[DEPRECATED] scripts/train/train_model.py has no standalone CLI entrypoint; "
        "import and call module functions instead.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(_run_deprecated_cli())
