# HTF Exit Context Bug (2025-10-16)

## Översikt

- **Status:** 🔧 Identifierad och åtgärdad i kod (verifiering pågår)
- **Allvarlighetsgrad:** Hög – slog ut hela HTF-exitlogiken och gav orimliga backtestresultat
- **Berörda delar:**
  - `src/core/strategy/features_asof.py`
  - `src/core/backtest/htf_exit_engine.py`
  - Förberäknade v17-filer (`data/curated/v1/features/...`)
- **Kortfattat:** Vid laddning av förberäknade features (v17) saknades HTF-Fibonacci-kontexten i metadata. HTF-exitmotorn fick därmed `dict` istället för `float` och kastade `TypeError: '<' not supported between instances of 'dict' and 'float'` för varje bar efter entry. Resultatet blev 0 % avkastning och hundratals felutskrifter, trots korrekt v17-modell.

---

## Symptom

1. Körning av `python scripts/test_6h_original_model.py` gav:
   - `[ERROR] Bar 51: '<' not supported between instances of 'dict' and 'float'`
   - Identiska fel på varje efterföljande bar (`Bar 53`, `Bar 54`, ...)
   - Trots fel genererades partial exits (`TP1_0618`, `TP2_05`), men slutresultatet blev **0.00 %** i total avkastning i stället för dokumenterade **+14.10 %**.
2. Logg från HTF-exitmotorn visade att `htf_levels` saknades eller innehöll dictionary-objekt:
   ```
   [DEBUG] HTF not available: {}
   ```
3. Crash inträffade i `_check_trailing_stop()` och `_check_partial_exits()` där historiskt `fib_0382` osv. ska vara floats:
   ```python
   fib_05 = htf_levels.get(0.5)
   fib_0382 = htf_levels.get(0.382)
   if fib_05 and fib_0382 and current_price < fib_0382:
       ...
   ```
   Eftersom `fib_0382` var en `dict` kastades `TypeError` vid jämförelsen.

---

## Rotorsak

- Vid backtest läses features via `extract_features(... now_index=...)`.
- I backtest-läget har vi optimerat för att först **ladda förberäknade v17-features** via `load_features()` i stället för att beräkna dem i realtid.
- Men den kodvägen byggde **inte** upp `htf_fibonacci_context`:
  ```python
  meta = {
      "versions": { ... },
      "htf_fibonacci_context": {},  # Will be populated by HTF logic
  }
  ```
- Därmed såg pipeline-utdata ut så här:
  ```python
  meta["features"]["htf_fibonacci"] == {}
  ```
- När `_initialize_position_exit_context()` försökte läsa `htf_fib_context = features_meta.get("htf_fibonacci", {})` fick vi `{}`.
- Fallbacken skrev ut `[DEBUG] HTF not available: {}` och **returnerade innan** `position.exit_ctx` hann armeras.
- Nästa bar antog exitmotorn att `position.exit_ctx` var korrekt uppsatt och försökte jämföra `dict` mot `float` → `TypeError`.

**TL;DR:** Förberäknade v17-features saknade HTF-metadata, vilket gav ofullständiga exitvärden och tonsvis med `TypeError`.

---

## Åtgärd i koden

1. **`features_asof.py`** – utökad precompute-path:

   ```python
   feature_row = features_df.iloc[now_index]
   features = { ... }

   htf_cols = {
       "levels": {
           0.382: "htf_fib_0382",
           0.5: "htf_fib_05",
           0.618: "htf_fib_0618",
           0.786: "htf_fib_0786",
       },
       "swing_high": "htf_swing_high",
       "swing_low": "htf_swing_low",
       "swing_age_bars": "htf_swing_age_bars",
   }

   if ...:
       htf_fib_context = {
           "available": True,
           "levels": {lvl: float(feature_row[col]) ...},
           "swing_high": float(feature_row[...]),
           ...
           "source": "precomputed",
       }
   else:
       htf_fib_context = {"available": False}

   meta = {
       ...
       "htf_fibonacci_context": htf_fib_context,
   }
   ```

2. Säkerhetskontroll: Om kolumner saknas eller innehåller NaN flaggar vi `available=False`, så exitmotorn faller tillbaka till traditionella exits (utan crash).
3. Ingen ändring i `htf_exit_engine.py` behövdes efter att HTF-kontexten levererades korrekt. (Tidigare debug-utskrifter togs bort.)

---

## Verifiering (pågår)

1. Rebuilda features **(ALLTID)** eller säkerställ att de befintliga v17-parquet/feather-filerna innehåller kolumnerna `htf_fib_0382`, `htf_fib_05`, `htf_fib_0618`, `htf_fib_0786`, `htf_swing_high`, `htf_swing_low`, `htf_swing_age_bars`.
2. Kör `python scripts/test_6h_original_model.py`:
   - Förväntat: inga `TypeError` längre
   - Backtesten ska producera dokumenterade +14.10 % (4 trades, 75 % win rate)
   - Loggen ska visa att HTF-data är `available=True`.
3. Kör gärna `debug_htf_levels.py` för att bekräfta att `get_htf_fibonacci_context()` returnerar rätt struktur när features laddas från disk.

---

## Relaterade dokument

- `docs/6H_BACKTEST_MYSTERY_SOLVED.md` – analyserar varför exit-logik saknades och gav 11 månaders holding
- `docs/EXIT_LOGIC_IMPLEMENTATION.md` – visar hur vi införde SL/TP/time/conf/regime-exits
- `docs/BACKTEST_CRITICAL_BUGS_FIXED.md` – tidigare tvillingbuggar (fel storleksuttag + EV‐bias)
- Denna fil kompletterar ovan genom att beskriva **HTF‐metadata‐buggen** som låste HTF‐exits

---

## Nästa steg

1. ✅ Fixa metadata in i `features_asof.py` precompute-path
2. 🔄 Köra om 6h-testet och bekräfta +14.10 % utfallet
3. 🔄 Om allt stämmer: uppdatera `README.agents.md` + `EXIT_LOGIC_IMPLEMENTATION.md` med hänvisning till denna bug och åtgärd
4. ⬜ Fundera på integrationstest:
   ```python
   def test_precomputed_features_include_htf_context():
       df = load_features("tBTCUSD", "6h", version="v17")
       required = {"htf_fib_0382", "htf_fib_05", "htf_swing_high", ...}
       assert required.issubset(df.columns)
   ```

---

## Slutsats

- Felorsaken var inte exitmotorn i sig, utan att HTF-kontexten aldrig nådde dit när vi använde förberäknade features.
- Utan korrekt `htf_fibonacci_context` blev exitmotorn blind och kraschade på varje bar.
- Med fixen får vi både stabil drift och möjlighet att reproducera historiska +14 % på 6h.
- Dokumentationen här ska fungera som referens vid framtida regressioner och när vi kör full pipeline på v17/v18.

---

## Uppföljning (2025-12-26): "Invalid swing" hardening och strict AS-OF

Efter att HTF-context-metadata-buggen var löst hittades en separat felklass i HTF-exitflödet: återkommande
"Invalid swing"-varningar (ofta p.g.a. osunda bounds eller implicit lookahead när `reference_ts` saknades).

Åtgärder (kort):

- HTF-context (`get_htf_fibonacci_context`) är nu strikt AS-OF/no-lookahead och returnerar inte context utan `reference_ts`.
- Nivåer/bounds valideras hårdare (krav på 0.382/0.5/0.618/0.786, finite bounds, nivåer inom bounds).
- Exit engine alignas mot producer-schemat (`swing_high/swing_low`, `last_update`) och uppdaterar frusen `exit_ctx`
  konsekvent efter swing updates.

I stället för att jaga "Invalid swing" i loggar: börja med `reason` i HTF-context (t.ex. `HTF_LEVELS_INCOMPLETE`,
`HTF_INVALID_SWING_BOUNDS`, `HTF_MISSING_REFERENCE_TS`). Regressionstester finns i `tests/test_htf_fibonacci_*` och
`tests/test_htf_exit_engine_*`.
