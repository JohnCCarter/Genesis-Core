# Python engineering (3.11+)

## Skill-ID

`python_engineering`

## Syfte

Kodstandard för Genesis-Core: typade funktioner, små diffar, ruff/black/pytest först, och inga hemligheter i repo.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: python, quality, stabilization

## Regler

### Måste

- Använd Python 3.11+ och moderna type hints (X | None).
- Skriv enhetstester för ny logik.
- Kör ruff + pytest innan merge.

### Får inte

- Lägg aldrig in secrets i repo (.env ska vara gitignored).
- Skapa inte experimentell kod på mainline utan specifikation.
