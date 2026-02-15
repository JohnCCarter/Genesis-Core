# Repo Cleanup D6 Policy Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- `.gitignore`
- `docs/ops/REPO_CLEANUP_D6_POLICY_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D6_POLICY_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D4B_POLICY_OPTIONS_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `results/**` content
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ignore-policy-ändringen ska vara minimal och begränsad till allowlist för:
  - `archive/_orphaned/results/**`
- Root `results/**` ska fortsatt vara ignorerat.
- Ingen move/delete execution av artefakter i denna tranche.
- Ingen ändring i runtime/API/config.

## Required gates (BEFORE + AFTER)

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. `.gitignore` har minimal policydelta för `archive/_orphaned/results/**`.
2. D6 kontrakt och rapport finns i `docs/ops/`.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Inga ändringar i kod/runtime-zoner.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D6 i denna tranche är en policy/tooling-ändring utan artefakt-exekvering.
- Faktisk `results/**` move/delete execution är fortsatt föreslagen i separat execution-kontrakt.
