# Daily Summary — 2025-12-26

## Fokus

Hårda HTF Fibonacci-context (producer) och HTF-exit consumer så att:

- "Invalid swing"-loggspam försvinner (ersätts av tydliga reason-codes)
- HTF-context blir strikt AS-OF / no-lookahead
- producer/consumer följer samma schema
- Optuna smoke kan köras utan risk för champion promotion

## Genomfört

### HTF Fibonacci context: strikt validering + no-lookahead

I `src/core/indicators/htf_fibonacci.py`:

- Timeframe-normalisering + alias (t.ex. `60m → 1h`).
- Krav på `reference_ts` för att returnera HTF-context (ingen implicit "ta senaste" HTF-raden).
- Kompletthet för fib-nivåer: kräver $0.382, 0.5, 0.618, 0.786$.
- Bounds sanity för swing (finite, low < high).
- Kontroller att nivåer ligger inom swing-bounds.
- Tydliga `reason`-koder + metadata (t.ex. `missing_levels`).

### Mapping: korrekt HTF age

I `compute_htf_fibonacci_mapping(...)`:

- `htf_data_age_hours` beräknas från matchad HTF timestamp (AS-OF merge) istället för felaktigt från första HTF-raden.

### HTF exit engine: schema alignment + frusen context uppdateras

I `src/core/backtest/htf_exit_engine.py`:

- Läs producer-schemat (`swing_high/swing_low`, `last_update`) och behåll backward-compat där det behövs.
- Inkludera 0.786 i exit-levels.
- När swing uppdateras (DYNAMIC/HYBRID): uppdatera även frusen `position.exit_ctx["fib"]`/`swing_bounds`/`swing_id` så efterföljande barer inte kör med stale context.
- Re-validera direkt efter swing update innan exit-check fortsätter.

## Optuna smoke

Ny smoke-konfig:

- `config/optimizer/tBTCUSD_1h_optuna_smoke_htf_fix.yaml`
- Explicit: `promotion.enabled: false` (säker mot oavsiktlig champion-uppdatering)
- Kort sample-range och in-memory storage

## Tester / verifiering

- Full `pytest -q` grön.
- Optuna smoke körd (3 trials) med promotion avstängd.
- Logg-/resultatsökning efter "Invalid swing" visade 0 relevanta träffar efter fixen.

## Nya/uppdaterade reason-codes (HTF context)

Exempel på reason-codes som nu används i HTF-context för att undvika otydlig "Invalid swing":

- `HTF_MISSING_REFERENCE_TS`
- `HTF_TIMEFRAME_MISSING`
- `HTF_NOT_APPLICABLE`
- `HTF_LEVELS_INCOMPLETE`
- `HTF_INVALID_SWING_BOUNDS`
- `HTF_LEVELS_OUT_OF_BOUNDS`

## Uppföljning

- Håll fib-dokumentationen synkad med producer/consumer-schemat och reason-codes.
- Vid framtida HTF-relaterade regressions: börja med att kontrollera `reason` i HTF-context innan man jagar "Invalid swing" i logs.
