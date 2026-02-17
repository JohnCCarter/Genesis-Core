# Repo Cleanup Legitimacy Review Contract (2026-02-17)

## Category

`docs`

## Scope IN

1. `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_CONTRACT_2026-02-17.md`
2. `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `scripts/**`
- `registry/**`
- `mcp_server/**`
- `data/**`
- `results/**`
- alla övriga `docs/**` utanför Scope IN
- inga rename/delete utanför Scope IN

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast legitimetsgranskning och processdokumentation.
- Inga runtime- eller testlogikändringar.
- Statusdisciplin gäller:
  - `införd` används endast för verifierat genomförda ändringar i repo.
  - `föreslagen` används för ej exekverade nästa steg.
- Fasbeslut ska baseras på observerbar evidens (filreferenser, git-index, commitankare).

## Objective

Verifiera om cleanup-faserna B/C/D/F/G är legitima att planera och/eller exekvera i nuvarande branchläge innan nya destruktiva trancher startas.

## Known carry-forward (pre-existing, out-of-scope)

Följande paths var redan dirty före denna tranche och får inte ändras här:

- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
- `docs/ops/DOCS_STATUSSYNC_KICKOFF_CONTRACT_2026-02-17.md`
- `docs/ops/DOCS_STATUSSYNC_KICKOFF_REPORT_2026-02-17.md`

## Required gates (for this docs-only review tranche)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. `git diff --name-only` och `git status --porcelain` (scope check)

## Done criteria

1. Fasmatris B/C/D/F/G med beslut: `APPROVED TO PLAN`, `BLOCKED TO PLAN`, `BLOCKED TO EXECUTE`.
2. Minimikriterier per fas dokumenterade innan execution-kontrakt får skapas.
3. Evidensankare dokumenterade (deep analysis + governance + git-läge).
4. Inga nya out-of-scope ändringar utöver dokumenterade carry-forward paths.
5. Gateutfall dokumenterade i rapport.

## Status

- Legitimitetsgranskning: `införd` i arbetskopia.
- Execution av cleanup-faser: fortsatt `föreslagen` tills fasvisa kontrakt godkänts.
