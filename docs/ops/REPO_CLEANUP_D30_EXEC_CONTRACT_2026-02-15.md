# Repo Cleanup D30 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt tio föråldrade 1h-backtestfiler:
  1. `results/backtests/tBTCUSD_1h_20251225_182338.json`
  2. `results/backtests/tBTCUSD_1h_20251225_182533.json`
  3. `results/backtests/tBTCUSD_1h_20251225_182738.json`
  4. `results/backtests/tBTCUSD_1h_20251225_183122.json`
  5. `results/backtests/tBTCUSD_1h_20251225_183205.json`
  6. `results/backtests/tBTCUSD_1h_20251225_183248.json`
  7. `results/backtests/tBTCUSD_1h_20251225_183324.json`
  8. `results/backtests/tBTCUSD_1h_20251225_183417.json`
  9. `results/backtests/tBTCUSD_1h_20251225_183511.json`
  10. `results/backtests/tBTCUSD_1h_20251225_185329.json`
- `docs/ops/REPO_CLEANUP_D30_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D30_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `tmp/**`
- `results/**` (förutom exakt de tio scopeade filerna)

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen deletion utanför de tio scopeade filerna.
- Ingen runtime/API/config-ändring.

## Preconditions

- Explicit requester-intent att fortsätta delete-trancher.
- Scopeade filer är verifierade som existerande före execution.
- Ingen extern referensträff observerad i `results/hparam_search/**` för dessa tio basename-filer.

## Required gates (BEFORE + AFTER)

1. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Exakt tio scopeade backtestfiler raderade.
2. D30 kontrakt + rapport skapade.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Diffen är strikt scopead till 10 raderingar + docs i Scope IN.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D30 i denna tranche är en minimal delete-only execution för nästa kronologiska 1h-batch.
- Vidare destruktiv radering utanför scopead batch är fortsatt föreslagen i separat kontrakt.
