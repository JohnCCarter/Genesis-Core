---
goal: Retire legacy core.server_*_api alias stubs after server package split
version: 1.0
date_created: 2026-03-12
last_updated: 2026-03-12
owner: GitHub Copilot
status: 'Planned'
tags:
	- refactor
	- server
	- compatibility
	- alias
	- cleanup
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan defines a deterministic, multi-phase retirement path for the legacy `core.server_*_api` alias stub modules that remain after the `src/core/api/` package split. The plan is explicitly designed to preserve default behavior until removal criteria are fully proven. No phase in this plan may remove alias stubs before all migration and parity requirements are satisfied.

## 1. Requirements & Constraints

- **REQ-001**: Preserve default runtime behavior for `uvicorn core.server:app` throughout all phases.
- **REQ-002**: Preserve FastAPI router registration order in `src/core/server.py` until the final cleanup phase is complete.
- **REQ-003**: Prove that no production code under `src/` depends on direct imports from `core.server_*_api` before removing any alias stub.
- **REQ-004**: Prove that all remaining test imports from `core.server_*_api` have been migrated or intentionally retained with documented rationale before removing any alias stub.
- **REQ-005**: Maintain identical module behavior for monkeypatch-sensitive test surfaces until the phase that explicitly removes old import paths.
- **REQ-006**: Keep `src/core/server.py` as the canonical API entrypoint module even after alias stub retirement.
- **CON-001**: This plan must execute as a separate refactor batch after the already-completed package move to `src/core/api/`.
- **CON-002**: The alias retirement refactor must not be combined with unrelated runtime, strategy, backtest, optimizer, or documentation cleanup.
- **CON-003**: Historical audit artifacts under `docs/audit/refactor/server/` remain evidence and are not to be rewritten as part of runtime cleanup.
- **CON-004**: Removal of alias stubs is blocked until import-inventory evidence shows zero required product-code consumers of the old module paths.
- **GUD-001**: Use no-behavior-change sequencing: inventory first, migration second, removal last.
- **GUD-002**: Prefer one small removal batch over broad multi-surface deletion if evidence is incomplete.
- **PAT-001**: Treat `src/core/api/*.py` as canonical route implementation modules.
- **PAT-002**: Treat `src/core/server.py` as API assembler and compatibility facade, not as route-implementation storage.
- **TST-001**: Preserve or replace parity tests that currently prove old/new module identity before removing any file.
- **TST-002**: Run focused API tests, import smoke, determinism replay, feature cache invariance, and pipeline invariant checks before removal is considered complete.

## 2. Implementation Steps

### Implementation Phase 1

- **GOAL-001**: Create a complete alias-dependency inventory and classify all remaining consumers of `core.server_*_api` imports.

| Task     | Description                                                                                                                                                        | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ---- | ------ | ----- | ------ | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | --- |
| TASK-001 | Search `src/**` for `core.server\_(account                                                                                                                         | config    | info | models | paper | public | status | strategy | ui)\_api`imports and record every remaining product-code usage with exact file path and line reference. Exclude`.claude/worktrees/\*\*` from the inventory. |     |     |
| TASK-002 | Search `tests/**` for the same alias imports and classify each usage as one of: parity proof, monkeypatch dependency, route smoke, or removable legacy import.     |           |      |
| TASK-003 | Search docs and auxiliary files for old module-path references and classify them as runtime-doc reference, historical evidence, or ignorable archive material.     |           |      |
| TASK-004 | Produce an inventory artifact listing every alias stub file in `src/core/server_*_api.py`, every direct consumer, and a proposed migration target in `core.api.*`. |           |      |
| TASK-005 | Verify that no new imports from `core.server_*_api` have appeared in active product code since the package-split commit range.                                     |           |      |

### Implementation Phase 2

- **GOAL-002**: Migrate all active consumers from old import paths to canonical `core.api.*` paths while preserving test intent.

| Task     | Description                                                                                                                                                                                          | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-006 | Update all product-code imports under `src/**` that still reference `core.server_*_api` to use the matching `core.api.*` module. Preserve runtime behavior and import order in `src/core/server.py`. |           |      |
| TASK-007 | Replace test imports used only for basic route access or module access with canonical `core.api.*` imports where monkeypatch identity against the old path is no longer required.                    |           |      |
| TASK-008 | Split current mixed-purpose tests into two categories: canonical-behavior tests and legacy-compatibility tests. Keep legacy tests only as long as alias stub support remains in scope.               |           |      |
| TASK-009 | Add a guard test or lint-style search assertion that fails if new product code under `src/**` introduces fresh `core.server_*_api` imports.                                                          |           |      |
| TASK-010 | Verify that `src/core/config/validator.py` and any live architecture docs reference canonical `core.api.*` modules where appropriate, without rewriting historical audit evidence.                   |           |      |

### Implementation Phase 3

- **GOAL-003**: Prove that alias stubs are no longer required and prepare deterministic removal.

| Task     | Description                                                                                                                                                     | Completed | Date |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-011 | Add or update a targeted proof that canonical `core.api.*` modules satisfy all remaining route behavior without relying on old path imports.                    |           |      |
| TASK-012 | Remove old-path identity tests that exist only to prove alias-stub behavior once all consumers have migrated and legacy support is intentionally being dropped. |           |      |
| TASK-013 | Re-run import inventory and confirm zero required product-code imports from `core.server_*_api` and zero required test imports that block removal.              |           |      |
| TASK-014 | Obtain governance approval for alias-stub deletion using a dedicated command packet and context map scoped only to the retirement batch.                        |           |      |

### Implementation Phase 4

- **GOAL-004**: Remove alias stubs and close the server split with full verification.

| Task     | Description                                                                                                                                                                                                                                                                                                                                  | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-015 | Delete the legacy alias stub files: `src/core/server_account_api.py`, `src/core/server_config_api.py`, `src/core/server_info_api.py`, `src/core/server_models_api.py`, `src/core/server_paper_api.py`, `src/core/server_public_api.py`, `src/core/server_status_api.py`, `src/core/server_strategy_api.py`, and `src/core/server_ui_api.py`. |           |      |
| TASK-016 | Remove any final compatibility comments, import proofs, and dead references that were only needed while the stubs existed.                                                                                                                                                                                                                   |           |      |
| TASK-017 | Run the required gate set: `black --check`, `ruff check`, focused API tests, import smoke, determinism replay, feature cache invariance, pipeline invariant, and any config-authority selectors still applicable to the touched surface.                                                                                                     |           |      |
| TASK-018 | Record closure evidence showing that `src/core/api/` is canonical, `src/core/server.py` remains the entrypoint/assembler, and no `core.server_*_api` files remain.                                                                                                                                                                           |           |      |

## 3. Alternatives

- **ALT-001**: Delete alias stubs immediately after the package split. Rejected because tests demonstrated old-path monkeypatch semantics were part of the observable compatibility contract.
- **ALT-002**: Keep alias stubs indefinitely. Rejected because they preserve legacy surface area, increase cognitive load, and delay true closure of the server package split.
- **ALT-003**: Replace alias stubs with simple `from core.api.<module> import *` re-export shims. Rejected because this does not reliably preserve same-module-object semantics for monkeypatch-sensitive tests.
- **ALT-004**: Collapse `src/core/server.py` into `src/core/api/` directly. Rejected because `core.server:app` is still the canonical entrypoint and should remain stable while the split is being closed.

## 4. Dependencies

- **DEP-001**: `src/core/server.py` must continue to expose the assembled FastAPI app and router order during the migration phases.
- **DEP-002**: `src/core/api/config.py` currently pins logger identity to `core.server_config_api`; any future cleanup must preserve logging expectations or explicitly update tests and observability assumptions.
- **DEP-003**: `tests/integration/test_config_endpoints.py`, `tests/integration/test_ui_endpoints.py`, and `tests/utils/test_observability.py` currently contain alias-specific compatibility proofs that must be retired deliberately, not incidentally.
- **DEP-004**: Historical audit files in `docs/audit/refactor/server/` are reference evidence for the package split and should not be treated as active runtime docs.

## 5. Files

- **FILE-001**: `src/core/server.py` — retains API entrypoint and router assembly during and after alias retirement.
- **FILE-002**: `src/core/api/account.py`
- **FILE-003**: `src/core/api/config.py`
- **FILE-004**: `src/core/api/info.py`
- **FILE-005**: `src/core/api/models.py`
- **FILE-006**: `src/core/api/paper.py`
- **FILE-007**: `src/core/api/public.py`
- **FILE-008**: `src/core/api/status.py`
- **FILE-009**: `src/core/api/strategy.py`
- **FILE-010**: `src/core/api/ui.py`
- **FILE-011**: `src/core/server_account_api.py`
- **FILE-012**: `src/core/server_config_api.py`
- **FILE-013**: `src/core/server_info_api.py`
- **FILE-014**: `src/core/server_models_api.py`
- **FILE-015**: `src/core/server_paper_api.py`
- **FILE-016**: `src/core/server_public_api.py`
- **FILE-017**: `src/core/server_status_api.py`
- **FILE-018**: `src/core/server_strategy_api.py`
- **FILE-019**: `src/core/server_ui_api.py`
- **FILE-020**: `tests/integration/test_config_endpoints.py`
- **FILE-021**: `tests/integration/test_ui_endpoints.py`
- **FILE-022**: `tests/utils/test_observability.py`
- **FILE-023**: `tests/utils/test_health.py`
- **FILE-024**: `tests/integration/test_account_endpoints.py`

## 6. Testing

- **TEST-001**: Focused inventory check showing zero product-code imports from `core.server_*_api` before deletion.
- **TEST-002**: Focused API route tests currently used by the package split: `tests/integration/test_ui_endpoints.py`, `tests/integration/test_config_endpoints.py`, `tests/utils/test_observability.py`, `tests/utils/test_health.py`, `tests/integration/test_account_endpoints.py`.
- **TEST-003**: Import smoke: `tests/governance/test_import_smoke_backtest_optuna.py`.
- **TEST-004**: Determinism replay: `tests/backtest/test_backtest_determinism_smoke.py`.
- **TEST-005**: Feature cache invariance: `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`.
- **TEST-006**: Pipeline invariant: `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`.
- **TEST-007**: If `config` alias-removal touches config-authority semantics, rerun the focused config selectors previously used for the package split.

## 7. Risks & Assumptions

- **RISK-001**: Some remaining tests intentionally exercise old import paths as part of compatibility coverage. Mitigation: classify and retire them explicitly instead of deleting en masse.
- **RISK-002**: `src/core/api/config.py` uses logger name `core.server_config_api`; removing the stub without revisiting logging assumptions may create metadata drift. Mitigation: treat config cleanup as its own verified sub-step.
- **RISK-003**: Function-local imports or monkeypatch behavior may hide residual dependencies not obvious from a naive text search. Mitigation: combine text inventory with focused test passes and import-smoke coverage.
- **RISK-004**: Worktree copies under `.claude/worktrees/**` may produce false positives during inventory. Mitigation: exclude worktrees from retirement evidence for the active branch.
- **ASSUMPTION-001**: The canonical long-term target keeps `src/core/server.py` as the stable entrypoint while route implementations remain in `src/core/api/`.
- **ASSUMPTION-002**: Alias retirement will be executed as a separate governed batch after the already-pushed package split.

## 8. Related Specifications / Further Reading

- `docs/audit/refactor/server/command_packet_server_api_package_move_2026-03-12.md`
- `docs/audit/refactor/server/context_map_server_api_package_move_2026-03-12.md`
- `.github/copilot-instructions.md`
- `docs/governance_mode.md`
- `AGENTS.md`
