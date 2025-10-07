"""
Model calibration utilities for ML training.

Provides tools for calibrating probability outputs to improve reliability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


def calibrate_with_platt_scaling(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
) -> tuple[float, float]:
    """
    Calibrate probabilities using Platt scaling (logistic regression).
    
    Platt scaling fits a sigmoid function to the predicted probabilities:
    P_calibrated = 1 / (1 + exp(A * logit(P_raw) + B))
    
    Args:
        y_true: True binary labels
        y_pred_proba: Raw predicted probabilities
    
    Returns:
        Tuple of (A, B) calibration parameters
    """
    # Avoid log(0) and log(1) by clipping probabilities
    y_pred_proba_clipped = np.clip(y_pred_proba, 1e-7, 1 - 1e-7)
    
    # Convert to logits
    logits = np.log(y_pred_proba_clipped / (1 - y_pred_proba_clipped))
    
    # Fit logistic regression: y_true = sigmoid(A * logits + B)
    calibrator = LogisticRegression()
    calibrator.fit(logits.reshape(-1, 1), y_true)
    
    # Extract parameters
    A = calibrator.coef_[0, 0]
    B = calibrator.intercept_[0]
    
    return float(A), float(B)


def calibrate_with_isotonic_regression(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
) -> IsotonicRegression:
    """
    Calibrate probabilities using isotonic regression.
    
    Isotonic regression fits a non-decreasing function to the probabilities.
    More flexible than Platt scaling but requires more data.
    
    Args:
        y_true: True binary labels
        y_pred_proba: Raw predicted probabilities
    
    Returns:
        Fitted IsotonicRegression model
    """
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(y_pred_proba, y_true)
    
    return calibrator


def apply_platt_calibration(
    y_pred_proba: np.ndarray,
    A: float,
    B: float,
) -> np.ndarray:
    """
    Apply Platt scaling calibration to probabilities.
    
    Args:
        y_pred_proba: Raw predicted probabilities
        A: Platt scaling parameter A
        B: Platt scaling parameter B
    
    Returns:
        Calibrated probabilities
    """
    # Avoid log(0) and log(1)
    y_pred_proba_clipped = np.clip(y_pred_proba, 1e-7, 1 - 1e-7)
    
    # Convert to logits
    logits = np.log(y_pred_proba_clipped / (1 - y_pred_proba_clipped))
    
    # Apply calibration: P_calibrated = sigmoid(A * logits + B)
    calibrated_logits = A * logits + B
    calibrated_proba = 1.0 / (1.0 + np.exp(-calibrated_logits))
    
    return calibrated_proba


def apply_isotonic_calibration(
    y_pred_proba: np.ndarray,
    calibrator: IsotonicRegression,
) -> np.ndarray:
    """
    Apply isotonic regression calibration to probabilities.
    
    Args:
        y_pred_proba: Raw predicted probabilities
        calibrator: Fitted IsotonicRegression model
    
    Returns:
        Calibrated probabilities
    """
    return calibrator.predict(y_pred_proba)


def calibrate_model(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    method: str = "platt",
) -> dict[str, Any]:
    """
    Calibrate model probabilities using specified method.
    
    Args:
        y_true: True binary labels
        y_pred_proba: Raw predicted probabilities
        method: Calibration method ("platt" or "isotonic")
    
    Returns:
        Dictionary with calibration results and parameters
    """
    if method == "platt":
        A, B = calibrate_with_platt_scaling(y_true, y_pred_proba)
        calibrated_proba = apply_platt_calibration(y_pred_proba, A, B)
        
        return {
            "method": "platt",
            "parameters": {"A": A, "B": B},
            "calibrated_proba": calibrated_proba,
        }
    
    elif method == "isotonic":
        calibrator = calibrate_with_isotonic_regression(y_true, y_pred_proba)
        calibrated_proba = apply_isotonic_calibration(y_pred_proba, calibrator)
        
        # For isotonic, we need to save the full model (not just parameters)
        return {
            "method": "isotonic",
            "parameters": {
                "x_thresholds": calibrator.X_thresholds_.tolist(),
                "y_thresholds": calibrator.y_thresholds_.tolist(),
            },
            "calibrated_proba": calibrated_proba,
        }
    
    else:
        raise ValueError(f"Unsupported calibration method: {method}")


def save_calibration_params(
    calibration_results: dict[str, Any],
    output_path: Path | str,
) -> None:
    """
    Save calibration parameters to file.
    
    Args:
        calibration_results: Results from calibrate_model()
        output_path: Output file path
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save only the parameters (not the full results)
    params_to_save = {
        "method": calibration_results["method"],
        "parameters": calibration_results["parameters"],
    }
    
    with open(output_path, "w") as f:
        json.dump(params_to_save, f, indent=2)


def load_calibration_params(
    input_path: Path | str,
) -> dict[str, Any]:
    """
    Load calibration parameters from file.
    
    Args:
        input_path: Input file path
    
    Returns:
        Dictionary with calibration parameters
    """
    input_path = Path(input_path)
    
    with open(input_path) as f:
        return json.load(f)


def apply_calibration_from_params(
    y_pred_proba: np.ndarray,
    calibration_params: dict[str, Any],
) -> np.ndarray:
    """
    Apply calibration using loaded parameters.
    
    Args:
        y_pred_proba: Raw predicted probabilities
        calibration_params: Calibration parameters from load_calibration_params()
    
    Returns:
        Calibrated probabilities
    """
    method = calibration_params["method"]
    params = calibration_params["parameters"]
    
    if method == "platt":
        A = params["A"]
        B = params["B"]
        return apply_platt_calibration(y_pred_proba, A, B)
    
    elif method == "isotonic":
        # For isotonic, we need to retrain or use a simpler approach
        # For now, return original probabilities with a warning
        import warnings
        warnings.warn("Isotonic regression parameters cannot be easily reconstructed. Returning original probabilities.")
        return y_pred_proba
    
    else:
        raise ValueError(f"Unsupported calibration method: {method}")


def compare_calibration_methods(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
) -> dict[str, Any]:
    """
    Compare different calibration methods.
    
    Args:
        y_true: True binary labels
        y_pred_proba: Raw predicted probabilities
    
    Returns:
        Dictionary with comparison results
    """
    from sklearn.metrics import brier_score_loss
    
    # Original performance
    original_brier = brier_score_loss(y_true, y_pred_proba)
    
    # Platt scaling
    platt_results = calibrate_model(y_true, y_pred_proba, method="platt")
    platt_brier = brier_score_loss(y_true, platt_results["calibrated_proba"])
    
    # Isotonic regression
    isotonic_results = calibrate_model(y_true, y_pred_proba, method="isotonic")
    isotonic_brier = brier_score_loss(y_true, isotonic_results["calibrated_proba"])
    
    return {
        "original": {
            "brier_score": float(original_brier),
            "method": "none",
        },
        "platt": {
            "brier_score": float(platt_brier),
            "method": "platt",
            "parameters": platt_results["parameters"],
            "improvement": float(original_brier - platt_brier),
        },
        "isotonic": {
            "brier_score": float(isotonic_brier),
            "method": "isotonic",
            "parameters": isotonic_results["parameters"],
            "improvement": float(original_brier - isotonic_brier),
        },
        "best_method": "platt" if platt_brier < isotonic_brier else "isotonic",
        "best_improvement": float(min(original_brier - platt_brier, original_brier - isotonic_brier)),
    }
