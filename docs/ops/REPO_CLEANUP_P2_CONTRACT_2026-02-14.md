# Repo Cleanup P2 Contract (2026-02-14)

## Category

`docs`

## Scope IN

- `docs/ops/REPO_CLEANUP_P2_CONTRACT_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `scripts/**`
- `config/**`
- `.github/agents/**`
- `results/**`
- `archive/**`
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- P2 i detta kontrakt är **planeringsfas** och är icke-destruktiv.
- Inga flyttar eller raderingar av filer/kataloger i P2 under detta kontrakt.
- Inga ändringar i runtime-logik, API-kontrakt, config-tolkning eller CI-blockering.
- Statusdisciplin ska följa `föreslagen`/`införd` enligt governance-dokument.

## Done criteria

1. P2-kontrakt dokumenterar non-destructive läge explicit.
2. Förutsättningar för framtida destruktiv fas är tydligt definierade:
   - retention policy,
   - dry-run med verifierbar output,
   - explicit godkännande innan utförande.
3. `AGENTS.md` reflekterar att P2 är planerad/`föreslagen`, inte införd destruktiv städning.
4. Opus post-code diff-audit godkänd.

## Gates (docs-only)

1. Scope gate: endast Scope IN-filer ändrade.
2. Terminologi gate: korrekt användning av `föreslagen` och `införd`.
3. Non-destructive gate: inga claims om utförd flytt/radering i P2.
4. Opus diff-audit: APPROVED.

## Status

- P2-destructive cleanup är fortsatt **föreslagen** och kräver separat kontrakt.
- Ingen flytt/radering är införd under detta kontrakt.
