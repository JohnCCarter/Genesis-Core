# Vectorized Parity Checklist

1. **Precompute features**
   - Kör `scripts/precompute_features_fast.py --symbol tBTCUSD --timeframe 1h`
   - Spara Feather/Parquet till `data/archive/features/`

2. **Kör paritetskoll**
   - `python scripts/validate_vectorized_features.py --symbol tBTCUSD --timeframe 1h --samples 500 --tolerance 1e-5`
   - Kör `pytest tests/test_vectorized_features.py::test_vectorized_features_parity_tbtc_usd_1h`
   - Innan `--use-vectorized` aktiveras i längre backtests: verifiera att vald cache-version matchar bästa parity-run (t.ex. `v17`).
   - Kontrollera output: `max_diff == 0` för alla features

3. **Utöka tester**
   - PyTest-case som matar samma candles via `_extract_asof()` och vectorized-cache
   - Säkerställ att `features`, `meta`, `state_out` matchar (inkl. fib-context)

4. **Diagnostik vid mismatch**
   - Logga bar-index och feature-namn
   - Jämför HTF/LTF meta och ATR percentiler
   - Åtgärda, kör om skriptet

5. **Automatisering**
   - Lägg till parity-check i CI när toggle aktiveras första gången
   - Dokumentera avvikelselogg i `docs/vectorized/`
