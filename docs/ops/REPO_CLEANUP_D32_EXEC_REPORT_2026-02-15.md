# Repo Cleanup D32 Minimal Delete Execution Report (2026-02-15)

## Syfte

Fortsätta kontrollerad delete-only cleanup i `results/hparam_search/**` i ~250MB-trancher.

## Genomfört

### Scoped delete-only execution (exakt 31 filer)

- `results/hparam_search/run_20251227_180204/tBTCUSD_1h_1.json`
- ...
- `results/hparam_search/run_20251227_180204/tBTCUSD_1h_31.json`

Verifierad före/efter på filesystem:

- Före: `305` filer i run-katalogen
- Efter: `274` filer i run-katalogen
- Borttagen mängd: exakt `31` filer
- Storlek borttagen: `250.30 MB` (`262453996` bytes)
- Out-of-scope-raderingar: `0`

## Preconditions

- Explicit requester-intent: fortsätt med D32, D33 osv.
- Scopead batch verifierad som existerande före execution.
- Opus pre-code review: `APPROVED`.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D32.
- Inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `tmp/**`.
- Ingen deletion utanför de 31 scopeade filerna.

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `git status --porcelain` tom före execution
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
7. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`

Gate-status:

- Before-gates: pass
- After-gates: pass

## Residual risk

- Målrun-katalogen innehåller fortsatt stora artefakter; fler trancher krävs för fortsatt volymreduktion.

## Status

- D32 minimal delete execution tranche: införd.
- Vidare destruktiv radering utanför scopead D32-batch: fortsatt föreslagen.
