"""Classification and calibration evaluation helpers for ML models."""

from __future__ import annotations

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

    accuracy = accuracy_score(y_true, y_pred)

    try:
        log_loss_score = log_loss(y_true, y_pred_proba)
    except ValueError:
        log_loss_score = 0.0

    brier_score = brier_score_loss(y_true, y_pred_proba)

    try:
        roc_auc = roc_auc_score(y_true, y_pred_proba)
        fpr, tpr, roc_thresholds = roc_curve(y_true, y_pred_proba)
    except ValueError:
        roc_auc = 0.5
        fpr = tpr = roc_thresholds = np.array([])

    try:
        precision, recall, pr_thresholds = precision_recall_curve(y_true, y_pred_proba)
        trapz_fn = getattr(np, "trapezoid", None)
        if trapz_fn is None:
            avg_precision = np.trapz(precision, recall)  # type: ignore[attr-defined]
        else:
            avg_precision = trapz_fn(precision, recall)
    except ValueError:
        precision = recall = pr_thresholds = np.array([])
        avg_precision = 0.0

    try:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    except ValueError:
        if np.all(y_true == 1):
            tn, fp, fn, tp = 0, 0, 0, len(y_true)
        else:
            tn, fp, fn, tp = len(y_true), 0, 0, 0

    precision_score = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall_score = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1_score = (
        2 * (precision_score * recall_score) / (precision_score + recall_score)
        if (precision_score + recall_score) > 0
        else 0.0
    )

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
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    bin_centers = []
    bin_accuracies = []
    bin_counts = []
    bin_confidences = []

    ece = 0.0

    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers, strict=False):
        in_bin = (y_pred_proba > bin_lower) & (y_pred_proba <= bin_upper)
        prop_in_bin = in_bin.mean()

        if prop_in_bin > 0:
            accuracy_in_bin = y_true[in_bin].mean()
            avg_confidence_in_bin = y_pred_proba[in_bin].mean()

            bin_centers.append((bin_lower + bin_upper) / 2)
            bin_accuracies.append(accuracy_in_bin)
            bin_confidences.append(avg_confidence_in_bin)
            bin_counts.append(int(in_bin.sum()))

            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        else:
            bin_centers.append((bin_lower + bin_upper) / 2)
            bin_accuracies.append(0.0)
            bin_confidences.append((bin_lower + bin_upper) / 2)
            bin_counts.append(0)

    brier_score = brier_score_loss(y_true, y_pred_proba)
    reliability = np.mean((y_pred_proba - y_true) ** 2) - np.mean(
        (y_pred_proba - np.mean(y_pred_proba)) ** 2
    )
    resolution = np.mean((y_pred_proba - np.mean(y_pred_proba)) ** 2)
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
