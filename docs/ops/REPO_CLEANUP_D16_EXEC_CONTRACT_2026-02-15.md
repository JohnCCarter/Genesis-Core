# Repo Cleanup D16 Minimal Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Move-only execution av exakt tre filer:
  1. `results/hparam_search/run_20251227_180204/trial_024.log`
  2. `results/hparam_search/run_20251227_180204/trial_025.log`
  3. `results/hparam_search/run_20251227_180204/trial_026.log`
- Målvägar (mirror under orphaned archive):
  1. `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_024.log`
  2. `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_025.log`
  3. `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_026.log`
- `docs/ops/REPO_CLEANUP_D16_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D16_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `results/**` (förutom exakt de tre scopeade källfilerna)
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen execution utanför de tre scopeade filerna.
- Destinationer måste vara frånvarande före move (no-overwrite precondition).
- Ingen runtime/API/config-ändring.

## Required gates (BEFORE + AFTER)

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Exakt tre nya scopeade filer flyttade till `archive/_orphaned/results/**`.
2. D16 kontrakt + rapport skapade.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Diffen är strikt scopead till 3 flyttar + docs i Scope IN.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D16 i denna tranche är en minimal execution-batch utan ytterligare carry-forward.
- Vidare execution utanför scopead batch är fortsatt föreslagen i separat kontrakt.
