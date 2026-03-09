# Command Packet — Candidate 12 Move `diagnose_zero_trades.py` (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Risk:** `MED` — why: script path is `__file__`-sensitive and move can change fallback resolution
- **Required Path:** `Full`
- **Objective:** Move `diagnose_zero_trades.py` to canonical `scripts/analyze/` path while preserving default behavior and updating live skill reference
- **Candidate:** `move_diagnose_zero_trades_to_scripts_analyze`
- **Base SHA:** `65c82bff`

### Scope

- **Scope IN:**
  - `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py` (delete old path)
  - `scripts/analyze/diagnose_zero_trades.py` (new canonical path)
  - `.github/skills/decision_gate_debug.json` (path/reference update only)
  - `docs/audit/refactor/command_packet_candidate12_move_diagnose_zero_trades_2026-03-09.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (read/search only for gates)
  - `mcp_server/**`
  - `.github/workflows/**`
- **Expected changed files:** `4`
- **Max files touched:** `4`

### No-behavior-change containment

- Preserve legacy fallback semantics for exactly two fallback path resolutions in moved script:
  - result backtests fallback
  - hparam_search fallback
- No changes to CLI args, diagnostics logic, thresholds, decision logic, or defaults.

### Skill usage (explicit)

- `repo_clean_refactor` invocation evidence: `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`
- `python_engineering` invocation evidence: `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`
- Skill evidence is supplemental and does not replace mandatory gates.

### Gates required

- `pre-commit run --all-files`
- Smoke test: `python -m py_compile scripts/analyze/diagnose_zero_trades.py`
- Path-parity check: verify both legacy fallback resolutions (`results/backtests` + `results/hparam_search`) remain unchanged after move
- `pytest -q tests/test_backtest_determinism_smoke.py`
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift
- Behavior change without explicit exception
- Hash/determinism regression
- Forbidden paths touched

### Output required

- **Implementation Report**
- **PR evidence template**
