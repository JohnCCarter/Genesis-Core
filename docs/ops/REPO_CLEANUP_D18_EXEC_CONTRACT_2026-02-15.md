# Repo Cleanup D18 Minimal Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Move-only execution av exakt tre filer:
  1. `results/hparam_search/run_20251227_180204/trial_030.log`
  2. `results/hparam_search/run_20251227_180204/trial_031.log`
  3. `results/hparam_search/run_20251227_180204/trial_032.log`
- Målvägar (mirror under orphaned archive):
  1. `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_030.log`
  2. `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_031.log`
  3. `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_032.log`
- Carry-forward (newline-only):
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_027.log`
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_028.log`
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_029.log`
  - `docs/ops/REPO_CLEANUP_D17_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D17_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D18_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D18_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `results/**` (förutom exakt de tre scopeade källfilerna)
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen execution utanför de tre scopeade filerna.
- Destinationer måste vara frånvarande före move (no-overwrite precondition).
- Carry-forward är strikt newline-only (ingen innehållsändring).
- Ingen runtime/API/config-ändring.

## Preconditions

- Exakta fullpath-referenser för scopeade source paths saknas.
- Basename-referenser finns i run-artefakter och accepteras som residual risk:
  - `results/hparam_search/run_20251227_180204/trial_030.json:113`
  - `results/hparam_search/run_20251227_180204/trial_031.json:113`
  - `results/hparam_search/run_20251227_180204/trial_032.json:113`
  - `results/hparam_search/run_20251227_180204/_cache/*.json:14`

## Required gates (BEFORE + AFTER)

1. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Exakt tre nya scopeade filer flyttade till `archive/_orphaned/results/**`.
2. D18 kontrakt + rapport skapade.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Diffen är strikt scopead till 3 flyttar + docs i Scope IN.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D18 i denna tranche är en minimal execution-batch med explicit noterad basename-residual risk.
- Vidare execution utanför scopead batch är fortsatt föreslagen i separat kontrakt.
