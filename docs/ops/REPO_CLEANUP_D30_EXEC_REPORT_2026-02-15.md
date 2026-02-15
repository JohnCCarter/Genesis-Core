# Repo Cleanup D30 Minimal Delete Execution Report (2026-02-15)

## Syfte

Fortsätta kontrollerad delete-only cleanup för nästa kronologiska 1h-batch med strikt scope, gates och auditspår.

## Genomfört

### Scoped delete-only execution (exakt 10 filer)

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

## Preconditions

- Explicit requester-intent att fortsätta radera föråldrade resultat.
- Scopeade filer verifierade som existerande före execution.
- Ingen extern referensträff observerad i `results/hparam_search/**` för dessa tio basename-filer.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D30.
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

- Ingen extern referensdrift observerad för denna batch inom `results/hparam_search/**` vid genomförandet.

## Status

- D30 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D30-batch: fortsatt föreslagen.
