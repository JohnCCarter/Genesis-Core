# Repo Cleanup D3I Execution Report (2026-02-14)

## Syfte

Genomföra kandidatvis flytt av tre testscript med måttlig extern referensyta.

## Flyttade script (move-only)

1. `scripts/test_htf_exit_engine.py`
2. `scripts/test_htf_fibonacci_mapping.py`
3. `scripts/test_partial_exit_infrastructure.py`

Nya paths:

- `scripts/archive/test_prototypes/2026-02-14/test_htf_exit_engine.py`
- `scripts/archive/test_prototypes/2026-02-14/test_htf_fibonacci_mapping.py`
- `scripts/archive/test_prototypes/2026-02-14/test_partial_exit_infrastructure.py`

## Känd docs-referenspåverkan

Följande docs nämner tidigare script-paths eller scriptnamn och uppdateras inte i D3I:

- `docs/fibonacci/HTF_FIBONACCI_EXITS_SUMMARY.md`
- `docs/fibonacci/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_NEXT_PLAN.md`
- `docs/fibonacci/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`
- `docs/archive/COMMIT_MSG_HTF_EXITS.txt`

Notering (path-kollision): `test_htf_exit_engine.py` förekommer både i `scripts/` och `tests/`.
D3I omfattar endast flytt av scriptfilen under `scripts/`.

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
- Rename-diff verifierad för samtliga 3 flyttar.
- Move-only verifierad: inga kodhunks i de flyttade `.py`-filerna.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `results/**`, `tmp/**`.
- Before-gates: pass.
- After-gates: pass.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D3I är införd som move-only för tre testscript.
- D3 övergripande scope är fortsatt föreslaget kandidatvis.
