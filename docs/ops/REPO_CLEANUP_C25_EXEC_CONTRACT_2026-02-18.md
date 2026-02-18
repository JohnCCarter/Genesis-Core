# Repo Cleanup Fas C25 Execution Contract (2026-02-18)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/calculate_score_260.py` (delete)
2. `scripts/calculate_score_realistic.py` (delete)
3. `scripts/check_robustness_top_trials.py` (delete)
4. `docs/ops/REPO_CLEANUP_C25_EXEC_CONTRACT_2026-02-18.md`
5. `docs/ops/REPO_CLEANUP_C25_EXEC_REPORT_2026-02-18.md`

## Scope OUT

- Alla övriga filer i `scripts/**`
- Alla övriga filer i `docs/**`
- `src/**`, `tests/**`, `config/**`, `mcp_server/**`

## Constraints

- Default: `NO BEHAVIOR CHANGE`
- Explicitt undantag (user-authorized 2026-02-18): borttagning av legacy wrapper-paths i tre filer ovan för att avsluta scriptfasen.
- Inga ändringar i runtime-logik, API-kontrakt, config-semantik eller testkod.
- Inga opportunistiska sidostädningar utanför Scope IN.

## Preconditions

1. Kandidaterna är markerade `STALE` med noll refs i:
   - `reports/script_activity_latest.md` (rader 101-103)
2. Archive-targets finns:
   - `scripts/archive/2026-02/analysis/calculate_score_260.py`
   - `scripts/archive/2026-02/analysis/calculate_score_realistic.py`
   - `scripts/archive/2026-02/analysis/check_robustness_top_trials.py`
3. Scoped grep före execution visar endast self-wrapper-referenser i scope för legacy-paths.
4. Opus pre-code review: `APPROVED`.

## Retention exception

- Normpolicy i `scripts/README.md` anger wrapper-retention 2-4 veckor.
- C25 körs tidigare än detta fönster.
- Undantag är explicit user-authorized (2026-02-18) för att stänga scriptfasen nu.

## Required gates

### BEFORE (redan körda)

1. `pre-commit run --all-files`
2. `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `python -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `python -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`

### AFTER

1. `pre-commit run --all-files`
2. `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `python -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `python -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope guard:
   - `git diff --name-only` måste vara exakt Scope IN
7. Legacy negative grep:
   - tomt resultat för:
     - `scripts/calculate_score_260.py`
     - `scripts/calculate_score_realistic.py`
     - `scripts/check_robustness_top_trials.py`
   - över `src/**`, `tests/**`, `mcp_server/**`, `config/**`, `scripts/**`

## Stop condition

- Om någon gate failar eller scope drift upptäcks: markera `BLOCKED`, stoppa commit/push och kör minimal remediation + Opus re-review.

## Done criteria

1. Tre wrappers är borttagna.
2. Endast Scope IN-filer ändrade.
3. AFTER-gates gröna och dokumenterade i report.
4. Opus post-code diff-audit: `APPROVED`.
