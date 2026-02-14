# Repo Cleanup D4A Trackability Contract (2026-02-14)

## Category

`docs`

## Scope IN

- `docs/ops/REPO_CLEANUP_D4A_TRACKABILITY_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D4A_TRACKABILITY_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- Alla kod-/runtime-/configfiler
- `.gitignore`
- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `results/**`
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Endast docs-ändringar.
- Ignore-policy får inte ändras i D4A.
- Trackability-blocker måste dokumenteras med evidens från `.gitignore`.

## Trackability-evidens

- `.gitignore:212` innehåller `results/`.
- Mönstret gör artefakter under kataloger med namnet `results` ospårbara i git.

## Required gates (BEFORE + AFTER)

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. D4A trackability-kontrakt och rapport skapade.
2. Backlog och AGENTS uppdaterade med blockerstatus och nästa säkra alternativ.
3. Inga ändringar utanför docs/AGENTS.
4. Required gates passerar efter docs-ändring.
5. Opus post-code diff-audit godkänd.

## Status

- D4A execution i denna tranche är docs-only blocker-dokumentation.
- Faktisk `results/**` move-only execution är fortsatt föreslagen tills separat policybeslut finns.
