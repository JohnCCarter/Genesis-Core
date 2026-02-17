# Repo Cleanup Fas C8 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/compare_htf_exits.py` (move to `scripts/archive/analysis/compare_htf_exits.py`)
2. `scripts/compare_modes.py` (move to `scripts/archive/analysis/compare_modes.py`)
3. `scripts/compare_swing_strategies.py` (move to `scripts/archive/analysis/compare_swing_strategies.py`)
4. `scripts/archive/analysis/compare_htf_exits.py` (move destination)
5. `scripts/archive/analysis/compare_modes.py` (move destination)
6. `scripts/archive/analysis/compare_swing_strategies.py` (move destination)
7. `docs/ops/REPO_CLEANUP_C8_EXEC_CONTRACT_2026-02-17.md`
8. `docs/ops/REPO_CLEANUP_C8_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Alla övriga script-kandidater i Fas C (inkl. `burn_in.py`, `smoke_submit_*`, `analyze_optuna_db.py`, `summarize_hparam_results.py`)
- Alla B/D/F/G-trancher
- Alla övriga filer utanför Scope IN
- Inga runtime-kodändringar i `src/**` eller `tests/**`

## Known carry-forward (pre-existing, out-of-scope)

Följande paths var redan dirty före denna tranche och får inte ändras här:

- `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
- `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`
- `reports/script_activity_latest.json`
- `reports/script_activity_latest.md`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast move-only av tre evidensklassade stale scripts till `scripts/archive/analysis/`.
- Minimal import-bootstrap justering är tillåten för flyttade script som använder `Path(__file__).parent.parent / "src"`, så att pre-move path-resolution bevaras (via `Path(__file__).resolve().parents[3] / "src"`).
- Icke-beteendepåverkande self-usage textjustering i flyttade scripts är tillåten för att ersätta legacy-path (`scripts/<name>.py`) med archive-path (`scripts/archive/analysis/<name>.py`).
- Ingen ändring av runtime-logik, API-kontrakt, config-semantik eller tester.
- Inga opportunistiska sidostädningar utanför Scope IN.

## Preconditions

1. Kandidaterna är markerade i stale-evidens med låg score i:
   - `reports/script_activity_latest.md`
   - `reports/script_activity_latest.json`
2. Kandidaterna återfinns i deprecated candidate-lista:
   - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
3. Tracked proof före execution:
   - `git ls-files --error-unmatch scripts/compare_htf_exits.py scripts/compare_modes.py scripts/compare_swing_strategies.py`
4. Scoped referensscan före execution:
   - `git grep -n -E "scripts/compare_htf_exits\.py|scripts/compare_modes\.py|scripts/compare_swing_strategies\.py" -- src scripts mcp_server config tests`
5. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Allowed residual references

Följande kvarvarande referenser är tillåtna och blockerar inte C8-scope:

- `docs/ops/*`
- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `docs/bugs/*`
- `docs/daily_summaries/*`
- `reports/script_activity_latest.*`
- `scripts/archive/analysis/compare_htf_exits.py` (self-usage text)
- `scripts/archive/analysis/compare_modes.py` (self-usage text)
- `scripts/archive/analysis/compare_swing_strategies.py` (self-usage text)

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_C8_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C8_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Script compatibility checks (BEFORE/AFTER):
   - `python scripts/compare_modes.py --help` ska ge exit=0.
   - Modulimport (utan att köra `main`) ska ge exit=0 för:
     - `scripts/compare_htf_exits.py`
     - `scripts/compare_swing_strategies.py`
     - `scripts/compare_modes.py`
7. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - Legacy-path negative check (måste vara tom efter execution):
     - `git grep -n -E "scripts/compare_htf_exits\.py|scripts/compare_modes\.py|scripts/compare_swing_strategies\.py" -- src scripts mcp_server config tests`

## Stop condition

- Om någon required gate failar, eller om legacy-path negative check inte är tom, ska C8 markeras `BLOCKED` och ingen commit/push får ske innan remediations + Opus re-review.

## Done criteria

1. Tre script-filer är flyttade till `scripts/archive/analysis/`.
2. Minimal bootstrap-kompatibilitet bibehållen för flyttade script.
3. Legacy self-usage path-text i flyttade scripts är uppdaterad till archive-path där relevant.
4. Inga out-of-scope filändringar utanför Scope IN.
5. Required gates BEFORE/AFTER dokumenterade i report med PASS/FAIL.
6. Opus pre-code + post-code beslut dokumenterade i report.

## Status

- Contract readiness: `införd` i arbetskopia.
- C8 execution: `föreslagen` i arbetskopia.
