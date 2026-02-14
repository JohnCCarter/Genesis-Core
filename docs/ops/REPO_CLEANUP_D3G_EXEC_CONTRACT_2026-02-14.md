# Repo Cleanup D3G Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/test_htf_simple_validation.py` (move)
- `scripts/test_optuna_cache_reuse.py` (move)
- `scripts/archive/test_prototypes/2026-02-14/test_htf_simple_validation.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_optuna_cache_reuse.py` (new path)
- `docs/ops/REPO_CLEANUP_D3G_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3G_EXEC_REPORT_2026-02-14.md`
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
- Move-only: inga innehållsändringar i de 2 `.py`-filerna.
- Inga runtime/API/config-ändringar.
- Historiska docs-referenser uppdateras inte i D3G; påverkan dokumenteras i rapporten.

## Done criteria

1. Exakt 2 script flyttade till målpaths med rename-integritet.
2. D3G kontrakt + exekveringsrapport dokumenterade.
3. AGENTS uppdaterad kandidatvis utan claim om full D3-slutförande.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i de 2 flyttade filerna.
3. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
4. Opus diff-audit: APPROVED.

## Status

- D3G i detta kontrakt är kandidatvis destruktiv flytt av två testscript med låg referensyta.
