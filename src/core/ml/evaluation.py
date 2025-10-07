"""
Model evaluation utilities for ML training.

Provides comprehensive evaluation metrics and visualizations for trading models.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    log_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


def evaluate_binary_classification(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    y_pred: np.ndarray | None = None,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """
    Comprehensive evaluation of binary classification model.

    Args:
        y_true: True binary labels (0 or 1)
        y_pred_proba: Predicted probabilities for positive class
        y_pred: Predicted binary labels (optional, will be computed if None)
        threshold: Decision threshold for binary predictions

    Returns:
        Dictionary with comprehensive evaluation metrics
    """
    if y_pred is None:
        y_pred = (y_pred_proba >= threshold).astype(int)

    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred)

    # Handle log_loss for single class
    try:
        log_loss_score = log_loss(y_true, y_pred_proba)
    except ValueError:
        # Single class case
        log_loss_score = 0.0

    brier_score = brier_score_loss(y_true, y_pred_proba)

    # ROC metrics
    try:
        roc_auc = roc_auc_score(y_true, y_pred_proba)
        fpr, tpr, roc_thresholds = roc_curve(y_true, y_pred_proba)
    except ValueError:
        # Handle case where only one class is present
        roc_auc = 0.5
        fpr = tpr = roc_thresholds = np.array([])

    # Precision-Recall metrics
    try:
        precision, recall, pr_thresholds = precision_recall_curve(y_true, y_pred_proba)
        # Average precision (area under PR curve)
        avg_precision = np.trapz(precision, recall)
    except ValueError:
        precision = recall = pr_thresholds = np.array([])
        avg_precision = 0.0

    # Confusion matrix
    try:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    except ValueError:
        # Single class case - create dummy confusion matrix
        if np.all(y_true == 1):
            tn, fp, fn, tp = 0, 0, 0, len(y_true)
        else:
            tn, fp, fn, tp = len(y_true), 0, 0, 0

    # Derived metrics
    precision_score = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall_score = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1_score = (
        2 * (precision_score * recall_score) / (precision_score + recall_score)
        if (precision_score + recall_score) > 0
        else 0.0
    )

    # Class distribution
    n_samples = len(y_true)
    n_positive = np.sum(y_true)
    n_negative = n_samples - n_positive
    positive_rate = n_positive / n_samples

    return {
        "basic_metrics": {
            "accuracy": float(accuracy),
            "log_loss": float(log_loss_score),
            "brier_score": float(brier_score),
            "roc_auc": float(roc_auc),
            "avg_precision": float(avg_precision),
        },
        "classification_metrics": {
            "precision": float(precision_score),
            "recall": float(recall_score),
            "specificity": float(specificity),
            "f1_score": float(f1_score),
        },
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "class_distribution": {
            "n_samples": int(n_samples),
            "n_positive": int(n_positive),
            "n_negative": int(n_negative),
            "positive_rate": float(positive_rate),
        },
        "curves": {
            "roc": {
                "fpr": fpr.tolist(),
                "tpr": tpr.tolist(),
                "thresholds": roc_thresholds.tolist(),
            },
            "precision_recall": {
                "precision": precision.tolist(),
                "recall": recall.tolist(),
                "thresholds": pr_thresholds.tolist(),
            },
        },
        "threshold": float(threshold),
    }


def evaluate_calibration(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    n_bins: int = 10,
) -> dict[str, Any]:
    """
    Evaluate probability calibration using reliability diagram.

    Args:
        y_true: True binary labels
        y_pred_proba: Predicted probabilities
        n_bins: Number of bins for reliability diagram

    Returns:
        Dictionary with calibration metrics and reliability data
    """
    # Create bins
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    bin_centers = []
    bin_accuracies = []
    bin_counts = []
    bin_confidences = []

    ece = 0.0  # Expected Calibration Error

    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers, strict=False):
        # Find samples in this bin
        in_bin = (y_pred_proba > bin_lower) & (y_pred_proba <= bin_upper)
        prop_in_bin = in_bin.mean()

        if prop_in_bin > 0:
            # Calculate accuracy and confidence for this bin
            accuracy_in_bin = y_true[in_bin].mean()
            avg_confidence_in_bin = y_pred_proba[in_bin].mean()

            bin_centers.append((bin_lower + bin_upper) / 2)
            bin_accuracies.append(accuracy_in_bin)
            bin_confidences.append(avg_confidence_in_bin)
            bin_counts.append(int(in_bin.sum()))

            # Add to ECE
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        else:
            bin_centers.append((bin_lower + bin_upper) / 2)
            bin_accuracies.append(0.0)
            bin_confidences.append((bin_lower + bin_upper) / 2)
            bin_counts.append(0)

    # Brier score decomposition
    brier_score = brier_score_loss(y_true, y_pred_proba)

    # Reliability (calibration)
    reliability = np.mean((y_pred_proba - y_true) ** 2) - np.mean(
        (y_pred_proba - np.mean(y_pred_proba)) ** 2
    )

    # Resolution (sharpness)
    resolution = np.mean((y_pred_proba - np.mean(y_pred_proba)) ** 2)

    # Uncertainty
    uncertainty = np.mean(y_true) * (1 - np.mean(y_true))

    return {
        "expected_calibration_error": float(ece),
        "brier_score": float(brier_score),
        "brier_decomposition": {
            "reliability": float(reliability),
            "resolution": float(resolution),
            "uncertainty": float(uncertainty),
        },
        "reliability_diagram": {
            "bin_centers": bin_centers,
            "bin_accuracies": bin_accuracies,
            "bin_confidences": bin_confidences,
            "bin_counts": bin_counts,
            "n_bins": n_bins,
        },
    }


def evaluate_trading_performance(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    returns: np.ndarray | None = None,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """
    Evaluate trading-specific performance metrics.

    Args:
        y_true: True binary labels (1=up, 0=down)
        y_pred_proba: Predicted probabilities for up movement
        returns: Actual returns (optional, for profit/loss calculation)
        threshold: Decision threshold for trading signals

    Returns:
        Dictionary with trading performance metrics
    """
    y_pred = (y_pred_proba >= threshold).astype(int)

    # Signal analysis
    n_signals = np.sum(y_pred)
    signal_rate = n_signals / len(y_pred)

    # Hit rate (accuracy on signals only)
    if n_signals > 0:
        hit_rate = np.sum((y_pred == 1) & (y_true == 1)) / n_signals
    else:
        hit_rate = 0.0

    # Win rate (overall accuracy)
    win_rate = accuracy_score(y_true, y_pred)

    # Precision and recall for trading
    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # Trading metrics
    metrics = {
        "signal_analysis": {
            "n_signals": int(n_signals),
            "signal_rate": float(signal_rate),
            "hit_rate": float(hit_rate),
            "win_rate": float(win_rate),
        },
        "trading_metrics": {
            "precision": float(precision),
            "recall": float(recall),
            "true_positives": int(tp),
            "false_positives": int(fp),
            "false_negatives": int(fn),
        },
    }

    # Add return-based metrics if returns provided
    if returns is not None:
        # Calculate returns for different strategies
        buy_and_hold_return = np.mean(returns)

        # Strategy returns (only trade on signals)
        strategy_returns = returns * y_pred
        strategy_return = np.mean(strategy_returns)

        # Risk-adjusted metrics
        strategy_volatility = np.std(strategy_returns)
        buy_hold_volatility = np.std(returns)

        sharpe_ratio = strategy_return / strategy_volatility if strategy_volatility > 0 else 0.0
        buy_hold_sharpe = (
            buy_and_hold_return / buy_hold_volatility if buy_hold_volatility > 0 else 0.0
        )

        metrics["return_analysis"] = {
            "strategy_return": float(strategy_return),
            "buy_hold_return": float(buy_and_hold_return),
            "strategy_volatility": float(strategy_volatility),
            "buy_hold_volatility": float(buy_hold_volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "buy_hold_sharpe": float(buy_hold_sharpe),
            "excess_return": float(strategy_return - buy_and_hold_return),
        }

    return metrics


def generate_evaluation_report(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    y_pred: np.ndarray | None = None,
    returns: np.ndarray | None = None,
    model_name: str = "Model",
    threshold: float = 0.5,
) -> dict[str, Any]:
    """
    Generate comprehensive evaluation report.

    Args:
        y_true: True binary labels
        y_pred_proba: Predicted probabilities
        y_pred: Predicted binary labels (optional)
        returns: Actual returns (optional)
        model_name: Name of the model
        threshold: Decision threshold

    Returns:
        Complete evaluation report
    """
    # Basic classification evaluation
    classification_metrics = evaluate_binary_classification(y_true, y_pred_proba, y_pred, threshold)

    # Calibration evaluation
    calibration_metrics = evaluate_calibration(y_true, y_pred_proba)

    # Trading performance
    trading_metrics = evaluate_trading_performance(y_true, y_pred_proba, returns, threshold)

    # Combine all metrics
    report = {
        "model_info": {
            "name": model_name,
            "threshold": threshold,
            "n_samples": int(len(y_true)),
        },
        "classification": classification_metrics,
        "calibration": calibration_metrics,
        "trading": trading_metrics,
    }

    return report


def save_evaluation_report(
    report: dict[str, Any],
    output_path: Path | str,
    format: str = "json",
) -> None:
    """
    Save evaluation report to file.

    Args:
        report: Evaluation report dictionary
        output_path: Output file path
        format: Output format ("json" or "html")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format.lower() == "json":
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

    elif format.lower() == "html":
        # Generate HTML report
        html_content = generate_html_report(report)
        with open(output_path, "w") as f:
            f.write(html_content)

    else:
        raise ValueError(f"Unsupported format: {format}")


def generate_html_report(report: dict[str, Any]) -> str:
    """
    Generate HTML evaluation report.

    Args:
        report: Evaluation report dictionary

    Returns:
        HTML content as string
    """
    model_info = report["model_info"]
    classification = report["classification"]
    calibration = report["calibration"]
    trading = report["trading"]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Model Evaluation Report - {model_info['name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .metric {{ margin: 10px 0; }}
            .metric-label {{ font-weight: bold; }}
            .metric-value {{ color: #333; }}
            .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; }}
            .good {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .bad {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <h1>Model Evaluation Report</h1>

        <div class="section">
            <h2>Model Information</h2>
            <div class="metric">
                <span class="metric-label">Model:</span>
                <span class="metric-value">{model_info['name']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Samples:</span>
                <span class="metric-value">{model_info['n_samples']:,}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Threshold:</span>
                <span class="metric-value">{model_info['threshold']:.3f}</span>
            </div>
        </div>

        <div class="section">
            <h2>Classification Metrics</h2>
            <div class="metric">
                <span class="metric-label">Accuracy:</span>
                <span class="metric-value">{classification['basic_metrics']['accuracy']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">ROC-AUC:</span>
                <span class="metric-value">{classification['basic_metrics']['roc_auc']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Log Loss:</span>
                <span class="metric-value">{classification['basic_metrics']['log_loss']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Brier Score:</span>
                <span class="metric-value">{classification['basic_metrics']['brier_score']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">F1 Score:</span>
                <span class="metric-value">{classification['classification_metrics']['f1_score']:.3f}</span>
            </div>
        </div>

        <div class="section">
            <h2>Calibration Metrics</h2>
            <div class="metric">
                <span class="metric-label">Expected Calibration Error:</span>
                <span class="metric-value">{calibration['expected_calibration_error']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Reliability:</span>
                <span class="metric-value">{calibration['brier_decomposition']['reliability']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Resolution:</span>
                <span class="metric-value">{calibration['brier_decomposition']['resolution']:.3f}</span>
            </div>
        </div>

        <div class="section">
            <h2>Trading Performance</h2>
            <div class="metric">
                <span class="metric-label">Signal Rate:</span>
                <span class="metric-value">{trading['signal_analysis']['signal_rate']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Hit Rate:</span>
                <span class="metric-value">{trading['signal_analysis']['hit_rate']:.3f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Win Rate:</span>
                <span class="metric-value">{trading['signal_analysis']['win_rate']:.3f}</span>
            </div>
        </div>

        <div class="section">
            <h2>Confusion Matrix</h2>
            <table border="1" style="border-collapse: collapse;">
                <tr>
                    <td></td>
                    <td><strong>Predicted 0</strong></td>
                    <td><strong>Predicted 1</strong></td>
                </tr>
                <tr>
                    <td><strong>Actual 0</strong></td>
                    <td>{classification['confusion_matrix']['true_negative']}</td>
                    <td>{classification['confusion_matrix']['false_positive']}</td>
                </tr>
                <tr>
                    <td><strong>Actual 1</strong></td>
                    <td>{classification['confusion_matrix']['false_negative']}</td>
                    <td>{classification['confusion_matrix']['true_positive']}</td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """

    return html
