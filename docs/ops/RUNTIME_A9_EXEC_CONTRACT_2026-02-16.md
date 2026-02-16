# Runtime A9 Execution Contract (2026-02-16)

## Category

`api`

## Scope IN

- `src/core/server.py` (endast `/strategy/evaluate`-validering)
- `tests/test_ui_endpoints.py` (evaluate-regressioner)
- `docs/ops/RUNTIME_A9_EXEC_CONTRACT_2026-02-16.md`
- `docs/ops/RUNTIME_A9_EXEC_REPORT_2026-02-16.md`

## Scope OUT

- `.github/**`
- `src/core/strategy/**`
- `src/core/backtest/**`
- `src/core/optimizer/**`
- `scripts/**`
- `config/**`
- `data/**`
- `results/**`
- `tmp/**`
- alla övriga paths

## Constraints

Default: `NO BEHAVIOR CHANGE`

Explicit undantag för A9:

- Ta bort dummy-data fallback i `/strategy/evaluate`.
- Behåll HTTP-status `200`.
- Behåll happy-path shape (`result`, `meta`) för giltig payload.
- Returnera explicit `INVALID_CANDLES` vid saknad/ogiltig candles.

## Preconditions

- Explicit requester-intent att fortsätta enligt governance.
- Opus pre-code review: `APPROVED`.
- Tranche är exekverad och verifierad i commit `51e11ff`.

## Required gates (BEFORE + AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
6. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
7. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post`
8. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_ui_endpoints.py -k "evaluate"`

## Done criteria

1. Ingen dummy-fallback kvar i `/strategy/evaluate`.
2. Missing/empty/invalid candles ger explicit `INVALID_CANDLES` med HTTP 200.
3. Diff i exekveringscommit är strikt till server + testfil.
4. Before/After-gates är passerade.
5. Opus post-code audit: `APPROVED`.

## Status

- A9 execution: `införd` (retrospektivt dokumenterad via commit `51e11ff`).
- Denna fil är ops-backfill i full governance-stil.
