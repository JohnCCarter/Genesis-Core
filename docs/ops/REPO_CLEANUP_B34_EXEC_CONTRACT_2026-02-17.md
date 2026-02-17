# Repo Cleanup Fas B3+B4 Execution Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `src/core/strategy/ema_cross.py` (delete)
2. `tests/test_strategy_ema_cross.py` (delete)
3. `src/core/indicators/fvg.py` (delete)
4. `tests/test_fvg.py` (delete)
5. `src/genesis_core.egg-info/SOURCES.txt` (remove stale entries for deleted files)
6. `docs/architecture/ARCHITECTURE_VISUAL.md` (remove/adjust references to deleted modules)
7. `docs/features/GENESIS-CORE_FEATURES.md` (remove stale `strategy/ema_cross.py` reference)
8. `docs/archive/GENESIS-CORE_FEATURES_phase1-4.md` (remove stale `strategy/ema_cross.py` reference)
9. `docs/ops/REPO_CLEANUP_B34_EXEC_CONTRACT_2026-02-17.md`
10. `docs/ops/REPO_CLEANUP_B34_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Alla övriga B-kandidater (B2, B5, B6, B7, B8)
- Alla övriga paths utanför Scope IN
- Inga rename/delete utanför Scope IN

## Known carry-forward (pre-existing, out-of-scope)

Följande paths var redan dirty före denna tranche och får inte ändras här:

- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `docs/ops/DOCS_STATUSSYNC_KICKOFF_CONTRACT_2026-02-17.md`
- `docs/ops/DOCS_STATUSSYNC_KICKOFF_REPORT_2026-02-17.md`
- `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_CONTRACT_2026-02-17.md`
- `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`
- `docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_CONTRACT_2026-02-17.md`
- `docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_REPORT_2026-02-17.md`
- `docs/ops/REPO_CLEANUP_B1_EXEC_CONTRACT_2026-02-17.md`
- `docs/ops/REPO_CLEANUP_B1_EXEC_REPORT_2026-02-17.md`
- `src/core/strategy/example.py` (delete från B1)

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast borttagning av test-only moduler B3+B4 och deras direkta testfiler.
- Ingen runtime-logik, API-kontrakt, config-semantik eller testbeteende utanför Scope IN får ändras.
- Inga opportunistiska städningar utanför Scope IN.
- Statusdisciplin gäller strikt:
  - `införd` endast efter verifierad implementation + gateutfall + Opus post-audit.
  - annars `föreslagen`.

## Preconditions

1. Legitimitetsgranskning dokumenterad i:
   - `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`
2. B3/B4 kandidater tracked före execution:
   - `git ls-files --error-unmatch src/core/strategy/ema_cross.py tests/test_strategy_ema_cross.py src/core/indicators/fvg.py tests/test_fvg.py`
3. Scoped referensbevis före execution:
   - `git grep -n -E "core\.strategy\.ema_cross|strategy/ema_cross\.py|core\.indicators\.fvg|indicators/fvg\.py|test_strategy_ema_cross\.py|test_fvg\.py" -- src scripts mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md docs/features/GENESIS-CORE_FEATURES.md docs/archive/GENESIS-CORE_FEATURES_phase1-4.md`
4. Opus pre-code review måste ge `APPROVED` innan kodändringar.

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md docs/features/GENESIS-CORE_FEATURES.md docs/archive/GENESIS-CORE_FEATURES_phase1-4.md docs/ops/REPO_CLEANUP_B34_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_B34_EXEC_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope checks:
   - `git status --porcelain` BEFORE
   - `git diff --name-only`
   - `git status --porcelain` AFTER
   - `git grep -n -E "core\.strategy\.ema_cross|strategy/ema_cross\.py|core\.indicators\.fvg|indicators/fvg\.py|test_strategy_ema_cross\.py|test_fvg\.py" -- src scripts mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md docs/features/GENESIS-CORE_FEATURES.md docs/archive/GENESIS-CORE_FEATURES_phase1-4.md` (ska ge exit=1 efter execution)

## Done criteria

1. B3/B4 source+test-filer borttagna och `SOURCES.txt` uppdaterad.
2. Kända stale refs i Scope IN-docs borttagna/justerade.
3. Required gates BEFORE/AFTER dokumenterade i report med PASS/FAIL.
4. Opus pre-code + post-code beslut dokumenterade i report.
5. Inga nya out-of-scope ändringar utöver dokumenterade carry-forward paths.

## Status

- Contract readiness: `införd` i arbetskopia.
- B3+B4 execution: `föreslagen` tills Opus pre-review + implementation + post-audit är klara.
