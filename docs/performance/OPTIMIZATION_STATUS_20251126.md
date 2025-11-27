# Statusrapport: Prestandaoptimering av Backtest

**Datum:** 2025-11-26
**Status:** Pågående analys & åtgärd

## 1. Problembeskrivning

Användaren rapporterade att backtester och optimeringar går extremt långsamt ("tar för lång tid") och verkar "fastna" eller gå trögt runt bar 2000 av 17 000. Detta observerades även efter att ha aktiverat parallellisering (`GENESIS_IN_PROCESS=0`).

## 2. Analys av grundorsak

Efter kodgranskning har vi identifierat att flaskhalsen sannolikt ligger i **feature extraction** (`features_asof.py`).

### "Slow Path" vs "Fast Path"

Systemet har två sätt att beräkna indikatorer (RSI, ATR, Bollinger Bands, etc.):

1.  **Slow Path (Standard):** För _varje_ bar i backtestet (17 000+ gånger) räknas indikatorer om baserat på det fönster av data som skickas in. Även med optimerade fönster skapar detta en stor overhead i Python-loopar och objektallokering.
2.  **Fast Path (Vectorized):** Alla indikatorer beräknas _en gång_ vid start (precompute) med hjälp av NumPy/Pandas vektorisering (snabbt). Under backtestet görs endast en O(1)-uppslagning i en färdig lista.

**Hypotes:** Systemet faller tyst tillbaka på "Slow Path" för att:

- Flaggan `precompute_features` inte propagerades korrekt från `runner` till `engine`.
- `features_asof.py` saknade tillgång till det globala indexet (`_global_index`) som krävs för att slå upp värden i de förberäknade listorna.
- Dataflödet för `precomputed_features` i `configs`-objektet kan vara brutet.

## 3. Utförda åtgärder

Vi har genomfört följande kodändringar för att tvinga fram "Fast Path":

1.  **`src/core/optimizer/runner.py`**:

    - Lagt till logik som explicit sätter `engine.precompute_features = True` om miljövariabeln `GENESIS_PRECOMPUTE_FEATURES` är satt. Detta säkerställer att motorn faktiskt gör jobbet vid start.

2.  **`src/core/backtest/engine.py`**:

    - Uppdaterat huvudloopen (`run`) för att injicera `configs["_global_index"] = i`. Detta ger strategin tillgång till det absoluta indexet, vilket är nödvändigt för att slå upp förberäknad data korrekt.

3.  **`src/core/strategy/features_asof.py`**:
    - Skrivit om logiken för att prioritera `_global_index` vid uppslagning.
    - Implementerat "Fast Path"-block för RSI, Bollinger Bands, ATR och Volatility Shift som direkt läser från `pre`-dictionaryn i stället för att räkna om.
    - Lagt till stöd för att hämta Fibonacci-swings från förberäknad data via `bisect`-sökning (O(log N)) i stället för tung detektion.

## 4. Kvarstående risker & nästa steg

Vi har "kopplat rören" men inte bekräftat att det rinner vatten.

- **Risk:** Om `configs["precomputed_features"]` är tom (None) kommer koden fortfarande att falla tillbaka på Slow Path utan att varna.
- **Åtgärd:**
  1.  Lägg in en temporär debug-utskrift i `features_asof.py` för att verifiera att `pre`-objektet innehåller data.
  2.  Kör `scripts/test_optimization_modes_v2.py` för att mäta den faktiska tidsvinsten.

## 5. Rekommendation för körning

För att dra nytta av optimeringarna, säkerställ att din miljö (.env eller terminal) har följande variabler satta:

```powershell
$Env:GENESIS_IN_PROCESS="0"          # Använd ProcessPoolExecutor (flera kärnor)
$Env:GENESIS_FAST_WINDOW="1"         # Använd NumPy views för fönster (inget kopierande)
$Env:GENESIS_PRECOMPUTE_FEATURES="1" # Aktivera förberäkning av indikatorer
```
