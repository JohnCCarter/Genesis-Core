# Repo Cleanup Fas C3 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/train_meta_model.py` (move to `scripts/archive/experiments/train_meta_model.py`)
2. `scripts/probe_min_order_sizes.py` (move to `scripts/archive/experiments/probe_min_order_sizes.py`)
3. `scripts/probe_min_order_sizes_live.py` (move to `scripts/archive/experiments/probe_min_order_sizes_live.py`)
4. `scripts/archive/experiments/train_meta_model.py` (move destination)
5. `scripts/archive/experiments/probe_min_order_sizes.py` (move destination)
6. `scripts/archive/experiments/probe_min_order_sizes_live.py` (move destination)
7. `docs/ops/REPO_CLEANUP_C3_EXEC_CONTRACT_2026-02-17.md`
8. `docs/ops/REPO_CLEANUP_C3_EXEC_REPORT_2026-02-17.md`

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
   - `git ls-files --error-unmatch scripts/train_meta_model.py scripts/probe_min_order_sizes.py scripts/probe_min_order_sizes_live.py`
3. Referensbevis före execution:
   - `git grep -n -E "scripts/train_meta_model\.py|train_meta_model\.py|scripts/probe_min_order_sizes\.py|probe_min_order_sizes\.py|scripts/probe_min_order_sizes_live\.py|probe_min_order_sizes_live\.py" -- src scripts mcp_server config tests docs`
4. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Allowed residual references

Följande kvarvarande referenser är tillåtna och blockerar inte C3-scope:

- `docs/ops/*`
- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_C3_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C3_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - `git grep -n -E "scripts/train_meta_model\.py|train_meta_model\.py|scripts/probe_min_order_sizes\.py|probe_min_order_sizes\.py|scripts/probe_min_order_sizes_live\.py|probe_min_order_sizes_live\.py" -- src scripts mcp_server config tests docs` (ska endast lämna allowlistade docs/historikträffar efter execution)

## Stop condition

- Om scoped `git grep` efter execution visar träffar utanför `Allowed residual references` ska C3 omedelbart markeras `BLOCKED` och ingen commit/push får ske innan kontrakt/allowlist uppdaterats och Opus har re-godkänt.

## Done criteria

1. Tre script-filer är flyttade till `scripts/archive/experiments/`.
2. Inga out-of-scope filändringar utanför Scope IN.
3. Required gates BEFORE/AFTER dokumenterade i report med PASS/FAIL.
4. Opus pre-code + post-code beslut dokumenterade i report.

## Status

- Contract readiness: `införd` i arbetskopia.
- C3 execution: `införd`.
