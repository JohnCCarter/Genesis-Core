# Repo Cleanup D3H Execution Report (2026-02-14)

## Syfte

Genomföra kandidatvis flytt av ett testscript med måttlig extern referensyta.

## Flyttat script (move-only)

1. `scripts/test_rest_public.py`

Ny path:

- `scripts/archive/test_prototypes/2026-02-14/test_rest_public.py`

## Känd docs-referenspåverkan

Följande docs nämner tidigare script-path eller scriptnamn och uppdateras inte i D3H:

- `docs/features/GENESIS-CORE_FEATURES.md`
- `docs/ops/SHARE.md`
- `docs/archive/README_2025-10-07_pre-phase3.md`
- `docs/archive/SHARE_overview.md`
- `docs/archive/GENESIS-CORE_FEATURES_phase1-4.md`

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_backtest_hook_invariants.py -q`

## Verifiering

- Scope gate: endast kontrakterade filer i diff.
- Rename-diff verifierad för flytten.
- Move-only verifierad: inga kodhunks i flyttad `.py`-fil.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `results/**`, `tmp/**`.
- Before-gates: pass.
- After-gates: pass.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D3H är införd som move-only för ett testscript.
- D3 övergripande scope är fortsatt föreslaget kandidatvis.
