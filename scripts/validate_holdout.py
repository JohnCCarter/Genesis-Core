"""
Validate model on holdout set.

This script performs final, unbiased validation on the reserved holdout set (20% of data)
that was never used during training or validation. It provides true out-of-sample metrics.

Usage:
    python scripts/validate_holdout.py --model config/models/champion_20250108.json

Key Metrics:
- Information Coefficient (IC): Spearman correlation between predictions and forward returns
- AUC: Classification performance
- Q5-Q1 Spread: Economic significance (top quintile - bottom quintile returns)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.ml.prob_model import ProbModel  # noqa: I001
from core.utils.data_loader import load_features  # noqa: I001


def calculate_forward_returns(close_prices: pd.Series, horizon: int) -> pd.Series:
    """Calculate forward returns for a given horizon."""
    return close_prices.pct_change(horizon).shift(-horizon)


def calculate_ic(predictions: np.ndarray, returns: np.ndarray) -> dict:
    """Calculate Information Coefficient and statistical significance."""
    mask = ~np.isnan(predictions) & ~np.isnan(returns)
    if mask.sum() < 10:
        return {"ic": 0.0, "p_value": 1.0, "n_samples": 0}

    pred_clean = predictions[mask]
    ret_clean = returns[mask]

    ic, p_value = spearmanr(pred_clean, ret_clean)
    return {"ic": float(ic), "p_value": float(p_value), "n_samples": int(mask.sum())}


def calculate_quintile_spread(predictions: np.ndarray, returns: np.ndarray) -> dict:
    """Calculate Q5-Q1 spread (top quintile - bottom quintile returns)."""
    mask = ~np.isnan(predictions) & ~np.isnan(returns)
    if mask.sum() < 10:
        return {"q5_mean": 0.0, "q1_mean": 0.0, "spread": 0.0}

    pred_clean = predictions[mask]
    ret_clean = returns[mask]

    # Divide into quintiles
    quintiles = pd.qcut(pred_clean, q=5, labels=False, duplicates="drop")
    q5_mask = quintiles == 4
    q1_mask = quintiles == 0

    q5_mean = ret_clean[q5_mask].mean() if q5_mask.sum() > 0 else 0.0
    q1_mean = ret_clean[q1_mask].mean() if q1_mask.sum() > 0 else 0.0
    spread = q5_mean - q1_mean

    return {
        "q5_mean": float(q5_mean),
        "q1_mean": float(q1_mean),
        "spread": float(spread),
    }


def validate_holdout(model_path: Path, verbose: bool = True) -> dict:
    """
    Validate model on reserved holdout set.

    Returns:
        dict: Validation metrics including IC, AUC, and Q5-Q1 spread
    """
    # Load model and metadata
    with open(model_path) as f:
        model_config = json.load(f)

    symbol = model_config["symbol"]
    timeframe = model_config["timeframe"]

    # Load holdout indices
    holdout_path = model_path.parent / f"{model_path.stem}_holdout_indices.json"
    if not holdout_path.exists():
        raise FileNotFoundError(
            f"Holdout indices not found: {holdout_path}\n"
            "This model was not trained with --use-holdout flag."
        )

    with open(holdout_path) as f:
        holdout_data = json.load(f)
        holdout_indices = holdout_data["holdout_indices"]

    if verbose:
        print(f"\n{'='*60}")
        print("HOLDOUT VALIDATION")
        print(f"{'='*60}")
        print(f"Model: {model_path.name}")
        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Holdout size: {len(holdout_indices)} samples")
        print(f"{'='*60}\n")

    # Load features and candles
    features_df = load_features(symbol, timeframe)

    # Extract holdout set
    holdout_features = features_df.iloc[holdout_indices].copy()

    # Load model
    model = ProbModel()
    model.load(str(model_path))

    # Get predictions
    X_holdout = holdout_features.drop(columns=["timestamp"], errors="ignore").values
    predictions = model.predict_proba(X_holdout)

    # Load candles for forward returns calculation
    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
    if not candles_path.exists():
        raise FileNotFoundError(f"Candles file not found: {candles_path}")

    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"]

    # Calculate forward returns (10-bar horizon)
    horizon = 10
    forward_returns = calculate_forward_returns(close_prices, horizon)

    # Extract returns for holdout indices
    holdout_returns = forward_returns.iloc[holdout_indices].values

    # Calculate metrics
    ic_metrics = calculate_ic(predictions, holdout_returns)
    quintile_metrics = calculate_quintile_spread(predictions, holdout_returns)

    # Calculate AUC (for binary labels if available)
    auc = None
    if "labels" in model_config:
        # Try to load labels from meta_labels file
        meta_labels_path = Path(f"data/meta_labels/{symbol}_{timeframe}_meta_labels.parquet")
        if meta_labels_path.exists():
            meta_labels_df = pd.read_parquet(meta_labels_path)
            if "label" in meta_labels_df.columns:
                holdout_labels = meta_labels_df["label"].iloc[holdout_indices].values
                mask = ~np.isnan(predictions) & ~np.isnan(holdout_labels)
                if mask.sum() > 10:
                    auc = roc_auc_score(holdout_labels[mask], predictions[mask])

    # Build results
    results = {
        "model": str(model_path.name),
        "symbol": symbol,
        "timeframe": timeframe,
        "holdout_size": len(holdout_indices),
        "ic": ic_metrics["ic"],
        "ic_p_value": ic_metrics["p_value"],
        "ic_n_samples": ic_metrics["n_samples"],
        "q5_mean_return": quintile_metrics["q5_mean"],
        "q1_mean_return": quintile_metrics["q1_mean"],
        "q5_q1_spread": quintile_metrics["spread"],
    }

    if auc is not None:
        results["auc"] = float(auc)

    # Print results
    if verbose:
        print("RESULTS:")
        print(f"  IC: {results['ic']:.4f} (p={results['ic_p_value']:.4f})")
        if auc is not None:
            print(f"  AUC: {auc:.4f}")
        print(
            f"  Q5-Q1 Spread: {results['q5_q1_spread']:.4f} "
            f"(Q5={results['q5_mean_return']:.4f}, Q1={results['q1_mean_return']:.4f})"
        )
        print(f"\n{'='*60}")

        # Interpretation
        print("\nINTERPRETATION:")
        if results["ic"] > 0.02 and results["ic_p_value"] < 0.05:
            print("  [SIG] IC > 0.02 and significant → Strong predictive power")
        elif results["ic"] > 0.01:
            print("  Weak IC → Marginal predictive power")
        else:
            print("  [WARN] IC < 0.01 → No predictive power")

        if results["q5_q1_spread"] > 0.002:
            print("  [SIG] Q5-Q1 > 0.2% → Economically significant")
        elif results["q5_q1_spread"] > 0.001:
            print("  Weak spread → Marginal economic value")
        else:
            print("  [WARN] Spread < 0.1% → No economic value")

        print(f"{'='*60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate model on holdout set")
    parser.add_argument("--model", type=str, required=True, help="Path to model JSON file")
    parser.add_argument("--output", type=str, help="Path to save results JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: Model file not found: {model_path}")
        sys.exit(1)

    results = validate_holdout(model_path, verbose=not args.quiet)

    # Save results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
