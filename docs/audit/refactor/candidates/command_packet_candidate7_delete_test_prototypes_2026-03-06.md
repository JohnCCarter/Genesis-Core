# Command Packet — Candidate 7 Delete `archive/test_prototypes` (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — delete of historical scripts can break hidden path contracts if references are missed
- **Required Path:** `Full`
- **Objective:** Execute a safe, traceable deletion of `scripts/archive/test_prototypes/**` as one-candidate removal with evidence and full gates.
- **Candidate:** `delete_archive_test_prototypes`
- **Base SHA:** `0b537b4d3b73219c13351162572ecb9347097869`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - All 36 Python files listed in:
    - `docs/audit/refactor/evidence/candidate7_test_prototypes_manifest_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_manifest_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_refcheck_2026-03-06.json`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_path_refcheck_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_exact_path_refcheck_2026-03-06.json`
  - `docs/audit/refactor/command_packet_candidate7_delete_test_prototypes_2026-03-06.md`
  - `docs/audit/refactor/test_prototypes_delete_signoff_2026-03-06.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `.github/workflows/**`
  - all non-target script paths under `scripts/**`
- **Expected changed files:** `42` (36 deletes + 6 docs/evidence files)
- **Max files touched:** `43`
- **Hard lock:** one-candidate-per-PR (`delete_archive_test_prototypes`) with explicit no-active-reference evidence.

### Gates required

- `pre-commit run --all-files`
- smoke selector: `pytest -q tests/test_import_smoke_backtest_optuna.py`
- determinism selector: `pytest -q tests/test_backtest_determinism_smoke.py`
- feature cache selectors: `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
- pipeline invariant selector: `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Default parity constraints (mandatory)

- No default behavior change.
- No env/config interpretation changes.
- No API contract changes.

### Evidence for candidate safety

- Exact delete manifest: `docs/audit/refactor/evidence/candidate7_test_prototypes_manifest_2026-03-06.txt`
- Strict folder path refcheck outside docs/archive is empty:
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_path_refcheck_2026-03-06.txt`
- Exact per-file path refcheck outside docs/archive:
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_exact_path_refcheck_2026-03-06.json`
- Basename sweep reports 2 hits in package metadata (`src/genesis_core.egg-info/SOURCES.txt`) for
  `tests/test_exit_fibonacci.py` and `tests/test_htf_exit_engine.py`; these are not archive path
  references and do not indicate runtime dependency on `scripts/archive/test_prototypes/**`.

### Skill Usage (evidence)

- `repo_clean_refactor` run_id `d7c98a85d7ba` (manifest `dev`, Triggered=`OK`, Verified/Result=`STOP` reason `no_steps`).
- `python_engineering` run_id `d8859a61e5cf` (manifest `dev`, Triggered=`OK`, Verified/Result=`STOP` reason `no_steps`).
- Note: These are governance-evidence invocations and **not** substitutes for required test gates.

### Stop Conditions

- Scope drift outside Scope IN.
- Any active reference to target paths outside docs/archive surfaces.
- Any behavior change without explicit exception.
- Any required gate failure.

### Output required

- **Implementation Report**
- **PR evidence template**
