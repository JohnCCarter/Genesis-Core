"""
Select the best model (champion) from multiple candidates.

Usage:
    python scripts/select_champion.py --symbol tBTCUSD --timeframe 15m
    python scripts/select_champion.py --symbol tBTCUSD --timeframe 15m --output results/champion/
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

from core.ml.calibration import apply_calibration_from_params, load_calibration_params
from core.ml.decision_matrix import ChampionDecisionMatrix, ModelMetrics
from core.ml.evaluation import generate_evaluation_report
from core.ml.labeling import align_features_with_labels, generate_labels
from core.ml.visualization import create_champion_summary, create_radar_chart
from core.strategy.prob_model import predict_proba_for
from core.utils import get_candles_path


def load_baseline_model(symbol: str, timeframe: str) -> dict:
    """Load baseline model (placeholder weights)."""
    from core.strategy.model_registry import ModelRegistry

    registry = ModelRegistry()
    model_data = registry.get_meta(symbol, timeframe)

    return {
        "name": "Baseline",
        "type": "placeholder",
        "model_data": model_data,
    }


def load_ml_model(model_path: Path) -> dict:
    """Load ML-trained model."""
    with open(model_path) as f:
        model_json = json.load(f)

    return {
        "name": "ML-Trained",
        "type": "ml",
        "model_data": model_json,
    }


def load_calibrated_model(
    model_path: Path,
    calibration_dir: Path,
    symbol: str,
    timeframe: str,
) -> dict:
    """Load calibrated model."""
    with open(model_path) as f:
        model_json = json.load(f)

    # Load calibration parameters
    buy_calib_path = calibration_dir / f"{symbol}_{timeframe}_buy_calibration.json"
    sell_calib_path = calibration_dir / f"{symbol}_{timeframe}_sell_calibration.json"

    if not buy_calib_path.exists() or not sell_calib_path.exists():
        raise FileNotFoundError(f"Calibration files not found in {calibration_dir}")

    buy_calib = load_calibration_params(buy_calib_path)
    sell_calib = load_calibration_params(sell_calib_path)

    return {
        "name": "Calibrated",
        "type": "calibrated",
        "model_data": model_json,
        "calibration": {
            "buy": buy_calib,
            "sell": sell_calib,
        },
    }


def create_sklearn_model_from_json(
    model_json: dict,
) -> tuple[LogisticRegression, LogisticRegression]:
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


def evaluate_model(
    model_info: dict,
    features_df: pd.DataFrame,
    close_prices: list[float],
    lookahead_bars: int = 10,
    threshold_pct: float = 0.0,
) -> dict:
    """Evaluate a single model on historical data."""
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

    # Handle NaN values
    nan_mask = np.isnan(X).any(axis=1)
    if nan_mask.any():
        print(f"[CLEAN] Removing {nan_mask.sum()} rows with NaN values")
        X = X[~nan_mask]
        aligned_labels = aligned_labels[~nan_mask]
        aligned_features = aligned_features.iloc[~nan_mask]

    # Get predictions based on model type
    if model_info["type"] == "placeholder":
        # Use baseline model (current prob_model)
        y_pred_proba = []
        for _i, row in aligned_features.iterrows():
            # Handle NaN values
            ema_val = row["ema_delta_pct"]
            rsi_val = row["rsi"]

            if pd.isna(ema_val) or pd.isna(rsi_val):
                y_pred_proba.append(0.5)  # Neutral prediction for NaN
                continue

            feats = {"ema_delta_pct": float(ema_val), "rsi": float(rsi_val)}
            probas, _ = predict_proba_for("tBTCUSD", "15m", feats)
            y_pred_proba.append(probas["buy"])

        y_pred_proba = np.array(y_pred_proba)

    elif model_info["type"] == "ml":
        # Use ML-trained model
        buy_model, sell_model = create_sklearn_model_from_json(model_info["model_data"])
        y_pred_proba = buy_model.predict_proba(X)[:, 1]

    elif model_info["type"] == "calibrated":
        # Use calibrated model
        buy_model, sell_model = create_sklearn_model_from_json(model_info["model_data"])
        raw_proba = buy_model.predict_proba(X)[:, 1]

        # Apply calibration
        buy_calib = model_info["calibration"]["buy"]
        y_pred_proba = apply_calibration_from_params(raw_proba, buy_calib)

    else:
        raise ValueError(f"Unknown model type: {model_info['type']}")

    # Generate evaluation report
    report = generate_evaluation_report(aligned_labels, y_pred_proba, model_name=model_info["name"])

    return {
        "model_info": model_info,
        "evaluation": report,
        "data_info": {
            "n_samples": len(X),
            "feature_names": feature_columns,
            "lookahead_bars": lookahead_bars,
            "threshold_pct": threshold_pct,
        },
    }


def extract_metrics_from_results(result: dict) -> ModelMetrics:
    """Extract ModelMetrics from evaluation results."""
    eval_data = result["evaluation"]
    basic = eval_data["classification"]["basic_metrics"]

    # Default values for trading metrics (to be computed from backtest)
    profit_factor = 1.0  # Placeholder
    sharpe_ratio = 0.0  # Placeholder
    max_drawdown = -0.15  # Placeholder
    win_rate = 0.5  # Placeholder
    avg_trade_duration = 10.0  # Placeholder
    num_trades = 100  # Placeholder
    consistency = 0.7  # Placeholder

    return ModelMetrics(
        auc=basic["roc_auc"],
        accuracy=basic["accuracy"],
        log_loss=basic["log_loss"],
        profit_factor=profit_factor,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
        avg_trade_duration=avg_trade_duration,
        num_trades=num_trades,
        consistency=consistency,
    )


def compare_models_with_matrix(model_results: list[dict], weights: dict[str, float]) -> dict:
    """
    Compare models using weighted decision matrix.

    Args:
        model_results: List of model evaluation results
        weights: Dict of metric weights

    Returns:
        Dict with comparison results and champion
    """
    # Create decision matrix
    matrix = ChampionDecisionMatrix(weights)

    # Extract metrics for each model
    models_metrics = {}
    for result in model_results:
        model_name = result["model_info"]["name"]
        metrics = extract_metrics_from_results(result)
        models_metrics[model_name] = metrics

    # Get champion and ranking
    champion_name, champion_score, ranking = matrix.get_champion(models_metrics)

    # Build comparison data with full results
    comparison_data = []
    for _, row in ranking.iterrows():
        model_name = row["model"]
        # Find matching result
        model_result = next(
            (r for r in model_results if r["model_info"]["name"] == model_name), None
        )

        comparison_data.append(
            {
                "name": model_name,
                "type": model_result["model_info"]["type"] if model_result else "unknown",
                "score": row["total_score"],
                "metrics": models_metrics[model_name],
                "result": model_result,
            }
        )

    best_model = comparison_data[0]

    return {
        "method": "decision_matrix",
        "weights": weights,
        "best_model": best_model,
        "all_models": comparison_data,
        "ranking_df": ranking,
        "champion_name": champion_name,
        "champion_score": champion_score,
    }


def compare_models(
    model_results: list[dict],
    metric: str = "roc_auc",
) -> dict:
    """Compare multiple models and select the best one."""
    if not model_results:
        raise ValueError("No model results to compare")

    # Extract metrics for comparison
    comparison_data = []
    for result in model_results:
        model_name = result["model_info"]["name"]
        model_type = result["model_info"]["type"]

        # Get the specified metric
        if metric == "roc_auc":
            score = result["evaluation"]["classification"]["basic_metrics"]["roc_auc"]
        elif metric == "accuracy":
            score = result["evaluation"]["classification"]["basic_metrics"]["accuracy"]
        elif metric == "log_loss":
            score = result["evaluation"]["classification"]["basic_metrics"]["log_loss"]
        elif metric == "brier_score":
            score = result["evaluation"]["classification"]["basic_metrics"]["brier_score"]
        elif metric == "f1_score":
            score = result["evaluation"]["classification"]["classification_metrics"]["f1_score"]
        else:
            raise ValueError(f"Unknown metric: {metric}")

        comparison_data.append(
            {
                "name": model_name,
                "type": model_type,
                "score": score,
                "result": result,
            }
        )

    # Sort by score (higher is better for most metrics, lower for log_loss and brier_score)
    if metric in ["log_loss", "brier_score"]:
        comparison_data.sort(key=lambda x: x["score"])  # Lower is better
        best_model = comparison_data[0]
    else:
        comparison_data.sort(key=lambda x: x["score"], reverse=True)  # Higher is better
        best_model = comparison_data[0]

    return {
        "metric": metric,
        "best_model": best_model,
        "all_models": comparison_data,
        "ranking": comparison_data,
    }


def generate_champion_report(
    comparison_results: dict,
    output_path: Path,
) -> None:
    """Generate comprehensive champion selection report."""
    best_model = comparison_results["best_model"]
    all_models = comparison_results["all_models"]
    metric = comparison_results["metric"]

    report = {
        "champion_selection": {
            "metric_used": metric,
            "best_model": {
                "name": best_model["name"],
                "type": best_model["type"],
                "score": best_model["score"],
            },
            "all_models": [
                {
                    "name": model["name"],
                    "type": model["type"],
                    "score": model["score"],
                }
                for model in all_models
            ],
        },
        "detailed_results": {
            model["name"]: {
                "model_info": model["result"]["model_info"],
                "evaluation": model["result"]["evaluation"],
                "data_info": model["result"]["data_info"],
            }
            for model in all_models
        },
    }

    # Save report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Select the best model (champion)")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe (e.g., 15m)")
    parser.add_argument("--ml-model", type=str, help="Path to ML-trained model JSON")
    parser.add_argument(
        "--calibration-dir", type=str, default="results/calibration", help="Calibration directory"
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="balanced",
        choices=["balanced", "conservative", "aggressive", "quality"],
        help="Weight profile for decision matrix",
    )
    parser.add_argument(
        "--weights-config",
        type=str,
        default="config/champion_weights.json",
        help="Path to weights configuration file",
    )
    parser.add_argument(
        "--metric",
        type=str,
        default="decision_matrix",
        choices=["decision_matrix", "roc_auc", "accuracy", "log_loss", "brier_score", "f1_score"],
        help="Selection method: decision_matrix (recommended) or single metric",
    )
    parser.add_argument("--lookahead", type=int, default=10, help="Lookahead bars for evaluation")
    parser.add_argument("--threshold", type=float, default=0.0, help="Price change threshold %")
    parser.add_argument("--output", type=str, default="results/champion", help="Output directory")
    parser.add_argument(
        "--visualize",
        action="store_true",
        default=True,
        help="Generate visualization charts (default: True)",
    )
    parser.add_argument(
        "--no-visualize", dest="visualize", action="store_false", help="Skip visualization"
    )

    args = parser.parse_args()

    try:
        symbol = args.symbol
        timeframe = args.timeframe

        print(f"[CHAMPION] Selecting best model for {symbol} {timeframe}")

        # Load data
        print("[DATA] Loading features and candles...")
        features_path = Path("data/features") / f"{symbol}_{timeframe}_features.parquet"

        if not features_path.exists():
            raise FileNotFoundError(f"Features file not found: {features_path}")

        from core.utils.data_loader import load_features

        features_df = load_features(symbol, timeframe)

        try:
            candles_path = get_candles_path(symbol, timeframe)
        except FileNotFoundError as e:
            print(f"[WARN] Missing candles for {symbol} {timeframe}: {e}")
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "status": "missing_candles",
            }

        candles = pd.read_parquet(candles_path)
        close_prices = candles["close"].tolist()

        # Load models
        models_to_evaluate = []

        # 1. Baseline model
        print("[MODEL] Loading baseline model...")
        baseline_model = load_baseline_model(symbol, timeframe)
        models_to_evaluate.append(baseline_model)

        # 2. ML-trained model
        if args.ml_model:
            ml_model_path = Path(args.ml_model)
            if ml_model_path.exists():
                print("[MODEL] Loading ML-trained model...")
                ml_model = load_ml_model(ml_model_path)
                models_to_evaluate.append(ml_model)
            else:
                print(f"[WARN] ML model not found: {ml_model_path}")

        # 3. Calibrated model
        calibration_dir = Path(args.calibration_dir)
        if calibration_dir.exists():
            # Look for ML model in results/models
            ml_model_path = Path("results/models") / f"{symbol}_{timeframe}_v2.json"
            if ml_model_path.exists():
                print("[MODEL] Loading calibrated model...")
                try:
                    calibrated_model = load_calibrated_model(
                        ml_model_path, calibration_dir, symbol, timeframe
                    )
                    models_to_evaluate.append(calibrated_model)
                except FileNotFoundError as e:
                    print(f"[WARN] Calibrated model not available: {e}")

        if len(models_to_evaluate) < 2:
            raise ValueError("Need at least 2 models to compare")

        # Evaluate all models
        print(f"[EVAL] Evaluating {len(models_to_evaluate)} models...")
        model_results = []
        for model_info in models_to_evaluate:
            print(f"[EVAL] Evaluating {model_info['name']}...")
            result = evaluate_model(
                model_info, features_df, close_prices, args.lookahead, args.threshold
            )
            model_results.append(result)

        # Compare models
        if args.metric == "decision_matrix":
            # Load weights from config
            print(f"[COMPARE] Using decision matrix with profile: {args.profile}")
            weights_path = Path(args.weights_config)
            if not weights_path.exists():
                raise FileNotFoundError(f"Weights config not found: {weights_path}")

            with open(weights_path) as f:
                weights_config = json.load(f)

            profile_weights = weights_config["profiles"][args.profile]["weights"]
            print(f"[WEIGHTS] {profile_weights}")

            comparison_results = compare_models_with_matrix(model_results, profile_weights)
        else:
            print(f"[COMPARE] Comparing models using single metric: {args.metric}...")
            comparison_results = compare_models(model_results, args.metric)

        # Generate report
        output_dir = Path(args.output)
        report_path = output_dir / f"{symbol}_{timeframe}_champion_report.json"
        generate_champion_report(comparison_results, report_path)

        # Generate visualizations
        if args.visualize and args.metric == "decision_matrix":
            print("\n[VIZ] Generating visualizations...")
            try:
                # Extract normalized metrics for visualization
                models_normalized = {}
                for _, row in comparison_results["ranking_df"].iterrows():
                    model_name = row["model"]
                    # Get normalized values for key metrics
                    models_normalized[model_name] = {
                        metric: row[metric] for metric in profile_weights.keys() if metric in row
                    }

                # 1. Radar chart
                radar_path = output_dir / f"{symbol}_{timeframe}_radar_comparison.png"
                create_radar_chart(
                    models_normalized,
                    list(profile_weights.keys()),
                    radar_path,
                    title=f"Model Comparison - {symbol} {timeframe} ({args.profile} profile)",
                )
                print(f"   ✓ Radar chart: {radar_path}")

                # 2. Champion summary (comprehensive)
                summary_path = output_dir / f"{symbol}_{timeframe}_champion_summary.png"
                create_champion_summary(
                    comparison_results["ranking_df"],
                    profile_weights,
                    comparison_results["champion_name"],
                    summary_path,
                )
                print(f"   ✓ Champion summary: {summary_path}")

            except Exception as e:
                print(f"   ⚠ Visualization failed: {e}")
                print("   (Report still saved successfully)")

        # Print summary
        print("\n" + "=" * 80)
        print("CHAMPION SELECTION COMPLETE")
        print("=" * 80)
        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Method: {args.metric}")
        if args.metric == "decision_matrix":
            print(f"Profile: {args.profile}")
        print(f"Samples: {model_results[0]['data_info']['n_samples']}")

        best_model = comparison_results["best_model"]
        print(f"\n🏆 CHAMPION: {best_model['name']}")
        print(f"   Type: {best_model['type']}")
        if args.metric == "decision_matrix":
            print(f"   Total Score: {best_model['score']:.2f}/10.0")
        else:
            print(f"   {args.metric}: {best_model['score']:.6f}")

        print("\n[RESULTS] ALL MODELS:")
        for i, model in enumerate(comparison_results["all_models"], 1):
            marker = "[WINNER]" if model["name"] == best_model["name"] else f"{i}."
            print(f"   {marker} {model['name']}: {model['score']:.6f}")

        print(f"\n[SAVE] Report saved: {report_path}")

    except Exception as e:
        print(f"\n[ERROR] Champion selection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
