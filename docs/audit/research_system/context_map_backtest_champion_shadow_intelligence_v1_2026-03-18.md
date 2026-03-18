## Context Map

### Files to Modify

| File                                                                                               | Purpose                                            | Changes Needed                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/run/run_backtest.py`                                                                      | CLI orchestration for canonical backtest execution | Add explicit opt-in shadow artifact path flag(s); compose intelligence shadow hook alongside existing decision-row hook; save summary artifact after run            |
| `src/core/backtest/intelligence_shadow.py`                                                         | New backtest-local shadow adapter module           | Build deterministic shadow hook, event capture, derived approved parameter set, orchestrator execution, and summary serialization without mutating decision outputs |
| `tests/backtest/test_run_backtest_intelligence_shadow.py`                                          | CLI/backtest shadow parity proof                   | Verify shadow opt-in writes artifact but preserves `action`, `size`, `reasons`, trades, and exit behavior                                                           |
| `tests/integration/test_backtest_champion_intelligence_shadow.py`                                  | Champion-path shadow integration proof             | Verify existing `tBTCUSD_3h` champion can run with shadow enabled and produce deterministic summary + ledger artifacts                                              |
| `docs/audit/research_system/command_packet_backtest_champion_shadow_intelligence_v1_2026-03-18.md` | Governance packet                                  | Lock scope, gates, stop conditions, and artifact homes                                                                                                              |
| `docs/features/feature-champion-shadow-intelligence-1.md`                                          | Executable implementation plan                     | Describe atomic phases, files, tests, rollback, and risks                                                                                                           |

### Dependencies (may need updates)

| File                                                | Relationship                                                                                                                          |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/backtest/engine.py`                       | Already provides `evaluation_hook(result, meta, candles)` seam; should remain unchanged if possible                                   |
| `src/core/backtest/composable_engine.py`            | Reference pattern for passive hook composition that does not monkey-patch runtime strategy logic                                      |
| `src/core/intelligence/events/models.py`            | Defines `IntelligenceEvent` / `ValidatedIntelligenceEvent` contract to be populated by the shadow adapter                             |
| `src/core/intelligence/parameter/interface.py`      | Defines required non-empty `ApprovedParameterSet` contract for orchestrator input                                                     |
| `src/core/intelligence/ledger_adapter/interface.py` | Defines `LedgerPersistenceRequest` / `LedgerPersistenceResult` artifact boundary                                                      |
| `src/core/research_orchestrator/workflow.py`        | Requires non-empty collection output, non-empty approved parameter sets, and persisted ids; shadow adapter must honor these contracts |
| `tests/helpers/research_system.py`                  | Reference helper for constructing deterministic orchestrator/service stacks                                                           |
| `src/core/backtest/trade_logger.py`                 | Reference output path pattern for machine-readable run artifacts                                                                      |

### Test Files

| Test                                                                                                       | Coverage                                                                            |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `tests/research_orchestrator/test_workflow.py`                                                             | Existing deterministic orchestrator ordering / persistence expectations             |
| `tests/integration/test_orchestrator_flow.py`                                                              | Existing end-to-end research orchestration pattern                                  |
| `tests/backtest/test_run_backtest_decision_rows.py`                                                        | Existing run_backtest artifact-hook CLI pattern                                     |
| `tests/backtest/test_runner_direct_includes_merged_config.py`                                              | Existing proof that direct backtest execution preserves effective config provenance |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | Required pipeline invariant guard                                                   |
| `tests/utils/test_feature_cache.py`                                                                        | Explicit feature-cache invariance selector required by STRICT notes                 |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | Required determinism replay guard for shadow-enabled backtest path                  |

### Reference Patterns

| File                                          | Pattern                                                                                                                   |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `scripts/run/run_backtest.py`                 | Existing `_compose_decision_row_capture_hook` shows how to compose a passive artifact hook over an optional upstream hook |
| `src/core/backtest/composable_engine.py`      | Existing evaluation-hook wrapper pattern that keeps decision execution external and passive                               |
| `tests/helpers/research_system.py`            | Existing deterministic builder for orchestrator + ledger service stack                                                    |
| `tests/integration/test_orchestrator_flow.py` | Existing expectation shape for counts/order/persisted ids                                                                 |

### Risk Assessment

- [x] Breaking changes to public API possible if new CLI flags are not opt-in only
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] High-sensitivity backtest path touched; parity proof is mandatory
- [x] Shadow adapter must not mutate `result`, `meta`, `configs`, or `state`
- [x] Summary artifact belongs under `results/`; ledger root should remain under `artifacts/`
- [x] Derived approved parameter set must be explicitly advisory-only and not interpreted as promotion semantics
