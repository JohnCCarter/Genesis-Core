# Repo Cleanup D26 Minimal Delete Execution Report (2026-02-15)

## Syfte

Slutföra kontrollerad delete-only cleanup för sista kvarvarande `20251022`-batchen med strikt scope, gates och auditspår.

## Genomfört

### Scoped delete-only execution (exakt 7 filer)

1. `results/backtests/tBTCUSD_1h_20251022_172222.json`
2. `results/backtests/tBTCUSD_1h_20251022_172529.json`
3. `results/backtests/tBTCUSD_1h_20251022_172854.json`
4. `results/backtests/tBTCUSD_1h_20251022_175346.json`
5. `results/backtests/tBTCUSD_1h_20251022_175710.json`
6. `results/backtests/tBTCUSD_1h_20251022_180017.json`
7. `results/backtests/tBTCUSD_1h_20251022_180346.json`

## Preconditions

- Explicit requester-intent att fortsätta radera föråldrade resultat.
- Scopeade filer utgjorde sista kvarvarande 1h-batchen för `20251022`.
- Referenser i legacy run-artefakter (`phase7b_grid_simple`, `phase7b_grid_fixed`, `phase7b_grid_final_test`) identifierades och noterades som residual risk.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D26.
- Inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `tmp/**`.
- Ingen deletion utanför de sju scopeade filerna.

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

- Legacy `results/hparam_search/phase7b_grid_simple/**`, `phase7b_grid_fixed/**` och `phase7b_grid_final_test/**` innehåller referenser till raderade backtests; accepterat inom cleanup-scope.

## Status

- D26 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D26-batch: fortsatt föreslagen.
