# Repo Cleanup D7 Minimal Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Move-only execution av exakt en fil:
  - `results/hparam_search/run_seeds/run_meta.json`
  - `archive/_orphaned/results/hparam_search/run_seeds/run_meta.json`
- `docs/ops/REPO_CLEANUP_D7_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D7_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `results/**` (förutom den scopeade källfilen ovan)
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Exakt en kandidatfil får exekveras i D7.
- Ingen ytterligare policyändring i `.gitignore`.
- Ingen övrig `results/**` move/delete i denna tranche.
- Ingen runtime/API/config-ändring.

## Required gates (BEFORE + AFTER)

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Scopead one-file move-only execution genomförd.
2. D7 kontrakt + rapport skapade.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Diffen är strikt scopead till exakt flyttfil + docsfiler i Scope IN.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D7 i denna tranche är en minimal execution-pilot som verifierar spårbarhet via
  `archive/_orphaned/results/**`.
- Ytterligare execution utanför den scopeade filen är fortsatt föreslagen i separat kontrakt.
