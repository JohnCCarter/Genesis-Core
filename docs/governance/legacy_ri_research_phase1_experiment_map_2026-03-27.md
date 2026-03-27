# Legacy + RI research Phase 1 experiment map

Date: 2026-03-27
Status: tracked / analysis-only / no implementation authority
Lane: `run_intent: research_experiment`
Phase: `1 - define the experiment map`

## Purpose

This artifact defines the governed experiment map for the Legacy + RI research lane after the Phase 0 baseline lock.

This artifact does not authorize implementation, config changes, launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Carry-forward constraints

- Legacy and RI remain separate strategy families.
- Mixed family surfaces must not be reintroduced.
- Coordination, routing, and orchestration must live above the families, not inside them.
- Research outputs remain research-only unless a later lane is explicitly opened.

## Experiment classes

### A. RI internal next-hypothesis experiments

Allowed classes:

- new signal hypothesis
- new regime hypothesis
- new decision or gating hypothesis
- new objective or scoring hypothesis

Constraint:

- do not reopen already exhausted local retuning surfaces as if they were a new class of evidence

### B. Legacy internal next-hypothesis experiments

Allowed classes:

- Legacy-specific signal hypothesis
- Legacy-specific regime or context hypothesis
- Legacy-specific decision or gating hypothesis
- Legacy-specific objective or robustness hypothesis

Constraint:

- do not import RI semantics, thresholds, or gates into Legacy internals

### C. Cross-family coordination experiments

Allowed classes:

- Legacy primary plus RI veto
- RI primary plus Legacy veto
- regime-based router
- confidence-based router
- consensus coordinator
- abstain or no-trade coordinator

Constraint:

- coordination may consume family outputs externally, but must not merge family internals or mutate family semantics

### D. Meta-governance experiments

Allowed classes:

- admissibility rules for coordination lanes
- authority boundaries for router outputs
- classification rules for research-only coordination artifacts

Constraint:

- governance clarification here does not itself open implementation authority

## Out of scope

- no code changes
- no config changes
- no launches
- no runtime default changes
- no champion changes
- no comparison, readiness, or promotion opening
- no implementation of coordination, router, or ensemble logic

## Phase 1 decision gate

- The first experiment class to open after this map is `A. RI internal next-hypothesis experiments`.
- Reason: Phase 0 locked RI as a separate family, locked the current RI plateau baseline, and recorded that current RI local surfaces are exhausted for further local retuning.
- Therefore the next admissible step is not more local RI retuning, but one narrow RI internal next-hypothesis packet.

## Next admissible step

- The next admissible step after this Phase 1 map is a single Phase 2 RI internal research packet for exactly one new RI hypothesis.
- That next step must remain docs-first and hypothesis-bounded before any config or execution is considered.
