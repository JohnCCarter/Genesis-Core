# Repo Cleanup D37 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt 5 datafiler:
  - `data/raw/bitfinex/candles/tBTCUSD_1D_2025-10-11.parquet`
  - `data/raw/bitfinex/candles/tBTCUSD_1D_2025-10-27.parquet`
  - `data/raw/bitfinex/candles/tBTCUSD_1h_2025-10-11.parquet`
  - `data/raw/bitfinex/candles/tBTCUSD_3h_2025-10-11.parquet`
  - `data/raw/bitfinex/candles/tBTCUSD_6h_2025-10-11.parquet`
- `docs/ops/REPO_CLEANUP_D37_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D37_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `tmp/**`
- `results/**`
- alla övriga paths

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen deletion utanför exakt de 5 scopeade datafilerna.
- Ingen runtime/API/config-ändring.

## Preconditions

- Explicit requester-intent att köra rekommenderade nästa steg.
- Tracked workspace clean verifierad före execution.
- Scope verifierad före execution: exakt 5 filer existerar.
- Uppmätt batchstorlek: `763748` bytes (~745.85 KB).
- Opus pre-code review: `APPROVED`.

## Required gates (BEFORE + AFTER)

1. Tracked workspace clean verifierad före execution.
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
7. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`

## Done criteria

1. Exakt 5 scopeade datafiler raderade.
2. Delete-utfall verifierat: inga out-of-scope-raderingar.
3. D37 kontrakt + rapport skapade.
4. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
5. Diffen är strikt scopead till Scope IN-paths.
6. Required gates passerar efter ändring.
7. Opus post-code diff-audit är `APPROVED`.

## Status

- D37 i denna tranche är en minimal delete-only execution av scopeade oktoberfiler
  i `data/raw/bitfinex/candles`.
- Vidare data- eller kodstädning utanför D37-scope är fortsatt föreslagen i
  separat kontrakt.
