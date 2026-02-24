# Repo clean/refactor (no behavior change)

## Skill-ID

`repo_clean_refactor`

## Syfte

Säkerställer att repo-cleanup och strukturrefaktoreringar sker med strikt scope, minimal diff, verifieringsgates och tydlig rollback-plan.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: cleanup, refactor, governance, stabilization

## Regler

### Måste

- Skapa commit-kontrakt med Scope IN/OUT och default NO BEHAVIOR CHANGE innan implementation.
- Inventera ändringsvolym (antal filer, storlek, toppmappar) innan åtgärd.
- Exkludera high-sensitivity-zoner om inte explicit godkända.
- Håll diffen minimal och reversibel (preferera ignore + avindexering framför destruktiva raderingar).
- Kör relevanta verifieringsgates före och efter ändring.
- Rapportera exakt vad som ändrats, varför, och hur det återställs vid behov.

### Får inte

- Inför inte beteendeförändring i runtime-kod under cleanup/refactor utan explicit undantag.
- Gör inte opportunistiska sidostädningar utanför godkänd scope.
- Radera inte användardata eller resultatfiler utan spårbar policy och explicit beslut.
- Claima inte införda processförändringar som blockerande utan verifierad konfiguration.
