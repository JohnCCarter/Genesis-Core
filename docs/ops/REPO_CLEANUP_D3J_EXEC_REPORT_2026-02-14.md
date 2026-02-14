# Repo Cleanup D3J Execution Report (2026-02-14)

## Syfte

Genomföra kandidatvis flytt av ett diagnose-script med måttlig extern referensyta.

## Flyttat script (move-only)

1. `scripts/diagnose_fib_flow.py`

Ny path:

- `scripts/archive/debug/2026-02-14/diagnose_fib_flow.py`

## Känd docs-referenspåverkan

Följande docs nämner tidigare script-path eller scriptnamn och uppdateras inte i D3J:

- `docs/daily_summaries/daily_summary_2025-11-17.md`
- `docs/bugs/FELSÖKNING_HANDOFF_2025-11-20.md`

Notering: historiska docs-referenser i `docs/archive/**` för detta script = 0 vid D3J-körning.

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

Verifierbar gate-evidens (exitkoder):

- BEFORE: `black=0`, `ruff=0`, `smoke_import_optuna=0`, `smoke_determinism=0`, `feature_cache_invariance=0`, `pipeline_fast_hash_guard=0`
- AFTER: `black=0`, `ruff=0`, `smoke_import_optuna=0`, `smoke_determinism=0`, `feature_cache_invariance=0`, `pipeline_fast_hash_guard=0`

## Verifiering

- Scope gate: endast kontrakterade filer i diff.
- Rename-diff verifierad för flytten.
- Move-only verifierad: inga kodhunks i flyttad `.py`-fil.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `results/**`, `tmp/**`.
- Before-gates: pass.
- After-gates: pass.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D3J är införd som move-only för ett diagnose-script.
- D3 övergripande scope är fortsatt föreslaget kandidatvis.
