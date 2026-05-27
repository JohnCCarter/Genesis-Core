# Genesis-Core — runtime legacy containment

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base classification anchor: `docs/analysis/system/genesis_runtime_surface_classification_2026-05-27.md`
Base SHA anchor: `96af7d12`
Status: `completed / docs+artifact containment verification / no behavior change`

## Purpose

This bounded slice verifies the smallest admissible cleanup pilot identified by the runtime surface classification:

> legacy containment

The goal is not to move or delete legacy surfaces.
The goal is to verify whether the repo already contains enough guardrails to keep the two retained legacy surfaces demoted from branch-current runtime SSOT.

Target legacy surfaces:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`

## Mode proof

This work remains `RESEARCH` because it is a bounded docs+artifact verification slice with focused test evidence.
It does not change runtime behavior, config semantics, default authority, champion surfaces, or filesystem placement.
If this slice were to edit runtime-authority/config/champion surfaces, or perform archive/delete execution, it would need stricter governance handling.

## Scope

### Scope IN

- verify the current legacy-containment state of the two identified legacy surfaces
- confirm whether existing guardrails already demote them from active runtime SSOT
- record focused test evidence from this session
- emit one machine-readable containment artifact

### Scope OUT

- code deletion
- file moves or archive execution
- runtime or config behavior changes
- changes to `config/runtime.json`
- changes to champions or authority logic
- edits to already locally modified research artifacts outside this slice

## Evidence inputs

Classification basis:

- `docs/analysis/system/genesis_runtime_surface_classification_2026-05-27.md`
- `results/research/runtime_truth_inventory/genesis_runtime_surface_classification_2026-05-27.json` (read-only input only)

Containment evidence:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`
- `src/core/strategy/evaluate.py`
- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`
- `tests/integration/test_config_endpoints.py`

Verification run in this session:

- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`
- `tests/integration/test_config_endpoints.py`
- result: `17 passed, 0 failed`

## Emitted artifact

- `results/research/runtime_truth_inventory/genesis_runtime_legacy_containment_2026-05-27.json`

## Observed

### 1. The feature legacy shim is already explicitly fenced away from internal runtime use

Observed support:

- `src/core/strategy/features.py` declares itself a `Legacy compatibility shim`
- the module text says internal runtime code should import `core.strategy.features_asof` instead
- `tests/governance/test_no_legacy_feature_imports.py` blocks imports of `core.strategy.features` across repo Python sources except a narrow allow-list used for governance enforcement
- the same test also blocks internal imports of `core.strategy.features_asof.extract_features`, pushing internal runtime toward `extract_features_live` / `extract_features_backtest`
- `tests/governance/test_dead_code_tripwires.py` verifies the shim still delegates directly to `_extract_features_asof`

So this legacy surface is not uncontained drift.
It is a retained compatibility shim with active tripwires around it.

### 2. The legacy config validator is already fenced away from runtime authority

Observed support:

- `src/core/config/validator.py` declares itself `intentionally legacy/test-only`
- the same file states runtime config validation must go through `ConfigAuthority.validate`
- `tests/governance/test_dead_code_tripwires.py` asserts runtime source under `src/` must not import `core.config.validator`
- the same governance test also asserts the module exports only `LEGACY_SCHEMA_PATH`, `validate_legacy_config`, and `diff_legacy_config`
- `tests/integration/test_config_endpoints.py` still imports `validate_legacy_config` and `diff_legacy_config`, which proves the module still has a live test-only compatibility role

So this surface is also not archive-ready by default.
It is retained legacy/test-only support with explicit runtime separation.

### 3. The current repo already implements most of the containment pilot in practice

The classification slice proposed a `legacy containment` pilot.
This verification slice shows that the repo already has most of that pilot införd in practice via:

- module-level self-labeling
- runtime-import guardrails
- delegation tripwires
- export-surface tripwires
- integration tests that keep the remaining compatibility role explicit

That means the immediate next step is **not** to invent new control logic.
The immediate next step is to record that the containment boundary already exists and should remain stable.

### 4. The remaining uncertainty is external usage and future lifecycle, not current containment

This slice did not find evidence that the legacy surfaces are currently leaking back into the runtime spine.
The remaining uncertainty is narrower:

- whether out-of-repo or future consumers still rely on the legacy shim
- whether a later archive/delete workflow could clear these surfaces after broader provenance checks

That is a later lifecycle question, not a current containment failure.

## Inferred

### 1. Legacy containment is already materially present, not merely proposed

The repo is past the point of “should we contain these surfaces?”
It is already doing so.

The practical rule now is:

- preserve the containment boundary
- avoid re-promoting these surfaces into active runtime imports or generic validator aliases
- avoid premature move/delete/archive decisions until provenance and external-usage uncertainty is resolved

### 2. The smallest admissible follow-up is maintenance of the boundary, not expansion of the pilot

Because the containment tests already exist and passed, the smallest admissible next step is simply:

- keep the guardrails green
- keep the legacy labels intact
- do not widen the legacy footprint

This is smaller and safer than adding more speculative cleanup layers.

### 3. V2 seeding should still exclude these surfaces by default

Even though the legacy surfaces are safely contained, they are still legacy.
So a future `Genesis-Core-V2` seed should still default to excluding them unless a specific compatibility requirement is proven.

## Unverified

- whether any external automation or consumer outside the repo still imports `core.strategy.features`
- whether any external automation or consumer outside the repo still imports `core.config.validator`
- whether a later provenance-checked lifecycle slice could demote these surfaces further from retained-legacy to archive/delete candidates

## Containment verdict

### Retained legacy surfaces with verified containment

- `src/core/strategy/features.py`
- `src/core/config/validator.py`

### Verified guardrails

- no internal repo imports of `core.strategy.features` except the narrow governance allow-list
- no internal repo imports of deprecated `features_asof.extract_features` except approved compatibility/test allow-list
- no runtime-source imports of `core.config.validator`
- legacy validator exports remain legacy-named only
- feature legacy shim remains a delegator
- focused tests passed: `17/17`

### Not established in this slice

- archive readiness
- delete readiness
- external-consumer absence

## Decision

`CONFIRM_LEGACY_CONTAINMENT_ALREADY_PRESENT_AND_HOLD_BOUNDARY`

Meaning:

- keep the existing containment guardrails
- do not promote these surfaces back into runtime SSOT
- do not archive/move/delete them from this slice
- treat future lifecycle action as a separate provenance-aware decision

## What changed and what did not

What changed:

- the repo now has one bounded legacy-containment verification note
- the containment pilot is now recorded as already materially present
- focused governance/integration evidence from this session is frozen in one place

What did **not** change:

- no runtime behavior changed
- no code file was moved, archived, or deleted
- no new runtime authority was introduced
- the locally modified Edge Topology files remained out of scope
- the locally modified `results/research/runtime_truth_inventory/genesis_runtime_surface_classification_2026-05-27.json` remained untouched by this slice
