## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/htf-exit-engine-split`
- **Risk:** `HIGH` — why: HTF exit logic in `src/core/backtest/*` affects trading exits and determinism, even though slice 1 is intended as a structure-only extraction.
- **Required Path:** `Full`
- **Objective:** Extract partial-exit responsibility from `HTFFibonacciExitEngine` into `src/core/backtest/htf_exit_partials.py` while preserving runtime behavior, public API, defaults, flags, and trigger semantics.
- **Candidate:** `slice1-partials`
- **Base SHA:** `8ed46ea0060194426d290305dba4be2f0fd5c2dc`

### Scope

- **Scope IN:**
  - `src/core/backtest/htf_exit_engine.py`
  - `src/core/backtest/htf_exit_partials.py`
  - `tests/backtest/test_htf_exit_engine_htf_context_schema.py`
  - `tests/backtest/test_htf_exit_engine_selection.py` (only if required for compatibility assertions)
  - `docs/audit/refactor/htf_exit/context_map_htf_exit_engine_split_slice1_2026-03-12.md`
  - `docs/audit/refactor/htf_exit/command_packet_htf_exit_engine_split_slice1_2026-03-12.md`
- **Scope OUT:**
  - `src/core/strategy/htf_exit_engine.py`
  - `src/core/backtest/engine.py`
  - config files, runtime authority files, optimizer/backtest orchestration, docs outside this audit folder
- **Expected changed files:** 3–5
- **Max files touched:** 5

### Constraints

- **Default:** `NO BEHAVIOR CHANGE`
- Keep `HTFFibonacciExitEngine.check_exits()` signature and return contract unchanged.
- Keep feature flags (`enable_partials`, `enable_trailing`, `enable_structure_breaks`) unchanged.
- Do not change default partial percentages, thresholds, trigger IDs, padding semantics, or fallback behavior.
- Do not alter swing update, trailing, structure break, or frozen-context behavior in slice 1.

### Gates required

- `python -m pytest tests/backtest/test_htf_exit_engine_htf_context_schema.py -q`
- `python -m pytest tests/backtest/test_htf_exit_engine_swing_update_updates_exit_ctx.py -q`
- `python -m pytest tests/backtest/test_htf_exit_engine_selection.py -q`
- `python -m pytest tests/backtest/test_backtest_applies_htf_exit_config.py -q`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py -q`
- `python -m ruff check src tests`
- `python -m pytest tests/integration/test_new_htf_exit_engine_adapter.py -q` (recommended)

### Stop Conditions

- Scope drift beyond listed files
- Any behavior change in partial trigger order, sizes, reasons, or dedup semantics
- Any drift in engine flags, `check_exits()` contract, or determinism guards
- Any need to modify trailing/structure/fallback logic to make slice 1 work

### Output required

- **Implementation Report**
- **PR evidence template**
- **Opus pre-code verdict before implementation**
