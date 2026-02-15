# Repo Cleanup D24 Minimal Delete Execution Report (2026-02-15)

## Syfte

Fortsätta kontrollerad delete-only cleanup med strikt scope, gates och auditspår.

## Genomfört

### Scoped delete-only execution (exakt 10 filer)

1. `results/backtests/tBTCUSD_1h_20251022_160814.json`
2. `results/backtests/tBTCUSD_1h_20251022_161401.json`
3. `results/backtests/tBTCUSD_1h_20251022_161453.json`
4. `results/backtests/tBTCUSD_1h_20251022_161544.json`
5. `results/backtests/tBTCUSD_1h_20251022_161901.json`
6. `results/backtests/tBTCUSD_1h_20251022_161954.json`
7. `results/backtests/tBTCUSD_1h_20251022_162052.json`
8. `results/backtests/tBTCUSD_1h_20251022_162200.json`
9. `results/backtests/tBTCUSD_1h_20251022_162250.json`
10. `results/backtests/tBTCUSD_1h_20251022_162341.json`

## Preconditions

- Explicit requester-intent att fortsätta radera föråldrade resultat.
- Scopeade filer utgör nästa äldsta 1h-batch efter D23.
- Referenser i legacy run-artefakter (`phase7b_optuna_quick`, `phase7b_grid_baseline`, `phase7b_grid_ultra_low`) identifierades och noterades som residual risk.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D24.
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

- Legacy `results/hparam_search/phase7b_optuna_quick/**`, `phase7b_grid_baseline/**` och `phase7b_grid_ultra_low/**` innehåller referenser till raderade backtests; accepterat inom cleanup-scope.

## Status

- D24 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D24-batch: fortsatt föreslagen.
