"""Overfit detection: Deflated Sharpe Ratio and PBO."""

import numpy as np
from scipy import stats


def calculate_deflated_sharpe(returns, n_trials, skewness, kurtosis):
    """
    Deflated Sharpe Ratio (Bailey & López de Prado, 2014).

    Adjusts Sharpe for multiple testing and non-normal returns.
    """
    mean_ret = np.mean(returns)
    std_ret = np.std(returns)

    if std_ret == 0:
        return {"sharpe": 0.0, "deflated_sharpe": 0.0, "p_value": 1.0}

    sharpe = mean_ret / std_ret * np.sqrt(252)

    n = len(returns)
    V_sharpe = (1 / (n - 1)) * (
        1 + (1 / 2) * sharpe**2 - skewness * sharpe + (kurtosis - 1) / 4 * sharpe**2
    )

    expected_max_sharpe = (1 - np.euler_gamma) * stats.norm.ppf(
        1 - 1 / n_trials
    ) + np.euler_gamma * stats.norm.ppf(1 - 1 / (n_trials * np.e))

    deflated_sharpe = (sharpe - expected_max_sharpe) / np.sqrt(V_sharpe)

    return {
        "sharpe": float(sharpe),
        "deflated_sharpe": float(deflated_sharpe),
        "variance_inflation": float(V_sharpe),
        "p_value": float(1 - stats.norm.cdf(deflated_sharpe)),
    }


def calculate_pbo(is_sharpes, oos_sharpes):
    """
    Probability of Backtest Overfitting (Bailey et al., 2015).

    Args:
        is_sharpes: In-sample Sharpe ratios
        oos_sharpes: Out-of-sample Sharpe ratios

    Returns:
        PBO score (0-1)
    """
    if len(is_sharpes) != len(oos_sharpes):
        raise ValueError("IS and OOS must have same length")

    n_overfit = sum(
        1 for is_sr, oos_sr in zip(is_sharpes, oos_sharpes, strict=True) if is_sr > oos_sr
    )

    pbo = n_overfit / len(is_sharpes)

    assessment = "ROBUST" if pbo < 0.3 else ("MARGINAL" if pbo < 0.5 else "OVERFIT_RISK")

    return {
        "pbo": float(pbo),
        "n_splits": len(is_sharpes),
        "n_overfit": n_overfit,
        "assessment": assessment,
    }
