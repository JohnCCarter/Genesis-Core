# RI policy router continuation_release_hysteresis phase-age transport — 2026-05-25

## Scope

Bounded RESEARCH follow-up to the landed clean-continuation normalized phase-age slice.

Question:

> if `subject_progress_pct` and `subject_rank_pct` transported on the clean-continuation holdout bench, what happens when the same subject-relative coordinates are projected onto the frozen `continuation_release_hysteresis` exact-subject triad?

This slice is observational only.

It does **not** run new backtests, change runtime logic, modify config/schema authority, alter the frozen hysteresis bench, or reopen subject selection beyond the already-closed triad.

## Inputs

- clean-continuation reference artifact: `results/evaluation/ri_policy_router_clean_continuation_normalized_phase_age_transport_2026-05-25.json`
- frozen triad synthesis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md`
- exact subject summaries:
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/continuation_release_hysteresis_topline_subject_summary.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/continuation_release_hysteresis_topline_subject_2025_10_summary.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/continuation_release_hysteresis_topline_subject_2018_03_summary.json`
- exact subject row-diff surfaces:
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/continuation_release_hysteresis_topline_subject_row_diffs.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/continuation_release_hysteresis_topline_subject_2025_10_row_diffs.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/continuation_release_hysteresis_topline_subject_2018_03_row_diffs.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_phase_age_transport_2026-05-25.json`

## What changed and what did not

- **Changed:** one new read-only helper projected the frozen hysteresis exact-subject triad onto the already-landed clean-continuation normalized phase-age envelopes and retained a new evaluation artifact.
- **Did not change:** no new backtests were run, no carrier/config/runtime code changed, no taxonomy labels changed, and the frozen triad itself was not widened or re-ranked.

## Observed

### 1. The clean-continuation reference still defines a clean early-vs-late split

The incoming reference envelopes were unchanged from the prior slice:

- `subject_progress_pct`
  - `wave_one = 0.0 -> 0.333333`
  - `wave_two = 0.466667 -> 1.0`
- `subject_rank_pct`
  - `wave_one = 0.0 -> 0.416667`
  - `wave_two = 0.5 -> 1.0`

So the hysteresis triad was projected onto an already-fixed reference, not a newly tuned one.

### 2. Every continuation-release cluster in the triad maps to the same early-phase envelope

Across the full frozen exact-subject triad, the entire continuation-release cluster stays inside the `wave_one` side for both subject-relative features.

#### `2021-08` — positive top-line subject

- top-line delta: `+0.188901 pp`
- cluster rows: `6`
- cluster bars: `2, 4`
- `subject_progress_pct = 0.111111 -> 0.222222`
- `subject_rank_pct = 0.119658 -> 0.205128`
- verdict: `maps_to_wave_one_envelope_only` on both features

#### `2025-10` — positive top-line subject

- top-line delta: `+0.171348 pp`
- cluster rows: `13`
- cluster bars: `2, 3, 5`
- `subject_progress_pct = 0.117647 -> 0.294118`
- `subject_rank_pct = 0.066667 -> 0.191667`
- verdict: `maps_to_wave_one_envelope_only` on both features

#### `2018-03` — negative top-line subject

- top-line delta: `-0.009372 pp`
- cluster rows: `12`
- cluster bars: `1, 3, 4, 5`
- `subject_progress_pct = 0.035714 -> 0.178571`
- `subject_rank_pct = 0.025 -> 0.141667`
- verdict: `maps_to_wave_one_envelope_only` on both features

So the whole exact triad shares one common bounded fact:

> the continuation-release seam is exercised inside the same early subject-relative phase band, regardless of top-line sign.

### 3. The first decisive local split is also wave-one-like in every exact subject

The first decisive local split is the first continuation-release row where the seam actually flips the local policy path from:

- baseline: `RI_defensive_transition_policy` + `switch_blocked_by_hysteresis`

to

- `release_zero`: `RI_continuation_policy` + `continuation_state_supported`

Those decisive rows are:

- `2021-08-19T03:00:00+00:00`
  - `bars_since_regime_change = 4`
  - `subject_progress_pct = 0.222222`
  - `subject_rank_pct = 0.188034`
- `2025-10-17T21:00:00+00:00`
  - `bars_since_regime_change = 3`
  - `subject_progress_pct = 0.176471`
  - `subject_rank_pct = 0.125`
- `2018-03-17T03:00:00+00:00`
  - `bars_since_regime_change = 3`
  - `subject_progress_pct = 0.107143`
  - `subject_rank_pct = 0.075`

All three decisive rows also map to `wave_one` only on both features.

### 4. Sign stays mixed inside that same early-phase band

Despite the shared early-phase placement:

- `2021-08` is positive
- `2025-10` is positive
- `2018-03` is negative

So the transported phase-age read does **not** separate top-line sign on this triad.

The new artifact records that directly:

- `cluster_wave_one_only_counts.subject_progress_pct = 3`
- `cluster_wave_one_only_counts.subject_rank_pct = 3`
- `decisive_wave_one_only_counts.subject_progress_pct = 3`
- `decisive_wave_one_only_counts.subject_rank_pct = 3`
- `mixed_signs_inside_same_phase_band = true`

## Inferred

### 1. Subject-relative phase-age still transports, but only as an early-phase marker here

The smallest honest read is:

- clean-continuation normalized phase-age remains reusable across benches
- on the hysteresis triad it says something real and stable
- but the stable statement is only that the seam fires in an early phase band

So the transported signal here is:

> `continuation_release_hysteresis` is an **early-phase seam marker** on the frozen exact-subject triad.

### 2. Early-phase location is not enough to explain sign

Because both positive subjects and the one negative subject live inside the same early envelope, the triad now falsifies a tempting overreach:

> “if the seam sits in the right transported phase-age band, sign should stabilize.”

That is not supported.

The current bounded evidence says the opposite:

> phase-age tells us **where** the seam is firing, but not yet **whether** that firing is beneficial or harmful.

## Unverified

The following remain open:

1. whether intra-band structure inside the early continuation-release zone separates sign better than broader subject-relative phase-age does
2. whether cluster-local timing, cluster length, or edge/clarity path explains why `2018-03` is negative while `2021-08` and `2025-10` are positive
3. whether any broader negative subgroup exists beyond the frozen exact triad without widening the packet beyond the current bench

## Verification

- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_phase_age_transport_20260525.py` -> pass
- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_phase_age_transport_20260525.py` -> emitted artifact with status `subject_relative_phase_age_marks_early_hysteresis_release_without_sign_separation`

## Bottom line

Carrying the clean-continuation normalized phase-age read onto the frozen `continuation_release_hysteresis` triad does produce a coherent result.

But the coherent result is **not** a sign rule.

It is this:

> all three exact hysteresis subjects exercise the seam inside the same early `wave_one`-like subject-relative phase band, yet the top-line sign is still mixed.

So the next honest move is **not** more broad phase-age transport.

If this chain continues, the next bounded test should target **intra-band structure inside the early continuation-release zone**, not broader subject-relative phase placement alone.
