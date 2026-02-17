# Docs Status Sync Kickoff Contract (2026-02-17)

## Category

`docs`

## Scope IN

1. `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
2. `docs/ops/DOCS_STATUSSYNC_KICKOFF_CONTRACT_2026-02-17.md`
3. `docs/ops/DOCS_STATUSSYNC_KICKOFF_REPORT_2026-02-17.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `scripts/**`
- `registry/**`
- `mcp_server/**`
- alla övriga `docs/**` utanför Scope IN
- inga rename/delete utanför Scope IN

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast docs-statussync, ingen runtime- eller testlogik får ändras.
- Statusdisciplin gäller strikt:
  - `införd` används endast när konkret evidens finns citerad.
  - annars används `föreslagen`.
- Commit-anchors ska verifieras via `.git/logs/HEAD` och vid behov `git show` fallback.
- Ändringar ska hållas minimala och följa befintlig ton i berörda docs.

## Preconditions

- Opus pre-code review: `APPROVED` (enligt requester-kontext).
- Baseline-gates: passerade pre-change (enligt requester-kontext).

## Required gates (POST-CHANGE)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md docs/ops/DOCS_STATUSSYNC_KICKOFF_CONTRACT_2026-02-17.md docs/ops/DOCS_STATUSSYNC_KICKOFF_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. `git diff --name-only` (scope check)

## Evidence policy

- Primär evidens: `.git/logs/HEAD` med linjeankare för A9/A10/docs/tooling-övergångar.
- Fallback evidens: `git show --name-only` för verifiering av commit-innehåll och scope.
- Endast observerbara fakta (filer, commit-id, testutfall) får användas för `införd`.

## Done criteria

1. Scope IN-filer uppdaterade/skapade enligt uppgiften; inga out-of-scope filer ändrade.
2. `DEEP_ANALYSIS_REPORT_2026-02-15.md` uppdaterad minimalt för statussync från gårdagens validerade docs/commits.
3. Kickoff-report innehåller: pre-code-resultat, ändringsbeskrivning, evidenscitat, gateutfall, residual risks.
4. Samtliga post-change gates ovan är körda och dokumenterade med PASS/FAIL.
5. Scope-check (`git diff --name-only`) visar endast whitelist-filer.

## Status

- Kickoff-tranche: `införd` i arbetskopia (post-change gates dokumenterade i kickoff-report).
