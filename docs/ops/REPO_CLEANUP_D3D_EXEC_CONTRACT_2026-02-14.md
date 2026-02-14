# Repo Cleanup D3D Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/diagnose_execution_layer_gap.py` (move)
- `scripts/diagnose_ml_probas.py` (move)
- `scripts/test_frozen_exit_context.py` (move)
- `scripts/archive/debug/2026-02-14/diagnose_execution_layer_gap.py` (new path)
- `scripts/archive/debug/2026-02-14/diagnose_ml_probas.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_frozen_exit_context.py` (new path)
- `docs/ops/REPO_CLEANUP_D3D_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3D_EXEC_REPORT_2026-02-14.md`
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

## Done criteria

1. Exakt 3 script flyttade till målpaths med rename-integritet.
2. D3D kontrakt + exekveringsrapport dokumenterade.
3. AGENTS uppdaterad kandidatvis utan claim om full D3-slutförande.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i de 3 flyttade filerna.
3. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
4. Opus diff-audit: APPROVED.

## Status

- D3D i detta kontrakt är kandidatvis destruktiv flytt av tre lågrefererade script.
