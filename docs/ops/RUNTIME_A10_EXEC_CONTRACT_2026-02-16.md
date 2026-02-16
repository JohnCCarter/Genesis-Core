# Runtime A10 Execution Contract (2026-02-16)

## Category

`api`

## Scope IN

- `src/core/server.py` (endast `/paper/submit` symbolvalidering)
- `tests/test_ui_endpoints.py` (paper_submit-regressioner)
- `docs/ops/RUNTIME_A10_EXEC_CONTRACT_2026-02-16.md`
- `docs/ops/RUNTIME_A10_EXEC_REPORT_2026-02-16.md`

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

Explicit undantag för A10:

- Ta bort tyst symbol-substitution i `/paper/submit`.
- Behåll HTTP-status `200`.
- Behåll whitelistad happy-path oförändrad.
- Behåll wallet-cap `try/except`-beteende oförändrat i denna tranche.
- Invalid symbol payload är pinnad till:
  - `ok: false`
  - `error: invalid_symbol`
  - `requested_symbol: <raw_input>`
  - `message: symbol must be one of TEST_SPOT_WHITELIST`

## Preconditions

- Explicit requester-intent att fortsätta enligt governance.
- Opus pre-code review: `APPROVED`.
- Tranche är exekverad och verifierad i commit `d886d89`.

## Required gates (BEFORE + AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
6. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
7. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_ui_endpoints.py::test_paper_submit_monkeypatched`
8. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_ui_endpoints.py -k "paper_submit"`
9. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_paper_trading_runner.py::test_map_policy_symbol_to_test_symbol tests/test_paper_trading_runner.py::test_submit_paper_order_uses_test_symbol_and_size_from_meta`

## Done criteria

1. Ingen tyst symbol-fallback kvar för ogiltig symbol.
2. Invalid symbol returnerar pinnad payload med HTTP 200.
3. Diff i exekveringscommit är strikt till server + testfil.
4. Before/After-gates är passerade.
5. Opus post-code audit: `APPROVED`.

## Status

- A10 execution: `införd` (retrospektivt dokumenterad via commit `d886d89`).
- Denna fil är ops-backfill i full governance-stil.
