# Genesis-Core Edge Topology — Phase 2 period comparison packs

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `fe591061`
Status: `completed / observational comparison pack / annual-primary plus monthly-sidecar`

## Purpose

This slice moves beyond rankings and compares the content of selected period buckets.

It does **not** claim that every ranked year or month now has a fully observed local mechanism.
Instead, it freezes one bounded comparison pack built from the strongest currently retained period surfaces.

## Scope

### Scope IN

- one annual primary cohort spanning distinct Edge Topology classes
- one explicit monthly sidecar for the only current month-level exact-subject triad with retained local policy-path evidence
- comparison of decision behavior, policy activation, regime/state mix, execution/non-execution proxies, drawdown behavior, and failure-mode concentration where the current retained surfaces support them

### Scope OUT

- runtime behavior changes
- new backtests
- feature-level raw mining
- fake month-level `enabled vs absent` generalization
- pretending that exit-family or full ledger decomposition is already present on every selected period surface

## Evidence inputs

- `results/research/edge_topology/phase_1_period_rankings/year_rankings_2017_to_2025.json`
- `results/research/edge_topology/phase_1_period_rankings/month_rankings_2016_07_to_2026_03.json`
- `results/research/ri_policy_router_negative_year_pockets_20260428/negative_year_pocket_summary.json`
- `results/research/ri_policy_router_positive_year_pockets_20260428/positive_year_pocket_summary.json`
- `results/research/ri_policy_router_shared_pocket_outcome_quality_20260428/shared_pocket_outcome_quality_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/continuation_release_hysteresis_topline_subject_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/continuation_release_hysteresis_topline_subject_2025_10_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/continuation_release_hysteresis_topline_subject_2018_03_summary.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.md`

## Emitted artifact

- `results/research/edge_topology/phase_2_period_comparisons/phase_2_period_comparison_bundle_annual_primary_with_monthly_sidecar_2019_2025.json`

## Selected cohort

### Annual primary cohort

The annual primary pack intentionally spans four different topology classes:

1. `2025` — absolute-positive and control-positive
2. `2024` — absolute-top but control-negative
3. `2022` — absolute-negative but control-positive
4. `2019` — flat absolute and control-negative

### Monthly sidecar

The month sidecar remains narrower.
It uses the only current full-month exact-subject triad with retained local policy-path evidence:

- `2021-08` — positive toggle delta
- `2025-10` — positive toggle delta
- `2018-03` — negative toggle delta

This sidecar is **not** a general monthly `enabled vs absent` comparison pack.
It is a comparator-family-specific local pack for the continuation-release hysteresis seam.

## Observed

### 1. The annual primary cohort shares one structural pocket, regardless of sign

Across all four annual subjects, the same broad structural pocket recurs:

- `low` zone dominates (`65.54%` to `68.69%` of action diffs)
- `bars_since_regime_change >= 8` dominates (`97.16%` to `100%`)
- `LONG -> NONE` suppression is the largest flow (`64.68%` to `69.99%`)
- `NONE -> LONG` continuation substitution is the second flow (`29.48%` to `35.21%`)
- `RI_continuation_policy` plus `RI_no_trade_policy` carry almost all policy mass

That means period class is **not** first separated by whether this pocket exists.
The pocket is structurally common across both strong and weak classes.

### 2. The clearest annual split is policy mix and control-relative outcome, not pocket presence

`2025` and `2022` are the two control-positive subjects in the primary cohort.
Relative to `2024` and `2019`, they lean more continuation-heavy and less suppressor-heavy:

- `2022` continuation-policy share = `70.41%`
- `2025` continuation-policy share = `63.78%`
- `2024` continuation-policy share = `57.90%`
- `2019` continuation-policy share = `64.41%`

The suppressor side is heaviest in the absolute-top but control-negative year:

- `2024` no-trade-policy share = `41.04%`
- `2024` aged-weak share = `25.76%`

So the current annual comparison pack says the relative edge split lives more in **mix and quality** than in whether the late low-zone shape exists at all.

### 3. Absolute strength and control-relative strength diverge inside the comparison pack

The most visually important subject is `2024`:

- enabled return = `+4.745629%`
- absent return = `+6.339013%`
- delta = `-1.593385 pp`

So the strongest absolute year in the pack is still a control-negative year.

The mirror case is `2022`:

- enabled return = `-0.876681%`
- absent return = `-2.751242%`
- delta = `+1.874561 pp`

So a negative absolute year can still be one of the strongest control-positive periods.

This comparison pack therefore locks the second topology rule:

- **absolute strength and relative edge are different coordinates, not variants of one score**

### 4. Drawdown behavior also follows the same split

Drawdown comparison across the annual primary cohort is consistent with the control-relative split:

- `2025`: enabled max drawdown `2.622936%` vs absent `3.489014%` -> enabled better
- `2022`: enabled max drawdown `2.354833%` vs absent `3.350683%` -> enabled better
- `2024`: enabled max drawdown `2.219202%` vs absent `1.428062%` -> enabled worse
- `2019`: enabled max drawdown `1.073599%` vs absent `0.489823%` -> enabled worse

So the control-negative annual subjects are not merely weaker on return versus control; they also carry worse drawdown containment on the same retained summary surface.

### 5. The strongest cross-year failure boundary is the blocked baseline-long cohort, not the substituted continuation cohort

The retained shared-pocket proxy surface remains clearest on blocked baseline longs.

Blocked baseline-long `fwd_16` proxy summary:

- negative full years: mean `+0.356117%`, median `+0.076866%`, `>0` share `51.08%`
- positive full years: mean `-0.172585%`, median `-0.261849%`, `>0` share `45.99%`

So the blocked cohort flips descriptive quality by year-group direction.

The substituted continuation cohort does **not** separate as cleanly:

- negative full years: mean `+0.458476%`, median `+0.182040%`
- positive full years: mean `-0.307565%`, median `+0.212351%`

That keeps the strongest current anti-edge boundary on the blocked side rather than on a simple continuation-good / continuation-bad rule.

### 6. The monthly sidecar confirms a real seam, but not a stable sign

The frozen month triad shares the same local continuation-release mechanism, but not the same sign:

- `2021-08` delta = `+0.188901 pp`
- `2025-10` delta = `+0.171348 pp`
- `2018-03` delta = `-0.009372 pp`

The negative subject also carries the heaviest local behavioral drift:

- `2018-03` behavioral row diffs = `35`
- `2025-10` behavioral row diffs = `19`
- `2021-08` behavioral row diffs = `13`

So Phase 2 now has a month-level local warning as well:

- **the seam is real, but more drift does not imply better sign**

## Inferred

### 1. The next attribution map should treat the late low-zone pocket as shared background, not as the discriminator itself

The discriminator appears to be:

- policy mix
- suppressor share
- blocked-entry quality
- local seam timing/retention quality

not the mere existence of the late low-zone bars-`8+` pocket.

### 2. The annual surface is the stronger backbone for topology promotion than the monthly surface

The annual primary pack supports:

- returns
- profit factor
- drawdown
- action-flow mix
- policy mix
- switch-reason concentration
- blocked/substituted proxy comparison

The monthly sidecar supports a narrower but useful local seam comparison.
So later promotions should lean annual-first and use the month triad as local corroboration, not as a universal month law.

### 3. Flat periods remain important but not yet fully explained

`2019` is still useful because it shows a near-flat year can already sit on the control-negative side with worse drawdown and a suppressor-heavier mix.
But Phase 2 still does **not** prove that the flat bucket forms one coherent structural class.

## Unverified

- This slice does **not** prove a full annual exit-family map; the current annual pocket summaries do not expose one.
- This slice does **not** prove a general monthly `enabled vs absent` control map.
- This slice does **not** prove that the selected annual four-year cohort exhausts every meaningful topology class on the full annual surface.
- This slice does **not** prove that local month-sidecar sign differences transport beyond the frozen exact-subject triad.

## Consequence

Phase 2 is now complete.
The lane has one stable comparison bundle that is strong enough to start attribution mapping without reselecting subjects ad hoc.

## What changed and what did not

What changed:

- the lane now has one bounded annual comparison pack spanning four distinct topology classes
- the lane now carries an explicit month-level sidecar instead of silently pretending month evidence is general
- blocked-cohort quality inversion is now locked as the strongest current anti-edge boundary on the annual surface

What did **not** change:

- no runtime behavior changed
- no strategy logic changed
- no new backtests were run
- no fake exit-family or full-ledger explanation was introduced where the retained surfaces do not support it
