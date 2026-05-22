Status: `historical merge-readiness context map / retained for traceability / not current approval or work order`

> Current status note (2026-05-22, `feature/genesis-topology-lifecycle-authority-map`): this
> file is retained as historical context for the merge-readiness packet from
> `feature/research-ledger-v1`. It is not current merge authority, current implementation
> guidance, or current work order. For current authority, see `docs/CURRENT_AUTHORITY_INDEX.md`.

## Context Map

### Files to Modify

| File                                            | Purpose                                      | Changes Needed                                                                                     |
| ----------------------------------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `src/core/research_ledger/__init__.py`          | Public package surface for ledger substrate  | Stage and commit canonical implementation already present locally                                  |
| `src/core/research_ledger/enums.py`             | Ledger enums/contracts                       | Stage and commit canonical implementation already present locally                                  |
| `src/core/research_ledger/models.py`            | Ledger record datamodels                     | Stage and commit canonical implementation already present locally                                  |
| `src/core/research_ledger/indexes.py`           | Deterministic index builders                 | Stage and commit canonical implementation already present locally                                  |
| `src/core/research_ledger/storage.py`           | Stable JSON persistence and ID allocation    | Stage and commit canonical implementation already present locally                                  |
| `src/core/research_ledger/queries.py`           | Read/query helpers                           | Stage and commit canonical implementation already present locally                                  |
| `src/core/research_ledger/validators.py`        | Schema validation rules                      | Stage and commit canonical implementation already present locally                                  |
| `src/core/research_ledger/service.py`           | Append/query orchestration                   | Stage and commit canonical implementation already present locally                                  |
| `tests/core/research_ledger/test_storage.py`    | Storage determinism coverage                 | Stage and commit canonical tests already present locally                                           |
| `tests/core/research_ledger/test_validators.py` | Validation coverage                          | Stage and commit canonical tests already present locally                                           |
| `tests/core/research_ledger/test_service.py`    | Service/index/lineage coverage               | Stage and commit canonical tests already present locally                                           |
| `tests/utils/test_optimizer_performance.py`     | Flaky blocker selector for full verification | Apply the same median-based stabilization already verified/pushed on `fix/flaky-trial-key-caching` |
| `handoff.md`                                    | Branch readiness note                        | Update blocker note only if full verification completes successfully                               |

### Dependencies (may need updates)

| File                                        | Relationship                                                |
| ------------------------------------------- | ----------------------------------------------------------- |
| `src/core/research_ledger/__init__.py`      | Re-exports public substrate types/services                  |
| `src/core/research_ledger/service.py`       | Imports storage, queries, validators, indexes               |
| `src/core/research_ledger/storage.py`       | Imports models + enum contracts                             |
| `src/core/research_ledger/queries.py`       | Imports storage + models                                    |
| `src/core/research_ledger/validators.py`    | Validates model payloads and references                     |
| `tests/utils/test_optimizer_performance.py` | Exercises `core.optimizer.runner._trial_key` cache behavior |

### Test Files

| Test                                                                                                       | Coverage                                                      |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `tests/core/research_ledger/test_storage.py`                                                               | stable JSON, deterministic ID allocation, index round-trip    |
| `tests/core/research_ledger/test_validators.py`                                                            | schema validity, bad IDs, JSON metadata, timezone requirement |
| `tests/core/research_ledger/test_service.py`                                                               | append flow, lineage, index refresh, duplicate rejection      |
| `tests/utils/test_optimizer_performance.py`                                                                | performance guard including flaky trial-key caching selector  |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | determinism replay guard                                      |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                | feature-cache invariance guard                                |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant guard                                      |

### Reference Patterns

| File                                                                                                | Pattern                                                           |
| --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `.worktrees/feature-regime-intelligence-layer-migration/src/core/research_ledger/validators.py`     | Canonical validated ledger substrate implementation               |
| `.worktrees/feature-regime-intelligence-layer-migration/tests/core/research_ledger/test_service.py` | Canonical validated ledger service tests                          |
| `.worktrees/fix-flaky-trial-key-caching/tests/utils/test_optimizer_performance.py`                  | Verified stabilization pattern for noisy micro-benchmark selector |
| `handoff.md`                                                                                        | Existing branch-readiness note to update rather than duplicate    |

### Risk Assessment

- [x] Breaking changes to public API: low risk; package is additive and not yet integrated into runtime paths
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Full verification required before merge-readiness can be claimed
