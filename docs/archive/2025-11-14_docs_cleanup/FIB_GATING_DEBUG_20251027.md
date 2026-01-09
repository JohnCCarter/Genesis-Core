# FIB gating debug 2025-10-27

## Bakgrund

- `tmp_champion_clone.json` gav identiska resultat (+4.85 %, 77 trades) oavsett fib justeringar.
- `tmp_reason_counts.py` visade att 100 % av besluten blockerades av `HTF_FIB_UNAVAILABLE`.
- `htf_fibonacci`-featuren returnerade `{available: False, reason: NO_HTF_DATA}`; standardpolicyn `block` stoppade all handel innan nivåkontroll.

## Åtgärder

1. Flyttade hela override-konfigurationen in under `cfg` så att runtime-mergen respekterar fib-inställningarna.
2. Satte `htf_fib.entry.missing_policy = "pass"` och `ltf_fib.entry.missing_policy = "pass"` för att släppa igenom trades när fib-data saknas.
3. Verifierade med `python tmp_reason_counts.py --config tmp_champion_clone.json`:
   - Första körningen (före fix) ➜ `NONE: 200`, `HTF_FIB_UNAVAILABLE: 169`.
   - Efter fix ➜ `LONG: 93`, `SHORT: 19`; `ltf_fib_debug` visar faktiska nivåer och `reason: PASS`.
4. Kör backtest `python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2024-10-27 --end 2025-10-27 --config-file tmp_champion_clone.json --no-save`.

## Resultat

- Före fix: +4.85 %, 77 trades, PF 1.78.
- Efter fix: +34.85 %, 58 trades, PF 2.86, max DD 5.80 %.
- Partials triggas nu vid fib-targets; risk_map + fib-gate ger faktisk effekt.

## Uppdatering 2025-10-27 kväll

- Införde adaptiv svängdetektion i `core/indicators/fibonacci.py` (relaxerad ATR-tröskel, fallback till prefix-extrema).
- `compute_htf_fibonacci_levels` i `core/indicators/htf_fibonacci.py` fyller nu nivåer AS-OF från första 1D-baren (2020-11-23 i `tBTCUSD_1D.parquet`).
- `tmp_reason_counts.py` visar enstaka `HTF_FIB_UNAVAILABLE` (1 av 200) i stället för total blockering.
- Backtest 2024-10-01→2025-10-27 (`tmp_champion_clone.json`) levererar +18.46 %, PF 2.39 med HTF-data aktiv.
- Bandit-fix: bytte cache-nyckel i `core/optimizer/runner.py` till `hashlib.sha256`.

## Nästa steg

- Utreda varför `htf_fibonacci` saknar data (troligen featurepipelinen för 1h ➜ `NO_HTF_DATA`).
- Testa striktare toleranser/targetlistor när feature-feeden är löst.
- Kör jämförelse mot aggressiva profilen för att kvantifiera fib bidrag.

## HTF-dataanalys

- Körning `python -c "... compute_htf_fibonacci_levels ..."` visade att de första dagarna i `tBTCUSD_1D.parquet` (start 2024-10-16) saknar swings och ger `htf_fib_* = NaN` samt negativa `htf_swing_age_bars`.
- Därför returnerar `get_htf_fibonacci_context` `{'available': False, 'reason': 'NO_HTF_DATA'}` tills tillräckligt många 1D-barer ackumulerats efter dataset-starten.
- Möjliga fixes:
   1. Ladda längre HTF-historik (behöver äldre 1D-data i `data/curated/v1/candles`).
   2. Lägga fallback i `compute_htf_fibonacci_levels` som räknar nivåer från senaste high/low även utan pivots.
   3. Tillfälligt kräva `missing_policy: "pass"` (nu aktivt) så att signaler inte blockeras medan vi adresserar databristen.
