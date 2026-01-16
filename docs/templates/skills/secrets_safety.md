# Secrets safety (no leaks)

## Skill-ID

`secrets_safety`

## Syfte

Skyddar mot att hemligheter hamnar i repo eller loggar och kräver env-baserade nycklar.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: security, secrets

## Regler

### Måste

- Använd endast miljövariabler för API-nycklar.
- Redigera loggar för att inte exponera hemligheter.
- Se till att .env och lokala overrides är gitignored.

### Får inte

- Lägg in secrets i kod, testdata eller resultatfiler.
- Skriv ut raw headers eller signaturer i loggar.
- Commit:a .env eller lokala override-filer.

## Referenser

- doc: README.md
- file: .gitignore
