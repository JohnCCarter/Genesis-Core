"""Trading-oriented evaluation helpers for ML model outputs."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score


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

    n_signals = np.sum(y_pred)
    signal_rate = n_signals / len(y_pred)

    if n_signals > 0:
        hit_rate = np.sum((y_pred == 1) & (y_true == 1)) / n_signals
    else:
        hit_rate = 0.0

    win_rate = accuracy_score(y_true, y_pred)

    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

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

    if returns is not None:
        buy_and_hold_return = np.mean(returns)
        strategy_returns = returns * y_pred
        strategy_return = np.mean(strategy_returns)
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
