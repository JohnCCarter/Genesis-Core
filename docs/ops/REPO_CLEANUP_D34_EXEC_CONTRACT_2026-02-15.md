# Repo Cleanup D34 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt 23 filer i:
  - `results/hparam_search/run_20251227_180204/tBTCUSD_1h_63.json`
  - ...
  - `results/hparam_search/run_20251227_180204/tBTCUSD_1h_85.json`
- `docs/ops/REPO_CLEANUP_D34_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D34_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `tmp/**`
- `results/**` (förutom exakt de 23 scopeade filerna ovan)

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen deletion utanför exakt de 23 scopeade filerna.
- Ingen runtime/API/config-ändring.

## Preconditions

- Explicit requester-intent att fortsätta D32, D33 osv.
- Scope verifierad före execution: 23 filer (`tBTCUSD_1h_63..85.json`).
- Uppmätt batchstorlek: `187.61 MB` (`196725669` bytes).
- Opus pre-code review: `APPROVED`.

## Required gates (BEFORE + AFTER)

1. `git status --porcelain` tom (BEFORE)
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
7. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`

## Done criteria

1. Exakt 23 scopeade filer raderade: `tBTCUSD_1h_63..85.json`.
2. Delete-utfall verifierat: inga out-of-scope-raderingar i run-katalogen.
3. D34 kontrakt + rapport skapade.
4. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
5. Diffen är strikt scopead till docs i Scope IN.
6. Required gates passerar efter ändring.
7. Opus post-code diff-audit är `APPROVED`.

## Status

- D34 i denna tranche är en minimal delete-only tail-tranche för resterande målrange i `run_20251227_180204`.
- Vidare destruktiv radering utanför D34-scope är fortsatt föreslagen i separat kontrakt.
