# Repo Cleanup Fas C7 Evidence Contract (2026-02-17)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/classify_script_activity.py` (new evidence-driven classifier)
2. `docs/ops/REPO_CLEANUP_C7_EVIDENCE_CONTRACT_2026-02-17.md`
3. `docs/ops/REPO_CLEANUP_C7_EVIDENCE_REPORT_2026-02-17.md`

## Scope OUT

- Alla script-moves/raderingar i Fas C
- Alla ändringar i `src/**`, `tests/**`, `config/**`, `mcp_server/**`
- Alla övriga filer utanför Scope IN

## Known carry-forward (pre-existing, out-of-scope)

- `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
- `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast ny read-only tooling för evidensbaserad klassificering av scripts (`ACTIVE` / `REVIEW` / `STALE`).
- Ingen exekvering som flyttar/raderar filer.
- Ingen ändring av runtime-logik eller API-kontrakt.
- Output-filer från verktyget (t.ex. under `tmp/**` eller `reports/**`) får genereras lokalt för evidens men ska inte ingå i commit om ej explicit scopead.

## Preconditions

1. Basline-status verifierad med `git status --porcelain`.
2. Required BEFORE-gates gröna.
3. Opus pre-code review måste ge `APPROVED` innan implementation.

## Required gates (BEFORE and AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\pre-commit.exe run --files docs/ops/REPO_CLEANUP_C7_EVIDENCE_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C7_EVIDENCE_REPORT_2026-02-17.md`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Script smoke check:
   - `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe scripts/classify_script_activity.py --help` (exit=0)
   - `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe scripts/classify_script_activity.py --limit 5 --output-json tmp/c7_script_activity_sample.json --output-md tmp/c7_script_activity_sample.md` (exit=0)
7. Script lint/sanity check (AFTER):
   - `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m ruff check scripts/classify_script_activity.py`
8. Scope checks (carry-forward-safe):
   - Scoped diff:
     - `git diff --name-only -- docs/ops/REPO_CLEANUP_C7_EVIDENCE_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C7_EVIDENCE_REPORT_2026-02-17.md scripts/classify_script_activity.py`
   - Staged diff (måste vara exakt Scope IN):
     - `git diff --cached --name-only`

## Stop condition

- Om någon required gate failar: markera `BLOCKED`, stoppa commit/push och kör minimal remediation + Opus re-review.
- Om staged diff innehåller paths utanför Scope IN: markera `BLOCKED`.

## Done criteria

1. Ett nytt script (`scripts/classify_script_activity.py`) finns och körs utan fel.
2. Scriptet producerar evidensfiler med klassificering + score + orsakssignaler.
3. Inga out-of-scope filändringar utanför Scope IN.
4. BEFORE/AFTER-gates dokumenterade i report.
5. Opus pre-code + post-code beslut dokumenterade i report.

## Status

- Contract readiness: `införd` i arbetskopia.
- C7 implementation: `föreslagen` i arbetskopia.
