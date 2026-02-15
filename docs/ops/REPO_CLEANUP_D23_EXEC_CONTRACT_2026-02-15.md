# Repo Cleanup D23 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt tio föråldrade 1h-backtestfiler:
  1. `results/backtests/tBTCUSD_1h_20251022_153336.json`
  2. `results/backtests/tBTCUSD_1h_20251022_153337.json`
  3. `results/backtests/tBTCUSD_1h_20251022_154020.json`
  4. `results/backtests/tBTCUSD_1h_20251022_154021.json`
  5. `results/backtests/tBTCUSD_1h_20251022_154030.json`
  6. `results/backtests/tBTCUSD_1h_20251022_154822.json`
  7. `results/backtests/tBTCUSD_1h_20251022_154828.json`
  8. `results/backtests/tBTCUSD_1h_20251022_154838.json`
  9. `results/backtests/tBTCUSD_1h_20251022_160630.json`
  10. `results/backtests/tBTCUSD_1h_20251022_160723.json`
- `docs/ops/REPO_CLEANUP_D23_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D23_EXEC_REPORT_2026-02-15.md`
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
- Scopeade filer är nästa äldsta 1h-backtestbatch efter D22.
- Referenser finns i legacy run-artefakter (`results/hparam_search/phase7b_optuna/**`, `results/hparam_search/phase7b_optuna_quick/**`) och noteras som residual risk.

## Required gates (BEFORE + AFTER)

1. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Exakt tio scopeade backtestfiler raderade.
2. D23 kontrakt + rapport skapade.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Diffen är strikt scopead till 10 raderingar + docs i Scope IN.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D23 i denna tranche är en minimal delete-only batch med utökad batchstorlek.
- Vidare destruktiv radering utanför scopead batch är fortsatt föreslagen i separat kontrakt.
