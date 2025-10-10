#!/usr/bin/env python3
"""
Calibrate ML model SEPARATELY for each regime.

This creates regime-specific calibration parameters to fix mis-calibration
that occurs when training on mixed-regime data.

Usage:
    python scripts/calibrate_by_regime.py --model results/models/tBTCUSD_1h_v3.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.strategy.prob_model import predict_proba
from core.utils.data_loader import load_features


def classify_trend_regime(closes: pd.Series, window: int = 50) -> pd.Series:
    """Classify trend regime."""
    ema = closes.ewm(span=window, adjust=False).mean()
    trend = (closes - ema) / ema

    regimes = []
    for t in trend:
        if t > 0.02:
            regimes.append("bull")
        elif t < -0.02:
            regimes.append("bear")
        else:
            regimes.append("ranging")
    return pd.Series(regimes, index=closes.index)


def calibrate_for_regime(
    raw_predictions: np.ndarray, labels: np.ndarray, method: str = "platt"
) -> dict:
    """
    Calibrate predictions for a specific regime using Platt scaling.

    Platt scaling: p_calibrated = sigmoid(a * logit(p_raw) + b)

    Returns calibration parameters (a, b).
    """
    if len(labels) < 50:
        return {"method": "none", "a": 1.0, "b": 0.0, "error": "Insufficient samples"}

    try:
        from sklearn.metrics import brier_score_loss

        # Logit transform
        def logit(p):
            p_clipped = np.clip(p, 1e-7, 1 - 1e-7)
            return np.log(p_clipped / (1 - p_clipped))

        def sigmoid(z):
            return 1 / (1 + np.exp(-z))

        # Convert predictions to logits
        raw_logits = logit(raw_predictions)

        # Fit logistic regression: y ~ a * raw_logit + b
        # This is Platt scaling
        X_calib = raw_logits.reshape(-1, 1)
        lr = LogisticRegression(penalty=None, solver="lbfgs", max_iter=1000)
        lr.fit(X_calib, labels)

        # Extract parameters
        a = float(lr.coef_[0][0])
        b = float(lr.intercept_[0])

        # Calculate calibrated predictions
        calibrated_preds = sigmoid(a * raw_logits + b)

        # Calculate metrics
        brier_before = brier_score_loss(labels, raw_predictions)
        brier_after = brier_score_loss(labels, calibrated_preds)
        improvement = brier_before - brier_after

        return {
            "method": "platt",
            "a": a,
            "b": b,
            "brier_before": float(brier_before),
            "brier_after": float(brier_after),
            "improvement": float(improvement),
            "n_samples": int(len(labels)),
        }

    except Exception as e:
        return {
            "method": "none",
            "a": 1.0,
            "b": 0.0,
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Calibrate model per regime")
    parser.add_argument("--model", required=True, help="Path to model JSON")
    parser.add_argument(
        "--method", default="isotonic", choices=["sigmoid", "isotonic"], help="Calibration method"
    )
    parser.add_argument("--output", help="Output model path (default: overwrite input)")

    args = parser.parse_args()

    model_path = Path(args.model)

    # Extract symbol/timeframe
    parts = model_path.stem.split("_")
    symbol = parts[0] if len(parts) >= 2 else "tBTCUSD"
    timeframe = parts[1] if len(parts) >= 2 else "1h"

    print("=" * 80)
    print("REGIME-AWARE CALIBRATION")
    print("=" * 80)
    print(f"Model: {model_path.name}")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Method: {args.method}")
    print("=" * 80)

    # Load model
    with open(model_path) as f:
        model_config = json.load(f)

    # Load features and candles
    print("\n[LOAD] Loading data...")
    features_df = load_features(symbol, timeframe)
    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path)

    # Get predictions
    print("[PREDICT] Generating raw predictions...")
    feature_cols = [col for col in features_df.columns if col != "timestamp"]
    X = features_df[feature_cols].values

    schema = model_config.get("schema", feature_cols)
    buy_w = model_config.get("buy", {}).get("w")
    buy_b = model_config.get("buy", {}).get("b", 0.0)

    # Get RAW predictions (WITHOUT calibration)
    predictions_raw = []
    for i in range(len(X)):
        feats_dict = {col: X[i, j] for j, col in enumerate(feature_cols)}
        probas = predict_proba(
            feats_dict,
            schema=schema,
            buy_w=buy_w,
            buy_b=buy_b,
            calib_buy=(1.0, 0.0),  # NO calibration for raw
        )
        predictions_raw.append(probas["buy"])

    predictions_raw = np.array(predictions_raw)

    # Get labels
    print("[LABELS] Calculating forward returns...")
    close_prices = candles_df["close"]
    forward_returns = close_prices.pct_change(10).shift(-10)
    labels = (forward_returns > 0).astype(int).values

    # Classify regimes
    print("[CLASSIFY] Detecting regimes...")
    regimes = classify_trend_regime(close_prices, window=50)

    # Align
    min_len = min(len(predictions_raw), len(labels), len(regimes))
    predictions_raw = predictions_raw[:min_len]
    labels = labels[:min_len]
    regimes = regimes.iloc[:min_len]

    # Remove NaN
    valid_mask = ~np.isnan(labels)
    predictions_raw = predictions_raw[valid_mask]
    labels = labels[valid_mask]
    regimes = regimes[valid_mask]

    # Get SELL predictions too
    print("[PREDICT] Generating SELL predictions...")
    sell_w = model_config.get("sell", {}).get("w")
    sell_b = model_config.get("sell", {}).get("b", 0.0)

    predictions_sell_raw = []
    for i in range(len(X)):
        feats_dict = {col: X[i, j] for j, col in enumerate(feature_cols)}
        probas = predict_proba(
            feats_dict, schema=schema, sell_w=sell_w, sell_b=sell_b, calib_sell=(1.0, 0.0)
        )
        predictions_sell_raw.append(probas["sell"])

    predictions_sell_raw = np.array(predictions_sell_raw)[:min_len][valid_mask]

    # Calibrate per regime (BOTH buy and sell!)
    print("\n[CALIBRATE] Calibrating BUY model per regime...")
    regime_calibrations_buy = {}
    regime_calibrations_sell = {}

    for regime_name in ["bear", "bull", "ranging"]:
        mask = (regimes == regime_name).values
        if mask.sum() < 50:
            print(f"  {regime_name}: SKIP (only {mask.sum()} samples)")
            continue

        regime_preds_buy = predictions_raw[mask]
        regime_preds_sell = predictions_sell_raw[mask]
        regime_labels = labels[mask]

        # Calibrate BUY
        calib_buy = calibrate_for_regime(regime_preds_buy, regime_labels, method=args.method)
        regime_calibrations_buy[regime_name] = calib_buy

        # Calibrate SELL (with INVERTED labels: sell wants label=0)
        calib_sell = calibrate_for_regime(regime_preds_sell, 1 - regime_labels, method=args.method)
        regime_calibrations_sell[regime_name] = calib_sell

        if "error" in calib_buy:
            print(f"\n  {regime_name}: ERROR - {calib_buy['error']}")
            continue

        print(f"\n  {regime_name} ({calib_buy.get('n_samples', 0)} samples):")
        print(
            f"    BUY:  a={calib_buy['a']:.4f}, b={calib_buy['b']:.4f}, improvement={calib_buy.get('improvement', 0):.4f}"
        )
        print(
            f"    SELL: a={calib_sell['a']:.4f}, b={calib_sell['b']:.4f}, improvement={calib_sell.get('improvement', 0):.4f}"
        )

    # Update model config
    print("\n[UPDATE] Updating model configuration...")

    # Store regime-specific calibration for BOTH buy and sell
    model_config["calibration_by_regime"] = {
        "buy": regime_calibrations_buy,
        "sell": regime_calibrations_sell,
        "method": args.method,
        "note": "Regime-specific calibration to handle varying data distributions",
    }

    # Save updated model
    output_path = Path(args.output) if args.output else model_path
    with open(output_path, "w") as f:
        json.dump(model_config, f, indent=2)

    print(f"\n[SAVED] Updated model: {output_path}")
    print("\n" + "=" * 80)
    print("CALIBRATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Update predict_proba_for() to use regime-specific calibration")
    print("2. Backtest with new calibration")
    print("3. Compare metrics vs original calibration")
    print("=" * 80)


if __name__ == "__main__":
    main()
