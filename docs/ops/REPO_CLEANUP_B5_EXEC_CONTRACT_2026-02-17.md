# Repo Cleanup Fas B5 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `src/core/indicators/macd.py` (delete)
2. `src/genesis_core.egg-info/SOURCES.txt` (remove stale source entry)
3. `docs/architecture/ARCHITECTURE_VISUAL.md` (remove/adjust `core.indicators.macd` references and counts)
4. `docs/ops/REPO_CLEANUP_B5_EXEC_CONTRACT_2026-02-17.md`
5. `docs/ops/REPO_CLEANUP_B5_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Alla övriga B-kandidater (B2, B6, B7, B8)
- Alla övriga filer utanför Scope IN
- Inga rename/delete utanför Scope IN

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast borttagning av B5 (`src/core/indicators/macd.py`) + nödvändig index/docs-städning inom Scope IN.
- Ingen runtime-logik, API-kontrakt, config-semantik eller testbeteende får ändras.
- Inga opportunistiska sidostädningar utanför Scope IN.
- Statusdisciplin gäller strikt:
  - `införd` endast efter verifierad implementation + gateutfall + Opus post-audit.
  - annars `föreslagen`.

## Preconditions

1. Legitimitetsgranskning dokumenterad i:
   - `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`
2. Tracked proof före execution:
   - `git ls-files --error-unmatch src/core/indicators/macd.py`
3. Referensbevis före execution:
   - `git grep -n -E "core\.indicators\.macd|indicators/macd\.py" -- src mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md`
4. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Allowed residual references

Följande kvarvarande referenser är tillåtna (governance/historik eller archive-only) och är inte blockerande för B5-scope:

- `docs/ops/*`
- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `scripts/archive/**`

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md docs/ops/REPO_CLEANUP_B5_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_B5_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - `git grep -n -E "core\.indicators\.macd|indicators/macd\.py" -- src mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md` (ska ge exit=1 efter execution)

## Done criteria

1. `src/core/indicators/macd.py` borttagen.
2. `SOURCES.txt` uppdaterad med borttagen `macd.py`-rad.
3. `ARCHITECTURE_VISUAL.md` uppdaterad så `macd` är borttagen ur snapshot/diagram/evidence.
4. Required gates BEFORE/AFTER dokumenterade i report med PASS/FAIL.
5. Opus pre-code + post-code beslut dokumenterade i report.
6. Inga out-of-scope ändringar.

## Status

- Contract readiness: `införd` i arbetskopia.
- B5 execution: `föreslagen` tills Opus pre-review + implementation + post-audit är klara.
