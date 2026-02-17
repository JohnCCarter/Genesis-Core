# Repo Cleanup Fas B Microtranche-1 Precheck Contract (2026-02-17)

## Category

`tooling`

## Scope IN

1. `docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_CONTRACT_2026-02-17.md`
2. `docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_REPORT_2026-02-17.md`

## Scope OUT

- Alla runtime-filer (`src/**`) och tester (`tests/**`)
- Alla config-filer (`config/**`)
- Alla scripts (`scripts/**`)
- Alla data/results-filer
- Alla övriga docs utanför Scope IN

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Detta är en **precheck-tranche** (plan-only) för Fas B.
- Ingen filradering/flytt får ske i denna tranche.
- Inga kodändringar får ske.
- Statusdisciplin gäller strikt: `införd` endast för verifierad docs/precheck; execution-status är `föreslagen` tills separat execution-kontrakt godkänns.

## Objective

Ta fram färsk, verifierad beslutsgrund för första exekverbara Fas B-mikrotranche genom att:

1. isolera kandidat B1 (`src/core/strategy/example.py`) från högre riskkandidater,
2. markera B2 (`src/core/ml/overfit_detection.py`) som blockerad i mikrotranche-1 p.g.a. stark docs/config-ankring,
3. definiera exakt preconditions för nästa execution-kontrakt.

## Required gates (POST-CHANGE)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. `git diff --name-only` + `git status --porcelain` (scope check)

## Done criteria

1. Fas B microtranche-1 precheck rapporterad med tydlig beslutsmatris för B1/B2.
2. Preconditions för execution-kontrakt dokumenterade och verifierbara.
3. Inga out-of-scope ändringar.
4. Gateutfall dokumenterade i rapport.

## Status

- Precheck-dokumentation: `införd` i arbetskopia.
- Fas B execution microtranche-1: fortsatt `föreslagen`.
