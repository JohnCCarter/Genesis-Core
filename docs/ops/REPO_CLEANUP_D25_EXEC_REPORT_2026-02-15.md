# Repo Cleanup D25 Minimal Delete Execution Report (2026-02-15)

## Syfte

Fortsätta kontrollerad delete-only cleanup med strikt scope, gates och auditspår.

## Genomfört

### Scoped delete-only execution (exakt 10 filer)

1. `results/backtests/tBTCUSD_1h_20251022_164122.json`
2. `results/backtests/tBTCUSD_1h_20251022_164446.json`
3. `results/backtests/tBTCUSD_1h_20251022_164752.json`
4. `results/backtests/tBTCUSD_1h_20251022_165101.json`
5. `results/backtests/tBTCUSD_1h_20251022_165813.json`
6. `results/backtests/tBTCUSD_1h_20251022_170314.json`
7. `results/backtests/tBTCUSD_1h_20251022_170619.json`
8. `results/backtests/tBTCUSD_1h_20251022_170930.json`
9. `results/backtests/tBTCUSD_1h_20251022_171438.json`
10. `results/backtests/tBTCUSD_1h_20251022_171912.json`

## Preconditions

- Explicit requester-intent att fortsätta radera föråldrade resultat.
- Scopeade filer utgör nästa äldsta 1h-batch efter D24.
- Referenser i legacy run-artefakter (`phase7b_grid_simple`, `phase7b_grid_fixed`) identifierades och noterades som residual risk.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D25.
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

- Legacy `results/hparam_search/phase7b_grid_simple/**` och `phase7b_grid_fixed/**` innehåller referenser till raderade backtests; accepterat inom cleanup-scope.

## Status

- D25 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D25-batch: fortsatt föreslagen.
