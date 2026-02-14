# Repo Cleanup P0 Contract (2026-02-14)

## Category

`docs`

## Scope IN

- `.github/copilot-instructions.md`
- `docs/OPUS_46_GOVERNANCE.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`
- `docs/history/AGENTS_HISTORY.md`
- `docs/ops/ROOT_ARTIFACT_INVENTORY_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P0_CONTRACT_2026-02-14.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/runtime*.json`
- `results/**` (ingen flytt/radering i P0)
- `archive/**` (ingen destruktiv åtgärd i P0)
- `tmp/**` (ingen destruktiv åtgärd i P0)

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Inga ändringar i defaults, sortering, numerik, seeds eller cache keys.
- Inga ändringar i endpoint paths, status codes eller response shapes.
- Inga ändringar i env/config-tolkning eller config authority paths.
- Ingen opportunistisk städning utanför Scope IN.

## Done criteria

1. Styrdokument harmoniserade utan kontradiktoriska agentregler.
2. `AGENTS.md` uppdelad i aktiv guide + historikpekare.
3. Root-artefakter inventerade och klassificerade (ingen destruktiv åtgärd).
4. Opus diff-audit utförd med scope-kontroll.

## Gates (docs-only)

1. Scope gate: endast Scope IN-filer ändrade.
2. Terminologi gate: `föreslagen` vs `införd` korrekt.
3. Source-of-truth gate: samma prioritering i styrdokument.
4. Opus diff-audit: inga out-of-scope eller behavior flags.

## Status

- `results/**`: föreslagen policy, ingen genomförd flytt/radering i P0.
- Root-artefakter: inventering införd i separat dokument.
