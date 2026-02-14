# Repo Cleanup D3L Execution Report (2026-02-14)

## Syfte

Genomföra kandidatvis flytt av sista kvarvarande diagnose-script i `scripts/`.

## Flyttat script (move-only)

1. `scripts/diagnose_optuna_issues.py`

Ny path:

- `scripts/archive/debug/2026-02-14/diagnose_optuna_issues.py`

## Känd docs-referenspåverkan

Följande docs nämner tidigare script-path eller scriptnamn och uppdateras inte i D3L:

- `docs/optuna/OPTUNA_FIX_SUMMARY.md`
- `docs/optuna/OPTUNA_BEST_PRACTICES.md`
- `docs/archive/phase6/DOCUMENTATION_ANALYSIS.md`
- `docs/archive/phase6/ORIGINAL_REPO_MENTIONS.md`
- `docs/analysis/INVESTIGATION_COMPLETE.md`

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Verifiering

- Scope gate: endast kontrakterade filer i diff.
- Rename-diff verifierad för flytten.
- Move-only verifierad: inga kodhunks i flyttad `.py`-fil.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `results/**`, `tmp/**`.
- Before-gates: pass.
- After-gates: pass.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D3L är införd som move-only för sista diagnose-scriptet i `scripts/`.
- D3 övergripande scope är fortsatt föreslaget kandidatvis.
