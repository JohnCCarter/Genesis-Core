# Legacy + RI research Phase 2 RI slice definition

Date: 2026-03-27
Status: tracked / analysis-only / slice-defined / no execution authority
Lane: `run_intent: research_experiment`
Phase: `2 - RI internal research track`
Selected class: `A. RI internal next-hypothesis experiments`
Selected subtrack: `RI-S2 - regime hypothesis`
Slice: `ri regime calibration slice 1`

## Purpose

This artifact defines the first bounded slice for the already selected RI regime-hypothesis packet.

This artifact does not authorize launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Slice definition

- Candidate surface: `src/core/strategy/prob_model.py`
- Family claim: `ri`
- First drift layer: `calibration`
- Core question: can a narrow RI-specific regime normalization or calibration mapping improve upstream candidate quality before thresholding without reopening downstream local tuning surfaces?

## Scope IN

- RI-specific regime normalization or calibration seam upstream of thresholding
- `prob_model.py` as the primary candidate surface
- only the minimum evidence needed to prove that any observed effect begins upstream of thresholding

## Scope OUT

- `family_registry` or family-admission semantics
- Legacy internals
- threshold family or threshold topology
- `decision_gates.py`
- `decision_fib_gating.py`
- `decision_sizing.py`
- exits and observability policy
- runtime defaults
- champion artifacts
- coordination, router, ensemble, comparison, readiness, or promotion work

## Fixed assumptions

- `strategy_family = ri`
- `authority_mode = regime_module`
- canonical RI baseline remains the Phase 0 locked reference
- current local RI retuning surfaces remain exhausted and must not be reopened under a new label

## Minimal evidence package

- minimikrav-selector: `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`
- driftvakt: `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_pipeline_hash_stability`
- replay anchor: `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode`
- optional support only if the seam opens materially: `tests/backtest/test_evaluation.py`

## Stop conditions

- stop if the slice requires reopening threshold, exit, override, fib, sizing, `risk_state`, or `clarity` surfaces
- stop if the slice starts to affect Legacy semantics or mixed-family interpretation
- stop if it becomes unclear whether the first drift layer is calibration rather than a later decision surface
- stop if the slice requires strict-only surfaces

## Outcome rule

- classify only as `improvement`, `plateau`, or `degradation`
- fail closed on ambiguity

## Next admissible step

- The next admissible step after this slice definition is one bounded implementation-or-config preparation artifact for this exact slice only.
- That next step must remain single-slice, evidence-scoped, and must not combine implementation and execution in the same move.
