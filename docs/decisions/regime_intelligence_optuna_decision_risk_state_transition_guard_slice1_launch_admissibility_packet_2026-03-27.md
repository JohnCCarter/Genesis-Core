# Regime Intelligence challenger family — DECISION risk-state transition-guard slice1 launch admissibility packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `admissibility-defined / docs-only / no setup or launch authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines the minimum research-launch admissibility conditions for a later separate transition-guard setup packet, but must remain docs-only and must not authorize YAML materialization, smoke configuration, validator/preflight claims, research launch, runtime-validity, comparison, readiness, promotion, or writeback.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define exactly when a later separate docs-only setup packet for `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}` may be considered governance-admissible for research preparation.
- **Candidate:** `future tBTCUSD 3h RI DECISION transition-guard slice1 setup gate`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only admissibility packet; exact seam carry-forward; exact tuple-grid carry-forward; exact freeze carry-forward; exact minimum conditions that a later separate setup packet must satisfy before YAML/setup work may even be reviewed.
- **Scope OUT:** no source-code changes, no test changes, no changes under `src/core/**`, no changes under `tests/**`, no changes under `config/optimizer/**`, no changes under `tmp/**`, no changes under `results/**`, no YAML creation, no smoke YAML creation, no validator/preflight/smoke execution, no launch authorization, no runtime-valid RI conformity, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_launch_admissibility_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains admissibility-only and does not imply setup or launch authority

For interpretation discipline inside this packet:

- the seam must remain strictly limited to `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
- the future tuple grid must remain exactly `{1,2,3} × {0.55,0.65,0.75}`
- the freeze carry-forward from the predecessor pre-code packet must remain unchanged
- no sentence may imply that YAML, smoke configuration, or launch is already authorized
- no sentence may reinterpret `research_slice` as runtime-valid RI conformity
- no sentence may introduce new config-authority, schema, or runtime-behavior claims

### Stop Conditions

- any wording that implies YAML materialization is approved now
- any wording that implies smoke or launch is approved now
- any wording that opens more than one seam
- any wording that reopens `risk_state.drawdown_guard.*`, `clarity_score.*`, `size_multiplier.{min,max}`, `OBJECTIVE`, or `SIGNAL / feature-surface`
- any wording that changes the exact tuple grid
- any wording that requires new config-authority, new schema semantics, or runtime interpretation changes
- any wording that weakens one-seam attribution or the predecessor freeze-table

### Output required

- one reviewable docs-only admissibility packet
- exact admissibility rule for a later separate setup packet
- exact non-authorizations
- exact freeze carry-forward
- exact red-line conditions that force return to new governance review

## Purpose

This packet answers one narrow question only:

- under what conditions may a later separate docs-only setup packet for the `transition_guard` slice be considered governance-admissible for research preparation?

This packet defines an **admissibility gate only**.

It does **not**:

- authorize YAML materialization
- authorize smoke configuration
- authorize validator or preflight pass claims
- authorize research launch
- authorize runtime-valid RI conformity
- authorize comparison, readiness, promotion, or writeback

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/decisions/regime_intelligence_optuna_decision_clarity_risk_state_direction_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_precode_command_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence_optuna_decision_ev_edge_slice1_execution_outcome_signoff_summary_2026-03-27.md`

Carried-forward meaning:

1. the broader `DECISION` class remains open, but the prior `EV / edge` seam is closed as `PLATEAU`
2. the chosen class-level next direction remains `DECISION / clarity-risk-state sizing surface`
3. the first proposed minimal slice remains exactly `risk_state.transition_guard.{guard_bars,mult}`
4. YAML, admissibility, smoke, and launch remained explicitly closed in the predecessor pre-code packet
5. this packet may define only the conditions for a later separate setup review, not the setup artifact itself

## Exact seam carried forward

The only seam covered by this admissibility gate is:

- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult`

The only admissible future tuple grid remains exactly:

- `(guard_bars=1, mult=0.55)`
- `(guard_bars=1, mult=0.65)`
- `(guard_bars=1, mult=0.75)`
- `(guard_bars=2, mult=0.55)`
- `(guard_bars=2, mult=0.65)`
- `(guard_bars=2, mult=0.75)`
- `(guard_bars=3, mult=0.55)`
- `(guard_bars=3, mult=0.65)`
- `(guard_bars=3, mult=0.75)`

No other tuple and no other seam is admissible under this packet.

## Freeze carry-forward

The predecessor pre-code packet remains authoritative for the full frozen backdrop and freeze-table.

For admissibility purposes, the following closures are carried forward unchanged:

- all family / authority / identity markers remain frozen
- the signal / regime-definition backdrop remains frozen
- the closed `EV / edge` seam remains frozen
- the execution-management backdrop remains frozen
- `multi_timeframe.regime_intelligence.clarity_score.*` remains frozen / unopened
- `multi_timeframe.regime_intelligence.size_multiplier.{min,max}` remains frozen / unopened
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.*` remains frozen / unopened
- `OBJECTIVE` remains deferred
- `SIGNAL / feature-surface` remains deferred

Scope remains strictly limited to `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}` with tuple-grid `{1,2,3} × {0.55,0.65,0.75}`; all other RI surfaces remain closed or deferred.

## Admissibility rule for a later separate setup packet

A later separate docs-only setup packet may be considered admissible for review only if all of the following are true:

1. it stays entirely inside the exact seam `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
2. it preserves the exact nine-tuple grid defined above without widening or pruning it
3. it carries forward the predecessor frozen backdrop and freeze-table without reinterpretation
4. it remains research-only under `run_intent=research_slice`
5. it remains config-only and does not require any source-code, test, schema, or config-authority change
6. it proposes at most one canonical optimizer YAML and at most one bounded smoke YAML in the canonical optimizer zone, without treating either as launch-authorized by their existence alone
7. it keeps promotion disabled and keeps comparison, readiness, promotion, and writeback closed
8. it defines the minimum later evidence requirements for validator, preflight, and smoke without claiming those gates have already passed
9. it preserves exact one-seam attribution so that any later result can still be attributed only to `transition_guard.{guard_bars,mult}`

If any one of those conditions fails, the later setup packet is inadmissible and work must stop for new governance review.

## What a later setup packet may and may not do

### What it may do, if separately reviewed later

A later separate setup packet may:

- identify one canonical optimizer-zone config subject for this seam
- identify one bounded smoke config subject for this seam
- restate the exact frozen backdrop
- restate the exact tuple grid
- define the minimum gate evidence that would still be required before any launch authorization could be considered

### What it may not do, unless separately re-governed later

A later separate setup packet may not:

- widen the tuple grid
- add `drawdown_guard`, `clarity_score`, or `size_multiplier` tunables
- alter the frozen backdrop
- introduce new runtime/config-authority semantics
- claim validator or preflight success before those gates are actually run
- treat YAML creation as research launch authorization
- treat setup review as outcome, comparison, readiness, promotion, or writeback authority

## Explicit non-authorizations

This packet must be read with the following sentence intact:

- **This packet authorizes neither YAML materialization, smoke configuration, validator/preflight pass claims, nor research launch; it defines only the conditions under which a later separate docs-only setup packet may be reviewed.**

This packet also does **not** authorize:

- any run id
- any artifact directory
- any smoke execution
- any full execution
- any launch-authorization packet
- any execution-outcome signoff

## Red-line conditions for immediate stop

Work must stop and return to fresh governance review if a later setup attempt requires any of the following:

- more than one open seam
- any reopening of the carried-forward freeze-table
- any change to the exact tuple grid
- any new config-authority or schema allowance
- any need for source-code or test changes
- any wording that equates `research_slice` preparation with runtime-valid RI conformity
- any wording that converts setup review into launch authorization by implication

## Next allowed step

The next allowed step after this packet is limited to:

- a later separate docs-only setup packet review for the exact `transition_guard` seam, if and only if the admissibility rule above is carried forward unchanged

That later step remains distinct from launch authorization.

## Bottom line

The `transition_guard` slice is now bounded not only by a pre-code seam definition, but also by an explicit admissibility gate.

That gate says only this:

- a later separate setup packet may be reviewed **only** if it stays inside `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`, preserves tuple-grid `{1,2,3} × {0.55,0.65,0.75}`, carries the full freeze-table forward unchanged, and does not claim YAML, smoke, or launch authority.

Anything broader must stop and return to new governance review.
