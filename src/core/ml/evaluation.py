"""Compatibility facade for model evaluation utilities."""

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

from .evaluation_metrics import (
    evaluate_binary_classification as _evaluate_binary_classification,
)
from .evaluation_metrics import (
    evaluate_calibration as _evaluate_calibration,
)
from .evaluation_report import (
    generate_evaluation_report as _generate_evaluation_report,
)
from .evaluation_report import (
    generate_html_report as _generate_html_report,
)
from .evaluation_report import (
    save_evaluation_report as _save_evaluation_report,
)
from .evaluation_trading import (
    evaluate_trading_performance as _evaluate_trading_performance,
)

_LEGACY_STAR_IMPORT_COMPAT = (
    json,
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
    return _evaluate_binary_classification(y_true, y_pred_proba, y_pred, threshold)


def evaluate_calibration(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    n_bins: int = 10,
) -> dict[str, Any]:
    return _evaluate_calibration(y_true, y_pred_proba, n_bins)


def evaluate_trading_performance(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    returns: np.ndarray | None = None,
    threshold: float = 0.5,
) -> dict[str, Any]:
    return _evaluate_trading_performance(y_true, y_pred_proba, returns, threshold)


def generate_evaluation_report(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    y_pred: np.ndarray | None = None,
    returns: np.ndarray | None = None,
    model_name: str = "Model",
    threshold: float = 0.5,
) -> dict[str, Any]:
    return _generate_evaluation_report(y_true, y_pred_proba, y_pred, returns, model_name, threshold)


def save_evaluation_report(
    report: dict[str, Any],
    output_path: Path | str,
    format: str = "json",
) -> None:
    _save_evaluation_report(report, output_path, format)


def generate_html_report(report: dict[str, Any]) -> str:
    return _generate_html_report(report)
