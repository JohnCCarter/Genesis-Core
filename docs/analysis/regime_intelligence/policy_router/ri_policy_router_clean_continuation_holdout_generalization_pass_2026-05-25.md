# RI policy router clean_continuation holdout generalization pass — 2026-05-25

## Scope

Bounded RESEARCH reread of the already-landed `clean_continuation` wave discriminator.

Question:

> does the perfect `bars_since_regime_change` split learned on exact `2023-12` wave one vs wave two transport to unseen continuation-family holdouts, or is it only a carrier-local absolute-age rule?

This slice is observational only.

It does **not** change runtime logic, config authority, defaults, promotion state, or family structure.

## Inputs

- rule source: `results/evaluation/ri_policy_router_clean_continuation_wave_phase_discriminator_2026-05-25.json`
- taxonomy source: `results/evaluation/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json`
- external holdout surface: `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2017_enabled_vs_absent_action_diffs.json`
- supporting 2017 packaging reference: `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`
- emitted artifact: `results/evaluation/ri_policy_router_clean_continuation_holdout_generalization_pass_2026-05-25.json`

## What changed and what did not

- **Changed:** one new read-only analysis helper and one new evaluation artifact that test holdout transport explicitly.
- **Did not change:** router behavior, taxonomy rules, training surfaces, curated data, findings-bank state, or any runtime/test contract.

## Observed

### 1. The learned reference rule is still exact on the original carrier

The landed wave discriminator keeps the same perfect rule on exact `2023-12`:

- reference feature: `bars_since_regime_change`
- perfect threshold: `369`
- `wave_one` envelope: `363 -> 368`
- `wave_two` envelope: `370 -> 378`

So the original local result remains intact.

### 2. `harmful_2024_displacement` keeps the clean-continuation shell but sits far below the reference age envelope

The already-materialized taxonomy holdout row remains:

- `selected_policy = RI_continuation_policy`
- `switch_reason = stable_continuation_state`
- `zone = low`
- `phase_label = continuation_release`

But its regime age is:

- `bars_since_regime_change = 281`

That is `82` bars below the reference combined envelope floor (`363`).

At the same time, its non-age features still sit inside the reference combined ranges:

- `action_edge = 0.072747` -> overlaps reference range
- `clarity_score = 39` -> inside reference range
- `confidence_gate = 0.536374` -> inside reference range

### 3. `2017-03` exposes the same visible continuation family while living at much smaller absolute ages

The retained `2017-03` continuation-family surface preserves the visible shell used by the older local-window concentration slice:

- `absent_action = NONE`
- `enabled_action = LONG`
- `selected_policy = RI_continuation_policy` on all `17` retained rows
- `switch_reason = stable_continuation_state` on all `17` retained rows
- `zone = low` on all `17` retained rows

Important caveat:

- `phase_label` is **not** present on this retained annual action-diff surface, so this holdout is a visible continuation-family match, not a full taxonomy relabel.

Its regime-age profile is dramatically lower than the `2023-12` reference:

- full holdout range: `35 -> 65`
- mean: `49.411765`
- distance below reference floor: `298` bars

Its three largest local windows remain:

- `2017-03-04T09:00:00+00:00 -> 2017-03-05T21:00:00+00:00` with bars `36 -> 39`
- `2017-03-23T18:00:00+00:00 -> 2017-03-24T12:00:00+00:00` with bars `58 -> 60`
- `2017-03-29T21:00:00+00:00 -> 2017-03-30T15:00:00+00:00` with bars `63 -> 65`

But its non-age features still overlap the `2023-12` reference combined ranges:

- `action_edge`: overlap present
- `clarity_score`: overlap present, fully contained
- `confidence_gate`: overlap present

### 4. The holdout result is a clean falsification of raw absolute-age transport

Across the two holdouts tested here:

- holdouts with any `bars_since_regime_change` overlap against the `2023-12` reference envelope: `0`
- holdouts with `action_edge` overlap: `2`
- holdouts with `clarity_score` overlap: `2`
- holdouts with `confidence_gate` overlap: `2`

So the transport result is not “everything changed.”

Instead it is narrower and more useful:

> the visible continuation shell can recur while the absolute regime-age coordinate does not.

## Inferred

### 1. The `369` split is carrier-local in absolute-age terms

The cleanest current reading is:

- `2023-12` learned a real local phase-age split
- but the split is **not** portable as a raw absolute `bars_since_regime_change` rule

The new artifact therefore supports:

> `absolute_clean_continuation_age_split_falsified_on_holdouts`

### 2. Non-age shell features appear more stable than raw absolute age

Both holdouts preserve substantial overlap on:

- `action_edge`
- `clarity_score`
- `confidence_gate`

while failing the absolute-age envelope completely.

That suggests the next honest hypothesis is not “throw away age entirely,” but rather:

> phase-age probably needs **subject-local normalization** before it can transport.

## Unverified

The following are still open:

1. whether a normalized age coordinate, local percentile, or within-carrier dwell-age measure rescues transport
2. whether the continuation-release hysteresis bench (`2021-08`, `2025-10`, `2018-03`) shows the same non-age overlap plus age non-transport pattern
3. whether a later bounded slice can relabel `2017-03` on a full taxonomy-capable surface instead of the retained annual action-diff surface

## Verification

- `ruff check scripts/analyze/ri_policy_router_clean_continuation_holdout_generalization_pass_20260525.py` -> pass
- `python scripts/analyze/ri_policy_router_clean_continuation_holdout_generalization_pass_20260525.py` -> emitted artifact with status `absolute_clean_continuation_age_split_falsified_on_holdouts`

## Bottom line

The perfect `2023-12` split survives as a **local** result, but not as a portable absolute-age law.

The best next move is no longer “reuse `369` elsewhere.”
The best next move is to test a **normalized phase-age** candidate on the same holdout bench.
