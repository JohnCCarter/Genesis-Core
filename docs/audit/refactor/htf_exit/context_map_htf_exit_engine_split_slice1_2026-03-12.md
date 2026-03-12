## Context Map

### Files to Modify

| File                                                        | Purpose                                                        | Changes Needed                                                     |
| ----------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------ |
| `src/core/backtest/htf_exit_engine.py`                      | Main HTF exit engine with mixed responsibilities               | Extract partial-exit logic behind unchanged public behavior        |
| `src/core/backtest/htf_exit_partials.py`                    | New focused helper module                                      | Host partial-exit calculations and trigger bookkeeping             |
| `tests/backtest/test_htf_exit_engine_htf_context_schema.py` | Direct unit coverage of partial logic and schema compatibility | Extend/adjust tests for extracted helper while preserving behavior |

### Dependencies (may need updates)

| File                                                      | Relationship                                                                                                              |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `src/core/backtest/engine.py`                             | Instantiates the new strategy HTF exit engine and also adapts `check_exits()` results while expecting unchanged flags/API |
| `tests/backtest/test_backtest_applies_htf_exit_config.py` | Asserts exit-engine flags/defaults                                                                                        |
| `tests/integration/test_new_htf_exit_engine_adapter.py`   | Adapter-level compatibility check around `check_exits()`                                                                  |
| `tests/backtest/test_htf_exit_engine.py`                  | Read-only legacy/simple engine coverage reference                                                                         |

### Test Files

| Test                                                                   | Coverage                                                 |
| ---------------------------------------------------------------------- | -------------------------------------------------------- |
| `tests/backtest/test_htf_exit_engine_htf_context_schema.py`            | Producer schema, swing update, partial padding semantics |
| `tests/backtest/test_htf_exit_engine_swing_update_updates_exit_ctx.py` | Frozen `exit_ctx` remains consistent after swing updates |
| `tests/backtest/test_htf_exit_engine_selection.py`                     | New/legacy engine selection and config flag behavior     |
| `tests/backtest/test_backtest_applies_htf_exit_config.py`              | Exit-engine flags/defaults remain compatible             |
| `tests/backtest/test_backtest_determinism_smoke.py`                    | Determinism replay smoke for backtest/exits              |
| `tests/governance/test_pipeline_fast_hash_guard.py`                    | Pipeline invariant hash guard                            |
| `tests/utils/test_features_asof_cache_key_deterministic.py`            | Feature cache invariance guard                           |

### Reference Patterns

| File                                   | Pattern                                                              |
| -------------------------------------- | -------------------------------------------------------------------- |
| `src/core/backtest/engine.py`          | Thin orchestration over exit actions with helper-style decomposition |
| `src/core/backtest/exit_strategies.py` | Focused policy/helper classes for HTF-related decisions              |

### Risk Assessment

- [x] Breaking changes to public API: possible if `check_exits()` or engine flags drift
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] High-sensitivity zone: `src/core/backtest/*` and related exit behavior
- [x] No-behavior-change default required for slice 1
