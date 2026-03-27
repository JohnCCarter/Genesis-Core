# Legacy + RI research Phase 3 Legacy packet

Date: 2026-03-27
Status: tracked / analysis-only / no implementation authority
Lane: `run_intent: research_experiment`
Phase: `3 - Legacy internal research track`
Selected class: `B. Legacy internal next-hypothesis experiments`
Selected subtrack: `L-S3 - Legacy decision or gating hypothesis`

## Purpose

This artifact opens exactly one narrow Legacy internal research packet after the Phase 3 Legacy class opening.

This artifact does not authorize implementation, config changes, launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Exact hypothesis

- The current Legacy reference family may still contain productive internal research room in its decision or gating surface without borrowing any RI semantics.
- The next Legacy hypothesis is therefore: test one narrow Legacy-internal threshold or candidate-resolution question in the Legacy decision path while keeping Legacy family identity and all cross-family boundaries fixed.

## Why this subtrack is opened first

- The Phase 3 class-opening artifact required the next step to choose exactly one Legacy subtrack.
- The role-map analysis identifies the threshold / candidate surface as the clearest practical trade/no-trade boundary in the shared decision chain.
- The same analysis provides a bounded slice format for `decision_gates.py` with a minimikrav-selector and a driftvakt, which makes this subtrack easier to keep explicit and fail-closed than a broader Legacy reopening.
- This selects `L-S3` as the first Legacy packet for this lane; it does not claim that `L-S1`, `L-S2`, or `L-S4` are globally invalid, only that they are not opened by this artifact.

## Allowed surface

- Legacy-only hypothesis work
- Legacy decision or gating behavior in the shared decision chain
- Legacy threshold or candidate-resolution questions that remain internal to the Legacy family
- analysis and future bounded slice-definition work only if kept strictly inside this Legacy hypothesis

## Fixed surface

- `strategy_family = legacy`
- Legacy family identity and admission semantics
- RI authority, RI calibration, RI thresholds, RI gates, and RI family semantics
- `src/core/strategy/prob_model.py`
- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_sizing.py`
- exits and observability policy
- runtime defaults
- champion artifacts

## Explicit non-goals

- no Legacy signal-hypothesis opening
- no Legacy regime/context-hypothesis opening
- no Legacy objective/robustness-hypothesis opening
- no RI reopening from the exhausted current chain
- no import of RI thresholds, RI gate semantics, RI calibration logic, or mixed-family interpretation into Legacy internals
- no coordination, router, ensemble, comparison, readiness, or promotion work
- no implementation, config creation, or launch authorization

## Minimal evidence package for the next slice

- minimikrav-selector: `tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_zone_overrides_base_thresholds`
- driftvakt: `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- family-boundary guard: `tests/core/strategy/test_families.py::test_resolve_strategy_family_rejects_declared_ri_with_wrong_gates`
- optional wider support only if threshold shape is materially opened: `tests/governance/test_config_schema_backcompat.py`

## Decision rule

- If a bounded Legacy decision/gating slice yields meaningful evidence of Legacy-only uplift without contaminating family boundaries, the Legacy internal lane may continue with that narrow hypothesis line.
- If the result plateaus or degrades, this hypothesis should be closed or falsified before a broader Legacy reopening is considered.
- If ambiguity appears about whether the slice is actually reopening RI semantics, survival logic, sizing, or a different Legacy subtrack, fail closed.

## Next admissible step

- The next admissible step after this packet is one single bounded Legacy slice-definition artifact for this exact `L-S3` hypothesis line.
- That next step must remain docs-first, single-slice, research-only, and must not combine implementation and execution in the same move.
