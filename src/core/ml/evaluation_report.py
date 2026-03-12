"""Evaluation report assembly and rendering helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from .evaluation_metrics import evaluate_binary_classification, evaluate_calibration
from .evaluation_trading import evaluate_trading_performance


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
    classification_metrics = evaluate_binary_classification(y_true, y_pred_proba, y_pred, threshold)
    calibration_metrics = evaluate_calibration(y_true, y_pred_proba)
    trading_metrics = evaluate_trading_performance(y_true, y_pred_proba, returns, threshold)

    return {
        "model_info": {
            "name": model_name,
            "threshold": threshold,
            "n_samples": int(len(y_true)),
        },
        "classification": classification_metrics,
        "calibration": calibration_metrics,
        "trading": trading_metrics,
    }


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
