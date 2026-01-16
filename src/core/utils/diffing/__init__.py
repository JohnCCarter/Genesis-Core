"""Convenience exports for diffing utilities."""

from __future__ import annotations

from .canonical import canonicalize_config, fingerprint_config
from .feature_cache import IndicatorCache, make_indicator_fingerprint
from .optuna_guard import TrialFingerprint, estimate_zero_trade, evaluate_trial_with_cache
from .results_diff import (
    check_backtest_comparability,
    diff_backtest_files,
    diff_backtest_results,
    diff_metrics,
    format_comparability_issues,
    summarize_metric_deltas,
    summarize_metrics_diff,
)
from .trial_cache import TrialResultCache

__all__ = [
    "canonicalize_config",
    "fingerprint_config",
    "TrialFingerprint",
    "TrialResultCache",
    "estimate_zero_trade",
    "evaluate_trial_with_cache",
    "IndicatorCache",
    "make_indicator_fingerprint",
    "diff_metrics",
    "diff_backtest_results",
    "diff_backtest_files",
    "check_backtest_comparability",
    "format_comparability_issues",
    "summarize_metric_deltas",
    "summarize_metrics_diff",
]
