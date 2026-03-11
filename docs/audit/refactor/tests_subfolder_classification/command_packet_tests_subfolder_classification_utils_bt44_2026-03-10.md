# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification-bt34`)
- **Risk:** `LOW` — batch relocation of test files only, no runtime/config changes.
- **Required Path:** `Full`
- **Objective:** Relocate remaining `Features/Fibonacci/HTF/LTF` root tests from `tests/` to `tests/utils/` with no behavior change.
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Execution mode:** `edit-only` (no terminal commands run in this step)

### Scope IN

- `tests/test_feature_*.py` (remaining root files at start of batch)
- `tests/test_features*.py` (remaining root files at start of batch)
- `tests/test_fibonacci.py`
- `tests/test_fib_*.py`
- `tests/test_htf_*.py`
- `tests/test_ltf_fibonacci_context.py`
- `tests/test_exit_fibonacci.py`
- `tests/utils/test_*.py` (destination files for moved candidates)
- `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
- `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt44_2026-03-10.md`

### Scope OUT

- `src/**`, `scripts/**`, `config/**`, `.github/workflows/**`
- all runtime logic and production code paths

### Relocated candidates

- `tests/test_feature_cache.py -> tests/utils/test_feature_cache.py`
- `tests/test_feature_parity.py -> tests/utils/test_feature_parity.py`
- `tests/test_feature_schema_contract_tBTCUSD_1h.py -> tests/utils/test_feature_schema_contract_tBTCUSD_1h.py`
- `tests/test_features.py -> tests/utils/test_features.py`
- `tests/test_features_asof_cache.py -> tests/utils/test_features_asof_cache.py`
- `tests/test_features_asof_cache_key_deterministic.py -> tests/utils/test_features_asof_cache_key_deterministic.py`
- `tests/test_features_asof_fast_hash_env_case.py -> tests/utils/test_features_asof_fast_hash_env_case.py`
- `tests/test_features_asof_fib_error_handling.py -> tests/utils/test_features_asof_fib_error_handling.py`
- `tests/test_fibonacci.py -> tests/utils/test_fibonacci.py`
- `tests/test_fib_logging.py -> tests/utils/test_fib_logging.py`
- `tests/test_fib_logging_env_flag.py -> tests/utils/test_fib_logging_env_flag.py`
- `tests/test_htf_exit_atr_no_lookahead.py -> tests/utils/test_htf_exit_atr_no_lookahead.py`
- `tests/test_htf_exit_engine.py -> tests/utils/test_htf_exit_engine.py`
- `tests/test_htf_exit_engine_htf_context_schema.py -> tests/utils/test_htf_exit_engine_htf_context_schema.py`
- `tests/test_htf_exit_engine_selection.py -> tests/utils/test_htf_exit_engine_selection.py`
- `tests/test_htf_exit_engine_swing_update_updates_exit_ctx.py -> tests/utils/test_htf_exit_engine_swing_update_updates_exit_ctx.py`
- `tests/test_htf_fibonacci.py -> tests/utils/test_htf_fibonacci.py`
- `tests/test_htf_fibonacci_asof_levels.py -> tests/utils/test_htf_fibonacci_asof_levels.py`
- `tests/test_htf_fibonacci_context_edge_cases_table.py -> tests/utils/test_htf_fibonacci_context_edge_cases_table.py`
- `tests/test_htf_fibonacci_context_invalid_swing_bounds.py -> tests/utils/test_htf_fibonacci_context_invalid_swing_bounds.py`
- `tests/test_htf_fibonacci_context_levels_completeness.py -> tests/utils/test_htf_fibonacci_context_levels_completeness.py`
- `tests/test_htf_fibonacci_context_requires_reference_ts.py -> tests/utils/test_htf_fibonacci_context_requires_reference_ts.py`
- `tests/test_htf_fibonacci_context_timeframe_aliases.py -> tests/utils/test_htf_fibonacci_context_timeframe_aliases.py`
- `tests/test_htf_fibonacci_mapping_age_hours.py -> tests/utils/test_htf_fibonacci_mapping_age_hours.py`
- `tests/test_htf_selector.py -> tests/utils/test_htf_selector.py`
- `tests/test_ltf_fibonacci_context.py -> tests/utils/test_ltf_fibonacci_context.py`
- `tests/test_exit_fibonacci.py -> tests/utils/test_exit_fibonacci.py`

### Gates required (coordinator run)

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q`

### Gate execution status

- Not run in this step (`edit-only` requested).
- **READY_FOR_COORDINATOR_GATES**
