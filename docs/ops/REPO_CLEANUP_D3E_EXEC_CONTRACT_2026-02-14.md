# Repo Cleanup D3E Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/diagnose_cooldown_vetoes.py` (move)
- `scripts/diagnose_execution_gap_v2.py` (move)
- `scripts/diagnose_feature_parity.py` (move)
- `scripts/test_6h_original_model.py` (move)
- `scripts/test_exit_fibonacci.py` (move)
- `scripts/archive/debug/2026-02-14/diagnose_cooldown_vetoes.py` (new path)
- `scripts/archive/debug/2026-02-14/diagnose_execution_gap_v2.py` (new path)
- `scripts/archive/debug/2026-02-14/diagnose_feature_parity.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_6h_original_model.py` (new path)
- `scripts/archive/test_prototypes/2026-02-14/test_exit_fibonacci.py` (new path)
- `docs/ops/REPO_CLEANUP_D3E_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3E_EXEC_REPORT_2026-02-14.md`
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
- Move-only: inga innehållsändringar i de 5 `.py`-filerna.
- Inga runtime/API/config-ändringar.
- Historiska docs-referenser uppdateras inte i D3E; påverkan dokumenteras i rapporten.

## Done criteria

1. Exakt 5 script flyttade till målpaths med rename-integritet.
2. D3E kontrakt + exekveringsrapport dokumenterade.
3. AGENTS uppdaterad kandidatvis utan claim om full D3-slutförande.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i de 5 flyttade filerna.
3. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
4. Opus diff-audit: APPROVED.

## Status

- D3E i detta kontrakt är kandidatvis destruktiv flytt av fem script med låg referensyta.
