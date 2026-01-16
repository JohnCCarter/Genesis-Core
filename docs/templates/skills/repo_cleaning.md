# Repo cleaning (safe + tracked)

## Skill-ID

`repo_cleaning`

## Syfte

Säker repo-rensning som undviker att radera spårbar data och följer .gitignore/regler.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: maintenance, cleanup, stabilization

## Regler

### Måste

- Verifiera att filer är cache/artefakter innan borttagning.
- Respektera .gitignore och känsliga filer.
- Dokumentera borttagna filer om de påverkar spårbarhet.

### Får inte

- Radera results/backtests eller reports utan explicit beslut.
- Ta bort data som krävs för reproducerbarhet.
- Rensa okända filer utan att kontrollera innehåll.

## Referenser

- file: .gitignore
- doc: AGENTS.md
