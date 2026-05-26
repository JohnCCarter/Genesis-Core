# RI policy router fixed three-cohort phase discriminator

Date: 2026-05-26
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / read-only fixed-subject discriminator / observational only`

This slice continues option A by staying off the `continuation_release_hysteresis` seam and reusing the already-locked fixed-subject contrast surface.

The question is narrower than a new annual pass:

> within the already-locked local subjects, does any tiny decision-time discriminator separate
>
> - a **less-hostile phase-pure continuation wave**
> - a **phase-pure but still weak continuation wave**
> - a **blocked-dominant mixed harmful pocket**
>
> without reopening runtime tuning, annual screening, or a portable global rule claim?

This slice does **not**:

- reopen runtime/config/strategy tuning
- claim annual transport or promotion readiness
- override the earlier holdout falsification of raw absolute-age transport
- relax the standing warning that the policy also degraded a broadly good year like `2024`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW`
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** test whether a tiny decision-time discriminator separates the fixed `2023-12` wave one subject, the fixed `2023-12` wave two subject, and the fixed harmful `2024` target pocket
- **Candidate:** `fixed three-cohort phase discriminator`
- **Base SHA:** `f8b9e659ccd106a81bd8033d30dfe1646330ab42`

## Evidence inputs

Primary:

- `scripts/analyze/ri_policy_router_fixed_three_cohort_phase_discriminator_20260526.py`
- `results/evaluation/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json`
- `results/evaluation/ri_policy_router_fixed_three_cohort_phase_discriminator_2026-05-26.json`

Supporting context only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_clean_continuation_holdout_generalization_pass_2026-05-25.md`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_fixed_three_cohort_phase_discriminator_20260526.py --base-sha f8b9e659ccd106a81bd8033d30dfe1646330ab42`

## Fixed cohort lock

### `2023-12` wave one

- source cohort: `continuation_2023_wave_one`
- `6` rows
- `action_pair = NONE -> LONG`
- `switch_reason = stable_continuation_state`
- `phase_label = continuation_release`
- `bars_since_regime_change = 363 -> 368`

### `2023-12` wave two

- source cohort: `continuation_2023_wave_two`
- `7` rows
- `action_pair = NONE -> LONG`
- `switch_reason = stable_continuation_state`
- `phase_label = continuation_release`
- `bars_since_regime_change = 370 -> 378`

### fixed harmful `2024` target pocket

- source cohort: `harmful_2024_regression_target`
- `9` rows
- `action_pair = LONG -> NONE`
- mixed blocked target reason split retained from the source artifact
- `bars_since_regime_change = 281 -> 282`

## Main result

A perfect single-feature ordered split exists on this fixed local surface.

Using `bars_since_regime_change` alone:

- `<= 322.5` -> `2024 harmful target`
- `322.5 < value <= 369.0` -> `2023-12 wave 1`
- `> 369.0` -> `2023-12 wave 2`

That split classifies all `22 / 22` rows correctly.

So the next non-seam leaf slice did **not** collapse into overlap.
It found one tiny decision-time coordinate that cleanly orders all three already-locked cohorts.

But that result stays local.
The earlier holdout pass already showed that raw absolute phase age does **not** transport cleanly across other continuation-family holdouts, so this is a fixed-subject discriminator, not a deployable threshold law.

## Observed

### 1. `bars_since_regime_change` cleanly orders all three cohorts

Single-feature ordered split search:

- feature: `bars_since_regime_change`
- lower threshold: `322.5`
- upper threshold: `369.0`
- class order:
  - `2024 harmful target`
  - `2023-12 wave 1`
  - `2023-12 wave 2`
- accuracy: `1.0`

Cohort envelopes:

- `2024 harmful target`: `281 -> 282`, mean `281.222222`
- `2023-12 wave 1`: `363 -> 368`, mean `365.5`
- `2023-12 wave 2`: `370 -> 378`, mean `373.428571`

So the three fixed cohorts are not merely different in average age.
They are fully non-overlapping on this local coordinate.

### 2. Softer router-local descriptive fields preserve the same harmful -> weak -> less-hostile ordering, but they do not fully separate all three cohorts

Ordered mean ranking is the same on all three softer numeric fields:

- `action_edge`: `0.040542 < 0.095016 < 0.108708`
- `confidence_gate`: `0.520271 < 0.547508 < 0.554354`
- `clarity_score`: `36.888889 < 40.285714 < 41.0`

Best single-feature ordered split accuracy by field:

- `action_edge`: `0.863636`
- `confidence_gate`: `0.863636`
- `clarity_score`: `0.818182`

All three softer fields isolate the harmful `2024` target cleanly on the low end, but they leak overlap between `2023-12 wave 1` and `2023-12 wave 2`.

### 3. The harmful `2024` pocket is perfectly isolatable one-vs-rest even without the age field

Perfect one-vs-rest rules for `2024 harmful target`:

- `action_edge <= 0.067972`
- `clarity_score <= 38.5`
- `confidence_gate <= 0.533986`
- `bars_since_regime_change <= 322.5`

So the `2024` target pocket does not only differ by raw regime age.
It also sits on a distinctly weaker local router-quality shell than either `2023-12` continuation wave.

### 4. Outcome context remains mixed and keeps this slice descriptive only

Observed `fwd_16_close_return_pct` means:

- `2024 harmful target`: `-0.441517%` (`11.11%` positive)
- `2023-12 wave 1`: `-0.154828%` (`50.0%` positive)
- `2023-12 wave 2`: `-1.027688%` (`0.0%` positive)

So the ordered discriminator is a structural/local-quality read, not a full local payoff law.
`wave 1` is less hostile than the harmful `2024` target, but `wave 2` is still worse on this proxy surface even though it remains phase-pure.

## Inferred

The best current A-aligned reading is now tighter:

> the leading local explanation has moved away from seam hysteresis and toward a combination of **phase-age / dwell-age ordering** plus **blocked-dominant mixed-pocket structure**.

This is more useful than the weaker stories we have already squeezed dry:

- the seam does not explain broader annual `2024` harm on the fixed same-stack annual surface
- exact monthly seam positives like `2025-10` are anchor-sensitive and not safely annualizable
- `insufficient_evidence` alone is too narrow to explain the harmful pocket

The new fixed three-cohort read says something sharper:

- the harmful `2024` target pocket sits both **earlier** and **weaker** on the local decision-time surface than the two `2023-12` continuation waves
- `wave 1` and `wave 2` stay phase-pure alike, but the local age coordinate still separates the less-hostile wave from the weaker one

That keeps the standing `2024` warning explicit instead of softening it away: the policy can still degrade a broadly good year, and the current local evidence says the harmful pocket is structurally distinct even before outcome claims are made.

## Unverified

This slice does **not** prove:

- that raw absolute `bars_since_regime_change` is portable outside these fixed subjects
- that a deployable global threshold should be introduced
- that the same three-way ordering appears on another positive-year or negative-year pocket
- that normalized phase age, local percentile age, or another subject-relative age measure will transport
- that runtime tuning is justified

## Consequence

The next honest A-aligned move is now smaller and clearer than another seam pass.

If we continue, the best bounded follow-up is to test a **subject-relative or normalized phase-age coordinate** against this same three-cohort setup and then on a tiny external holdout bench.

That would directly answer the remaining gap:

- keep the newly found local three-way ordering,
- preserve the explicit `2024` harm warning,
- and test whether the useful part of the discriminator is the ordering itself or only its raw absolute-age carrier coordinate.

## Verification

- `python -m black scripts/analyze/ri_policy_router_fixed_three_cohort_phase_discriminator_20260526.py` -> pass
- `python -m ruff check scripts/analyze/ri_policy_router_fixed_three_cohort_phase_discriminator_20260526.py` -> pass
- `python scripts/analyze/ri_policy_router_fixed_three_cohort_phase_discriminator_20260526.py --base-sha f8b9e659ccd106a81bd8033d30dfe1646330ab42` -> emitted artifact with status `fixed_three_cohort_phase_discriminator_generated`

## What changed and what did not

What changed:

- one new read-only analysis helper now materializes a fixed-subject three-cohort discriminator
- one new evaluation artifact now captures numeric ordering, one-vs-rest rules, and ordered-split search
- the non-seam leaf evidence chain now has an explicit answer to the “next tiny descriptive discriminator” question raised by the earlier fixed-window contrast note

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no annual screening was reopened
- no seam parameter was retuned
- no portable deployment rule was claimed
- no readiness or promotion claim was made
