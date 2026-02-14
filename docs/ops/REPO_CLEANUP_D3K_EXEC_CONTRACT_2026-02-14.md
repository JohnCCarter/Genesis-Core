# Repo Cleanup D3K Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/diagnose_zero_trades.py` (move)
- `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py` (new path)
- `.github/skills/decision_gate_debug.json` (path-reference updates only)
- `docs/ops/REPO_CLEANUP_D3K_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3K_EXEC_REPORT_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `results/**`
- `tmp/**`
- `.github/**` except `.github/skills/decision_gate_debug.json`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Explicit behavior-change exception gäller endast filplacering för listat script och länkad path-uppdatering i scopead skill-fil.
- Move-only: inga innehållsändringar i `scripts/diagnose_zero_trades.py`.
- `.github/skills/decision_gate_debug.json`: endast 2 path-strängar uppdateras.
- Inga runtime/API/config-ändringar.
- Befintliga docs-referenser (aktiva + historiska) uppdateras inte i D3K; påverkan dokumenteras i rapporten.

## Required gates (BEFORE + AFTER)

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Exakt 1 script flyttat till målpath med rename-integritet.
2. Exakt 2 path-referenser uppdaterade i `.github/skills/decision_gate_debug.json`.
3. D3K kontrakt + exekveringsrapport dokumenterade.
4. AGENTS uppdaterad kandidatvis utan claim om full D3-slutförande.
5. Required gates passerar både före och efter.
6. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i flyttad scriptfil.
3. Linked-reference gate: endast 2 path-strängar ändrade i skill-filen.
4. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
5. Before/after gate-suite: pass.
6. Opus diff-audit: APPROVED.

## Status

- D3K i detta kontrakt är kandidatvis destruktiv flytt av ett diagnose-script samt länkad referensjustering i en skill-fil.
