## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/htf-exit-engine-split`
- **Risk:** `HIGH` — why: remaining work still touches high-sensitivity HTF exit behavior in `src/core/backtest/*`, including trailing, structure-break, and frozen-context mutation logic.
- **Required Path:** `Full`
- **Objective:** Complete the HTF exit engine split by extracting remaining responsibilities from `HTFFibonacciExitEngine` into helper modules for trailing, structure-breaks, and swing/context handling while preserving no-behavior-change defaults.
- **Candidate:** `remaining-split`
- **Base SHA:** `8ed46ea0060194426d290305dba4be2f0fd5c2dc` (builds on pending slice-1 partial extraction in this worktree)

### Scope

- **Scope IN:**
  - `src/core/backtest/htf_exit_engine.py`
  - `src/core/backtest/htf_exit_trailing.py`
  - `src/core/backtest/htf_exit_structure.py`
  - `src/core/backtest/htf_exit_swing_updates.py`
  - `tests/backtest/test_htf_exit_engine_htf_context_schema.py`
  - `tests/backtest/test_htf_exit_engine_swing_update_updates_exit_ctx.py`
  - `tests/backtest/test_htf_exit_engine_components.py`
  - `docs/audit/refactor/htf_exit/context_map_htf_exit_engine_split_remaining_2026-03-12.md`
  - `docs/audit/refactor/htf_exit/command_packet_htf_exit_engine_split_remaining_2026-03-12.md`
- **Scope OUT:**
  - `src/core/strategy/htf_exit_engine.py`
  - `src/core/backtest/engine.py`
  - `src/core/backtest/htf_exit_partials.py` (read-only unless import-level compatibility fix becomes unavoidable)
  - config files, runtime authority files, optimizer/backtest orchestration, docs outside this audit folder
- **Expected changed files:** 6-9
- **Max files touched:** 9

### Constraints

- **Default:** `NO BEHAVIOR CHANGE`
- Keep `HTFFibonacciExitEngine.check_exits()` signature, return type, action ordering, and reason strings unchanged.
- Keep feature flags, partial trigger semantics, thresholds, adaptive-near checks, and fallback reason unchanged.
- Keep swing update, frozen `exit_ctx`, and initialization semantics unchanged.
- Do not modify config loading, backtest engine orchestration, or adapter code in this packet.

### Gates required

- `python -m pytest tests/backtest/test_htf_exit_engine_htf_context_schema.py -q`
- `python -m pytest tests/backtest/test_htf_exit_engine_swing_update_updates_exit_ctx.py -q`
- `python -m pytest tests/backtest/test_htf_exit_engine_components.py -q`
- `python -m pytest tests/backtest/test_htf_exit_engine_selection.py -q`
- `python -m pytest tests/backtest/test_backtest_applies_htf_exit_config.py -q`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py -q`
- `python -m pytest tests/integration/test_new_htf_exit_engine_adapter.py -q`
- `python -m ruff check src tests`

### Stop Conditions

- Scope drift beyond listed files
- Any change in `check_exits()` public contract, action ordering, or reason strings
- Any drift in fallback trail, structure-break thresholds, or swing-update mutation semantics
- Any need to touch `src/core/backtest/engine.py`, config authority, or runtime files to make the split compile

### Output required

- **Implementation Report**
- **PR evidence template**
- **Opus pre-code verdict before implementation**
- **Opus post-diff verdict before closeout**
