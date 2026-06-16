"""Unit tests for core.optimizer.robustness (DSR / PBO / FDR).

These tests pin the statistical behaviour with synthetic inputs whose answers
are known a priori, so the estimators can be trusted before they are pointed at
real optimizer trial distributions.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from core.optimizer.robustness import (
    benjamini_hochberg,
    deflated_sharpe_from_trials,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    min_track_record_length,
    pbo_cscv,
    probabilistic_sharpe_ratio,
    return_moments,
    summarize_campaign,
)


# --------------------------------------------------------------------------- #
# return_moments
# --------------------------------------------------------------------------- #
def test_return_moments_normal_series():
    rng = np.random.default_rng(0)
    x = rng.normal(0.01, 0.1, size=5000)
    sharpe, skew, kurt, n = return_moments(x)
    assert n == 5000
    assert sharpe == pytest.approx(0.1, abs=0.03)  # 0.01 / 0.1
    assert skew == pytest.approx(0.0, abs=0.1)
    assert kurt == pytest.approx(3.0, abs=0.2)  # non-excess


def test_return_moments_degenerate():
    assert return_moments([1.0]) == (0.0, 0.0, 3.0, 1)
    assert return_moments([2.0, 2.0, 2.0])[0] == 0.0  # zero variance -> sharpe 0


# --------------------------------------------------------------------------- #
# PSR
# --------------------------------------------------------------------------- #
def test_psr_equals_half_at_benchmark():
    # observed == benchmark -> z == 0 -> CDF == 0.5
    assert probabilistic_sharpe_ratio(0.2, 0.2, n_obs=500) == pytest.approx(0.5, abs=1e-9)


def test_psr_monotonic_in_sharpe():
    base = probabilistic_sharpe_ratio(0.1, 0.0, 500)
    higher = probabilistic_sharpe_ratio(0.3, 0.0, 500)
    assert higher > base
    assert 0.0 <= base <= 1.0 and 0.0 <= higher <= 1.0


def test_psr_increases_with_sample_size():
    small = probabilistic_sharpe_ratio(0.1, 0.0, 30)
    large = probabilistic_sharpe_ratio(0.1, 0.0, 5000)
    assert large > small


# --------------------------------------------------------------------------- #
# expected_max_sharpe & DSR
# --------------------------------------------------------------------------- #
def test_expected_max_sharpe_grows_with_trials():
    v = 0.04  # variance of trial sharpes (std 0.2)
    e10 = expected_max_sharpe(10, v)
    e1000 = expected_max_sharpe(1000, v)
    assert e1000 > e10 > 0.0


def test_expected_max_sharpe_edge_cases():
    assert expected_max_sharpe(1, 0.04) == 0.0
    assert expected_max_sharpe(100, 0.0) == 0.0


def test_dsr_decreases_with_more_trials():
    # Same observed Sharpe, more trials searched -> lower deflated Sharpe.
    kwargs = dict(observed_sharpe=0.3, sharpe_variance=0.04, n_obs=500, skew=0.0, kurtosis=3.0)
    few = deflated_sharpe_ratio(n_trials=5, **kwargs)
    many = deflated_sharpe_ratio(n_trials=5000, **kwargs)
    assert few > many
    assert 0.0 <= many <= few <= 1.0


def test_dsr_strong_result_few_trials_passes():
    # Strong per-period Sharpe, long sample, few trials -> should clear 0.95.
    dsr = deflated_sharpe_ratio(
        observed_sharpe=0.5, sharpe_variance=0.01, n_trials=10, n_obs=2000
    )
    assert dsr > 0.95


def test_dsr_weak_result_many_trials_fails():
    # Weak Sharpe, huge trial count -> should not clear 0.95.
    dsr = deflated_sharpe_ratio(
        observed_sharpe=0.12, sharpe_variance=0.05, n_trials=5000, n_obs=120
    )
    assert dsr < 0.95


def test_deflated_sharpe_from_trials_wrapper():
    rng = np.random.default_rng(1)
    best = rng.normal(0.05, 0.1, size=1000)  # decent Sharpe ~0.5
    trial_sharpes = rng.normal(0.1, 0.2, size=200)
    res = deflated_sharpe_from_trials(best, trial_sharpes)
    assert res.n_trials == 200
    assert res.n_obs == 1000
    assert 0.0 <= res.deflated_sharpe <= 1.0
    assert res.probabilistic_sharpe >= res.deflated_sharpe  # benchmark>=0 lowers DSR
    assert isinstance(res.passes, bool)


# --------------------------------------------------------------------------- #
# min_track_record_length
# --------------------------------------------------------------------------- #
def test_mintrl_infinite_when_no_edge():
    assert math.isinf(min_track_record_length(0.1, benchmark_sharpe=0.1))
    assert math.isinf(min_track_record_length(0.05, benchmark_sharpe=0.2))


def test_mintrl_finite_positive():
    n = min_track_record_length(0.3, benchmark_sharpe=0.0)
    assert math.isfinite(n) and n > 1.0


# --------------------------------------------------------------------------- #
# PBO via CSCV
# --------------------------------------------------------------------------- #
def test_pbo_pure_noise_near_half():
    rng = np.random.default_rng(7)
    M = rng.normal(0.0, 1.0, size=(512, 20))  # no strategy has real skill
    res = pbo_cscv(M, n_partitions=14)
    assert res.n_strategies == 20
    assert 0.35 < res.pbo < 0.65  # symmetric -> ~0.5


def test_pbo_one_dominant_strategy_low():
    rng = np.random.default_rng(3)
    M = rng.normal(0.0, 1.0, size=(512, 20))
    M[:, 0] += 0.8  # column 0 has a persistent positive drift -> genuine edge
    res = pbo_cscv(M, n_partitions=14)
    assert res.pbo < 0.15  # IS-best is also OOS-best -> not overfit


def test_pbo_input_validation():
    with pytest.raises(ValueError):
        pbo_cscv(np.zeros((100, 1)))  # need >=2 strategies
    with pytest.raises(ValueError):
        pbo_cscv(np.zeros((100, 5)), n_partitions=7)  # must be even
    with pytest.raises(ValueError):
        pbo_cscv(np.zeros((4, 5)), n_partitions=8)  # too few observations


def test_pbo_respects_combination_cap():
    rng = np.random.default_rng(11)
    M = rng.normal(0.0, 1.0, size=(256, 8))
    res = pbo_cscv(M, n_partitions=16, max_combinations=100)
    assert res.n_combinations == 100


# --------------------------------------------------------------------------- #
# Benjamini-Hochberg FDR
# --------------------------------------------------------------------------- #
def test_bh_all_significant():
    res = benjamini_hochberg([0.001, 0.002, 0.003], alpha=0.05)
    assert res.n_significant == 3
    assert all(res.rejected)


def test_bh_none_significant():
    res = benjamini_hochberg([0.9, 0.8, 0.95], alpha=0.05)
    assert res.n_significant == 0
    assert not any(res.rejected)


def test_bh_boundary_line():
    # p == k/m*alpha for every k -> all rejected at the boundary.
    res = benjamini_hochberg([0.01, 0.02, 0.03, 0.04, 0.05], alpha=0.05)
    assert res.n_significant == 5
    assert res.threshold == pytest.approx(0.05)


def test_bh_mixed_and_monotone_adjusted():
    res = benjamini_hochberg([0.001, 0.2, 0.7, 0.008], alpha=0.05)
    # The two tiny p-values should be discovered, the large ones not.
    assert res.rejected[0] and res.rejected[3]
    assert not res.rejected[1] and not res.rejected[2]
    # Adjusted p-values are valid probabilities.
    assert all(0.0 <= q <= 1.0 for q in res.adjusted_pvalues)


def test_bh_empty():
    res = benjamini_hochberg([], alpha=0.05)
    assert res.n_significant == 0
    assert res.adjusted_pvalues == []


# --------------------------------------------------------------------------- #
# summarize_campaign
# --------------------------------------------------------------------------- #
def test_summarize_campaign_strong_passes():
    rng = np.random.default_rng(5)
    best = rng.normal(0.06, 0.1, size=2000)  # strong per-period Sharpe ~0.6
    trial_sharpes = rng.normal(0.1, 0.1, size=15)  # tight spread, few trials
    rep = summarize_campaign(best_returns=best, trial_sharpes=trial_sharpes)
    assert rep.n_trials == 15
    assert rep.deflated_sharpe > 0.95
    assert rep.verdict.startswith("PASS")


def test_summarize_campaign_overfit_fails():
    rng = np.random.default_rng(6)
    # Weak observed Sharpe, many trials with wide spread, short sample.
    trial_sharpes = rng.normal(0.0, 0.3, size=4000)
    rep = summarize_campaign(
        trial_sharpes=trial_sharpes, observed_sharpe=0.12, n_obs=120
    )
    assert rep.deflated_sharpe < 0.95
    assert "FAIL" in rep.verdict or "INCONCLUSIVE" in rep.verdict


def test_summarize_campaign_with_pbo_and_fdr():
    rng = np.random.default_rng(8)
    matrix = rng.normal(0.0, 1.0, size=(256, 12))  # pure noise -> PBO ~0.5
    rep = summarize_campaign(
        trial_sharpes=[0.1, 0.2, 0.15, 0.05],
        observed_sharpe=0.2,
        n_obs=300,
        returns_matrix=matrix,
        fdr_pvalues=[0.001, 0.5, 0.9],
    )
    assert rep.pbo is not None and 0.0 <= rep.pbo <= 1.0
    assert rep.fdr_significant == 1


def test_summarize_campaign_requires_n_obs():
    with pytest.raises(ValueError):
        summarize_campaign(trial_sharpes=[0.1, 0.2], observed_sharpe=0.2)
