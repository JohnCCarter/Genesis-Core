# Regime Intelligence challenger family — upstream candidate-authority direction packet

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `direction-selected / non-launch-authoritative / no slice opened`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet updates the active forward research direction after newer fib-lane evidence, but does not authorize a launchable lane, code change, config change, or run.
- **Required Path:** `Full gated docs-only`
- **Objective:** Select exactly one next hypothesis class after the fib-lane closeout, record the carried-forward evidence that motivates the shift, and define the future research direction at a non-launch-authoritative level only.
- **Candidate:** `future upstream candidate formation / candidate-authority research direction`
- **Base SHA:** `c27add49`

### Scope

- **Scope IN:** docs-only direction update; explicit carried-forward fib-lane evidence; exact selection of one next hypothesis class; narrow supersession of the earlier active direction selection; explicit future change surface; explicit fixed surface; qualitative expected improvement signature; qualitative falsification condition; explicit non-authorization language.
- **Scope OUT:** no source-code changes; no config changes; no tmp/result/artifact rewrites; no validator/preflight/smoke execution; no launch authorization; no slice opening; no comparison/readiness/promotion/writeback opening; no runtime/default/champion changes.
- **Expected changed files:** `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_candidate_authority_direction_packet_2026-03-30.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that exactly one hypothesis class is selected
- manual wording audit that no sentence opens a lane, authorizes execution, or implies implementation readiness

For interpretation discipline inside this packet:

- exactly one next hypothesis class must be selected
- fib-lane closure must remain carried-forward evidence, not a reopened lane
- the 2026-03-27 SIGNAL direction packet must remain historically intact
- supersession must apply only to the current active forward direction, not to prior historical validity
- expected improvement signature must remain qualitative and non-authorizing

### Stop Conditions

- any wording that opens a launchable lane or new slice
- any wording that retroactively invalidates the 2026-03-27 direction packet rather than narrowly superseding its active forward role
- any wording that selects more than one next hypothesis class
- any wording that turns qualitative expectations into operational acceptance gates

### Output required

- reviewable direction packet
- exact chosen hypothesis label
- exact non-chosen hypothesis labels
- explicit carried-forward evidence basis
- explicit fixed invariants and non-authorization boundary

## Purpose

This packet answers one narrow question only:

- what is the next admissible RI research direction after the fib lane was measured and closed as structurally inactive in the current decision surface?

This packet does **not**:

- open a new slice
- create a launchable optimizer lane
- create a YAML or run-plan
- authorize validator/preflight/smoke execution
- authorize implementation, comparison, readiness, promotion, or writeback

## Carried-forward evidence basis

This packet is downstream of the following tracked evidence and closeouts:

- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_exit_override_plateau_closeout_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_slice3_fib_gate_1h_2026-03-30.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_slice3_fib_gate_binding_1h_2026-03-30.md`
- `src/core/config/authority_mode_resolver.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/decision_gates.py`

Carried-forward meaning from those artifacts:

1. the prior exit/override-only lane remains closed in current tracked state
2. the bounded 1h fib toggle surface produced plateau rather than separation
3. the fixed 1h fib binding diagnostic showed fib is observed but structurally inactive as a decision gate in the current surface
4. the earliest meaningful divergence between legacy and RI remains upstream in authority resolution, regime-aware calibration, and candidate formation before fib gating

## Narrow supersession clause

This packet **narrowly supersedes** `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md` **only as the active forward direction selection**.

This means:

- the 2026-03-27 packet remains a historically correct governance artifact for the evidence available at that time
- this 2026-03-30 packet replaces only the currently active “what direction next?” answer
- no other historical conclusion, closeout status, or prior evidence record is rewritten by this packet

This supersession does **not**:

- invalidate the older packet as an artifact
- authorize a lane that the older packet did not authorize
- reopen any lane that prior closeouts already closed

## Hypothesis classes under decision

### Option 1 — UPSTREAM_CANDIDATE_FORMATION / CANDIDATE_AUTHORITY

Meaning:

- future research would inspect the earliest point where legacy-vs-RI drift becomes candidate/no-candidate or trade/no-trade behavior
- the relevant conceptual surface sits across authority resolution, regime-aware calibration, and `select_candidate(...)`
- the aim is not more local fib tuning, but to test whether the main bottleneck sits upstream of fib and post-fib handling

Current suitability:

- **selected by this packet**

Why it is selected now:

- newer fib evidence closed the fib lane as inactive rather than merely under-tuned
- the code-anchored role map shows the first practical action surface in `decision_gates.py::select_candidate(...)`
- `evaluate.py` and `prob_model.py` show that authoritative regime choice and regime-aware calibration can change the candidate surface before fib, cadence, or sizing ever engage

### Option 2 — SIGNAL_ADAPTATION_ONLY

Meaning:

- future research would treat the next step primarily as a signal/regime-threshold tuning problem inside `thresholds.signal_adaptation.*`

Current suitability:

- **not selected now**

Why it is not selected now:

- the newer fib evidence sharpens the upstream bottleneck question before a signal-only tuning framing is sufficient
- a signal-only label is now too narrow for the currently best-supported divergence surface

### Option 3 — DOWNSTREAM_DECISION_OR_OBJECTIVE

Meaning:

- future research would reopen downstream decision-gating logic, local management, or objective/scoring as the primary next class

Current suitability:

- **not selected now**

Why it is not selected now:

- the exit/override lane is already closed
- the fib lane is now closed as inactive in the current surface
- the current evidence points earlier in the chain than downstream decision/filter/objective work

## Decision

### Chosen hypothesis label

- `CHOSEN — UPSTREAM_CANDIDATE_FORMATION / CANDIDATE_AUTHORITY`

### Not chosen now

- `NOT CHOSEN NOW — SIGNAL_ADAPTATION_ONLY`
- `NOT CHOSEN NOW — DOWNSTREAM_DECISION_OR_OBJECTIVE`

## Meaning of the decision

This packet selects exactly one next admissible direction:

- **UPSTREAM_CANDIDATE_FORMATION / CANDIDATE_AUTHORITY**

This means the next legitimate RI continuation, if separately governed later, should begin from the question:

- does the practical bottleneck sit in how authority, calibration, and candidate thresholds shape the pre-fib candidate surface?

This decision does **not** mean:

- that a lane is now open
- that any code or config should now change
- that a future packet must use a specific YAML, run-id, or execution path
- that signal-only work, decision-only work, or objective work can never return later

## What could change in a future lane

If a separately governed future lane is opened later, the intended conceptual change surface would be limited to the upstream candidate-formation family, including for example:

- authority resolution as it determines the authoritative regime input
- regime-aware calibration as it shapes upstream probability interpretation
- candidate-threshold and candidate-selection behavior before fib gating

This description is conceptual only.

It is **not**:

- an implementation plan
- a run plan
- a parameter recommendation
- a launch authorization

## What remains fixed

Unless separately re-governed later, the following remain fixed by this packet:

- the fib lane remains closed as structurally inactive in the current decision surface
- the exit/override-only lane remains closed in current tracked state
- no source-code or config changes are authorized
- no comparison, readiness, promotion, or writeback path is opened
- no runtime/default/champion authority is changed
- no new slice, YAML, or execution packet is created by this document

## Expected qualitative improvement signature

A future upstream candidate-authority lane would count as directionally promising only if it produced evidence of a real upstream separation such as:

- changed candidate formation before fib gating
- clearer trade/no-trade separation attributable to authority/calibration/candidate-surface effects rather than downstream rescue logic
- observable reduction in “same trade path despite downstream toggles” behavior

These expectations are qualitative only.

They are recorded here to define the research intent, not to authorize a run or set a pass/fail gate.

## Qualitative falsification condition

This direction would be directionally weakened or falsified if later governed evidence shows that:

- upstream authority/calibration/candidate-surface perturbations still fail to change candidate formation in a meaningful way, or
- the practical behavior remains dominated by the same pre-existing plateau/no-separation pattern despite upstream framing changes

This falsification statement is interpretive only.

It is **not** a launch, test, or acceptance protocol.

## Explicit non-authorization boundary

This document is a direction-only governance artifact.

It does **not**:

- open a slice
- authorize implementation
- authorize validator/preflight/smoke execution
- authorize a launchable YAML
- authorize comparison, readiness, promotion, or writeback

Any future implementation, config work, or executable research lane requires a **separate governed opening / command packet**.

## Bottom line

After the fib lane was measured and closed as structurally inactive in the current decision surface, the next admissible RI direction is no longer best framed as a signal-only continuation.

The active forward direction is now:

- **UPSTREAM_CANDIDATE_FORMATION / CANDIDATE_AUTHORITY**

That choice supersedes the earlier SIGNAL-only direction **only as the current forward selection**, while leaving the earlier packet historically intact and while authorizing exactly nothing beyond this direction statement.
