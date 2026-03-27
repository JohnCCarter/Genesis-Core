# Legacy + RI research Phase 2 RI packet

Date: 2026-03-27
Status: tracked / analysis-only / no implementation authority
Lane: `run_intent: research_experiment`
Phase: `2 - RI internal research track`
Selected class: `A. RI internal next-hypothesis experiments`
Selected subtrack: `RI-S2 - regime hypothesis`

## Purpose

This artifact opens exactly one narrow RI internal research packet after the Phase 1 experiment map.

This artifact does not authorize implementation, config changes, launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Exact hypothesis

- The current RI plateau may be limited more by upstream regime-to-calibration behavior than by further local retuning of thresholds, exits, override cadence, or sizing levers.
- The next RI hypothesis is therefore: test a narrow alternate RI regime normalization or calibration mapping upstream of thresholding while keeping the RI family contract and downstream decision surfaces fixed.

## Why this hypothesis is opened first

- Phase 0 locked the RI local retuning surfaces as exhausted.
- Phase 1 selected RI internal next-hypothesis work as the first class to open.
- Existing analysis ranks `prob_model.py` and the calibration seam as the earliest plausible next RI candidate surface, before threshold, survival, sizing, exits, or observability.
- This keeps the next question upstream and hypothesis-level rather than reopening already-worked local tuning surfaces.

## Allowed surface

- RI-only hypothesis work
- upstream regime normalization or calibration mapping that is specific to the RI family
- analysis and future config or implementation work only if kept strictly bounded to this hypothesis

## Fixed surface

- `strategy_family = ri`
- `authority_mode = regime_module`
- canonical RI family identity already locked in the baseline chain
- Legacy internals
- threshold family and threshold topology
- exit surface
- override cadence and fib-survival surface
- sizing, `risk_state`, `clarity`, and regime/HTF size multipliers
- runtime defaults
- champion artifacts

## Explicit non-goals

- no reopening of threshold retuning as a disguised new hypothesis
- no reopening of exit, hold, override, or fib cadence search
- no reopening of risk-state or sizing breadth
- no Legacy-overlay or mixed-family surface
- no coordination, router, ensemble, comparison, readiness, or promotion work

## Minimal evidence package for the next slice

- minimikrav-selector: `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`
- driftvakt: `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_pipeline_hash_stability`
- replay anchor: `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode`
- optional wider support only if the seam opens materially: `tests/backtest/test_evaluation.py`

## Decision rule

- If evidence shows meaningful validation improvement from this upstream hypothesis, the RI internal lane may continue with another narrow RI slice.
- If the result plateaus or degrades, this hypothesis class should be closed or falsified before any broader reopening is considered.
- If ambiguity appears about family identity, regime authority, or whether the slice is actually reopening a later surface, fail closed.

## Next admissible step

- The next admissible step after this packet is a single bounded RI slice-definition artifact for this exact hypothesis.
- That next step must still remain hypothesis-bounded and must not widen into implementation plus execution in the same move.
