# Legacy + RI research Phase 3 Legacy slice definition

Date: 2026-03-27
Status: tracked / analysis-only / slice-defined / no execution authority
Lane: `run_intent: research_experiment`
Phase: `3 - Legacy internal research track`
Selected class: `B. Legacy internal next-hypothesis experiments`
Selected subtrack: `L-S3 - Legacy decision or gating hypothesis`
Slice: `legacy decision slice 1`

## Purpose

This artifact defines the first bounded slice for the already selected Legacy decision-hypothesis packet.

This artifact does not authorize launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Slice definition

- Candidate surface: `src/core/strategy/decision_gates.py`
- Family claim: `legacy`
- First drift layer: `threshold / candidate`
- Core question: can one narrow Legacy-only threshold or candidate-resolution hypothesis improve the Legacy family decision surface without reopening RI semantics, survival logic, sizing, or other Legacy subtracks?

## Scope IN

- Legacy-only threshold or candidate-resolution reasoning inside the shared decision chain
- `decision_gates.py` as the primary candidate surface
- only the minimum evidence needed to prove that any observed effect belongs to the Legacy threshold / candidate layer

## Scope OUT

- `family_registry` or family-admission semantics
- RI authority, RI calibration, RI thresholds, RI gates, or RI family semantics
- `src/core/strategy/prob_model.py`
- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_sizing.py`
- exits and observability policy
- runtime defaults
- champion artifacts
- coordination, router, ensemble, comparison, readiness, or promotion work

## Fixed assumptions

- `strategy_family = legacy`
- the Legacy reference family remains the incumbent control baseline for this lane
- the current RI parameterization chain remains exhausted and is not reopened here
- any valid Legacy hypothesis in this slice must remain internal to Legacy terms and must not borrow RI threshold or gate semantics

## Minimal evidence package

- minimikrav-selector: `tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_zone_overrides_base_thresholds`
- driftvakt: `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- family-boundary guard: `tests/core/strategy/test_families.py::test_resolve_strategy_family_rejects_declared_ri_with_wrong_gates`
- optional support only if threshold shape is materially opened: `tests/governance/test_config_schema_backcompat.py`

## Stop conditions

- stop if the slice starts to import RI thresholds, RI gates, or mixed-family interpretation into Legacy internals
- stop if the slice requires reopening `decision_fib_gating.py`, `decision_sizing.py`, exits, or another Legacy subtrack
- stop if it becomes unclear whether the first drift layer is Legacy threshold / candidate behavior rather than a different surface
- stop if the slice requires strict-only surfaces

## Outcome rule

- classify only as `improvement`, `plateau`, or `degradation`
- fail closed on ambiguity

## Next admissible step

- The next admissible step after this slice definition is one bounded implementation-or-config preparation artifact for this exact Legacy slice only.
- That next step must remain single-slice, evidence-scoped, research-only, and must not combine implementation and execution in the same move.
