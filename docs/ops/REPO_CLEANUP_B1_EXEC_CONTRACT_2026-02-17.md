# Repo Cleanup Fas B1 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `src/core/strategy/example.py` (delete)
2. `src/genesis_core.egg-info/SOURCES.txt` (remove stale source entry for deleted file)
3. `docs/architecture/ARCHITECTURE_VISUAL.md` (remove/adjust references to `core.strategy.example`)
4. `docs/features/GENESIS-CORE_FEATURES.md` (remove stale `strategy/example.py` reference)
5. `docs/archive/GENESIS-CORE_FEATURES_phase1-4.md` (remove stale `strategy/example.py` reference)
6. `docs/ops/REPO_CLEANUP_B1_EXEC_CONTRACT_2026-02-17.md`
7. `docs/ops/REPO_CLEANUP_B1_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Alla övriga B-kandidater (`B2-B8`), inklusive:
  - `src/core/ml/overfit_detection.py`
  - `src/core/strategy/ema_cross.py`
  - `src/core/indicators/fvg.py`
  - `src/core/indicators/macd.py`
  - `src/core/strategy/validation.py`
  - `src/core/backtest/walk_forward.py`
  - `src/core/strategy/fvg_filter.py`
- `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, `data/**` utanför Scope IN
- Inga rename/delete utanför Scope IN

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast borttagning av B1 (`src/core/strategy/example.py`) + nödvändig referensstädning.
- Ingen runtime-logik, API-kontrakt, config-semantik eller testbeteende får ändras.
- Statusdisciplin gäller strikt:
  - `införd` endast efter verifierad implementation + gateutfall.
  - Annars `föreslagen`.
- Inga opportunistiska cleanup-ändringar utanför Scope IN.

## Preconditions

1. B1 precheck är dokumenterad (`APPROVED TO PLAN`) i:
   - `docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_REPORT_2026-02-17.md`
2. Referensbevis verifierade före execution:
   - `git ls-files --error-unmatch src/core/strategy/example.py` (tracked)
   - `git grep -n "core\.strategy\.example|strategy/example\.py" -- src scripts mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md docs/features/GENESIS-CORE_FEATURES.md docs/archive/GENESIS-CORE_FEATURES_phase1-4.md`
3. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Required gates (BEFORE and AFTER execution)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md docs/features/GENESIS-CORE_FEATURES.md docs/archive/GENESIS-CORE_FEATURES_phase1-4.md docs/ops/REPO_CLEANUP_B1_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_B1_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - `git grep -n "core\.strategy\.example|strategy/example\.py" -- src scripts mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md docs/features/GENESIS-CORE_FEATURES.md docs/archive/GENESIS-CORE_FEATURES_phase1-4.md` (ska inte visa kvarvarande stale refs för B1 i dessa paths)

## Done criteria

1. `src/core/strategy/example.py` borttagen och inga out-of-scope filer ändrade.
2. Kända referenser i Scope IN uppdaterade så att inga stale B1-pekare kvarstår.
3. `SOURCES.txt` uppdaterad för borttagen fil.
4. Required gates före/efter dokumenterade i report med PASS/FAIL.
5. Opus pre-code + post-code beslut dokumenterade i report.
6. Eventuella kvarvarande referenser i governance/historikfiler (`docs/ops/*`, `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`) redovisas explicit som tillåtna och scope-irrelevanta för B1 execution.

## Status

- Contract readiness: `införd` i arbetskopia.
- B1 execution: `föreslagen` tills Opus pre-review + implementation + post-gates är klara.
