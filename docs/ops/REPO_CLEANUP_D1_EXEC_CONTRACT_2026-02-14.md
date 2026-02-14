# Repo Cleanup D1 Execution Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `DEV_MARKER.txt` (move)
- `burnin_summary.json` (move)
- `candles.json` (move)
- `archive/_orphaned/root_artifacts/2026-02-14/DEV_MARKER.txt` (new path)
- `archive/_orphaned/root_artifacts/2026-02-14/burnin_summary.json` (new path)
- `archive/_orphaned/root_artifacts/2026-02-14/candles.json` (new path)
- `docs/ops/REPO_CLEANUP_D1_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D1_EXEC_REPORT_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `scripts/**`
- `config/**`
- `.github/**`
- `results/**`
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Explicit behavior-change exception gäller endast filplacering för tre root-artefakter.
- Flytt är **move-only** (ingen innehållsändring i artefaktfiler).
- Inga kod-, script-, runtime-, API- eller config-ändringar.

## Done criteria

1. Exakt tre root-artefakter flyttade till archive-path.
2. Rename-integritet verifierad (`R100` / identiska blob-hashar).
3. D1 exekveringsrapport dokumenterar scope och verifiering.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer berörda.
2. Rename gate: tre artefaktflyttar med oförändrat innehåll.
3. No-code gate: inga ändringar i `src/**`, `tests/**`, `scripts/**`, `config/**`.
4. Opus diff-audit: APPROVED.

## Status

- D1 i detta kontrakt är genomförd som minimal move-only exekvering.
- Eventuella ytterligare destruktiva steg kräver separat kontrakt.
