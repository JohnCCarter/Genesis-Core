# Repo Cleanup D22 Minimal Delete Execution Report (2026-02-15)

## Syfte

Fortsätta kontrollerad destruktiv cleanup av föråldrade resultat med minimal, reviewbar batch.

## Genomfört

### Scoped delete-only execution (exakt 3 filer)

1. `results/backtests/tBTCUSD_1h_20251022_152515.json`
2. `results/backtests/tBTCUSD_1h_20251022_152517.json`
3. `results/backtests/tBTCUSD_1h_20251022_152519.json`

## Preconditions

- Explicit requester-intent att fortsätta radera föråldrade resultat.
- Scopeade filer utgör den äldsta 1h-trion i `results/backtests`.
- Basename-referenser i legacy run-artefakter (`phase7b_optuna`) noterades som residual risk före execution.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D22.
- Inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `tmp/**`.
- Ingen deletion utanför de tre scopeade filerna.

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

- Legacy `phase7b_optuna`-artefakter innehåller basename-referenser till raderade backtests; accepterat inom cleanup-scope.

## Status

- D22 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D22-batch: fortsatt föreslagen.
