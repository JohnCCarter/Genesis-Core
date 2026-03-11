# Command Packet — Archive Audit Candidate 6 Parity Move (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — script-path structure refactor may break imports if scope drifts
- **Required Path:** `Full`
- **Objective:** Remove archive→active split-brain by moving canonical implementation of parity audit to active script path.
- **Candidate:** `parity_script_canonicalization`
- **Base SHA:** `dd29bb9c8b6f36dc01faf54eda165959a918d3eb`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `scripts/audit/audit_optuna_objective_parity.py`
  - `scripts/archive/deprecated_2026-02/audit_optuna_objective_parity.py`
  - `docs/audit/refactor/command_packet_archive_audit_candidate6_parity_move_2026-03-06.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `tests/**` (read-only)
  - freeze-sensitive/runtime authority paths
- **Expected changed files:**
  - `scripts/audit/audit_optuna_objective_parity.py` (replace wrapper with implementation)
  - `scripts/archive/deprecated_2026-02/audit_optuna_objective_parity.py` (delete)
  - `docs/audit/refactor/command_packet_archive_audit_candidate6_parity_move_2026-03-06.md`
- **Max files touched:** `3`
- **Hard lock:** one-candidate-per-PR (`parity_script_canonicalization`).

### Gates required

- `pre-commit run --all-files`
- `ruff check .`
- `pytest -q`
- smoke selector: `pytest -q tests/test_import_smoke_backtest_optuna.py`
- determinism replay selector: `pytest -q tests/test_backtest_determinism_smoke.py`
- feature cache invariance selector: `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
- pipeline invariant/hash selector: `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- focused selector: `pytest -q tests/test_optimizer_duplicate_fixes.py -k objective_policy_expected_value_soft_constraints_penalty`
- CLI parity smoke: `c:/Users/salib/Desktop/Repos/Genesis-Core/.venv/Scripts/python.exe scripts/audit/audit_optuna_objective_parity.py --help`

### Default parity constraints (mandatory)

- No default behavior change.
- Public callable API from `scripts.audit.audit_optuna_objective_parity` remains available.
- No env/config interpretation changes.
- No default behavior change avser objective-beräkning, exit-koder och publik importyta från `scripts.audit.audit_optuna_objective_parity`.
- Eventuell förändring av deprecation-stderr betraktas som behavior change candidate och undviks i denna kandidat.

### Evidence for candidate safety

- Current active path (`scripts/audit/audit_optuna_objective_parity.py`) is wrapper-only pointing at archive path.
- Archive path currently holds full implementation.
- Tests import helper directly from active path (`tests/test_optimizer_duplicate_fixes.py`).
- Canonicalizing implementation into active path removes split-brain and avoids dependence on archive wrapper.

### Skill Usage (evidence)

- `repo_clean_refactor` run_id `d7c98a85d7ba` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).
- `python_engineering` run_id `d8859a61e5cf` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).

### Stop Conditions

- Scope drift outside hard lock files.
- Any import/test break in `tests/test_optimizer_duplicate_fixes.py` focused selector.
- Any required gate failure.

### Output required

- **Implementation Report**
- **PR evidence template**

### Gate evidence artifacts

- Pre-commit: `docs/audit/refactor/evidence/candidate6_precommit_2026-03-06.txt`
- Ruff: `docs/audit/refactor/evidence/candidate6_ruff_2026-03-06.txt`
- CLI help smoke: `docs/audit/refactor/evidence/candidate6_cli_help_2026-03-06.txt`
- Focused selector: `docs/audit/refactor/evidence/candidate6_focused_selector_2026-03-06.txt`
- Smoke selector: `docs/audit/refactor/evidence/candidate6_smoke_2026-03-06.txt`
- Determinism selector: `docs/audit/refactor/evidence/candidate6_determinism_2026-03-06.txt`
- Feature cache selectors: `docs/audit/refactor/evidence/candidate6_cache_2026-03-06.txt`
- Pipeline selector: `docs/audit/refactor/evidence/candidate6_pipeline_2026-03-06.txt`
- Full pytest: `docs/audit/refactor/evidence/candidate6_pytest_full_2026-03-06.txt`
- Full pytest exit code: `docs/audit/refactor/evidence/candidate6_pytest_exit_2026-03-06.txt`
