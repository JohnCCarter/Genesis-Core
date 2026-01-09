# HTF "Invalid swing" hardening (2025-12-26)

## Problem

I HTF Fibonacci exit-flödet kunde loggar spamma med "Invalid swing" i vissa marknadslägen.

Det var i praktiken en mix av:

- **Osunda swing-bounds** (t.ex. `swing_high <= swing_low`, NaN/inf)
- **Schema-mismatch** mellan producer (HTF context) och consumer (exit engine)
- **Implicit lookahead** när HTF-context togs fram utan `reference_ts` ("ta senaste" HTF-raden)

Konsekvens: brusiga loggar, svårare felsökning, och risk för att exit-logik körde med stale/inkonsistent context.

## Fix (sammanfattning)

### Producer: `src/core/indicators/htf_fibonacci.py`

- **Strict AS-OF / no-lookahead**: returnerar inte HTF-context utan `reference_ts`.
- **Timeframe-normalisering + alias** (ex. `60m → 1h`).
- **Levels completeness**: kräver nivåerna 0.382/0.5/0.618/0.786.
- **Bounds sanity**: swing bounds måste vara finita och `low < high`.
- **Levels-in-bounds**: fib-nivåer måste ligga inom bounds.
- **Reason codes** i context när HTF inte kan användas:
  - `HTF_MISSING_REFERENCE_TS`
  - `HTF_LEVELS_INCOMPLETE` (+ `missing_levels`)
  - `HTF_INVALID_SWING_BOUNDS`
  - `HTF_LEVELS_OUT_OF_BOUNDS`

### Mapping: korrekt `htf_data_age_hours`

- Beräknas från matchad HTF timestamp (AS-OF merge) i stället för från första HTF-raden.

### Consumer: `src/core/backtest/htf_exit_engine.py`

- Alignad mot producer-schemat (`swing_high/swing_low`, `last_update`).
- Inkluderar 0.786 i exit-levels.
- Vid swing updates (DYNAMIC/HYBRID): uppdaterar även frusen `position.exit_ctx` så kommande barer inte använder stale context.

## Reproduktion / verifiering

### Tester

Se regressionstester:

- `tests/test_htf_fibonacci_*`
- `tests/test_htf_exit_engine_*`

### Optuna smoke (säker)

`config/optimizer/tBTCUSD_1h_optuna_smoke_htf_fix.yaml`

- Promotion är explicit avstängd (`promotion.enabled: false`).

## Debug tips

Om HTF-exits inte triggar eller fallback används mycket:

1. Kontrollera `reason` i HTF-context (inte "Invalid swing"-strängar).
2. Kontrollera att `reference_ts` verkligen skickas i call chain.
3. Verifiera att fib-nivåer är kompletta och inom bounds.

## Relaterade dokument

- `docs/fibonacci/HTF_FIBONACCI_EXITS_SUMMARY.md`
- `docs/fibonacci/HTF_EXIT_CONTEXT_BUG.md`
- `docs/daily_summaries/daily_summary_2025-12-26.md`
