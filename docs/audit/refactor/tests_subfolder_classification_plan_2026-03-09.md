# Tests Subfolder Classification Plan (Phase 1)

## Current State

- Total test files (`tests/**/test_*.py`): **169**
- Already structured subfolders:
  - `tests/integration/` (**2** files)
  - `tests/utils/diffing/` (**4** files)
  - `tests/core/strategy/components/` (**2** files)
- Majority of suite remains flat under `tests/`.

## Sensitivity Assessment

This refactor is classified as **sensitive** because file moves can break:

1. path-based references in docs/contracts/audits,
2. hardcoded `tests/data/*` references in tests,
3. ad-hoc local commands/scripts that target exact test file paths.

No behavior/runtime code change is intended; this is a structural test-layout migration.

## Path-Sensitive References (verified)

### In tests (hardcoded data paths)

- `tests/test_feature_parity.py:58-59`
  - `Path("tests/data/tBTCUSD_1h_sample.parquet")`
  - `Path("tests/data/tBTCUSD_1h_features_v17.parquet")`
- `tests/test_precompute_vs_runtime.py:23`
  - `SAMPLE_PATH = Path("tests/data/tBTCUSD_1h_sample.parquet")`

### In CI / docs

- `.github/workflows/ci.yml:60`
  - `pytest -q`
- `docs/features/FEATURE_COMPUTATION_MODES.md:252-273`
  - explicit references to `tests/test_feature_parity.py`, `tests/test_precompute_vs_runtime.py`, and `tests/data/*`

> Note: There are numerous historical `tests/test_*.py` path references under `docs/ideas/**`, `docs/audit/**`, and `docs/archive/**`; these should be updated in batches aligned with file moves.

## Initial Classification (candidate buckets)

### Stable integration/regression (already clear)

- Keep under `tests/integration/` (already present)
- Add future regression-only tests here where appropriate.

### Candidate experimental / one-off / temporary (manual review required)

- `tests/experiments/test_components_poc.py` _(moved in Phase 2A batch 1)_
- `tests/experiments/test_composable_strategy_poc.py` _(moved in Phase 2A batch 2)_
- `tests/experiments/test_e2e_pipeline.py` _(moved in Phase 2A batch 3A)_
- `tests/experiments/test_performance_improvements.py` _(moved in Phase 2A batch 3B)_
- `tests/experiments/test_performance_improvements_2025.py` _(moved in Phase 2A batch 3C)_

These are **candidates only**; final classification requires owner review + usage check in active docs/contracts.

### Candidate active backtest tests (new bucket)

- `tests/backtest/test_backtest_trade_logger.py` _(moved in BT1)_
- `tests/backtest/test_backtest_metrics.py` _(moved in BT2)_
- `tests/backtest/test_backtest_position_tracker.py` _(moved in BT3)_
- `tests/backtest/test_backtest_entry_reasons.py` _(moved in BT4)_
- `tests/backtest/test_backtest_debug_env_flag.py` _(moved in BT5)_
- `tests/backtest/test_backtest_applies_htf_exit_config.py` _(moved in BT6)_

- `tests/backtest/test_backtest_hook_invariants.py` _(moved in BT7)_
- `tests/backtest/test_backtest_determinism_smoke.py` _(moved in BT8)_
- `tests/backtest/test_backtest_engine_hook.py` _(moved in BT10)_
- `tests/backtest/test_backtest_engine.py` _(moved in BT11)_

### Candidate utility tests (new bucket)

- `tests/utils/test_backoff_util.py` _(moved in BT12)_
- `tests/utils/test_build_auth_headers.py` _(moved in BT13)_
- `tests/utils/test_gate_dominance_utils.py` _(moved in BT14)_
- `tests/utils/test_dict_merge_stack_safe.py` _(moved in BT15)_
- `tests/utils/test_read_helpers.py` _(moved in BT16)_
- `tests/utils/test_nonce.py` _(moved in BT17)_
- `tests/utils/test_logging_redaction.py` _(moved in BT18)_
- `tests/utils/test_symbols.py` _(moved in BT19)_
- `tests/utils/test_mcp_blocked_patterns_windows_path.py` _(moved in BT20)_
- `tests/utils/test_pydantic_validator_exception_types.py` _(moved in BT21)_
- `tests/utils/test_health.py` _(moved in BT22)_
- `tests/utils/test_ev_gate.py` _(moved in BT23)_
- `tests/utils/test_env_flags.py` _(moved in BT24)_
- `tests/utils/test_indicators_min.py` _(moved in BT25)_
- `tests/utils/test_bollinger.py` _(moved in BT26)_
- `tests/utils/test_confidence.py` _(moved in BT27)_
- `tests/utils/test_cooldown.py` _(moved in BT28)_
- `tests/utils/test_indicators_rsi_adx.py` _(moved in BT29)_
- `tests/utils/test_decision_edge.py` _(moved in BT30)_
- `tests/utils/test_decision_matrix.py` _(moved in BT31)_
- `tests/utils/test_triple_barrier.py` _(moved in BT32)_
- `tests/utils/test_account_endpoints.py` _(moved in BT37)_
- `tests/utils/test_config_api_e2e.py` _(moved in BT42)_
- `tests/utils/test_config_endpoints.py` _(moved in BT47)_
- `tests/utils/test_ui_endpoints.py` _(moved in BT52)_
- `tests/utils/test_ws_public_min.py` _(moved in BT57)_
- `tests/utils/test_mcp_structure_allowlist.py` _(moved in BT62)_
- `tests/utils/test_mcp_stdio_encoding.py` _(moved in BT67)_
- `tests/utils/test_mcp_server.py` _(moved in BT72)_
- `tests/utils/test_mcp_resources.py` _(moved in BT77)_
- `tests/utils/test_mcp_remote_git_workflow_confirm.py` _(moved in BT82)_
- `tests/utils/test_mcp_remote_authorization.py` _(moved in BT87)_
- `tests/utils/test_mcp_logging_redaction.py` _(moved in BT92)_
- `tests/utils/test_mcp_integration.py` _(moved in BT97)_
- `tests/utils/test_mcp_git_workflow_tools.py` _(moved in BT102)_
- `tests/utils/test_mcp_git_status_remote_filters.py` _(moved in BT107)_
- `tests/utils/test_mcp_config_env_override.py` _(moved in BT112)_
- `tests/utils/test_remote_server_fastmcp_sse_alias.py` _(moved in BT117)_
- `tests/utils/test_no_sync_httpx_in_async_handlers.py` _(moved in BT122)_

Guardrail: selector-ankrade backtesttester är nu flyttade till `tests/backtest/`.
Historikharmonisering för `docs/ideas/REGIME_INTELLIGENCE_T0_*` .. `T8_*` är genomförd i BT9-batchen.
Referenser till `tests/test_backtest_determinism_smoke.py` är uppdaterade till `tests/backtest/test_backtest_determinism_smoke.py`.

## Proposed Target Layout (incremental)

- `tests/unit/` (new)
  - domain-grouped slices (e.g., strategy, optimizer, config, api, mcp)
- `tests/integration/` (existing)
  - cross-component flows/regressions
- `tests/experiments/` (new)
  - PoC/one-off/perf exploration tests
- `tests/utils/diffing/` (existing, keep)
- `tests/data/` (existing, keep)

## Migration Strategy (phased)

### Phase 2A (lowest risk)

- Move only clearly-labeled candidate files to `tests/experiments/`.
- Update direct path references in docs where those tests are explicitly named.
- Keep import behavior and test names unchanged.

### Phase 2B (structured unit grouping)

- Move selected stable flat tests into `tests/unit/<domain>/` in small batches.
- After each batch:
  - update direct path references in docs/contracts touched by that batch,
  - run selectors + targeted suite.

### Phase 2C (cleanup)

- normalize leftover references (`docs/audit/**`, `docs/ideas/**`) via scripted path rewrite guarded by review.

## Rollback Plan

If any batch breaks discovery or tooling:

1. Revert only the latest move batch commit.
2. Re-run:
   - `pytest -q`
   - determinism selector
   - pipeline invariant selector
3. Re-scope to a smaller move set and retry.

## Exit Criteria for Phase 1

- Classification artifact exists and is reviewed.
- Path-sensitive reference inventory is documented.
- Initial low-risk move batches are completed with gate evidence.
- Phase-2 move checklist is approved before implementation.
