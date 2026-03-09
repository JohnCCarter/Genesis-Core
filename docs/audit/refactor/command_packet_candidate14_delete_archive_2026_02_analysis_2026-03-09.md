# Command Packet — Candidate 14 Delete `archive/2026-02/analysis` subset (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — large archive delete set could hide stale path dependencies
- **Required Path:** `Full`
- **Objective:** Execute safe, traceable deletion of `scripts/archive/2026-02/analysis/*.py` after exact-path reference verification.
- **Candidate:** `delete_archive_2026_02_analysis_subset`
- **Base SHA:** `c31bc3d9`

### Scope

- **Scope IN:**
  - delete targets listed in `docs/audit/refactor/evidence/candidate14_archive_2026_02_analysis_manifest_2026-03-09.txt` (109 files)
  - `docs/audit/refactor/command_packet_candidate14_delete_archive_2026_02_analysis_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate14_archive_2026_02_analysis_manifest_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate14_archive_2026_02_analysis_path_refcheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate14_archive_2026_02_analysis_exact_path_refcheck_2026-03-09.json`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - non-candidate paths under `scripts/**`
- **Expected changed files:** `114`
- **Max files touched:** `116`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Ändringen är begränsad till docs/evidence + radering av arkiverade analys-skript under `scripts/archive/2026-02/analysis/`.
Inga ändringar i `src/**`, `config/**`, `tests/**` (förutom exekvering), `mcp_server/**`, `.github/workflows/**`.

### Evidence for candidate safety

- Manifest: `docs/audit/refactor/evidence/candidate14_archive_2026_02_analysis_manifest_2026-03-09.txt`
- Exact-path refcheck JSON: `docs/audit/refactor/evidence/candidate14_archive_2026_02_analysis_exact_path_refcheck_2026-03-09.json`
- Refcheck TXT summary: `docs/audit/refactor/evidence/candidate14_archive_2026_02_analysis_path_refcheck_2026-03-09.txt`
- Scope-drift proof: `docs/audit/refactor/evidence/candidate14_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate14_gate_transcript_2026-03-09.txt`

### Skill usage (explicit)

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`
- Evidence: `docs/audit/refactor/evidence/candidate14_skill_invocations_2026-03-09.txt`

### Gates required

- `pre-commit run --all-files`
- `pytest -q tests/test_import_smoke_backtest_optuna.py`
- `pytest -q tests/test_backtest_determinism_smoke.py`
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift
- Behavior change without explicit exception
- Determinism/cache/pipeline invariant regression
- Forbidden paths touched

### Output required

- **Implementation Report**
- **PR evidence template**
