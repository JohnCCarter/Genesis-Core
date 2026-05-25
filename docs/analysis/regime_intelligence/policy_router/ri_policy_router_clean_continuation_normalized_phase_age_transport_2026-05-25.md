# RI policy router clean_continuation normalized phase-age transport — 2026-05-25

## Scope

Bounded RESEARCH follow-up to the landed holdout falsifier.

Question:

> once raw absolute `bars_since_regime_change` has already failed on holdouts, can a simple normalized phase-age coordinate recover transport on the same clean-continuation bench?

This slice is observational only.

It does **not** change runtime logic, config authority, defaults, family structure, or prior taxonomy labels.

## Inputs

- taxonomy source: `results/evaluation/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json`
- reference wave discriminator: `results/evaluation/ri_policy_router_clean_continuation_wave_phase_discriminator_2026-05-25.json`
- prior holdout falsifier: `results/evaluation/ri_policy_router_clean_continuation_holdout_generalization_pass_2026-05-25.json`
- 2017 continuation-family surface: `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2017_enabled_vs_absent_action_diffs.json`
- 2017 local-window reference: `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`
- 2017 chronology reference: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_2026-05-06.md`
- emitted artifact: `results/evaluation/ri_policy_router_clean_continuation_normalized_phase_age_transport_2026-05-25.json`

## What changed and what did not

- **Changed:** one new read-only analysis helper and one new retained evaluation artifact that compare normalized phase-age candidates on the existing reference and holdout bench.
- **Did not change:** router code, state taxonomy, existing wave discriminator verdicts, curated data, findings-bank state, or any runtime/test surface.

## Observed

### 1. Three subject-level coordinates stay perfect on the original `2023-12` split

The original local split still separates perfectly not only on raw age, but also on subject-level rewrites of that age:

- raw absolute age: `bars_since_regime_change <= 369`
- subject floor offset: `subject_offset_from_floor <= 6`
- subject min-max progress: `subject_progress_pct <= 0.4`
- subject rank progress: `subject_rank_pct <= 0.458334`

Reference envelopes for the two scale-free candidates are especially clean:

- `subject_progress_pct`
  - `wave_one = 0.0 -> 0.333333`
  - `wave_two = 0.466667 -> 1.0`
- `subject_rank_pct`
  - `wave_one = 0.0 -> 0.416667`
  - `wave_two = 0.5 -> 1.0`

### 2. Window-reset candidates fail locally and act as a useful negative control

The window-relative candidates do **not** preserve the original local split:

- `window_offset_from_start` best accuracy: `0.615385`
- `window_progress_pct` best accuracy: `0.615385`
- `window_rank_pct` best accuracy: `0.538462`

That matches the structural intuition:

> if each continuation burst resets its own local clock, the two `2023-12` waves collapse onto the same `0 -> 1` style window progression surface and stop being separable.

### 3. The scale-free subject-relative candidates rescue all exact holdouts

The exact holdout set in this slice is:

- `harmful_2024_displacement`
- `2017_03_early_anchor`
- `2017_03_late_revisit`
- `2017_03_month_end_revisit`

Both scale-free subject-relative candidates produce coherent single-side mappings on **all 4 exact holdouts**:

- `subject_progress_pct`
- `subject_rank_pct`

Exact mappings:

- `harmful_2024_displacement` -> `wave_one` side only
  - `subject_progress_pct = 0.0`
  - `subject_rank_pct = 0.0`
- `2017_03_early_anchor` -> `wave_one` envelope only
  - `subject_progress_pct = 0.033333 -> 0.133333`
  - `subject_rank_pct = 0.0625 -> 0.25`
- `2017_03_late_revisit` -> `wave_two` envelope only
  - `subject_progress_pct = 0.766667 -> 0.833333`
  - `subject_rank_pct = 0.6875 -> 0.8125`
- `2017_03_month_end_revisit` -> `wave_two` envelope only
  - `subject_progress_pct = 0.933333 -> 1.0`
  - `subject_rank_pct = 0.875 -> 1.0`

### 4. The full `2017-03` family still spans both sides, which is expected

On the full March continuation-family holdout:

- `subject_progress_pct` spans `0.0 -> 1.0`
- `subject_rank_pct` spans `0.0 -> 1.0`

So the full family does **not** collapse to one side.
Instead it spans both wave envelopes.

That is not a contradiction.
It is consistent with the already-landed chronology reread:

> `2017-03` is one early anchor plus two later revisit waves.

In other words, the family-level holdout contains multiple phases, so the family surface should not be forced into one single-side verdict.

### 5. Subject floor offset is better than raw age, but weaker than the scale-free candidates

`subject_offset_from_floor` also stays perfect on the local `2023-12` split.
But on exact holdouts it only gets coherent single-side mappings for `2 / 4` exact subjects.

It succeeds for:

- `harmful_2024_displacement`
- `2017_03_early_anchor`

It fails on the later 2017 revisit windows because they sit above the original combined offset envelope rather than inside the `wave_two` offset range.

So the weaker but still useful conclusion is:

> localizing the age floor helps, but scale-free subject-relative progress helps more.

## Inferred

### 1. The transportable part is subject-relative phase progression, not raw absolute age

The smallest honest reading is now:

- raw absolute age is carrier-local and fails on holdouts
- window-reset progression destroys the original local split
- subject-relative normalized progress preserves the local split and maps the exact holdouts coherently

So the live inference is:

> `clean_continuation` phase-age looks more portable as **subject-relative progression** than as raw absolute regime age.

### 2. The 2017 chronology chain and the normalized-age chain now reinforce each other

The earlier chronology reread already said:

- `2017-03` = early anchor + later revisit waves

This new slice adds:

- early anchor maps to the `wave_one` side
- the two late revisit windows map to the `wave_two` side

So the subject-relative normalized-age read is not just numerically cleaner; it is also structurally aligned with the prior chronology language.

## Unverified

The following remain open:

1. whether the same scale-free subject-relative candidates survive on the continuation-release hysteresis bench (`2021-08`, `2025-10`, `2018-03`)
2. whether a full taxonomy-capable `2017-03` surface would keep the same early-anchor / late-revisit phase mapping
3. whether an even cheaper single canonical transport coordinate should prefer `subject_progress_pct` or `subject_rank_pct`

## Verification

- `ruff check scripts/analyze/ri_policy_router_clean_continuation_normalized_phase_age_transport_20260525.py` -> pass
- `python scripts/analyze/ri_policy_router_clean_continuation_normalized_phase_age_transport_20260525.py` -> emitted artifact with status `subject_relative_normalized_phase_age_partially_recovers_transport`

## Bottom line

The previous slice showed that raw absolute age does **not** transport.
This slice sharpens that result:

> subject-relative normalized phase-age **does** partially recover transport, while window-reset phase-age does not.

That makes the next best move clear:

test the same scale-free subject-relative candidates on the continuation-release hysteresis holdout bench, rather than reopening raw absolute thresholds.
