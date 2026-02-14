# Repo Retention Policy (Draft, 2026-02-14)

## Status

Denna policy är **föreslagen** och inte enforcement i nuläget.

Ingen automatisk radering, flytt eller CI-blockering införs av detta dokument.

## Syfte

Skapa en konsekvent, verifierbar grund för framtida cleanup av stora artefakt-ytor,
utan att påverka runtime-beteende eller reproducibilitet.

## Principer

1. Safety first: inga destruktiva åtgärder utan explicit godkännande.
2. Reproducibility first: behåll artefakter som krävs för att förklara beslut och jämförelser.
3. Determinism i processen: dry-run först, mätbar output, sedan beslut.
4. Små steg: en artefaktklass per destruktiv commit-kontrakt.

## Retention-klasser (föreslagen klassning)

### Klass R1 — Kärnartefakter (behåll)

Exempel:

- Kontrakt, governance och beslutande dokument under `docs/ops/`.
- Champion-/valideringsunderlag som används i aktiva beslut.

Policy:

- Behåll som standard.
- Ingen tidsbaserad purge i draft-läge.

### Klass R2 — Operativa mellanartefakter (kandidater för arkivering)

Exempel:

- Delmängder i `results/backtests/*` som inte längre används i aktiv jämförelse.
- Temporära analysutdata i `reports/` och `tmp/` när de ersatts av sammanfattning.

Policy:

- Kandidater för flytt till definierad archive-struktur efter godkänd dry-run.
- Flytt (inte radering) prioriteras i första destruktiva fas.

### Klass R3 — Scratch/engångsartefakter (kandidater för radering)

Exempel:

- Tydligt engångsfiler i repo-roten som klassats i inventeringen.
- Duplikata debug/scratch-utdata med verifierad ersättningskälla.

Policy:

- Endast efter retention-beslut + dry-run + explicit godkännande.
- Radering ska vara återställbar via git-historik/backup-policy.

## Operativ tillämpning (föreslagen)

Innan någon destruktiv cleanup:

1. Upprätta separat commit-kontrakt med exakt Scope IN/OUT.
2. Kör dry-run och publicera rapport med filantal + paths.
3. Kör Opus pre-code + diff-audit.
4. Inhämta explicit godkännande.
5. Genomför i små, spårbara commits.

## Out of scope i detta draft-dokument

- Ingen faktisk flytt/radering.
- Inga ändringar av runtime, API, config authority paths.
- Ingen ändring av .gitignore/CI som blockerar builds.
