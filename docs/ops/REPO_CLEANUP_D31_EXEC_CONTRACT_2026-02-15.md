# Repo Cleanup D31 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt en run-dir:
  - `results/hparam_search/run_20251226_173828/**`
- `docs/ops/REPO_CLEANUP_D31_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D31_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `tmp/**`
- `results/**` (förutom exakt `results/hparam_search/run_20251226_173828/**`)

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen deletion utanför den scopeade run-dir:en.
- Ingen runtime/API/config-ändring.

## Preconditions

- Explicit requester-intent att fortsätta cleanup i ~250MB-trancher under `results/hparam_search/**`.
- Scopead målkatalog verifierad före execution: `run_20251226_173828`.
- Uppmätt storlek före execution: `255.15 MB` (`1688` filer, `267543507` bytes).
- Opus pre-code review: `APPROVED`.

## Required gates (BEFORE + AFTER)

1. `git status --porcelain` är tom (BEFORE)
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`

## Done criteria

1. Exakt en scopead run-dir raderad: `results/hparam_search/run_20251226_173828/**`.
2. Delete-utfall verifierat: inga extra run-dir-raderingar utöver scope.
3. D31 kontrakt + rapport skapade.
4. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
5. Diffen är strikt scopead till docs i Scope IN.
6. Required gates passerar efter ändring.
7. Opus post-code diff-audit är `APPROVED`.

## Status

- D31 i denna tranche är en minimal delete-only execution för en ~250MB hparam-search-batch.
- Vidare destruktiv radering utanför D31-scope är fortsatt föreslagen i separat kontrakt.
