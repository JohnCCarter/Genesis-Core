"""
Evaluate trained ML models.

Usage:
    python scripts/evaluate_model.py --model results/models/tBTCUSD_15m_v2.json
    python scripts/evaluate_model.py --model results/models/tBTCUSD_15m_v2.json --output results/evaluation/
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

from core.ml.evaluation import generate_evaluation_report, save_evaluation_report
from core.ml.labeling import align_features_with_labels, generate_labels


def load_trained_model(model_path: Path) -> dict:
    """Load trained model from JSON file."""
    with open(model_path) as f:
        return json.load(f)


def create_model_from_json(model_json: dict) -> tuple[LogisticRegression, LogisticRegression]:
    """Create sklearn models from JSON format."""
    # Buy model
    buy_model = LogisticRegression()
    buy_model.coef_ = np.array([model_json["buy"]["w"]])
    buy_model.intercept_ = np.array([model_json["buy"]["b"]])
    buy_model.classes_ = np.array([0, 1])

    # Sell model
    sell_model = LogisticRegression()
    sell_model.coef_ = np.array([model_json["sell"]["w"]])
    sell_model.intercept_ = np.array([model_json["sell"]["b"]])
    sell_model.classes_ = np.array([0, 1])

    return buy_model, sell_model


def evaluate_model_on_data(
    model_json: dict,
    features_df: pd.DataFrame,
    close_prices: list[float],
    lookahead_bars: int = 10,
    threshold_pct: float = 0.0,
) -> dict:
    """Evaluate model on historical data."""
    # Generate labels
    labels = generate_labels(close_prices, lookahead_bars, threshold_pct)

    # Align features and labels
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)

    if end_idx <= start_idx:
        raise ValueError("No valid labels found after alignment")

    # Extract aligned data
    aligned_features = features_df.iloc[start_idx:end_idx]
    aligned_labels = np.array(labels[start_idx:end_idx])

    # Remove timestamp column
    feature_columns = [col for col in aligned_features.columns if col != "timestamp"]
    X = aligned_features[feature_columns].values
    feature_names = feature_columns

    # Handle NaN values
    nan_mask = np.isnan(X).any(axis=1)
    if nan_mask.any():
        print(f"[CLEAN] Removing {nan_mask.sum()} rows with NaN values")
        X = X[~nan_mask]
        aligned_labels = aligned_labels[~nan_mask]

    # Create models from JSON
    buy_model, sell_model = create_model_from_json(model_json)

    # Get predictions
    buy_pred_proba = buy_model.predict_proba(X)[:, 1]
    sell_pred_proba = sell_model.predict_proba(X)[:, 1]

    # Generate reports
    buy_report = generate_evaluation_report(
        aligned_labels, buy_pred_proba, model_name=f"{model_json.get('version', 'v1')}_Buy"
    )

    sell_report = generate_evaluation_report(
        1 - aligned_labels, sell_pred_proba, model_name=f"{model_json.get('version', 'v1')}_Sell"
    )

    return {
        "buy_model": buy_report,
        "sell_model": sell_report,
        "data_info": {
            "n_samples": len(X),
            "feature_names": feature_names,
            "lookahead_bars": lookahead_bars,
            "threshold_pct": threshold_pct,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained ML models")
    parser.add_argument("--model", type=str, required=True, help="Path to trained model JSON")
    parser.add_argument(
        "--symbol", type=str, help="Symbol (auto-detected from filename if not provided)"
    )
    parser.add_argument(
        "--timeframe", type=str, help="Timeframe (auto-detected from filename if not provided)"
    )
    parser.add_argument("--lookahead", type=int, default=10, help="Lookahead bars for evaluation")
    parser.add_argument("--threshold", type=float, default=0.0, help="Price change threshold %")
    parser.add_argument("--output", type=str, default="results/evaluation", help="Output directory")
    parser.add_argument(
        "--format", type=str, default="json", choices=["json", "html"], help="Output format"
    )

    args = parser.parse_args()

    try:
        model_path = Path(args.model)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        # Auto-detect symbol and timeframe from filename
        if not args.symbol or not args.timeframe:
            # Expected format: tBTCUSD_15m_v2.json
            stem = model_path.stem
            parts = stem.split("_")
            if len(parts) >= 2:
                detected_symbol = parts[0]
                detected_timeframe = parts[1]
            else:
                raise ValueError(
                    f"Cannot auto-detect symbol/timeframe from filename: {model_path.name}"
                )

        symbol = args.symbol or detected_symbol
        timeframe = args.timeframe or detected_timeframe

        print(f"[LOAD] Loading model: {model_path}")
        model_json = load_trained_model(model_path)

        print(f"[DATA] Loading features and candles for {symbol} {timeframe}")
        features_path = Path("data/features") / f"{symbol}_{timeframe}_features.parquet"
        candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"

        if not features_path.exists():
            raise FileNotFoundError(f"Features file not found: {features_path}")
        if not candles_path.exists():
            raise FileNotFoundError(f"Candles file not found: {candles_path}")

        features_df = pd.read_parquet(features_path)
        candles_df = pd.read_parquet(candles_path)
        close_prices = candles_df["close"].tolist()

        print(f"[EVAL] Evaluating model on {len(features_df)} samples")

        # Evaluate model
        evaluation_results = evaluate_model_on_data(
            model_json, features_df, close_prices, args.lookahead, args.threshold
        )

        # Save results
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save combined report
        combined_report = {
            "model_info": {
                "model_path": str(model_path),
                "symbol": symbol,
                "timeframe": timeframe,
                "version": model_json.get("version", "v1"),
                "lookahead_bars": args.lookahead,
                "threshold_pct": args.threshold,
            },
            "evaluation": evaluation_results,
        }

        output_path = output_dir / f"{symbol}_{timeframe}_evaluation.{args.format}"
        save_evaluation_report(combined_report, output_path, format=args.format)

        # Print summary
        print("\n" + "=" * 60)
        print("EVALUATION COMPLETE")
        print("=" * 60)
        print(f"Model: {model_path.name}")
        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Samples: {evaluation_results['data_info']['n_samples']}")
        print(f"Features: {', '.join(evaluation_results['data_info']['feature_names'])}")

        buy_metrics = evaluation_results["buy_model"]["classification"]["basic_metrics"]
        sell_metrics = evaluation_results["sell_model"]["classification"]["basic_metrics"]

        print("\nBuy Model:")
        print(f"  AUC: {buy_metrics['roc_auc']:.4f}")
        print(f"  Accuracy: {buy_metrics['accuracy']:.4f}")
        print(f"  Log Loss: {buy_metrics['log_loss']:.4f}")

        print("\nSell Model:")
        print(f"  AUC: {sell_metrics['roc_auc']:.4f}")
        print(f"  Accuracy: {sell_metrics['accuracy']:.4f}")
        print(f"  Log Loss: {sell_metrics['log_loss']:.4f}")

        print(f"\nReport saved: {output_path}")

    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
