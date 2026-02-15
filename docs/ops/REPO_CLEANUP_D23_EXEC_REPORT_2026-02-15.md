# Repo Cleanup D23 Minimal Delete Execution Report (2026-02-15)

## Syfte

Öka städtempot med en större men fortfarande strikt reviewbar delete-only batch.

## Genomfört

### Scoped delete-only execution (exakt 10 filer)

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

## Preconditions

- Explicit requester-intent att fortsätta radera föråldrade resultat.
- Scopeade filer utgör nästa äldsta 1h-batch efter D22.
- Referenser i legacy run-artefakter (`phase7b_optuna`, `phase7b_optuna_quick`) identifierades och noterades som residual risk.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D23.
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

- Legacy `results/hparam_search/phase7b_optuna/**` och `phase7b_optuna_quick/**` innehåller referenser till raderade backtests; accepterat inom cleanup-scope.

## Status

- D23 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D23-batch: fortsatt föreslagen.
