## Context Map

### Files to Modify

| File                                                                   | Purpose                               | Changes Needed                                                                                    |
| ---------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `src/core/backtest/htf_exit_engine.py`                                 | Main HTF exit engine orchestrator     | Replace remaining inline responsibilities with helper delegation while preserving public behavior |
| `src/core/backtest/htf_exit_trailing.py`                               | New trailing/fallback helper module   | Host trailing-stop promotion and fallback-trail calculations                                      |
| `src/core/backtest/htf_exit_structure.py`                              | New structure-break helper module     | Host full-exit structure-break decision logic                                                     |
| `src/core/backtest/htf_exit_swing_updates.py`                          | New context/swing helper module       | Host frozen-context validation, exit-level initialization, and swing-update mutation logic        |
| `tests/backtest/test_htf_exit_engine_htf_context_schema.py`            | Existing HTF exit schema coverage     | Keep producer-schema and swing-update behavior locked during extraction                           |
| `tests/backtest/test_htf_exit_engine_swing_update_updates_exit_ctx.py` | Existing frozen-context coverage      | Preserve exit_ctx update semantics after swing updates                                            |
| `tests/backtest/test_htf_exit_engine_components.py`                    | New focused engine component coverage | Lock trailing, structure-break, and fallback semantics after extraction                           |

### Dependencies (read-only unless scope exception approved)

| File                                                      | Relationship                                                                    |
| --------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `src/core/backtest/engine.py`                             | Instantiates the new HTF exit engine and consumes `check_exits()` actions/flags |
| `tests/backtest/test_backtest_applies_htf_exit_config.py` | Guards feature-flag propagation from config to engine instance                  |
| `tests/backtest/test_backtest_determinism_smoke.py`       | Guards determinism in backtest path when exit logic is involved                 |
| `tests/integration/test_new_htf_exit_engine_adapter.py`   | Guards adapter compatibility for new engine path                                |
| `src/core/backtest/htf_exit_partials.py`                  | Existing extracted helper whose semantics must remain unchanged                 |

### Test Files

| Test                                                                   | Coverage                                                          |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `tests/backtest/test_htf_exit_engine_htf_context_schema.py`            | Producer schema, partial padding, swing update + 0.786 retention  |
| `tests/backtest/test_htf_exit_engine_swing_update_updates_exit_ctx.py` | Frozen `exit_ctx` bounds and fib refresh after dynamic update     |
| `tests/backtest/test_htf_exit_engine_components.py`                    | Trailing promotion, fallback trail, and structure-break semantics |
| `tests/backtest/test_htf_exit_engine_selection.py`                     | New/legacy engine selection and flag behavior                     |
| `tests/backtest/test_backtest_applies_htf_exit_config.py`              | Config flag propagation                                           |
| `tests/backtest/test_backtest_determinism_smoke.py`                    | Determinism replay smoke                                          |
| `tests/governance/test_pipeline_fast_hash_guard.py`                    | Pipeline invariant hash guard                                     |
| `tests/utils/test_features_asof_cache_key_deterministic.py`            | Feature cache invariance guard                                    |
| `tests/integration/test_new_htf_exit_engine_adapter.py`                | Adapter compatibility smoke                                       |

### Reference Patterns

| File                                     | Pattern                                                         |
| ---------------------------------------- | --------------------------------------------------------------- |
| `src/core/backtest/exit_strategies.py`   | Focused HTF-related policy/helper code with explicit parameters |
| `src/core/backtest/htf_exit_partials.py` | Small pure helper extraction with preserved trigger semantics   |

### Risk Assessment

- [x] High-sensitivity zone: `src/core/backtest/*`
- [x] No-behavior-change default still required
- [x] Public behavior risk if `check_exits()` action ordering or reasons drift
- [x] Frozen-context risk if swing update or initialization mutates `exit_ctx` differently
- [ ] Config/schema changes required
- [ ] Runtime authority files touched
