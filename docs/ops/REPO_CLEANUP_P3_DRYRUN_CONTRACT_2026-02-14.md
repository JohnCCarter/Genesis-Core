# Repo Cleanup P3 Dry-Run Contract (2026-02-14)

## Category

`docs`

## Scope IN

- `docs/ops/REPO_CLEANUP_P3_DRYRUN_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P3_DRYRUN_SCOPE_2026-02-14.md`
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

- P3 i detta kontrakt är **dry-run only** och är icke-destruktiv.
- Inga flyttar eller raderingar av filer/kataloger genomförs i P3 under detta kontrakt.
- Inga ändringar i runtime-logik, API-kontrakt, config-tolkning eller CI-blockering.
- Terminologi följer `föreslagen`/`införd` enligt governance.

## Done criteria

1. P3-kontrakt dokumenterar dry-run som explicit icke-destruktivt.
2. Scope-dokument definierar kandidatmönster, exkluderingar och acceptance-checks.
3. `AGENTS.md` reflekterar P3 dry-run-scope som `införd` (docs) och destruktiv fas fortsatt `föreslagen`.
4. Opus post-code diff-audit godkänd.

## Gates (docs-only)

1. Scope gate: endast Scope IN-filer ändrade.
2. Non-destructive gate: inga claims om utförd flytt/radering i P3.
3. Terminologi gate: korrekt användning av `föreslagen` och `införd`.
4. Opus diff-audit: APPROVED.

## Status

- P3 dry-run-scope är **införd** som dokumenterad process.
- Destruktiv cleanup är fortsatt **föreslagen** och kräver separat kontrakt + explicit godkännande.
