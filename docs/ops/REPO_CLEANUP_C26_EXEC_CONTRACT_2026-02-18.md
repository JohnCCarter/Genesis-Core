# Repo Cleanup Fas C26 Execution Contract (2026-02-18)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/cleanup_optimizer_configs.py` (delete)
2. `scripts/create_parity_test_config.py` (delete)
3. `scripts/create_trial_1381_config.py` (delete)
4. `docs/ops/REPO_CLEANUP_C26_EXEC_CONTRACT_2026-02-18.md`
5. `docs/ops/REPO_CLEANUP_C26_EXEC_REPORT_2026-02-18.md`

## Scope OUT

- Alla övriga filer i `scripts/**`
- Alla övriga filer i `docs/**`
- `src/**`, `tests/**`, `config/**`, `mcp_server/**`

## Constraints

- Default: `NO BEHAVIOR CHANGE`
- Explicitt undantag (user-authorized 2026-02-18): delete-only av tre legacy wrappers för accelererad scriptstädning.
- Inga ändringar i runtime-logik, API-kontrakt, config-semantik eller testkod.
- Inga opportunistiska sidostädningar utanför Scope IN.

## Preconditions

1. Kandidaterna är markerade `STALE` med noll refs i:
   - `reports/script_activity_latest.md` (rader 104-106)
2. Archive-targets finns:
   - `scripts/archive/2026-02/analysis/cleanup_optimizer_configs.py`
   - `scripts/archive/2026-02/analysis/create_parity_test_config.py`
   - `scripts/archive/2026-02/analysis/create_trial_1381_config.py`
3. Scoped grep före execution visar inga träffar i `src/**`, `tests/**`, `mcp_server/**`, `config/**`.
4. Opus pre-code review: `APPROVED`.

## Retention exception

- Normpolicy i `scripts/README.md` anger wrapper-retention 2-4 veckor.
- Dessa wrappers är yngre än normal retention.
- Undantag är explicit user-authorized (2026-02-18) för just dessa tre wrappers i C26.

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
     - `scripts/cleanup_optimizer_configs.py`
     - `scripts/create_parity_test_config.py`
     - `scripts/create_trial_1381_config.py`
   - över `src/**`, `tests/**`, `mcp_server/**`, `config/**`, `scripts/**`

## Stop condition

- Om någon gate failar: stoppa och återställ endast de tre delete-filerna.

## Done criteria

1. Tre wrappers är borttagna.
2. Endast Scope IN-filer ändrade.
3. AFTER-gates gröna och dokumenterade i report.
4. Opus post-code diff-audit: `APPROVED`.
