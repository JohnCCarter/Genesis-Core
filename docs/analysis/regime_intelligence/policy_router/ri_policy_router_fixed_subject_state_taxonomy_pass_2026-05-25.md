# RI policy router fixed-subject state taxonomy pass

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / read-only deterministic state taxonomy pass / observational only`

This slice does **not** introduce a new runtime policy.
It applies a deterministic, decision-time-only state taxonomy over the already-fixed `2023-12` vs late-`2024` contrast carrier.

The taxonomy tested here is:

- `clean_continuation`
- `aging_continuation`
- `blocked_mixed`
- `transition_chop`

The purpose is to see which candidate **state labels** already materialize on the fixed carrier before any runtime routing change is proposed.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW` — read-only deterministic classification over an already-generated fixed-window artifact
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** test whether the candidate state labels can be described deterministically on the already-fixed `2023-12` and late-`2024` subjects without widening year screening or touching runtime code
- **Candidate:** `fixed subject state taxonomy pass`
- **Base SHA:** `270b65346ebe9208c953abfc7181bf83df34d8f5`

## Scope

### Scope IN

- one read-only taxonomy helper over the fixed-window phase-contrast artifact
- one JSON artifact with deterministic state classifications
- one short evidence note summarizing which state labels did and did not materialize

### Scope OUT

- `src/**`
- `tests/**`
- runtime routing changes
- threshold retuning
- new policy identities
- year-level widening
- promotion/readiness claims

## Evidence inputs

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_live_state_policy_execution_crosswalk_2026-05-25.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.md`
- `results/evaluation/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json`
- `results/evaluation/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json`
- `scripts/analyze/ri_policy_router_fixed_subject_state_taxonomy_pass_20260525.py`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_fixed_subject_state_taxonomy_pass_20260525.py --base-sha 270b65346ebe9208c953abfc7181bf83df34d8f5`

## Main result

The fixed carrier already supports a useful but incomplete state taxonomy.

Dominant subject labels that materialized cleanly:

- `clean_continuation`
- `blocked_mixed`

Segment-level labels that materialized inside the carrier:

- `clean_continuation`
- `aging_continuation`
- `blocked_mixed`

Candidate state label that **did not** materialize on this carrier:

- `transition_chop`

So the current fixed subject pair is already enough to support:

- a clean continuation state, and
- a blocked mixed harmful state,

while still showing that aged continuation appears as an embedded blocked substructure rather than as the dominant whole-subject state on this exact carrier.

## Observed

### 1. `2023-12` wave 1, wave 2, and combined all classify as `clean_continuation`

The deterministic pass classifies all fixed `2023-12` continuation subjects as `clean_continuation` because they remain:

- `continuation_release` only
- `RI_continuation_policy` only
- `stable_continuation_state` only
- free of blocked-like or defensive-transition segments

That holds for:

- `continuation_2023_wave_one`
- `continuation_2023_wave_two`
- `continuation_2023_combined`

### 2. The late-`2024` harmful subject classifies as `blocked_mixed`

The harmful late-`2024` combined subject classifies as `blocked_mixed` because blocked-like and aged-weak blocked rows dominate over the single continuation interruption.

Observed decision-time structure on `harmful_2024_combined`:

- phase labels:
  - `blocked_aged_weak_continuation_guard = 4`
  - `blocked_insufficient_evidence = 5`
  - `blocked_stable_context = 1`
  - `continuation_release = 1`
- selected policies:
  - `RI_no_trade_policy = 9`
  - `RI_continuation_policy = 2`

So this surface is not just negative or blocked; it is structurally mixed and blocked-dominant.

### 3. `aging_continuation` materializes only as embedded substructure inside the harmful `2024` pocket

The fixed carrier does materialize `aging_continuation`, but only at segment level.

Inside `harmful_2024_regression_target`, the pass finds two separate aged-weak segments:

- `2024-11-28T15:00:00+00:00` -> `2024-11-29T00:00:00+00:00` (`2` rows)
- `2024-11-30T12:00:00+00:00` -> `2024-11-30T21:00:00+00:00` (`2` rows)

Those segments classify as `aging_continuation` because they are explicitly governed by `AGED_WEAK_CONTINUATION_GUARD`.

But the full `harmful_2024_regression_target` still classifies as `blocked_mixed`, not `aging_continuation`, because the aged-weak rows are interleaved with a larger insufficient-evidence blocked structure.

### 4. `transition_chop` does not materialize on this fixed carrier

The deterministic pass found no segment that qualified as `transition_chop`.

The reason is narrow and useful:

- no segment carried `transition_pressure_detected`
- no segment carried `defensive_transition_state`
- no segment selected `RI_defensive_transition_policy`

So `transition_chop` is not falsified in general.
It simply does not appear on the current fixed `2023-12` vs late-`2024` carrier.

### 5. The classification boundary held: outcome metrics were reported, not used as taxonomy inputs

The pass used decision-time fields for classification and kept forward-return / MFE / MAE metrics observational only.

That matters because the taxonomy result is now honest about two things at once:

- `2023-12` still materializes as `clean_continuation`, and
- `2023-12` wave 2 can still be observationally weak without collapsing the state taxonomy back into outcome labels.

So this pass preserves the separation:

- **state** = what the local structure is
- **outcome** = what happened later

## Inferred

The fixed carrier is already strong enough to support a first explicit state-taxonomy reading:

- `clean_continuation` is real on the locked `2023-12` side
- `blocked_mixed` is real on the locked late-`2024` side
- `aging_continuation` is real as a bounded blocked subsegment
- `transition_chop` needs a different carrier if we want to test it honestly

That suggests the cheapest admissible next slice is **not** to widen the policy set.
It is one of these two narrower follow-ups:

1. keep the same carrier and test whether `wave 1` vs `wave 2` can be separated by a decision-time-only discriminator **inside** `clean_continuation`, or
2. bring in a separate fixed defensive-transition carrier if we want an honest first pass on `transition_chop`.

## Unverified

This slice does **not** prove:

- that the current router should gain new runtime state objects now
- that `transition_chop` is unimportant overall
- that `clean_continuation` is locally favorable just because it classifies cleanly
- that one portable state taxonomy will separate positive from negative years by itself
- that runtime tuning is justified

## What changed and what did not

What changed:

- the repo now contains a reproducible fixed-subject taxonomy helper
- the repo now contains a classification artifact showing which candidate state labels do and do not materialize on the current fixed carrier
- the policy discussion can now lean on an explicit state taxonomy result rather than only conceptual crosswalk language

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no new policy identity was introduced
- no thresholds, guards, or sizing rules changed
- no annual verdict was reopened
- no readiness or promotion claim was made
