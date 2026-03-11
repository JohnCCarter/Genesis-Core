# Command Packet — Candidate 11 Delete `archive/debug` subset (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — delete of archived scripts can break hidden path contracts if references are missed
- **Required Path:** `Full`
- **Objective:** Execute a safe, traceable deletion of the `scripts/archive/debug/**` subset with explicit preservation of the referenced debug script.
- **Candidate:** `delete_archive_debug_subset_except_diagnose_zero_trades`
- **Base SHA:** `7b81170f4583cbb6fd7f2a6eb8d0cdac0a8c593e`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - delete targets listed in `docs/audit/refactor/evidence/candidate11_debug_subset_manifest_2026-03-09.txt` (37 files)
  - `docs/audit/refactor/command_packet_candidate11_delete_archive_debug_subset_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate11_debug_subset_manifest_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate11_debug_subset_path_refcheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate11_debug_subset_exact_path_refcheck_2026-03-09.json`
  - `docs/audit/refactor/evidence/candidate11_final_rerun_transcript_2026-03-09.txt` (post-delete artifact)
  - `docs/audit/refactor/debug_subset_delete_signoff_2026-03-09.md` (post-delete artifact)
- **Explicitly preserved path:**
  - `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `tests/**`
  - `.github/workflows/**`
  - runtime/config authority paths
  - non-candidate paths under `scripts/**`
- **Expected changed files:** `43` (37 deletes + 6 docs/evidence files)
- **Max files touched:** `45`
- **Hard lock:** one-candidate-per-PR (`delete_archive_debug_subset_except_diagnose_zero_trades`) with explicit no-active-reference evidence.

### Gates required

- `pre-commit run --all-files`
- `pytest -q tests/test_import_smoke_backtest_optuna.py`
- `pytest -q tests/test_backtest_determinism_smoke.py`
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Default parity constraints (mandatory)

- No default behavior change.
- No env/config interpretation changes.
- No API contract changes.

### Evidence for candidate safety

- Exact delete manifest: `docs/audit/refactor/evidence/candidate11_debug_subset_manifest_2026-03-09.txt`
- Strict path refcheck artifact:
  - `docs/audit/refactor/evidence/candidate11_debug_subset_path_refcheck_2026-03-09.txt`
- Exact per-file path refcheck across active surfaces (`src`, `scripts`, `tests`, `config`, `mcp_server`, `.github/workflows`, `.github/skills`):
  - `target_count = 37`
  - `paths_with_hits = 0`
  - `total_hits = 0`
  - source: `docs/audit/refactor/evidence/candidate11_debug_subset_exact_path_refcheck_2026-03-09.json`
- Exact-path referensscan över repot visar en enda aktiv icke-doc/icke-archive referens till `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py`, i `.github/skills/decision_gate_debug.json` (r. 35, 57). Övriga filer i `scripts/archive/debug/**` saknar aktiva referenser utanför docs/archive-ytor enligt sparade refcheck-artifakter.

### Skill Usage (evidence)

- `repo_clean_refactor` run (`--manifest dev --dry-run`) -> Triggered `OK`, Verified/Result `STOP` (`skill has no executable steps`)
- `python_engineering` run (`--manifest dev --dry-run`) -> Triggered `OK`, Verified/Result `STOP` (`skill has no executable steps`)
- Note: Skill evidence is supplemental and does not replace required test gates.

### Stop Conditions

- Scope drift outside Scope IN.
- Any active reference to target paths outside docs/archive surfaces.
- Any behavior change without explicit exception.
- Any required gate failure.

### Output required

- **Implementation Report**
- **PR evidence template**
