#!/usr/bin/env python3
"""
Analyze ML model calibration quality per market regime.

This script answers:
1. Are ML probabilities well-calibrated in EACH regime?
2. Should we use regime-specific calibration?
3. What thresholds should we use per regime?

Usage:
    python scripts/analyze_calibration_by_regime.py --model results/models/tBTCUSD_1h_v3.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss, log_loss

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils.data_loader import load_features


def classify_volatility_regime(returns: pd.Series, window: int = 50) -> pd.Series:
    """Classify volatility regime."""
    rolling_std = returns.rolling(window=window, min_periods=20).std()
    median_vol = rolling_std.median()
    return pd.Series(
        ["HighVol" if vol > median_vol else "LowVol" for vol in rolling_std],
        index=returns.index,
    )


def classify_trend_regime(closes: pd.Series, window: int = 50) -> pd.Series:
    """Classify trend regime."""
    ema = closes.ewm(span=window, adjust=False).mean()
    trend = (closes - ema) / ema

    regimes = []
    for t in trend:
        if t > 0.02:
            regimes.append("Bull")
        elif t < -0.02:
            regimes.append("Bear")
        else:
            regimes.append("Ranging")
    return pd.Series(regimes, index=closes.index)


def analyze_calibration_for_regime(
    y_true: np.ndarray, y_pred_proba: np.ndarray, regime_name: str
) -> dict:
    """
    Analyze calibration quality for a specific regime.

    Returns calibration metrics and optimal threshold.
    """
    if len(y_true) < 20:
        return {
            "regime": regime_name,
            "n_samples": len(y_true),
            "error": "Insufficient samples",
        }

    # Calculate calibration metrics
    try:
        brier = brier_score_loss(y_true, y_pred_proba)
        logloss = log_loss(y_true, y_pred_proba)

        # Calibration curve (bin predictions and check if they match reality)
        prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=5, strategy="uniform")

        # Calculate calibration error (how far predicted probs are from true frequencies)
        calibration_error = np.abs(prob_pred - prob_true).mean()

        # IC (correlation between prediction and outcome)
        ic, p_value = spearmanr(y_pred_proba, y_true)

        # Find optimal threshold (maximize accuracy)
        thresholds = np.linspace(0.3, 0.9, 13)
        accuracies = []
        for thr in thresholds:
            y_pred_binary = (y_pred_proba >= thr).astype(int)
            accuracy = (y_pred_binary == y_true).mean()
            accuracies.append(accuracy)

        best_idx = np.argmax(accuracies)
        optimal_threshold = thresholds[best_idx]
        optimal_accuracy = accuracies[best_idx]

        # Calculate metrics at different thresholds
        metrics_by_threshold = {}
        for thr in [0.5, 0.6, 0.7, 0.8]:
            y_pred_binary = (y_pred_proba >= thr).astype(int)
            accuracy = (y_pred_binary == y_true).mean()
            precision = (
                y_true[y_pred_binary == 1].sum() / y_pred_binary.sum()
                if y_pred_binary.sum() > 0
                else 0.0
            )
            recall = y_true[y_pred_binary == 1].sum() / y_true.sum() if y_true.sum() > 0 else 0.0

            metrics_by_threshold[float(thr)] = {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "n_predictions": int(y_pred_binary.sum()),
            }

        return {
            "regime": regime_name,
            "n_samples": int(len(y_true)),
            "base_rate": float(y_true.mean()),  # Actual profit rate
            "brier_score": float(brier),
            "log_loss": float(logloss),
            "calibration_error": float(calibration_error),
            "ic": float(ic),
            "ic_p_value": float(p_value),
            "optimal_threshold": float(optimal_threshold),
            "optimal_accuracy": float(optimal_accuracy),
            "calibration_curve": {
                "predicted_probs": prob_pred.tolist(),
                "true_frequencies": prob_true.tolist(),
            },
            "metrics_by_threshold": metrics_by_threshold,
        }

    except Exception as e:
        return {
            "regime": regime_name,
            "n_samples": len(y_true),
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Analyze ML calibration quality by regime")
    parser.add_argument("--model", required=True, help="Path to model JSON")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", default="1h", help="Timeframe")
    parser.add_argument("--output", help="Output JSON path")

    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: Model not found: {model_path}")
        sys.exit(1)

    # Load model
    with open(model_path) as f:
        model_config = json.load(f)

    # Use args or try to extract from filename
    symbol = args.symbol
    timeframe = args.timeframe

    # Try to parse from filename (e.g., "tBTCUSD_1h_v3.json")
    try:
        parts = model_path.stem.split("_")
        if len(parts) >= 2:
            symbol = parts[0]
            timeframe = parts[1]
    except Exception as e:
        print(f"Failed to parse symbol/timeframe from filename: {e}")

    print("=" * 80)
    print("ML CALIBRATION ANALYSIS BY REGIME")
    print("=" * 80)
    print(f"Model: {model_path.name}")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print("=" * 80)

    # Load features
    print("\n[LOAD] Loading features...")
    features_df = load_features(symbol, timeframe)

    # Load candles for regime classification
    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path)

    # Load model for predictions
    from core.strategy.prob_model import predict_proba

    # Get feature columns
    feature_cols = [col for col in features_df.columns if col != "timestamp"]
    X = features_df[feature_cols].values

    # Get predictions using model weights
    schema = model_config.get("schema", feature_cols)
    buy_w = model_config.get("buy", {}).get("w")
    buy_b = model_config.get("buy", {}).get("b", 0.0)
    calib_buy = (
        model_config.get("buy", {}).get("calib", {}).get("a", 1.0),
        model_config.get("buy", {}).get("calib", {}).get("b", 0.0),
    )

    # Predict for each sample
    predictions = []
    for i in range(len(X)):
        feats_dict = {col: X[i, j] for j, col in enumerate(feature_cols)}
        probas = predict_proba(
            feats_dict,
            schema=schema,
            buy_w=buy_w,
            buy_b=buy_b,
            calib_buy=calib_buy,
        )
        predictions.append(probas["buy"])

    predictions = np.array(predictions)

    # Calculate forward returns for labels
    close_prices = candles_df["close"]
    forward_returns = close_prices.pct_change(10).shift(-10)
    binary_labels = (forward_returns > 0).astype(int).values

    # Align lengths
    min_len = min(len(predictions), len(binary_labels), len(close_prices))
    predictions = predictions[:min_len]
    binary_labels = binary_labels[:min_len]
    returns = candles_df["close"].pct_change().iloc[:min_len]
    closes = close_prices.iloc[:min_len]

    # Classify regimes
    print("[CLASSIFY] Detecting regimes...")
    vol_regimes = classify_volatility_regime(returns, window=50)
    trend_regimes = classify_trend_regime(closes, window=50)

    # Analyze by volatility regime
    print("\n" + "=" * 80)
    print("ANALYSIS BY VOLATILITY REGIME")
    print("=" * 80)

    results = {"model": str(model_path.name), "symbol": symbol, "timeframe": timeframe}

    vol_regime_results = {}
    for regime in ["HighVol", "LowVol"]:
        mask = (vol_regimes == regime).values
        if mask.sum() < 20:
            print(f"\n{regime}: SKIPPED (insufficient samples: {mask.sum()})")
            continue

        regime_preds = predictions[mask]
        regime_labels = binary_labels[mask]

        result = analyze_calibration_for_regime(regime_labels, regime_preds, regime)
        vol_regime_results[regime] = result

        print(f"\n{regime} ({result['n_samples']} samples):")
        print(f"  Base rate (actual profit %):  {result['base_rate']:.1%}")
        print(f"  Brier score (lower=better):   {result['brier_score']:.4f}")
        print(f"  Calibration error:             {result['calibration_error']:.4f}")
        print(
            f"  IC:                            {result['ic']:+.4f} (p={result['ic_p_value']:.4f})"
        )
        print(f"  Optimal threshold:             {result['optimal_threshold']:.2f}")
        print(f"  Optimal accuracy:              {result['optimal_accuracy']:.1%}")

        # Show threshold analysis
        print("\n  Metrics by threshold:")
        for thr, metrics in sorted(result["metrics_by_threshold"].items()):
            print(
                f"    {thr:.1f}: Acc={metrics['accuracy']:.1%}, "
                f"Prec={metrics['precision']:.1%}, "
                f"Trades={metrics['n_predictions']}"
            )

    results["volatility_regimes"] = vol_regime_results

    # Analyze by trend regime
    print("\n" + "=" * 80)
    print("ANALYSIS BY TREND REGIME")
    print("=" * 80)

    trend_regime_results = {}
    for regime in ["Bear", "Bull", "Ranging"]:
        mask = (trend_regimes == regime).values
        if mask.sum() < 20:
            print(f"\n{regime}: SKIPPED (insufficient samples: {mask.sum()})")
            continue

        regime_preds = predictions[mask]
        regime_labels = binary_labels[mask]

        result = analyze_calibration_for_regime(regime_labels, regime_preds, regime)
        trend_regime_results[regime] = result

        print(f"\n{regime} ({result['n_samples']} samples):")
        print(f"  Base rate (actual profit %):  {result['base_rate']:.1%}")
        print(f"  Brier score (lower=better):   {result['brier_score']:.4f}")
        print(f"  Calibration error:             {result['calibration_error']:.4f}")
        print(
            f"  IC:                            {result['ic']:+.4f} (p={result['ic_p_value']:.4f})"
        )
        print(f"  Optimal threshold:             {result['optimal_threshold']:.2f}")
        print(f"  Optimal accuracy:              {result['optimal_accuracy']:.1%}")

        print("\n  Metrics by threshold:")
        for thr, metrics in sorted(result["metrics_by_threshold"].items()):
            print(
                f"    {thr:.1f}: Acc={metrics['accuracy']:.1%}, "
                f"Prec={metrics['precision']:.1%}, "
                f"Trades={metrics['n_predictions']}"
            )

    results["trend_regimes"] = trend_regime_results

    # Summary and recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    print("\nSuggested regime-specific thresholds (based on optimal accuracy):")
    print("\nconfig/runtime.json:")
    print('"thresholds": {')
    print('  "entry_conf_overall": 0.6,')
    print('  "regime_proba": {')

    # Get optimal thresholds
    for regime, result in trend_regime_results.items():
        if "optimal_threshold" in result:
            print(f'    "{regime.lower()}": {result["optimal_threshold"]:.2f},')

    print("  }")
    print("}")

    # Calibration quality assessment
    print("\nCalibration Quality Assessment:")
    for regime, result in {**vol_regime_results, **trend_regime_results}.items():
        if "calibration_error" in result:
            error = result["calibration_error"]
            status = "GOOD" if error < 0.05 else "NEEDS_RECALIB" if error < 0.10 else "POOR"
            print(f"  {regime}: {error:.4f} [{status}]")

    # Save results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\n[SAVED] Results: {output_path}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
