# Candidate 8 Signoff — Delete `scripts/archive/deprecated_2026-02` subset (2026-03-06)

Mode: RESEARCH (source=branch mapping `feature/*`)
Candidate: `delete_archive_deprecated_2026_02_subset`

## Scope summary

- Deleted exactly 5 files:
  - `scripts/archive/deprecated_2026-02/diagnose_optuna_issues.py`
  - `scripts/archive/deprecated_2026-02/diagnose_zero_trades.py`
  - `scripts/archive/deprecated_2026-02/freeze_data.py`
  - `scripts/archive/deprecated_2026-02/sweep_optuna_holdout_top_trials.py`
  - `scripts/archive/deprecated_2026-02/sync_precompute_and_train.py`
- Added/updated candidate evidence/contract files:
-  - `docs/audit/refactor/candidates/command_packet_candidate8_delete_deprecated_2026_02_subset_2026-03-06.md`
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_manifest_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_path_refcheck_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_exact_path_refcheck_2026-03-06.json`
-  - `docs/audit/refactor/candidates/deprecated_2026_02_subset_delete_signoff_2026-03-06.md`
- Required pre-commit EOF hook also normalized:
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_path_refcheck_2026-03-06.txt`

## Reference safety evidence

- Manifest size: 5 targets (`candidate8_deprecated_2026_02_manifest_2026-03-06.txt`).
- Exact per-file path refcheck across active surfaces (`src`, `scripts`, `tests`, `config`, `mcp_server`, `.github/workflows`):
  - `target_count = 5`
  - `paths_with_hits = 0`
  - `total_hits = 0`
  - source: `candidate8_deprecated_2026_02_exact_path_refcheck_2026-03-06.json`
- Supplementary exact per-file path refcheck across `.github/skills`:
  - `target_count = 5`
  - `paths_with_hits = 0`
  - `total_hits = 0`
  - source: `candidate8_deprecated_2026_02_github_skills_refcheck_2026-03-06.json`
- Strict path refcheck artifact:
  - `candidate8_deprecated_2026_02_path_refcheck_2026-03-06.txt`
- Manifest parity check:
  - `remaining_files = 0`

## Skill evidence (governance supplement)

- `repo_clean_refactor` run_id `d7c98a85d7ba`: Triggered=`OK`, Verified/Result=`STOP` (`no_steps`).
- `python_engineering` run_id `d8859a61e5cf`: Triggered=`OK`, Verified/Result=`STOP` (`no_steps`).
- These invocations are supplemental evidence and not test gate replacements.

## Gates

### Pre-change gates

- `pre-commit run --all-files` -> initial FAIL (`end-of-file-fixer`), auto-fixed `candidate7_test_prototypes_path_refcheck_2026-03-06.txt`; re-run -> PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS

### Post-change gates

- `pre-commit run --all-files` -> PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS

### Final rerun before push

- `pre-commit run --all-files` -> PASS
- `pytest -q` selector bundle (smoke + determinism + feature cache + pipeline invariant) -> PASS (`11 passed`)

## No-behavior-change assertion

- No runtime/config/API paths changed.
- No env/config interpretation changes.
- Change is constrained to archive cleanup + governance evidence artifacts.
- Exact-path refcheck was executed over `src/`, `scripts/`, `tests/`, `config/`, `mcp_server/`, `.github/workflows/`, and `.github/skills/`.
- No hits were found for the 5 deleted paths in that scope.
