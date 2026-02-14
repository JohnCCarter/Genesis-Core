# Repo Cleanup D3C Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/test_abort_heuristic.py` (move)
- `scripts/test_deep_merge.py` (move)
- `scripts/test_local_keepalive.py` (move)
- `scripts/test_model_on_training_data.py` (move)
- `scripts/test_post_local.py` (move)
- `scripts/test_sse_local.py` (move)
- `scripts/test_static_frozen_exits.py` (move)
- `scripts/archive/test_prototypes/2026-02-14/test_abort_heuristic.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_deep_merge.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_local_keepalive.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_model_on_training_data.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_post_local.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_sse_local.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_static_frozen_exits.py` (new path)
- `docs/ops/REPO_CLEANUP_D3C_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3C_EXEC_REPORT_2026-02-14.md`
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
- Move-only: inga innehållsändringar i de 7 `.py`-filerna.
- Inga runtime/API/config-ändringar.

## Done criteria

1. Exakt 7 script flyttade till `scripts/archive/test_prototypes/2026-02-14/`.
2. Rename-integritet verifierad i diff.
3. D3C kontrakt + exekveringsrapport dokumenterade.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i de 7 flyttade filerna.
3. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
4. Opus diff-audit: APPROVED.

## Status

- D3C i detta kontrakt är kandidatvis destruktiv flytt av lågkopplade testprototyper.
