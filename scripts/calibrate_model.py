"""
Calibrate trained ML models.

Usage:
    python scripts/calibrate_model.py --model results/models/tBTCUSD_15m_v2.json
    python scripts/calibrate_model.py --model results/models/tBTCUSD_15m_v2.json --method platt
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

from core.ml.calibration import (
    calibrate_model,
    compare_calibration_methods,
    save_calibration_params,
)
from core.ml.labeling import generate_labels, align_features_with_labels


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


def calibrate_model_on_data(
    model_json: dict,
    features_df: pd.DataFrame,
    close_prices: list[float],
    lookahead_bars: int = 10,
    threshold_pct: float = 0.0,
    method: str = "auto",
) -> dict:
    """Calibrate model on historical data."""
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
    
    # Calibrate models
    if method == "auto":
        # Compare methods and choose best
        print("[CALIB] Comparing calibration methods for buy model...")
        buy_comparison = compare_calibration_methods(aligned_labels, buy_pred_proba)
        buy_method = buy_comparison["best_method"]
        buy_improvement = buy_comparison["best_improvement"]
        
        print("[CALIB] Comparing calibration methods for sell model...")
        sell_comparison = compare_calibration_methods(1 - aligned_labels, sell_pred_proba)
        sell_method = sell_comparison["best_method"]
        sell_improvement = sell_comparison["best_improvement"]
        
        print(f"[CALIB] Buy model: {buy_method} (improvement: {buy_improvement:.6f})")
        print(f"[CALIB] Sell model: {sell_method} (improvement: {sell_improvement:.6f})")
        
    else:
        buy_method = sell_method = method
        buy_improvement = sell_improvement = 0.0
    
    # Apply calibration
    buy_calibrated = calibrate_model(aligned_labels, buy_pred_proba, method=buy_method)
    sell_calibrated = calibrate_model(1 - aligned_labels, sell_pred_proba, method=sell_method)
    
    return {
        "buy_calibration": buy_calibrated,
        "sell_calibration": sell_calibrated,
        "data_info": {
            "n_samples": len(X),
            "feature_names": feature_names,
            "lookahead_bars": lookahead_bars,
            "threshold_pct": threshold_pct,
        },
        "method_info": {
            "buy_method": buy_method,
            "sell_method": sell_method,
            "buy_improvement": buy_improvement,
            "sell_improvement": sell_improvement,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Calibrate trained ML models")
    parser.add_argument("--model", type=str, required=True, help="Path to trained model JSON")
    parser.add_argument("--symbol", type=str, help="Symbol (auto-detected from filename if not provided)")
    parser.add_argument("--timeframe", type=str, help="Timeframe (auto-detected from filename if not provided)")
    parser.add_argument("--method", type=str, default="auto", choices=["auto", "platt", "isotonic"], help="Calibration method")
    parser.add_argument("--lookahead", type=int, default=10, help="Lookahead bars for calibration")
    parser.add_argument("--threshold", type=float, default=0.0, help="Price change threshold %")
    parser.add_argument("--output", type=str, default="results/calibration", help="Output directory")
    
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
                raise ValueError(f"Cannot auto-detect symbol/timeframe from filename: {model_path.name}")
        
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
        
        print(f"[CALIB] Calibrating model on {len(features_df)} samples")
        
        # Calibrate model
        calibration_results = calibrate_model_on_data(
            model_json, features_df, close_prices, args.lookahead, args.threshold, args.method
        )
        
        # Save calibration parameters
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save buy calibration
        buy_output_path = output_dir / f"{symbol}_{timeframe}_buy_calibration.json"
        save_calibration_params(calibration_results["buy_calibration"], buy_output_path)
        
        # Save sell calibration
        sell_output_path = output_dir / f"{symbol}_{timeframe}_sell_calibration.json"
        save_calibration_params(calibration_results["sell_calibration"], sell_output_path)
        
        # Save combined report (remove numpy arrays for JSON serialization)
        combined_report = {
            "model_info": {
                "model_path": str(model_path),
                "symbol": symbol,
                "timeframe": timeframe,
                "version": model_json.get("version", "v1"),
                "lookahead_bars": args.lookahead,
                "threshold_pct": args.threshold,
            },
            "calibration": {
                "buy_calibration": {
                    "method": calibration_results["buy_calibration"]["method"],
                    "parameters": calibration_results["buy_calibration"]["parameters"],
                },
                "sell_calibration": {
                    "method": calibration_results["sell_calibration"]["method"],
                    "parameters": calibration_results["sell_calibration"]["parameters"],
                },
                "data_info": calibration_results["data_info"],
                "method_info": calibration_results["method_info"],
            },
        }
        
        report_output_path = output_dir / f"{symbol}_{timeframe}_calibration_report.json"
        with open(report_output_path, "w") as f:
            json.dump(combined_report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("CALIBRATION COMPLETE")
        print("=" * 60)
        print(f"Model: {model_path.name}")
        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Samples: {calibration_results['data_info']['n_samples']}")
        print(f"Features: {', '.join(calibration_results['data_info']['feature_names'])}")
        
        method_info = calibration_results["method_info"]
        print(f"\nCalibration Methods:")
        print(f"  Buy: {method_info['buy_method']} (improvement: {method_info['buy_improvement']:.6f})")
        print(f"  Sell: {method_info['sell_method']} (improvement: {method_info['sell_improvement']:.6f})")
        
        print(f"\nCalibration files saved:")
        print(f"  Buy: {buy_output_path}")
        print(f"  Sell: {sell_output_path}")
        print(f"  Report: {report_output_path}")
        
    except Exception as e:
        print(f"\n[ERROR] Calibration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
