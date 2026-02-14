# Repo Cleanup D3H Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/test_rest_public.py` (move)
- `scripts/archive/test_prototypes/2026-02-14/test_rest_public.py` (new path)
- `docs/ops/REPO_CLEANUP_D3H_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3H_EXEC_REPORT_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `results/**`
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Explicit behavior-change exception gäller endast filplacering för listat script.
- Move-only: inga innehållsändringar i `scripts/test_rest_public.py`.
- Inga runtime/API/config-ändringar.
- Befintliga docs-referenser (aktiva + historiska) uppdateras inte i D3H; påverkan dokumenteras i rapporten.

## Required gates (BEFORE + AFTER)

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_backtest_hook_invariants.py -q`

## Done criteria

1. Exakt 1 script flyttat till målpath med rename-integritet.
2. D3H kontrakt + exekveringsrapport dokumenterade.
3. AGENTS uppdaterad kandidatvis utan claim om full D3-slutförande.
4. Required gates passerar både före och efter.
5. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i flyttad fil.
3. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
4. Before/after gate-suite: pass.
5. Opus diff-audit: APPROVED.

## Status

- D3H i detta kontrakt är kandidatvis destruktiv flytt av ett testscript med måttlig referensyta.
