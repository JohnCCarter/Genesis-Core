# Debug support (repro + root cause)

## Skill-ID

`debug_skill`

## Syfte

Styr debug-arbete mot reproducerbara steg, tydliga hypoteser och verifiering av rotorsak.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: debug, stabilization, quality

## Regler

### Måste

- Skapa reproducerbara steg innan fix.
- Formulera hypotes och verifiera rotorsak.
- Lägg till test eller mätpunkt när buggen är fixad.

### Får inte

- Gissa utan verifiering.
- Maskera fel med tyst exception-hantering.
- Lämna debug-logik utan borttagning eller dokumentation.

## Referenser

- doc: docs/bugs
