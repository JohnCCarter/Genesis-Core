# Repo Cleanup Fas C4 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/train_regression_model.py` (move to `scripts/archive/experiments/train_regression_model.py`)
2. `scripts/filter_model_features.py` (move to `scripts/archive/experiments/filter_model_features.py`)
3. `scripts/run_timeframe_sweep.py` (move to `scripts/archive/experiments/run_timeframe_sweep.py`)
4. `scripts/archive/experiments/train_regression_model.py` (move destination)
5. `scripts/archive/experiments/filter_model_features.py` (move destination)
6. `scripts/archive/experiments/run_timeframe_sweep.py` (move destination)
7. `docs/ops/REPO_CLEANUP_C4_EXEC_CONTRACT_2026-02-17.md`
8. `docs/ops/REPO_CLEANUP_C4_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Alla övriga script-kandidater i Fas C
- Alla B/D/F/G-trancher
- Alla övriga filer utanför Scope IN
- Inga runtime-kodändringar i `src/**` eller `tests/**`

## Known carry-forward (pre-existing, out-of-scope)

Följande paths var redan dirty före denna tranche och får inte ändras här:

- `docs/ops/REPO_CLEANUP_B2_EXEC_CONTRACT_2026-02-17.md`
- `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast move-only av tre deprecated scripts till `scripts/archive/experiments/`.
- Ingen ändring av runtime-logik, API-kontrakt, config-semantik eller tester.
- Inga opportunistiska sidostädningar utanför Scope IN.
- Statusdisciplin gäller strikt:
  - `införd` endast efter verifierad implementation + gateutfall + Opus post-audit.
  - annars `föreslagen`.

## Preconditions

1. Kandidaterna är markerade som deprecated script-kandidater i:
   - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md` (Fas C-lista)
2. Tracked proof före execution:
   - `git ls-files --error-unmatch scripts/train_regression_model.py scripts/filter_model_features.py scripts/run_timeframe_sweep.py`
3. Referensbevis före execution:
   - `git grep -n -E "scripts/train_regression_model\.py|train_regression_model\.py|scripts/filter_model_features\.py|filter_model_features\.py|scripts/run_timeframe_sweep\.py|run_timeframe_sweep\.py" -- src scripts mcp_server config tests docs`
4. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Allowed residual references

Följande kvarvarande referenser är tillåtna och blockerar inte C4-scope:

- `docs/ops/*`
- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `scripts/archive/experiments/train_regression_model.py` (self-usage text)
- `scripts/archive/experiments/filter_model_features.py` (self-usage text)
- `scripts/archive/experiments/run_timeframe_sweep.py` (self-usage text)

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_C4_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C4_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - `git grep -n -E "scripts/train_regression_model\.py|train_regression_model\.py|scripts/filter_model_features\.py|filter_model_features\.py|scripts/run_timeframe_sweep\.py|run_timeframe_sweep\.py" -- src scripts mcp_server config tests docs` (ska efter execution endast lämna allowlistade träffar enligt `Allowed residual references`)

## Stop condition

- Om scoped `git grep` efter execution visar träffar utanför `Allowed residual references` ska C4 omedelbart markeras `BLOCKED` och ingen commit/push får ske innan kontrakt/allowlist uppdaterats och Opus har re-godkänt.

## Done criteria

1. Tre script-filer är flyttade till `scripts/archive/experiments/`.
2. Inga out-of-scope filändringar utanför Scope IN.
3. Required gates BEFORE/AFTER dokumenterade i report med PASS/FAIL.
4. Opus pre-code + post-code beslut dokumenterade i report.

## Status

- Contract readiness: `införd` i arbetskopia.
- C4 execution: `införd` i arbetskopia.
