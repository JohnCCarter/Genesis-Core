# RI advisory environment-fit — trade-level label and mapping contract

This memo is docs-only and definitional.
It defines the minimal authority labels and mapping outputs that are admissible for the new RI trade-level-authority lane.

Governance packet: `docs/decisions/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`

## Why this slice is needed

The previous slice admitted a new lane in principle:

- authority may be defined primarily at the trade-outcome level
- entry rows must remain the scoring-time surface
- partial coverage and uncertainty may be admitted explicitly

But that admissibility decision alone did not define the contract.
Without a contract, the lane would risk drifting into one of two bad outcomes:

- trade-level labels that are too vague to govern later work
- row-level mapping outputs that quietly pretend to be restored exact authority

This slice fixes that boundary.

## Core contract rule

The lane must distinguish **trade-level authority labels** from **entry-row mapping outputs**.

### Trade-level authority labels

These are ex-post authority judgments about how a completed trade behaved on the governed evaluation surface.
They live on the trade surface.
They may use realized trade evidence.

### Entry-row mapping outputs

These are scoring-time outputs about how much authority from the trade surface can be carried back to an entry row or entry-time context estimate.
They live on the entry-row surface.
They must remain explicit about uncertainty, strength, and coverage.

These two surfaces must not be collapsed into one.
That distinction is the main safety rail of the new lane.

## Admissible trade-level authority labels

### 1. Supportive trade outcome

`supportive_trade_outcome`

Definition:

- the completed trade provides bounded evidence that the RI expression was helped by its surrounding context on the governed evaluation surface
- the trade is evaluable on the chosen authority surface
- the trade is not better explained as a transition-heavy or ambiguity-dominated case

Interpretation rule:

- supportive does **not** mean the context is universally good everywhere
- it means that this trade, on the governed surface, supports the idea that the context was favorable to the RI expression

Boundary rule:

- raw positive realized P&L alone is not sufficient by itself
- a later implementation slice must define the exact realized-trade evidence family explicitly before this label can be operationalized

### 2. Hostile trade outcome

`hostile_trade_outcome`

Definition:

- the completed trade provides bounded evidence that the RI expression was harmed by its surrounding context on the governed evaluation surface
- the trade is evaluable on the chosen authority surface
- the trade is not better explained as a transition-heavy or ambiguity-dominated case

Interpretation rule:

- hostile does **not** mean the strategy is always wrong in that regime forever
- it means this trade, on the governed surface, supports the idea that the surrounding context was unfavorable to the RI expression

Boundary rule:

- raw negative realized P&L alone is not sufficient by itself
- a later implementation slice must define the exact realized-trade evidence family explicitly before this label can be operationalized

### 3. Transition trade outcome

`transition_trade_outcome`

Definition:

- the completed trade is better explained as a transition-sensitive / instability-sensitive case than as clean supportive or hostile context
- the trade exhibits enough instability, disagreement, regime-change proximity, or mixed realized behavior that a stable-direction label would overclaim

Interpretation rule:

- this is a trade-level authority label for instability-dominated cases
- it is not merely a low-confidence version of supportive or hostile

Boundary rule:

- transition may not be used as a junk drawer for difficult cases
- a later implementation slice must keep this class narrow and evidence-based

### 4. Non-evaluable trade context

`non_evaluable_trade_context`

Definition:

- the trade does not have enough admissible authority evidence to support a bounded supportive, hostile, or transition judgment

Why this must remain explicit:

- partial coverage is part of the lane design now
- forcing all trades into a directional label would recreate the same dishonesty that closed the old row-level lane

This is a coverage label, not a hidden failure bucket.

## Admissible entry-row mapping outputs

The entry-row surface remains a scoring-time surface.
That means later mapping work may emit only bounded mapping outputs such as:

- `supportive_context_likelihood`
- `hostile_context_likelihood`
- `transition_risk_likelihood`
- `authority_strength`
- `coverage_state`

These are examples of admissible output types, not yet formulas.

### Meaning of those outputs

#### `supportive_context_likelihood`

A bounded estimate that the row’s entry-time context resembles trade-level supportive authority cases.

#### `hostile_context_likelihood`

A bounded estimate that the row’s entry-time context resembles trade-level hostile authority cases.

#### `transition_risk_likelihood`

A bounded estimate that the row’s entry-time context resembles trade-level transition-sensitive cases.

#### `authority_strength`

An explicit indicator of how much authority the mapping actually carries.
This is required so weak mappings cannot masquerade as strong ones.

#### `coverage_state`

An explicit coverage indicator such as:

- directly trade-anchored
- partially inferred
- unsupported
- non-evaluable

The exact value set may be refined later, but the idea itself is mandatory.

## What entry-row mapping may not claim

A later mapping slice may **not** claim any of the following by default:

- that an entry row now has restored exact Phase-2-faithful supportive/hostile authority
- that every row must receive a directional label
- that unsupported rows may be forced into supportive or hostile classes for completeness
- that mapping outputs are equivalent to ground truth

That means the row-level surface must remain explicitly advisory, probabilistic, and coverage-aware unless a later governed slice proves something stronger.

## Partial coverage and uncertainty contract

### 1. Partial coverage is allowed

This lane no longer requires forced completeness.
That is intentional.

A later slice may therefore leave some rows or trades as:

- unsupported
- non-evaluable
- below authority threshold

That is admissible.
What is not admissible is hiding that shortfall.

### 2. Uncertainty must be surfaced, not hidden

If a mapping is weak, mixed, or only partly anchored, the output must say so explicitly through:

- authority strength
- coverage state
- confidence interval / uncertainty band / similar bounded indicator in a later slice

The exact mechanism can be decided later.
The requirement to expose uncertainty cannot.

### 3. Unsupported rows must remain visible

If no admissible mapping is available for a row, the row must remain unsupported.
It may not be silently folded into a directional class for reporting neatness.

Neat dashboards are lovely.
Fake completeness is not.

## Leakage and shortcut rules

### Forbidden as row-mapping shortcuts

The following remain forbidden as direct scoring-time or row-mapping shortcuts:

- post-entry `pnl_delta`
- raw `total_pnl` sign
- post-entry continuation proxies as direct row labels
- any future-discovered cohort membership used as if it were entry-time information
- any deterministic one-step relabeling that says “trade label equals exact row label” without a separate governed proof

### Forbidden as trade-label shortcuts

The following are also forbidden as sole trade-level authority rules:

- raw realized P&L sign alone
- discovery-year success memory alone
- a label definition that ignores contradiction-year behavior

A future implementation slice must define a bounded realized-trade evidence family explicitly.
This contract only says what kinds of labels are admissible, not how to compute them yet.

## Relationship to the earlier Phase 2 taxonomy

The old Phase 2 taxonomy remains useful as reference, but it does not transfer one-to-one.

What remains aligned:

- supportive vs hostile still describe favorable vs unfavorable outcomes
- transition remains a distinct instability concept
- non-evaluable remains a required coverage state
- leakage rules still matter
- `2025` remains a mandatory contradiction-year check

What changes:

- authority is now primary at trade level, not row level
- row outputs become mapping outputs rather than restored labels
- partial coverage is now an explicit design feature rather than an embarrassing exception

## Required contradiction-year rule

Any future deterministic baseline in this lane must still report `2025` explicitly.

Why:

- the pivot changes the authority surface
- it does not remove the repository’s strongest contradiction-year warning

So this remains mandatory:

- no new baseline may be considered honest if it only looks coherent on discovery-friendly evidence and is not pressure-tested on `2025`

## Exact next admissible step

The next admissible move after this contract is:

- **one docs-only trade-level evidence-family and leakage-boundary slice**

That next slice should define only:

1. which realized-trade evidence families are admissible for supportive / hostile / transition trade labels
2. which entry-time fields may later support row mapping
3. which leakage checks must fail the lane closed
4. which coverage and uncertainty metrics must be reported before any deterministic baseline is attempted

That is still smaller than implementation and still more honest than jumping straight into scoring.

## Bottom line

The new lane now has a usable contract:

- **trade-level authority labels:** `supportive_trade_outcome`, `hostile_trade_outcome`, `transition_trade_outcome`, `non_evaluable_trade_context`
- **entry-row outputs:** bounded likelihood/strength/coverage outputs only, not restored exact row labels
- **partial coverage:** allowed, but must be explicit
- **uncertainty:** required, not optional
- **`2025`:** still mandatory as contradiction-year check

That is enough structure to continue the pivot without sliding back into the old exact-row authority claim.
