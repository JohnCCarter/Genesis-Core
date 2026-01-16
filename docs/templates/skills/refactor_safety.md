# Refactor safety (small + tested)

## Skill-ID

`refactor_safety`

## Syfte

Säkerställer att refaktoreringar är små, motiverade och testade utan oavsiktlig beteendeförändring.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: refactor, quality, stabilization

## Regler

### Måste

- Håll refaktoreringar små och fokuserade.
- Lägg till eller uppdatera tester när logik ändras.
- Dokumentera om beteende ändras avsiktligt.

### Får inte

- Ändra beteende utan specifikation.
- Samla flera orelaterade refaktoreringar i samma diff.
- Ta bort validering eller loggning utan ersättning.

## Referenser

- doc: docs/roadmap/STABILIZATION_PLAN_9_STEPS.md
