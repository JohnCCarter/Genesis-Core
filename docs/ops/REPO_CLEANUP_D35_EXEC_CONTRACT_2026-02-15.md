# Repo Cleanup D35 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt 1 run-dir:
  - `results/hparam_search/run_20251227_173827/**`
- `docs/ops/REPO_CLEANUP_D35_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D35_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `tmp/**`
- `results/**` (förutom exakt den scopeade run-dir ovan)

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen deletion utanför exakt 1 scopead run-dir.
- Ingen runtime/API/config-ändring.

## Preconditions

- Explicit requester-intent att fortsätta nästa tranche.
- Scope verifierad före execution: `run_20251227_173827/**`.
- Uppmätt batchstorlek: `13.32 MB` (`13964930` bytes) över `63` filer.
- Opus pre-code review: `APPROVED`.

## Required gates (BEFORE + AFTER)

1. Tracked workspace clean verifierad före execution.
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
7. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`

## Done criteria

1. Exakt 1 scopead run-dir raderad: `run_20251227_173827/**`.
2. Delete-utfall verifierat: inga out-of-scope-raderingar.
3. D35 kontrakt + rapport skapade.
4. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
5. Diffen är strikt scopead till Scope IN-paths.
6. Required gates passerar efter ändring.
7. Opus post-code diff-audit är `APPROVED`.

## Status

- D35 i denna tranche är en minimal delete-only execution för nästa kvarvarande
  `hparam_search`-run-dir.
- Vidare destruktiv radering utanför D35-scope är fortsatt föreslagen i separat
  kontrakt.
