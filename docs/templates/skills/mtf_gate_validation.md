# MTF gate validation (HTF/LTF coverage)

## Skill-ID

`mtf_gate_validation`

## Syfte

Kontrollerar att HTF/LTF-kontext finns och att gate-logik inte är inaktiv p.g.a. saknade nivåer.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: mtf, fib, validation

## Regler

### Måste

- Verifiera HTF- och LTF-täckning i aktuellt fönster innan gates tolkas.
- Logga om HTF/LTF saknas och ange varför (t.ex. NaNs eller saknade candles).
- Använd samma fönster vid A/B av gate-ändringar.

### Får inte

- Tolka gate-effekt när HTF/LTF inte är tillgängligt.
- Blanda fönster före/efter HTF-datatillgänglighet.
- Ignorera missing_policy när gates är aktiva.

## Referenser

- file: src/core/strategy/features_asof.py
- file: src/core/strategy/decision.py
