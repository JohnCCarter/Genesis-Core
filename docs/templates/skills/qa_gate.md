# QA gate (ruff + pytest + bandit)

## Skill-ID

`qa_gate`

## Syfte

Tvingar grundläggande QA-körningar innan merge för att skydda stabiliseringsfasen.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: qa, tests, security

## Regler

### Måste

- Kör ruff och pytest före merge.
- Kör bandit mot src/ för säkerhetskontroll.
- Dokumentera om något test är avsiktligt hoppat över.

### Får inte

- Mergas med röda tester.
- Ignorera säkerhetsvarningar utan motivering.
- Hoppa över QA för stabiliseringsrelaterade ändringar.

## Referenser

- doc: docs/dev_setup.md
