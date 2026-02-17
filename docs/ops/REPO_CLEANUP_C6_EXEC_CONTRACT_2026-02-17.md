# Repo Cleanup Fas C6 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/benchmark_optimizations.py` (move to `scripts/archive/analysis/benchmark_optimizations.py`)
2. `scripts/calculate_ic_metrics.py` (move to `scripts/archive/analysis/calculate_ic_metrics.py`)
3. `scripts/calculate_partial_ic.py` (move to `scripts/archive/analysis/calculate_partial_ic.py`)
4. `scripts/fdr_correction.py` (move to `scripts/archive/analysis/fdr_correction.py`)
5. `scripts/feature_ic_v18.py` (move to `scripts/archive/analysis/feature_ic_v18.py`)
6. `scripts/monitor_feature_drift.py` (move to `scripts/archive/analysis/monitor_feature_drift.py`)
7. `scripts/archive/analysis/benchmark_optimizations.py` (move destination)
8. `scripts/archive/analysis/calculate_ic_metrics.py` (move destination)
9. `scripts/archive/analysis/calculate_partial_ic.py` (move destination)
10. `scripts/archive/analysis/fdr_correction.py` (move destination)
11. `scripts/archive/analysis/feature_ic_v18.py` (move destination)
12. `scripts/archive/analysis/monitor_feature_drift.py` (move destination)
13. `docs/validation/VALIDATION_CHECKLIST.md` (path-reference update)
14. `docs/validation/ADVANCED_VALIDATION_PRODUCTION.md` (path-reference update)
15. `docs/ops/REPO_CLEANUP_C6_EXEC_CONTRACT_2026-02-17.md`
16. `docs/ops/REPO_CLEANUP_C6_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Alla övriga script-kandidater i Fas C (inkl. `compare_*`, `analyze_optuna_db.py`, `summarize_hparam_results.py`)
- Alla B/D/F/G-trancher
- Alla övriga filer utanför Scope IN
- Inga runtime-kodändringar i `src/**` eller `tests/**`

## Known carry-forward (pre-existing, out-of-scope)

Följande paths var redan dirty före denna tranche och får inte ändras här:

- `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
- `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast move-only av sex deprecated validation/analysis scripts till `scripts/archive/analysis/`.
- Endast dokumentreferens-uppdateringar för nya script-paths i Scope IN.
- Minimal import-bootstrap justering är tillåten för flyttade script som använder `Path(__file__).parent.parent / "src"`, så att pre-move path-resolution bevaras (via `Path(__file__).resolve().parents[3] / "src"`).
- Ingen ändring av runtime-logik, API-kontrakt, config-semantik eller tester.
- Inga opportunistiska sidostädningar utanför Scope IN.

## Preconditions

1. Kandidaterna är markerade som deprecated script-kandidater i:
   - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md` (Fas C-lista)
2. Tracked proof före execution:
   - `git ls-files --error-unmatch scripts/benchmark_optimizations.py scripts/calculate_ic_metrics.py scripts/calculate_partial_ic.py scripts/fdr_correction.py scripts/feature_ic_v18.py scripts/monitor_feature_drift.py`
3. Referensbevis före execution:
   - `git grep -n -E "scripts/benchmark_optimizations\.py|scripts/calculate_ic_metrics\.py|scripts/calculate_partial_ic\.py|scripts/fdr_correction\.py|scripts/feature_ic_v18\.py|scripts/monitor_feature_drift\.py" -- src scripts mcp_server config tests docs/validation`
4. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Allowed residual references

Följande kvarvarande referenser är tillåtna och blockerar inte C6-scope:

- `docs/ops/*`
- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `docs/archive/*`
- `scripts/archive/analysis/benchmark_optimizations.py` (self-usage text)
- `scripts/archive/analysis/calculate_ic_metrics.py` (self-usage text)
- `scripts/archive/analysis/calculate_partial_ic.py` (self-usage text)
- `scripts/archive/analysis/fdr_correction.py` (self-usage text)
- `scripts/archive/analysis/feature_ic_v18.py` (self-usage text)
- `scripts/archive/analysis/monitor_feature_drift.py` (self-usage text)

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_C6_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C6_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Script-run compatibility checks:
   - `python <script> --help` ska ge exit=0 för samtliga sex scripts före och efter flytt.
7. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - Legacy-path negative check (måste vara tom efter execution):
     - `git grep -n -E "scripts/benchmark_optimizations\.py|scripts/calculate_ic_metrics\.py|scripts/calculate_partial_ic\.py|scripts/fdr_correction\.py|scripts/feature_ic_v18\.py|scripts/monitor_feature_drift\.py" -- src scripts mcp_server config tests docs/validation`
   - Archive-path positive check (måste visa uppdaterade refs):
     - `git grep -n -E "scripts/archive/analysis/benchmark_optimizations\.py|scripts/archive/analysis/calculate_ic_metrics\.py|scripts/archive/analysis/calculate_partial_ic\.py|scripts/archive/analysis/fdr_correction\.py|scripts/archive/analysis/feature_ic_v18\.py|scripts/archive/analysis/monitor_feature_drift\.py" -- src scripts mcp_server config tests docs/validation`

## Stop condition

- Om någon required gate failar, eller om legacy-path negative check inte är tom, eller om archive-path positive check saknar scopeade refs, ska C6 markeras `BLOCKED` och ingen commit/push får ske innan remediations + Opus re-review.

## Done criteria

1. Sex script-filer är flyttade till `scripts/archive/analysis/`.
2. Scopeade docs-referenser pekar på nya archive-paths.
3. Inga out-of-scope filändringar utanför Scope IN.
4. Required gates BEFORE/AFTER dokumenterade i report med PASS/FAIL.
5. Opus pre-code + post-code beslut dokumenterade i report.

## Status

- Contract readiness: `införd` i arbetskopia.
- C6 execution: `föreslagen` i arbetskopia.
