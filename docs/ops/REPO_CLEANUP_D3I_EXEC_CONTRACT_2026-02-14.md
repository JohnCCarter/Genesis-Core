# Repo Cleanup D3I Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/test_htf_exit_engine.py` (move)
- `scripts/test_htf_fibonacci_mapping.py` (move)
- `scripts/test_partial_exit_infrastructure.py` (move)
- `scripts/archive/test_prototypes/2026-02-14/test_htf_exit_engine.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_htf_fibonacci_mapping.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_partial_exit_infrastructure.py` (new path)
- `docs/ops/REPO_CLEANUP_D3I_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3I_EXEC_REPORT_2026-02-14.md`
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

- Explicit behavior-change exception gäller endast filplacering för listade script.
- Move-only: inga innehållsändringar i de 3 `.py`-filerna.
- Inga runtime/API/config-ändringar.
- Befintliga docs-referenser (aktiva + historiska) uppdateras inte i D3I; påverkan dokumenteras i rapporten.
- Path-kollision för `test_htf_exit_engine.py` (`scripts/` vs `tests/`) ska explicit noteras i rapporten.

## Required gates (BEFORE + AFTER)

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Exakt 3 script flyttade till målpaths med rename-integritet.
2. D3I kontrakt + exekveringsrapport dokumenterade.
3. AGENTS uppdaterad kandidatvis utan claim om full D3-slutförande.
4. Required gates passerar både före och efter.
5. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i de 3 flyttade filerna.
3. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
4. Before/after gate-suite: pass.
5. Opus diff-audit: APPROVED.

## Status

- D3I i detta kontrakt är kandidatvis destruktiv flytt av tre testscript med måttlig referensyta.
