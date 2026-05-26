# RI policy router continuation_release_hysteresis widening candidate inventory — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `continuation_release_hysteresis` intra-band sign-candidate slice.

Question:

> if the frozen full-calendar-month inventory is already exhausted as an exact top-line-divergent bench, which seam-active **non-divergent** months are the best current widening candidates for a fresh packet?

This slice is observational only.

It does **not** run new backtests, create new exact-subject verdicts, widen the frozen monthly bench into a new authoritative subject set, or claim that any monthly near-miss already contains proven hidden local divergence.

## Inputs

- frozen monthly inventory windows: `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`
- frozen triad synthesis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md`
- triad-local sign-candidate artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_2026-05-26.json`

## What changed and what did not

- **Changed:** one new read-only helper ranked seam-active monthly near-miss windows by inventory-level proxy similarity to the frozen negative triad signature versus the positive triad centroid.
- **Did not change:** no new exact subjects were promoted, no new backtests were run, no runtime/config surfaces changed, and the frozen monthly bench was not reopened as if it still contained unresolved exact top-line-divergent subjects.

## Observed

### 1. The frozen monthly bench is still exhausted as an exact top-line-divergent subject set

The monthly inventory still contains exactly the same three top-line-divergent full-month subjects:

- `2018-03` — negative
- `2021-08` — positive
- `2025-10` — positive

So this slice did **not** discover a fourth divergent month.

It stayed inside the smaller honest question:

> among the seam-active months with **zero** monthly top-line divergence, which ones look most worth widening next?

### 2. Eight seam-active near-miss months are closer to the negative triad signature than to the positive centroid on the monthly proxy surface

Using the available monthly inventory proxies:

- `behavioral_row_diff_count`
- `selected_policy_diff_count`
- `switch_reason_diff_count`
- `size_diff_count`
- `baseline_continuation_release_row_count`
- `release_zero_continuation_release_row_count`
- `release_retention_ratio`

the helper found `8` seam-active non-divergent months that are closer to the frozen negative signature than to the positive centroid.

The strongest current negative-like widening candidates are:

1. `2021-04`
   - negative distance `0.308643`
   - positive distance `0.757418`
   - counts: `37 behavioral`, `6 policy`, `6 switch`, `2 size`
   - retention: `9 / 16 = 0.5625`
2. `2020-06`
   - negative distance `0.365853`
   - positive distance `0.856024`
   - counts: `28 behavioral`, `6 policy`, `6 switch`, `2 size`
   - retention: `3 / 9 = 0.333333`
3. `2024-01`
   - negative distance `0.431553`
   - positive distance `0.543995`
   - counts: `31 behavioral`, `5 policy`, `5 switch`, `1 size`
   - retention: `8 / 11 = 0.727273`
4. `2018-09`
   - negative distance `0.514624`
   - positive distance `0.922512`
   - counts: `46 behavioral`, `3 policy`, `3 switch`, `1 size`
   - retention: `9 / 14 = 0.642857`

So the current widening picture is no longer arbitrary.

There is now a bounded short-list for the next packet rather than a broad “look somewhere else” instruction.

### 3. The same inventory also supplies reasonable positive/neutral controls

The best current positive-like or neutral controls are:

1. `2023-05`
   - positive distance `0.377319`
   - negative distance `0.941918`
   - counts: `10 behavioral`, `7 policy`, `7 switch`, `1 size`
   - retention: `7 / 7 = 1.0`
2. `2024-02`
   - positive distance `0.481515`
   - negative distance `0.608882`
   - counts: `18 behavioral`, `3 policy`, `6 switch`, `1 size`
   - retention: `9 / 12 = 0.75`
3. `2018-12`
   - positive distance `0.521871`
   - negative distance `0.599382`
   - counts: `15 behavioral`, `3 policy`, `6 switch`, `1 size`
   - retention: `6 / 9 = 0.666667`

That matters because the next widening packet does not need to compare only negative-leaning candidates against the old triad.

It can pair negative-like near-misses against same-surface controls from the current inventory.

### 4. This ranking uses proxy fields, not the full intra-band feature set

The monthly inventory can only see whole-window count/retention proxies.

It cannot see the decisive local fields that separated the frozen triad more sharply in the prior slice, such as:

- `decisive_rank_pct`
- `decisive_hours_from_cluster_start`
- `decisive_action_edge`
- `decisive_confidence_gate`
- `decisive_clarity_score`

So this slice did **not** claim that `2021-04`, `2020-06`, `2024-01`, or `2018-09` already match `2018-03` on the full intra-band signature.

It only says they are the best current widening candidates on the monthly proxy surface.

## Inferred

### 1. The next honest widening packet should be localized, not global

Because the frozen monthly bench already exhausted the exact divergent months, the next admissible move is not a blind reopen of the entire monthly grid.

The smaller honest move is:

> localize around the top negative-like near-miss months and pair them with positive-like controls from the same inventory surface.

That is cheaper, more falsifiable, and more faithful to the packet boundary than re-running the whole month bench without a narrowing target.

### 2. `2021-04` is the cleanest first widening target on the current proxy surface

Among the near-miss months, `2021-04` is the closest to the frozen negative signature while still carrying the exact same `6 / 6 / 2` policy/switch/size count profile as `2018-03`.

So if only one first widening target is allowed, `2021-04` is the least arbitrary current pick.

## Unverified

The following remain open:

1. whether any of the shortlisted near-miss months contain local sub-window divergence once a fresh packet widens beyond the full-month grid
2. whether the monthly proxy ranking survives when the decisive-timing and decisive-support fields are restored on a localized surface
3. whether `2021-04` remains the best widening target once local-window evidence is actually generated

## Verification

- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_20260526.py` -> pass
- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_20260526.py` -> emitted artifact with status `seam_active_non_divergent_months_ranked_for_widening`

## Bottom line

The frozen monthly inventory still has only one negative exact subject and no hidden fourth divergent month.

But it is no longer shapeless.

The new bounded evidence says:

> if the next packet must widen beyond the frozen monthly triad, the least arbitrary negative-like targets are `2021-04`, `2020-06`, `2024-01`, and `2018-09`, and the cleanest current positive/neutral controls are `2023-05`, `2024-02`, and `2018-12`.

That gives the next widening packet a concrete starting roster without pretending that the packet has already been run.
