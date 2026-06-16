"""Overfitting-aware robustness statistics for the optimizer.

This module is a *read-side* analysis library. It does not change the optimizer
objective (``core.optimizer.scoring``) or any champion selection; it quantifies
how much of a reported result is likely an artifact of multiple testing /
backtest overfitting, given the trial distribution the optimizer already
retains.

Implemented estimators
-----------------------
- Probabilistic Sharpe Ratio (PSR) and Deflated Sharpe Ratio (DSR)
  Bailey & López de Prado (2014), "The Deflated Sharpe Ratio: Correcting for
  Selection Bias, Backtest Overfitting, and Non-Normality", Journal of
  Portfolio Management 40 (5).
- Probability of Backtest Overfitting (PBO) via Combinatorially-Symmetric
  Cross-Validation (CSCV)
  Bailey, Borwein, López de Prado & Zhu (2017), "The Probability of Backtest
  Overfitting", Journal of Computational Finance 20 (4).
- Benjamini-Hochberg false-discovery-rate control
  Benjamini & Hochberg (1995), JRSS-B 57 (1).

Conventions
-----------
- Sharpe ratios are handled in the SAME frequency as the supplied return
  series (i.e. *non-annualised* per-period Sharpe). The backtest computes a
  per-trade Sharpe (``core.backtest.metrics``); callers must stay consistent
  and not mix annualised and per-period numbers.
- ``kurtosis`` is the *non-excess* fourth standardized moment (Normal == 3.0).
  Use :func:`return_moments` to derive the right inputs from a return series.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import Sequence

import numpy as np
from scipy.stats import norm

# Euler-Mascheroni constant, used by the expected-maximum-Sharpe approximation.
_EULER_MASCHERONI = 0.5772156649015328606


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def return_moments(returns: Sequence[float]) -> tuple[float, float, float, int]:
    """Return ``(sharpe, skew, kurtosis_non_excess, n_obs)`` for a series.

    The Sharpe ratio is per-period (mean / std, ddof=1), matching the rest of
    the backtest. Skew and kurtosis are the standardized 3rd and 4th moments,
    with kurtosis reported in *non-excess* form (Normal == 3.0).
    """
    arr = np.asarray(list(returns), dtype=float)
    arr = arr[np.isfinite(arr)]
    n = int(arr.size)
    if n < 2:
        return 0.0, 0.0, 3.0, n
    mean = float(arr.mean())
    std = float(arr.std(ddof=1))
    if std <= 0.0:
        return 0.0, 0.0, 3.0, n
    sharpe = mean / std
    # Population-style standardized moments (divide by std with ddof=0 base) are
    # the standard inputs for the PSR formula.
    std_pop = float(arr.std(ddof=0))
    if std_pop <= 0.0:
        return sharpe, 0.0, 3.0, n
    z = (arr - mean) / std_pop
    skew = float(np.mean(z**3))
    kurtosis = float(np.mean(z**4))
    return sharpe, skew, kurtosis, n


# --------------------------------------------------------------------------- #
# Probabilistic / Deflated Sharpe Ratio
# --------------------------------------------------------------------------- #
def probabilistic_sharpe_ratio(
    observed_sharpe: float,
    benchmark_sharpe: float,
    n_obs: int,
    skew: float = 0.0,
    kurtosis: float = 3.0,
) -> float:
    """Probabilistic Sharpe Ratio: P(true SR > benchmark SR).

    Returns a probability in ``[0, 1]``. Higher is better; a common acceptance
    threshold is 0.95.

    ``kurtosis`` is non-excess (Normal == 3.0).
    """
    if n_obs < 2:
        return float("nan")
    denom_var = 1.0 - skew * observed_sharpe + ((kurtosis - 1.0) / 4.0) * observed_sharpe**2
    # Guard against a degenerate / negative variance term.
    if denom_var <= 0.0:
        denom_var = 1e-12
    z = (observed_sharpe - benchmark_sharpe) * math.sqrt(n_obs - 1) / math.sqrt(denom_var)
    return float(norm.cdf(z))


def expected_max_sharpe(n_trials: int, sharpe_variance: float) -> float:
    """Expected maximum Sharpe across ``n_trials`` independent random strategies.

    This is the DSR benchmark ``SR*``. It is the expected value of the maximum
    of ``n_trials`` draws from a Normal with the given variance of Sharpe
    estimates (Bailey & López de Prado 2014, eq. for E[max]).
    """
    if n_trials < 1:
        return 0.0
    if sharpe_variance <= 0.0:
        return 0.0
    if n_trials == 1:
        return 0.0
    sigma = math.sqrt(sharpe_variance)
    # E[max_N] ≈ sigma * [ (1-γ)·Z^{-1}(1 - 1/N) + γ·Z^{-1}(1 - 1/(N·e)) ]
    q1 = norm.ppf(1.0 - 1.0 / n_trials)
    q2 = norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    return float(sigma * ((1.0 - _EULER_MASCHERONI) * q1 + _EULER_MASCHERONI * q2))


def deflated_sharpe_ratio(
    observed_sharpe: float,
    sharpe_variance: float,
    n_trials: int,
    n_obs: int,
    skew: float = 0.0,
    kurtosis: float = 3.0,
) -> float:
    """Deflated Sharpe Ratio: PSR evaluated against the expected best-of-N benchmark.

    ``sharpe_variance`` is the variance of the Sharpe estimates *across the
    trials* (the spread the optimizer explored). ``n_trials`` is the number of
    configurations tried. Returns a probability in ``[0, 1]``; below 0.95 means
    the result is not distinguishable from the best of that many random trials.
    """
    benchmark = expected_max_sharpe(n_trials, sharpe_variance)
    return probabilistic_sharpe_ratio(
        observed_sharpe, benchmark, n_obs, skew=skew, kurtosis=kurtosis
    )


@dataclass(slots=True)
class DeflatedSharpeResult:
    deflated_sharpe: float
    probabilistic_sharpe: float
    observed_sharpe: float
    benchmark_sharpe: float
    sharpe_variance: float
    n_trials: int
    n_obs: int
    skew: float
    kurtosis: float

    @property
    def passes(self) -> bool:
        """True when the deflated Sharpe clears the conventional 0.95 bar."""
        return self.deflated_sharpe >= 0.95


def deflated_sharpe_from_trials(
    best_returns: Sequence[float],
    trial_sharpes: Sequence[float],
    *,
    n_trials: int | None = None,
) -> DeflatedSharpeResult:
    """Convenience wrapper computing DSR for the best trial from raw inputs.

    Parameters
    ----------
    best_returns:
        The per-period return series of the *selected* (best) configuration.
        Used to derive observed Sharpe, skew, kurtosis and sample length.
    trial_sharpes:
        The Sharpe ratios of all trials in the campaign. Their variance is the
        ``sharpe_variance`` term and their count is ``n_trials`` (unless
        overridden, e.g. when the true count exceeds the retained sample).
    """
    observed_sharpe, skew, kurtosis, n_obs = return_moments(best_returns)
    sh = np.asarray(list(trial_sharpes), dtype=float)
    sh = sh[np.isfinite(sh)]
    n = int(n_trials if n_trials is not None else sh.size)
    variance = float(sh.var(ddof=1)) if sh.size > 1 else 0.0
    benchmark = expected_max_sharpe(n, variance)
    psr = probabilistic_sharpe_ratio(observed_sharpe, 0.0, n_obs, skew=skew, kurtosis=kurtosis)
    dsr = probabilistic_sharpe_ratio(
        observed_sharpe, benchmark, n_obs, skew=skew, kurtosis=kurtosis
    )
    return DeflatedSharpeResult(
        deflated_sharpe=dsr,
        probabilistic_sharpe=psr,
        observed_sharpe=observed_sharpe,
        benchmark_sharpe=benchmark,
        sharpe_variance=variance,
        n_trials=n,
        n_obs=n_obs,
        skew=skew,
        kurtosis=kurtosis,
    )


def min_track_record_length(
    observed_sharpe: float,
    benchmark_sharpe: float = 0.0,
    skew: float = 0.0,
    kurtosis: float = 3.0,
    confidence: float = 0.95,
) -> float:
    """Minimum number of observations to assert SR > benchmark at ``confidence``.

    Returns ``inf`` when the observed Sharpe does not exceed the benchmark
    (no sample size can establish significance).
    """
    if observed_sharpe <= benchmark_sharpe:
        return float("inf")
    z = norm.ppf(confidence)
    denom_var = 1.0 - skew * observed_sharpe + ((kurtosis - 1.0) / 4.0) * observed_sharpe**2
    if denom_var <= 0.0:
        denom_var = 1e-12
    return float(1.0 + denom_var * (z / (observed_sharpe - benchmark_sharpe)) ** 2)


# --------------------------------------------------------------------------- #
# Probability of Backtest Overfitting (CSCV)
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class PBOResult:
    pbo: float
    logits: list[float] = field(default_factory=list)
    n_combinations: int = 0
    n_strategies: int = 0
    n_partitions: int = 0

    @property
    def is_overfit(self) -> bool:
        """Conventional read: PBO > 0.5 indicates the selection is likely overfit."""
        return self.pbo > 0.5


def _column_sharpe(block: np.ndarray) -> np.ndarray:
    """Per-column (per-strategy) Sharpe over the rows of ``block``."""
    if block.shape[0] < 2:
        return np.zeros(block.shape[1], dtype=float)
    mean = block.mean(axis=0)
    std = block.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sharpe = np.where(std > 0, mean / std, 0.0)
    return np.asarray(sharpe, dtype=float)


def pbo_cscv(
    performance_matrix: np.ndarray,
    n_partitions: int = 16,
    *,
    metric: str = "sharpe",
    max_combinations: int | None = 20000,
    random_state: int | None = 42,
) -> PBOResult:
    """Probability of Backtest Overfitting via Combinatorially-Symmetric CV.

    Parameters
    ----------
    performance_matrix:
        Shape ``(T, N)`` — ``T`` time observations (e.g. per-bar returns) for
        each of ``N`` strategy configurations/trials.
    n_partitions:
        Number of disjoint row blocks ``S`` (must be even). The IS/OOS split
        uses every way of choosing ``S/2`` blocks as in-sample.
    metric:
        ``"sharpe"`` (default) or ``"mean"`` — how each strategy is ranked.
    max_combinations:
        Cap on the number of CSCV combinations evaluated. If ``C(S, S/2)``
        exceeds this, a random subset is sampled (deterministic via
        ``random_state``). ``None`` evaluates all.

    Returns a :class:`PBOResult`. ``pbo`` is the fraction of splits where the
    in-sample-best strategy ranks below the OOS median (logit <= 0).
    """
    M = np.asarray(performance_matrix, dtype=float)
    if M.ndim != 2:
        raise ValueError("performance_matrix must be 2-D (T observations x N strategies)")
    T, N = M.shape
    if N < 2:
        raise ValueError("need at least 2 strategies/trials for PBO")
    if n_partitions < 2 or n_partitions % 2 != 0:
        raise ValueError("n_partitions must be an even integer >= 2")
    if T < n_partitions:
        raise ValueError(f"need at least n_partitions={n_partitions} observations, got {T}")

    if metric not in {"sharpe", "mean"}:
        raise ValueError("metric must be 'sharpe' or 'mean'")

    # Split rows into S contiguous, (near-)equal blocks.
    block_indices = np.array_split(np.arange(T), n_partitions)
    s = n_partitions
    all_blocks = list(range(s))
    is_choices = list(combinations(all_blocks, s // 2))

    rng = np.random.default_rng(random_state)
    if max_combinations is not None and len(is_choices) > max_combinations:
        picked = rng.choice(len(is_choices), size=max_combinations, replace=False)
        is_choices = [is_choices[i] for i in picked]

    def _perf(block: np.ndarray) -> np.ndarray:
        if metric == "mean":
            return block.mean(axis=0) if block.shape[0] else np.zeros(N)
        return _column_sharpe(block)

    logits: list[float] = []
    for is_blocks in is_choices:
        is_set = set(is_blocks)
        is_rows = np.concatenate([block_indices[b] for b in all_blocks if b in is_set])
        oos_rows = np.concatenate([block_indices[b] for b in all_blocks if b not in is_set])

        is_perf = _perf(M[is_rows])
        oos_perf = _perf(M[oos_rows])

        n_star = int(np.argmax(is_perf))
        # Relative OOS rank of the IS-best strategy (1 = worst .. N = best).
        rank = float(np.sum(oos_perf <= oos_perf[n_star]))
        omega = rank / (N + 1.0)
        omega = min(max(omega, 1e-9), 1.0 - 1e-9)
        logits.append(math.log(omega / (1.0 - omega)))

    arr = np.asarray(logits, dtype=float)
    pbo = float(np.mean(arr <= 0.0)) if arr.size else float("nan")
    return PBOResult(
        pbo=pbo,
        logits=logits,
        n_combinations=len(is_choices),
        n_strategies=N,
        n_partitions=n_partitions,
    )


# --------------------------------------------------------------------------- #
# Benjamini-Hochberg FDR
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class CampaignReport:
    """Top-level overfitting verdict for an optimization campaign."""

    n_trials: int
    observed_sharpe: float
    benchmark_sharpe: float
    sharpe_variance: float
    deflated_sharpe: float
    probabilistic_sharpe: float
    n_obs: int
    pbo: float | None = None
    fdr_significant: int | None = None
    verdict: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "n_trials": self.n_trials,
            "observed_sharpe": self.observed_sharpe,
            "benchmark_sharpe": self.benchmark_sharpe,
            "sharpe_variance": self.sharpe_variance,
            "deflated_sharpe": self.deflated_sharpe,
            "probabilistic_sharpe": self.probabilistic_sharpe,
            "n_obs": self.n_obs,
            "pbo": self.pbo,
            "fdr_significant": self.fdr_significant,
            "verdict": self.verdict,
        }


def summarize_campaign(
    trial_sharpes: Sequence[float],
    *,
    best_returns: Sequence[float] | None = None,
    observed_sharpe: float | None = None,
    n_obs: int | None = None,
    skew: float = 0.0,
    kurtosis: float = 3.0,
    n_trials: int | None = None,
    returns_matrix: np.ndarray | None = None,
    fdr_pvalues: Sequence[float] | None = None,
    alpha: float = 0.05,
) -> CampaignReport:
    """Roll DSR / PBO / FDR into a single overfitting verdict for a campaign.

    Provide either ``best_returns`` (the selected config's return series, from
    which observed Sharpe / skew / kurtosis / sample length are derived) or the
    pair ``observed_sharpe`` + ``n_obs``. ``trial_sharpes`` supplies the spread
    and count of the search. ``returns_matrix`` (T x N) enables PBO; a list of
    candidate p-values enables the FDR count.
    """
    sh = np.asarray(list(trial_sharpes), dtype=float)
    sh = sh[np.isfinite(sh)]
    n = int(n_trials if n_trials is not None else sh.size)
    variance = float(sh.var(ddof=1)) if sh.size > 1 else 0.0

    if best_returns is not None:
        observed_sharpe, skew, kurtosis, n_obs = return_moments(best_returns)
    if observed_sharpe is None:
        observed_sharpe = float(sh.max()) if sh.size else 0.0
    if n_obs is None:
        raise ValueError("summarize_campaign needs n_obs (or best_returns) to compute DSR")

    benchmark = expected_max_sharpe(n, variance)
    psr = probabilistic_sharpe_ratio(observed_sharpe, 0.0, n_obs, skew=skew, kurtosis=kurtosis)
    dsr = probabilistic_sharpe_ratio(
        observed_sharpe, benchmark, n_obs, skew=skew, kurtosis=kurtosis
    )

    pbo_val: float | None = None
    if returns_matrix is not None:
        pbo_val = pbo_cscv(np.asarray(returns_matrix, dtype=float)).pbo

    fdr_sig: int | None = None
    if fdr_pvalues is not None:
        fdr_sig = benjamini_hochberg(fdr_pvalues, alpha=alpha).n_significant

    overfit_pbo = pbo_val is not None and pbo_val > 0.5
    if dsr >= 0.95 and not overfit_pbo:
        verdict = "PASS — edge survives multiple-testing deflation"
    elif dsr < 0.5 or overfit_pbo:
        verdict = "FAIL — indistinguishable from the best of N random trials"
    else:
        verdict = "INCONCLUSIVE — weak after deflation; treat as unproven"

    return CampaignReport(
        n_trials=n,
        observed_sharpe=float(observed_sharpe),
        benchmark_sharpe=float(benchmark),
        sharpe_variance=variance,
        deflated_sharpe=float(dsr),
        probabilistic_sharpe=float(psr),
        n_obs=int(n_obs),
        pbo=pbo_val,
        fdr_significant=fdr_sig,
        verdict=verdict,
    )


@dataclass(slots=True)
class FDRResult:
    rejected: list[bool]
    adjusted_pvalues: list[float]
    threshold: float
    n_significant: int
    alpha: float


def benjamini_hochberg(pvalues: Sequence[float], alpha: float = 0.05) -> FDRResult:
    """Benjamini-Hochberg false-discovery-rate control.

    Given a list of p-values (e.g. one per candidate strategy's IS->OOS lift),
    returns which are significant at FDR ``alpha``, the BH-adjusted p-values,
    and the largest p-value threshold that was rejected.
    """
    p = np.asarray(list(pvalues), dtype=float)
    m = int(p.size)
    if m == 0:
        return FDRResult(rejected=[], adjusted_pvalues=[], threshold=0.0, n_significant=0, alpha=alpha)

    order = np.argsort(p)
    ranks = np.arange(1, m + 1)
    sorted_p = p[order]

    # BH critical values and rejection set.
    crit = ranks / m * alpha
    below = sorted_p <= crit
    if below.any():
        k = int(np.max(np.where(below)[0]))  # largest index passing the line
        threshold = float(sorted_p[k])
        rejected_sorted = np.arange(m) <= k
    else:
        threshold = 0.0
        rejected_sorted = np.zeros(m, dtype=bool)

    # BH-adjusted p-values (monotone from the largest rank down).
    adj_sorted = sorted_p * m / ranks
    adj_sorted = np.minimum.accumulate(adj_sorted[::-1])[::-1]
    adj_sorted = np.clip(adj_sorted, 0.0, 1.0)

    rejected = np.zeros(m, dtype=bool)
    adjusted = np.zeros(m, dtype=float)
    rejected[order] = rejected_sorted
    adjusted[order] = adj_sorted

    return FDRResult(
        rejected=[bool(x) for x in rejected],
        adjusted_pvalues=[float(x) for x in adjusted],
        threshold=threshold,
        n_significant=int(rejected.sum()),
        alpha=alpha,
    )
