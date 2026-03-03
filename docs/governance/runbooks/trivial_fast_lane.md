# Trivial Fast Lane (Quick Path)

Mål: hålla triviala uppgifter snabba utan att tumma på governance.

## Eligibility (alla måste vara sanna)

- Max 2 filer ändras
- Endast docs/comments/metadata/editor-config
- Ingen runtime/API/config-semantik ändras
- Ingen high-sensitivity-zon berörs

Om minsta tvekan finns: eskalera till Lite/Full path.

## Forbidden touches (auto-stop)

- Om någon HIGH-zon berörs i Quick Path ⇒ `STOP_CONDITION`
- Om `config/strategy/champions/**` eller freeze guard berörs ⇒ alltid HIGH + Full/STRICT

## Minimal process

1. Bekräfta eligibility
2. Applicera minimal diff
3. Kör riktad check (t.ex. pre-commit på berörda filer)
4. Självgranska för dold behaviorpåverkan
5. Rapportera kort Implementation Report

## Merge policy

- Merge sker via normal PR-flöde med branch protection/checks
- Ingen bypass merge

## Ready-krav

- Scope håller
- Inga forbidden touches
- Nödvändig kontroll grön
- Evidens med i PR/rapport
