# Repo Cleanup D3A Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/debug_config_merge.py` (move)
- `scripts/debug_decision_pipeline.py` (move)
- `scripts/debug_htf_loading.py` (move)
- `scripts/debug_model_bias.py` (move)
- `scripts/debug_param_transforms.py` (move)
- `scripts/debug_swing_detection.py` (move)
- `scripts/archive/debug/2026-02-14/debug_config_merge.py` (new path)
- `scripts/archive/debug/2026-02-14/debug_decision_pipeline.py` (new path)
- `scripts/archive/debug/2026-02-14/debug_htf_loading.py` (new path)
- `scripts/archive/debug/2026-02-14/debug_model_bias.py` (new path)
- `scripts/archive/debug/2026-02-14/debug_param_transforms.py` (new path)
- `scripts/archive/debug/2026-02-14/debug_swing_detection.py` (new path)
- `docs/ops/REPO_CLEANUP_D3A_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3A_EXEC_REPORT_2026-02-14.md`
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

- Explicit behavior-change exception gäller endast filplacering för listade debug-script.
- Move-only: inga innehållsändringar i de 6 `.py`-filerna.
- Refererade debug-script (`debug_htf_exit_usage.py`, `debug_mcp_tunnel.py`,
  `debug_strategy_signals.py`) ingår inte i D3A.

## Done criteria

1. Exakt 6 script flyttade till `scripts/archive/debug/2026-02-14/`.
2. Rename-integritet verifierad i diff.
3. D3A kontrakt + exekveringsrapport dokumenterade.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Move-only gate: inga kodhunks i de 6 flyttade filerna.
3. No-code-drift gate: inga ändringar i runtime-/API-/config-zoner.
4. Opus diff-audit: APPROVED.

## Status

- D3A i detta kontrakt är en kandidatvis destruktiv flytt med låg referensrisk.
