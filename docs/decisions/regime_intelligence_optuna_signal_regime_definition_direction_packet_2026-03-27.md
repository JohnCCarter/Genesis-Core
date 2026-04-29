# Regime Intelligence challenger family — SIGNAL regime-definition direction packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `direction-selected / planning-only / no authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet chooses exactly one next research direction after closing the first SIGNAL slice as plateau, but must remain planning-only and must not create admissibility or launch semantics
- **Required Path:** `Quick`
- **Objective:** Select exactly one next RI research direction after closing the zone-entry-threshold SIGNAL surface as non-improving.
- **Candidate:** `future RI SIGNAL regime-definition research lane`
- **Base SHA:** `d227be7e`

### Scope

- **Scope IN:** one docs-only direction decision selecting exactly one next direction and clearly parking the alternatives.
- **Scope OUT:** no source-code changes, no config YAML creation, no validator/preflight/smoke/launch work, no changes under `src/core/**`, no changes to `family_registry.py`, no changes to `family_admission.py`, no slice2, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_signal_regime_definition_direction_packet_2026-03-27.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that implies the next lane is launch-authorized now
- any wording that implies runtime-valid RI conformity
- any wording that selects more than one next direction
- any wording that treats `DECISION` as permanently rejected

## Purpose

This packet answers one narrow question only:

- what is the next chosen RI research direction after closing `SIGNAL slice1` on zone entry thresholds?

This packet is **planning-only governance**.

It does **not**:

- authorize a runnable next lane
- authorize config creation
- authorize validator/preflight/smoke/launch
- grant runtime-valid RI conformity
- reopen comparison, readiness, promotion, or writeback

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/decisions/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence_optuna_signal_slice1_execution_outcome_signoff_summary_2026-03-27.md`
- `docs/decisions/regime_intelligence_optuna_signal_slice1_launch_authorization_packet_2026-03-27.md`

Carried-forward meaning:

1. the broader `SIGNAL` class was previously chosen over `DECISION` and `OBJECTIVE`
2. the first tested SIGNAL surface — `zone entry thresholds` — is now closed as `PLATEAU`
3. that closure applies to the tested surface, not to the entire `SIGNAL` class
4. the next step is therefore to choose the next **specific** direction within the still-open SIGNAL class

## Candidate directions under decision

### Option 1 — SIGNAL / regime-definition surface

Meaning:

- keep the next lane inside the `SIGNAL` class
- move upstream from zone entry thresholds to the surface that shapes regime segmentation or authoritative regime interpretation
- continue to hold objective, EV, confidence, and exit surfaces fixed

Current suitability:

- **CHOSEN NOW**

Rationale:

- `zone entry thresholds` produced exact plateau reproduction and therefore did not separate outcomes
- the next SIGNAL attempt should therefore move upstream rather than repeat another threshold-only variation
- the most plausible upstream SIGNAL candidate class is `regime-definition`, not decision logic

Relevant rationale surfaces in the current codebase:

- `src/core/strategy/regime.py`
- `src/core/strategy/regime_unified.py`
- `src/core/intelligence/regime/authority.py`

Important boundary:

- these surfaces are cited here as **research rationale only**
- this packet does **not** declare them already authorized implementation or tuning surfaces

### Option 2 — SIGNAL / feature-surface

Meaning:

- keep the next lane inside `SIGNAL`, but move to feature selection or signal-input availability instead of regime-definition

Current suitability:

- **NOT CHOSEN NOW**

Reason:

- it remains a valid future SIGNAL alternative, but it is not the next chosen lane while regime-definition remains the cleaner upstream hypothesis

### Option 3 — DECISION

Meaning:

- move the next lane to EV, gating, confidence, or selection logic

Current suitability:

- **NOT CHOSEN NOW**

Reason:

- it remains a parked alternative for future governance review
- it is not permanently rejected
- it is simply not the next chosen lane while SIGNAL still has an upstream regime-definition route left to test

## Decision

### Chosen next direction

- `CHOSEN — SIGNAL / regime-definition surface`

### Parked alternatives

- `NOT CHOSEN NOW — SIGNAL / feature-surface`
- `NOT CHOSEN NOW — DECISION`

## Why this direction is chosen

The direction is chosen because the slice1 result indicates that changing zone entry thresholds did not alter the validated outcome geometry.

Observed meaning carried forward from the closed slice:

- multiple parameter combinations collapsed to the same validated result
- the best validated artifact reproduced the prior plateau signature exactly
- this suggests the previous SIGNAL attempt acted too far downstream to alter the information/regime structure materially

Therefore the next best `SIGNAL` hypothesis is to move **upstream** to `regime-definition surface` rather than abandoning SIGNAL immediately.

## Fixed surfaces in this direction choice

The following surfaces remain fixed in this direction choice:

- objective/scoring class
- EV surface
- confidence surface
- exit/management surface
- family-registry rules
- family-admission rules
- comparison closed
- readiness closed
- promotion closed
- champion/default writeback closed

## Expected improvement signature

A future regime-definition lane would count as an improvement only if at least one validated artifact:

1. has validation score strictly greater than `0.26974911658712664`, and
2. does **not** reproduce the closed plateau tuple below:
   - validation score: `0.26974911658712664`
   - profit factor: `1.8845797002042906`
   - max drawdown: `0.027808774550017137`
   - trades: `63`
   - sharpe: `0.20047738907046656`

## Falsification condition

A future regime-definition lane would be falsified if either:

1. no validated artifact exceeds validation score `0.26974911658712664`, or
2. the best validated artifact reproduces the exact plateau tuple above

## Explicit blocker

This direction packet does **not** make the next lane admissible or launchable.

A separate later packet is still required to resolve:

- whether the intended regime-definition surface is already tunable under existing config authority, or requires implementation-enablement first
- what exact fixed backdrop would govern a later first slice
- what exact boundaries would keep the lane inside `SIGNAL` rather than drifting into `DECISION`

Until that later packet exists, the following remain closed:

- runnable YAML creation
- validator/preflight/smoke/launch for the new lane
- slice2
- comparison/readiness/promotion/writeback

## Bottom line

The next chosen RI direction is now:

- **SIGNAL on regime-definition surface**

This closes only the prior threshold-only SIGNAL surface, keeps the broader SIGNAL class alive, parks `DECISION` for later review, and preserves all launch/admissibility/runtime boundaries for future separate governance.
