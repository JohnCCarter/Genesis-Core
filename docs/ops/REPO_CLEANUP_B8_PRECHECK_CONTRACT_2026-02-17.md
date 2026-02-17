# Repo Cleanup Fas B8 Precheck Contract (2026-02-17)

## Category

`tooling`

## Scope IN

1. `docs/ops/REPO_CLEANUP_B8_PRECHECK_CONTRACT_2026-02-17.md`
2. `docs/ops/REPO_CLEANUP_B8_PRECHECK_REPORT_2026-02-17.md`

## Scope OUT

- Alla runtime-filer (`src/**`)
- Alla tester (`tests/**`)
- Alla scripts (`scripts/**`)
- Alla config-filer (`config/**`)
- Alla övriga docs utanför Scope IN

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Detta är en **precheck-tranche** (plan-only) för B8.
- Ingen radering/flytt av kod får ske i denna tranche.
- Inga kodändringar utanför Scope IN.
- Statusdisciplin gäller strikt:
  - `införd` endast för verifierad precheck-dokumentation.
  - B8 execution är `föreslagen` tills separat execution-kontrakt godkänns.

## Objective

1. verifiera om B8 (`src/core/strategy/fvg_filter.py`) fortfarande är legitim för isolerad `git rm`,
2. dokumentera blockerande beroenden med färsk evidens,
3. definiera nästa säkra alternativ för fortsatt cleanup.

## Required gates (POST-CHANGE)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_B8_PRECHECK_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_B8_PRECHECK_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. `git diff --name-only` + `git status --porcelain` (scope check)

## Done criteria

1. B8 legitimitetsstatus dokumenterad med explicit beslut (`APPROVED TO PLAN` eller `BLOCKED TO EXECUTE`).
2. Blockerande referenser dokumenterade med filbevis.
3. Nästa rekommenderade steg definierat utan scope-drift.
4. Gateutfall dokumenterade i report.

## Status

- B8 precheck-dokumentation: `införd` i arbetskopia.
- B8 execution: fortsatt `föreslagen` tills separat execution-kontrakt + Opus pre-review.
