# Repo Cleanup D29 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt tio föråldrade 1h-backtestfiler:
  1. `results/backtests/tBTCUSD_1h_20251225_180629.json`
  2. `results/backtests/tBTCUSD_1h_20251225_180712.json`
  3. `results/backtests/tBTCUSD_1h_20251225_180837.json`
  4. `results/backtests/tBTCUSD_1h_20251225_180924.json`
  5. `results/backtests/tBTCUSD_1h_20251225_181038.json`
  6. `results/backtests/tBTCUSD_1h_20251225_181117.json`
  7. `results/backtests/tBTCUSD_1h_20251225_181157.json`
  8. `results/backtests/tBTCUSD_1h_20251225_181815.json`
  9. `results/backtests/tBTCUSD_1h_20251225_182014.json`
  10. `results/backtests/tBTCUSD_1h_20251225_182253.json`
- `docs/ops/REPO_CLEANUP_D29_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D29_EXEC_REPORT_2026-02-15.md`
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
2. D29 kontrakt + rapport skapade.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Diffen är strikt scopead till 10 raderingar + docs i Scope IN.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D29 i denna tranche är en minimal delete-only execution för nästa kronologiska 1h-batch.
- Vidare destruktiv radering utanför scopead batch är fortsatt föreslagen i separat kontrakt.
