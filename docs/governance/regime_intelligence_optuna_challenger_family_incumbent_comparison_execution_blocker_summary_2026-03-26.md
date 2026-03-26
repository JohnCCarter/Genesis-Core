# Regime Intelligence challenger family — incumbent comparison execution blocker summary

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `review-only / execution blocked / no runtime or champion change`

## Purpose

This tracked summary freezes the verified blocker state for the March 26 RI incumbent-comparison execution attempt.

It records:

- the governing execution-packet reference
- the validations that were green before the local execution attempt
- the two attempted local comparison-input materialization paths
- the exact runtime validation failures observed on those paths
- the resulting governance conclusion for the current same-head comparison attempt

This summary does **not** approve:

- promotion
- champion replacement
- runtime/default change
- local runtime forcing
- any new comparison-input contract

## Governing execution packet reference

The blocked execution attempt was governed by:

- `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_2026-03-26.md`

Tracked packet commit:

- `5eadeaac` — `docs: add RI incumbent comparison execution packet`

The execution packet framed the comparison narrowly as:

- slice8 full tuple as the RI lead research candidate surface
- incumbent same-head control as the only primary comparator surface
- bootstrap champion file as background context only
- no promotion, writeback, or runtime/default approval

## Green validations before the blocked local execution attempt

The following validations were green before the local materialization probes:

### Docs validation

- pre-commit/file validation on the execution packet passed

### Runtime-governance selectors

- `tests/backtest/test_backtest_determinism_smoke.py` → `PASS`
- `tests/utils/test_features_asof_cache_key_deterministic.py` → `PASS`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → `PASS`
- `tests/governance/test_authority_mode_resolver.py` → `PASS`

These green checks were necessary preconditions for a later comparison attempt.

They did **not** by themselves authorize bypassing runtime-family or strategy-validation semantics.

## Attempted local materialization paths

### Path A — parameters-only runtime override

Attempted local candidate materialization path:

- `tmp/ri_candidate_materializations/tBTCUSD_3h_slice8_trial_001_runtime_override.json`

Intended semantics:

- copy only the `parameters` payload from:
  - `results/hparam_search/run_20260324_174006/validation/trial_001.json`
- avoid carrying forward `merged_config`
- let `scripts/run/run_backtest.py` resolve the effective config by runtime-merge

### Verified runtime validation failure for Path A

Observed failure:

- `invalid_strategy_family:legacy_regime_module`

Interpretation:

- the parameters-only path did not resolve to an admissible RI runtime comparison surface
- the attempted resolution instead hit an invalid `legacy` / `regime_module` combination

This means Path A is **not currently permitted** for the same-head comparison attempt.

### Path B — cfg override with explicit top-level `strategy_family=ri`

Attempted local candidate materialization path:

- `tmp/ri_candidate_materializations/tBTCUSD_3h_slice8_trial_001_cfg_override.json`

Intended semantics:

- start from the slice8 trial's local config shape
- force top-level `strategy_family=ri`
- test whether a local cfg-based materialization could yield a valid RI comparison surface without changing tracked repo files

### Verified runtime validation failure for Path B

Observed failure:

- `invalid_strategy_family:ri_requires_canonical_gates`

Interpretation:

- the cfg-based path did not validate as an admissible RI runtime comparison surface either
- making the local candidate explicitly `ri` still triggered the runtime requirement for canonical RI gates

This means Path B is also **not currently permitted** for the same-head comparison attempt.

## Blocker conclusion

Verified outcome:

- the March 26 incumbent-comparison execution attempt cannot currently be materialized through local runtime-config paths A or B under existing runtime semantics

Therefore:

- same-head comparison execution is **not currently permitted** for this attempt
- no further local runtime forcing should be attempted from this blocker state
- no ad hoc gate additions should be introduced merely to satisfy RI canonical validation

## What this summary does and does not conclude

### Verified by this summary

- the governing execution packet was validly prepared and validated
- the listed pre-launch validations were green
- the two local materialization paths were attempted
- the two failures above are the verified runtime-semantics blockers for the current attempt

### Not decided by this summary

This summary does **not** decide:

- all possible future incumbent-comparison methods
- whether slice8 may be compared on a non-runtime evidence surface
- whether a sanctioned RI canonical materialization contract should ever exist
- any promotion/champion/default/runtime outcome

## Required next step

The next step is governance, not more local forcing.

Specifically:

- open a separate docs-only governance packet that decides the valid comparison-input surface for slice8
- decide whether slice8 is to be compared via:
  - runtime-config materialization,
  - a sanctioned RI canonical materialization contract, or
  - a different governed evidence surface entirely

Until that decision exists, no further same-head execution attempt should proceed.
