# Repo Cleanup D3B Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/debug_htf_exit_usage.py` (move)
- `scripts/debug_mcp_tunnel.py` (move)
- `scripts/debug_strategy_signals.py` (move)
- `scripts/archive/debug/2026-02-14/debug_htf_exit_usage.py` (new path)
- `scripts/archive/debug/2026-02-14/debug_mcp_tunnel.py` (new path)
- `scripts/archive/debug/2026-02-14/debug_strategy_signals.py` (new path)
- `docs/ops/REPO_CLEANUP_D3B_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3B_EXEC_REPORT_2026-02-14.md`
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
- Historiska docs/changelog uppdateras inte i D3B; referenspåverkan dokumenteras i rapport.
- Inga runtime/API/config-ändringar.

## Done criteria

1. Exakt 3 script flyttade till `scripts/archive/debug/2026-02-14/`.
2. Rename-integritet verifierad i diff.
3. D3B kontrakt + exekveringsrapport dokumenterade.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i de 3 flyttade filerna.
3. Docs-impact gate: rapport listar känd referensdrift/usage-impact.
4. Opus diff-audit: APPROVED.

## Status

- D3B i detta kontrakt är kandidatvis destruktiv flytt av refererade debug-script.
