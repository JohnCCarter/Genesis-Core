# Repo Cleanup D27 Minimal Delete Execution Report (2026-02-15)

## Syfte

Fortsätta kontrollerad delete-only cleanup för nästa kronologiska 1h-batch med strikt scope, gates och auditspår.

## Genomfört

### Scoped delete-only execution (exakt 10 filer)

1. `results/backtests/tBTCUSD_1h_20251026_205559.json`
2. `results/backtests/tBTCUSD_1h_20251026_210913.json`
3. `results/backtests/tBTCUSD_1h_20251026_212223.json`
4. `results/backtests/tBTCUSD_1h_20251026_213537.json`
5. `results/backtests/tBTCUSD_1h_20251026_214848.json`
6. `results/backtests/tBTCUSD_1h_20251026_220156.json`
7. `results/backtests/tBTCUSD_1h_20251026_221503.json`
8. `results/backtests/tBTCUSD_1h_20251026_222814.json`
9. `results/backtests/tBTCUSD_1h_20251027_155000.json`
10. `results/backtests/tBTCUSD_1h_20251027_230343.json`

## Preconditions

- Explicit requester-intent att fortsätta radera föråldrade resultat.
- Scopeade filer verifierade som existerande före execution.
- Referenser i legacy run-artefakter (`run_20251026_194233` med `trial_*.json`, `trial_*.log`, `_cache/*.json`) identifierades och noterades som residual risk.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D27.
- Inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `tmp/**`.
- Ingen deletion utanför de tio scopeade filerna.

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_pipeline_fast_hash_guard.py -q`

Gate-status:

- Before-gates: pass
- After-gates: pass

## Residual risk

- Legacy `results/hparam_search/run_20251026_194233/**` innehåller referenser till raderade backtests; accepterat inom cleanup-scope.

## Status

- D27 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D27-batch: fortsatt föreslagen.
