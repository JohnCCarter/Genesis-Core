# Command Packet — Archive Audit Candidate (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — archive refactor can break path contracts if references are missed
- **Required Path:** `Full`
- **Objective:** Complete a smart `scripts/archive/**` audit and apply exactly one high-confidence no-behavior-change candidate action.
- **Candidate:** `scripts/archive/deprecated_2026-02/compare_swing_strategies.py`
- **Base SHA:** `353fa93a2a0d5dfd7ca91a634e722fdce4528ec0`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `scripts/archive/deprecated_2026-02/compare_swing_strategies.py`
  - `docs/audit/refactor/command_packet_archive_audit_shard_a_2026-03-06.md`
  - `tmp/archive_audit_phase*.json` (read-only evidence)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `scripts/paper_trading_runner.py`
  - `scripts/mcp_session_preflight.py`
  - freeze-sensitive/runtime authority paths
- **Expected changed files:**
  - `scripts/archive/deprecated_2026-02/compare_swing_strategies.py`
  - `docs/audit/refactor/command_packet_archive_audit_shard_a_2026-03-06.md`
- **Max files touched:** `3`
- **Hard lock:** one-candidate-per-PR (`compare_swing_strategies`) with explicit evidence of zero external references and no archival policy blocker before action.

### Gates required

- `pre-commit run --all-files`
- `ruff check .`
- `pytest -q`
- smoke selector: `pytest -q tests/test_import_smoke_backtest_optuna.py`
- determinism replay selector: `pytest -q tests/test_backtest_determinism_smoke.py`
- feature cache invariance selector: `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
- pipeline invariant/hash selector: `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Default parity constraints (mandatory)

- No default behavior change.
- No env/config interpretation changes.
- No API contract changes.

### Skill Usage (evidence)

- `repo_clean_refactor` run_id `d7c98a85d7ba` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).
- `python_engineering` run_id `d8859a61e5cf` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).

### Stop Conditions

- Scope drift outside hard lock files.
- Any evidence of external references to archived candidate not accounted for.
- Any behavior change without explicit exception.
- Any required gate failure.

### Output required

- **Implementation Report**
- **PR evidence template**
