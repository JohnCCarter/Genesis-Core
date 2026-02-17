# Repo Cleanup Fas C5 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/analyze_feature_importance.py` (move to `scripts/archive/analysis/analyze_feature_importance.py`)
2. `scripts/analyze_feature_synergy.py` (move to `scripts/archive/analysis/analyze_feature_synergy.py`)
3. `scripts/analyze_permutation_importance.py` (move to `scripts/archive/analysis/analyze_permutation_importance.py`)
4. `scripts/archive/analysis/analyze_feature_importance.py` (move destination)
5. `scripts/archive/analysis/analyze_feature_synergy.py` (move destination)
6. `scripts/archive/analysis/analyze_permutation_importance.py` (move destination)
7. `docs/features/INDICATORS_REFERENCE.md` (path-reference update)
8. `docs/validation/VALIDATION_CHECKLIST.md` (path-reference update)
9. `docs/ops/REPO_CLEANUP_C5_EXEC_CONTRACT_2026-02-17.md`
10. `docs/ops/REPO_CLEANUP_C5_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Alla övriga script-kandidater i Fas C
- Alla B/D/F/G-trancher
- Alla övriga filer utanför Scope IN
- Inga runtime-kodändringar i `src/**` eller `tests/**`

## Known carry-forward (pre-existing, out-of-scope)

Följande paths var redan dirty före denna tranche och får inte ändras här:

- `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
- `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast move-only av tre deprecated analysis scripts till `scripts/archive/analysis/`.
- Endast move-only av tre deprecated analysis scripts till `scripts/archive/analysis/`, plus minimal import-bootstrap justering i `analyze_permutation_importance.py` for att bevara pre-move path-resolution.
- Endast dokumentreferens-uppdateringar för nya script-paths i Scope IN.
- Ingen ändring av runtime-logik, API-kontrakt, config-semantik eller tester.
- Inga opportunistiska sidostädningar utanför Scope IN.
- Statusdisciplin gäller strikt:
  - `införd` endast efter verifierad implementation + gateutfall + Opus post-audit.
  - annars `föreslagen`.

## Preconditions

1. Kandidaterna är markerade som deprecated script-kandidater i:
   - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md` (Fas C-lista)
2. Tracked proof före execution:
   - `git ls-files --error-unmatch scripts/analyze_feature_importance.py scripts/analyze_feature_synergy.py scripts/analyze_permutation_importance.py`
3. Referensbevis före execution:
   - `git grep -n -E "scripts/analyze_feature_importance\.py|analyze_feature_importance\.py|scripts/analyze_feature_synergy\.py|analyze_feature_synergy\.py|scripts/analyze_permutation_importance\.py|analyze_permutation_importance\.py" -- src scripts mcp_server config tests docs`
4. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Allowed residual references

Följande kvarvarande referenser är tillåtna och blockerar inte C5-scope:

- `docs/ops/*`
- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `docs/features/INDICATORS_REFERENCE.md` (**endast** `scripts/archive/analysis/analyze_feature_importance.py`, legacy source-path förbjuden)
- `docs/validation/VALIDATION_CHECKLIST.md` (**endast** `scripts/archive/analysis/analyze_feature_synergy.py`, legacy source-path förbjuden)
- `scripts/archive/analysis/analyze_feature_importance.py` (self-usage text)
- `scripts/archive/analysis/analyze_feature_synergy.py` (self-usage text)
- `scripts/archive/analysis/analyze_permutation_importance.py` (self-usage text)

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_C5_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C5_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - **Legacy-path negative check (måste vara tom efter execution):**
     - `git grep -n -E "scripts/analyze_feature_importance\.py|scripts/analyze_feature_synergy\.py|scripts/analyze_permutation_importance\.py" -- src scripts mcp_server config tests docs/features docs/validation`
   - **Archive-path positive check (måste visa uppdaterade refs):**
     - `git grep -n -E "scripts/archive/analysis/analyze_feature_importance\.py|scripts/archive/analysis/analyze_feature_synergy\.py|scripts/archive/analysis/analyze_permutation_importance\.py" -- src scripts mcp_server config tests docs`

## Stop condition

- Om legacy-path negative check inte är tom **eller** archive-path positive check saknar förväntade refs i Scope IN ska C5 omedelbart markeras `BLOCKED` och ingen commit/push får ske innan kontrakt/allowlist uppdaterats och Opus har re-godkänt.

## Done criteria

1. Tre script-filer är flyttade till `scripts/archive/analysis/`.
2. Scopeade docs-referenser pekar på nya archive-paths.
3. Inga out-of-scope filändringar utanför Scope IN.
4. Required gates BEFORE/AFTER dokumenterade i report med PASS/FAIL.
5. Opus pre-code + post-code beslut dokumenterade i report.

## Status

- Contract readiness: `införd` i arbetskopia.
- C5 execution: `föreslagen` i arbetskopia.
