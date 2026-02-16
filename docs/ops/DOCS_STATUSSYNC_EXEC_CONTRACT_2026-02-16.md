# Docs Status Sync Execution Contract (2026-02-16)

## Category

`docs`

## Scope IN

- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `docs/ops/DOCS_STATUSSYNC_EXEC_CONTRACT_2026-02-16.md`
- `docs/ops/DOCS_STATUSSYNC_EXEC_REPORT_2026-02-16.md`

## Scope OUT

- `src/**`
- `tests/**`
- `.github/**`
- `scripts/**`
- `config/**`
- `data/**`
- `results/**`
- `tmp/**`
- alla övriga paths

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast statusdrift-synk i auditrapport.
- Inga nya runtime-påståenden utan commit-evidens.
- Historisk tabell ska lämnas oförändrad.

## Preconditions

- Explicit requester-intent att fullfölja docs i samma governance-stil.
- Opus pre-code review: `APPROVED`.
- Tranche är exekverad och verifierad i commit `de9f417`.

## Required gates (BEFORE + AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
6. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`

## Done criteria

1. A7–A10 statusdrift dokumenterad med commitrefs i auditrapporten.
2. Diff i exekveringscommit begränsad till auditfilen.
3. Before/After-gates är passerade.
4. Opus post-code audit: `APPROVED`.

## Status

- Docs statussync tranche: `införd` (retrospektivt dokumenterad via commit `de9f417`).
