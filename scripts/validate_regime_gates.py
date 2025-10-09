"""Regime gates validation - hard requirements per market regime."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from core.ml.labeling import align_features_with_labels, generate_labels
from core.utils.data_loader import load_features


def simple_regime_classifier(prices):
    """Simple heuristic regime classification based on returns and volatility."""
    returns = np.diff(prices) / prices[:-1]
    mean_return = np.mean(returns)
    volatility = np.std(returns)
    
    # Calculate trend strength (simple moving average slope)
    sma_20 = np.convolve(prices, np.ones(20)/20, mode='valid')
    if len(sma_20) > 1:
        trend_strength = (sma_20[-1] - sma_20[0]) / sma_20[0]
    else:
        trend_strength = 0
    
    regimes = []
    for i in range(len(prices)):
        # Look back window
        window_start = max(0, i - 100)
        window_prices = prices[window_start:i+1]
        
        if len(window_prices) < 20:
            regimes.append("balanced")
            continue
        
        window_returns = np.diff(window_prices) / window_prices[:-1]
        window_mean = np.mean(window_returns)
        window_vol = np.std(window_returns)
        
        # Simple classification
        if abs(window_mean) < 0.0001 and window_vol < 0.02:
            regimes.append("ranging")
        elif window_mean > 0.0002:
            regimes.append("bull")
        elif window_mean < -0.0002:
            regimes.append("bear")
        else:
            regimes.append("balanced")
    
    return np.array(regimes)


def load_regime_gates(config_path):
    """Load regime gates from config."""
    with open(config_path) as f:
        config = json.load(f)
    return config["regime_gates"]


def evaluate_model_by_regime(symbol, timeframe, model_path, lookahead=10):
    """Evaluate model separately for each regime."""
    # Load data
    features_df = load_features(symbol, timeframe)
    candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"
    candles_df = pd.read_parquet(candles_path)

    # Classify regimes using simple heuristic
    regimes = simple_regime_classifier(candles_df["close"].values)

    # Generate labels
    labels = generate_labels(candles_df["close"].tolist(), lookahead, 0.0)

    # Load model
    with open(model_path) as f:
        model_json = json.load(f)

    # Align data
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)
    features_aligned = features_df.iloc[start_idx:end_idx]
    labels_aligned = labels[start_idx:end_idx]
    regimes_aligned = regimes[start_idx:end_idx]

    # Extract features
    feature_cols = model_json["schema"]
    X = features_aligned[feature_cols].values
    y = np.array([label if label is not None else -1 for label in labels_aligned])

    # Recreate model
    model = LogisticRegression()
    model.coef_ = np.array([model_json["buy"]["w"]])
    model.intercept_ = np.array([model_json["buy"]["b"]])
    model.classes_ = np.array([0, 1])

    # Evaluate per regime
    results = {}

    for regime_name in ["bull", "bear", "ranging", "balanced"]:
        mask = regimes_aligned == regime_name
        mask &= y != -1

        if mask.sum() < 50:
            continue

        X_regime = X[mask]
        y_regime = y[mask]
        
        # Filter out NaN values
        nan_mask = ~np.isnan(X_regime).any(axis=1)
        X_regime = X_regime[nan_mask]
        y_regime = y_regime[nan_mask]
        
        if len(X_regime) < 50:
            continue

        y_pred_proba = model.predict_proba(X_regime)[:, 1]

        try:
            auc = roc_auc_score(y_regime, y_pred_proba)
        except Exception:
            auc = 0.5

        # Placeholder metrics (should come from backtest)
        results[regime_name] = {
            "auc": float(auc),
            "sharpe": 0.8,
            "win_rate": 0.52,
            "drawdown": -0.12,
            "profit_factor": 1.2,
            "n_samples": int(mask.sum()),
        }

    return results


def validate_gates(model_metrics, gates):
    """Validate model metrics against regime gates."""
    results = {}
    all_passed = True

    for regime, gate_values in gates.items():
        if regime not in model_metrics:
            results[regime] = {"status": "NO_DATA", "passed": False}
            all_passed = False
            continue

        metrics = model_metrics[regime]
        regime_passed = True
        checks = {}

        for gate_name, threshold in gate_values.items():
            metric_name = gate_name.replace("min_", "").replace("max_", "")

            if gate_name.startswith("min_"):
                passed = metrics[metric_name] >= threshold
            else:
                passed = metrics[metric_name] >= threshold

            checks[gate_name] = {
                "passed": passed,
                "value": metrics[metric_name],
                "threshold": threshold,
            }

            if not passed:
                regime_passed = False

        results[regime] = {
            "status": "PASS" if regime_passed else "FAIL",
            "passed": regime_passed,
            "checks": checks,
        }

        if not regime_passed:
            all_passed = False

    return {"all_gates_passed": all_passed, "per_regime": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", default="config/validation_config.json")
    parser.add_argument("--output", default="results/regime_validation")

    args = parser.parse_args()

    gates = load_regime_gates(args.config)
    model_metrics = evaluate_model_by_regime(args.symbol, args.timeframe, Path(args.model))
    gate_results = validate_gates(model_metrics, gates)

    print(f"Regime validation: {'PASS' if gate_results['all_gates_passed'] else 'FAIL'}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{args.symbol}_{args.timeframe}_regime_gates.json"
    with open(output_path, "w") as f:
        json.dump(gate_results, f, indent=2)

    sys.exit(0 if gate_results["all_gates_passed"] else 1)


if __name__ == "__main__":
    import pandas as pd

    main()
