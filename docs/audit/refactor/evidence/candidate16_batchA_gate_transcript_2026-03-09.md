# Candidate16 Batch A — Gate Transcript (2026-03-09)

## Execution summary

- Branch: `feature/archive-mixed-assets-curation`
- Batch executed: **A (static historical assets)**
- Operation type: `git mv` only (rename/move, no content edits)
- Moved files (staged renames): **52**

## Pre-gates (before Batch A move)

1. `python -m pre_commit run --all-files` → **PASS**
2. `python -m pytest -q tests/test_backtest_determinism_smoke.py` → **PASS**
3. `python -m pytest -q tests/test_feature_cache.py` → **PASS**
4. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → **PASS**
5. `python scripts/run/run_backtest.py --help` → **PASS**

## Move execution

- Source of truth: `docs/audit/refactor/evidence/candidate16_exact_old_new_manifest_2026-03-09.tsv`
- Applied rows with `batch=A`: **52**
- Result: all `batch=A` rows moved successfully (`BATCH_A_MOVED=52`)

## Post-gates (after Batch A move)

1. `python -m pre_commit run --all-files` → **PASS**
2. `python -m pytest -q tests/test_backtest_determinism_smoke.py` → **PASS**
3. `python -m pytest -q tests/test_feature_cache.py` → **PASS**
4. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → **PASS**
5. `python scripts/run/run_backtest.py --help` → **PASS**

## Skill invocation evidence (packet requirement)

1. `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`
   - Output: `[SKILL] STOP: skill has no executable steps`
   - Exit code: `1` (expected for non-executable SPEC skill)
2. `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`
   - Output: `[SKILL] STOP: skill has no executable steps`
   - Exit code: `1` (expected for non-executable SPEC skill)

## Scope check

- In-scope paths moved:
  - `archive/2025-11-03/config_models/**`
  - `archive/2025-11-03/models_trimmed/**`
  - `archive/2025-11-03/optimizer_configs/**`
  - `archive/2025-11-03/docs/**`
  - `archive/model_optimization/1d_optimized_configs.json`
- Out-of-scope runtime paths modified: **none**
- Archive `.py` content edits: **none**
