# Command Packet — Archive Audit Candidate 4 Batch B (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — archive removals can break path contracts if references are missed
- **Required Path:** `Full`
- **Objective:** Apply one atomic no-behavior-change batch candidate (3 wrapper-only archive files).
- **Candidate:** `deprecated_wrapper_batch_B` (3 files)
- **Base SHA:** `6bf2188383bf2807851368350be1de608b098d09`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `scripts/archive/deprecated_2026-02/diagnose_feature_parity.py`
  - `scripts/archive/deprecated_2026-02/diagnose_fib_flow.py`
  - `scripts/archive/deprecated_2026-02/diagnose_ml_probas.py`
  - `docs/audit/refactor/command_packet_archive_audit_candidate4_batchB_2026-03-06.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `scripts/paper_trading_runner.py`
  - `scripts/mcp_session_preflight.py`
  - freeze-sensitive/runtime authority paths
- **Expected changed files:**
  - `scripts/archive/deprecated_2026-02/diagnose_feature_parity.py`
  - `scripts/archive/deprecated_2026-02/diagnose_fib_flow.py`
  - `scripts/archive/deprecated_2026-02/diagnose_ml_probas.py`
  - `docs/audit/refactor/command_packet_archive_audit_candidate4_batchB_2026-03-06.md`
- **Max files touched:** `4`
- **Hard lock:** one-candidate-per-PR (`deprecated_wrapper_batch_B`) with explicit no-active-reference evidence before action.

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

### Evidence for candidate safety

- All three files are wrapper-only (deprecated print + deprecated usage log + `runpy` handoff attempt) and located in deprecated archive surface.
- Target files exist:
  - `scripts/archive/debug/2026-02-14/diagnose_feature_parity.py`
  - `scripts/archive/debug/2026-02-14/diagnose_fib_flow.py`
  - `scripts/archive/debug/2026-02-14/diagnose_ml_probas.py`
- Active reference check:
  - `git grep -n -E "diagnose_feature_parity\.py|diagnose_fib_flow\.py|diagnose_ml_probas\.py" -- . ":(exclude)scripts/archive/**" ":(exclude)docs/archive/**"` returned no hits.
- Remaining references (if any) are historical in `docs/archive/**` only.

### Skill Usage (evidence)

- `repo_clean_refactor` run_id `d7c98a85d7ba` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).
- `python_engineering` run_id `d8859a61e5cf` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).

### Stop Conditions

- Scope drift outside hard lock files.
- Any active reference evidence outside archive/docs-archive.
- Any behavior change without explicit exception.
- Any required gate failure.

### Output required

- **Implementation Report**
- **PR evidence template**
