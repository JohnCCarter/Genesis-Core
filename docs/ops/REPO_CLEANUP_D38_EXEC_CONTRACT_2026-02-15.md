# Repo Cleanup D38 Minimal Move Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Move-only execution av exakt 2 root-DB artefakter:
  - `optimizer_phase7b.db` -> `results/hparam_search/storage/optimizer_phase7b.db`
  - `optuna_search.db` -> `results/hparam_search/storage/optuna_search.db`
- `docs/ops/REPO_CLEANUP_D38_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D38_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `tmp/**`
- `data/**`
- alla övriga paths

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen move/delete utanför exakt de 2 scopeade DB-filerna.
- Ingen runtime/API/config-ändring.

## Preconditions

- Explicit requester-intent att köra rekommenderade nästa steg.
- Tracked workspace clean verifierad före execution.
- Scope verifierad före execution: båda source-filer finns och destination saknas.
- Storlek/hash loggad i `tmp/d38_pre_hashes.txt`.
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

1. Exakt 2 source-filer saknas i root och finns i destination.
2. Hashparitet source -> destination verifierad.
3. D38 kontrakt + rapport skapade.
4. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
5. Diffen är strikt scopead till Scope IN-paths.
6. Required gates passerar efter ändring.
7. Opus post-code diff-audit är `APPROVED`.

## Status

- D38 i denna tranche är en minimal move-only execution för att flytta två root-DB
  artefakter till avsedd storage-path.
- Vidare cleanup utanför D38-scope är fortsatt föreslagen i separat kontrakt.
