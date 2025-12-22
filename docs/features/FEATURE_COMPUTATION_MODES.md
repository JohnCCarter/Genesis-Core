# FEATURE COMPUTATION - LIVE vs BACKTEST

## 🚨 CRITICAL DESIGN DECISION

Genesis-Core har **TVÅ** feature computation modes med **OLIKA** semantik:

---

## 1️⃣ LIVE TRADING MODE (`extract_features`)

**File:** `src/core/strategy/features.py::extract_features()`

**Purpose:** Real-time feature extraction för live trading

**Behavior:**

```python
extract_features(candles, now_index=99)
→ Använder bars 0-98 (EXKLUDERAR bar 99)
→ Antar att bar 99 är "current forming bar" (ej stängd)
```

**Rationale:**

- I live trading är "current bar" inte stängd ännu
- Vi kan bara använda STÄNGDA bars för features
- `now_index` = index för current FORMING bar
- Features beräknas från `now_index - 1` (senaste STÄNGDA)

**Example:**

```
Time: 14:30
Bars: [0, 1, 2, ... 98, 99]
       └── stängda ──┘  └open┘

extract_features(candles, now_index=99)
→ Uses bars 0-98
→ Avoids lookahead bias
```

---

## 2️⃣ BACKTEST MODE (`calculate_all_features_vectorized`)

**File:** `src/core/indicators/vectorized.py::calculate_all_features_vectorized()`

**Purpose:** Batch precomputation för backtesting/research

**Behavior:**

```python
calculate_all_features_vectorized(df.iloc[:100])
→ Använder bars 0-99 (INKLUDERAR alla)
→ Alla bars är redan STÄNGDA i backtest data
```

**Rationale:**

- I backtesting är ALL data historisk (stängd)
- Ingen "forming bar" concept
- Vi vill features för VARJE bar inklusive sista
- Används för precompute, IC testing, feature engineering

**Example:**

```
Historical data: [0, 1, 2, ... 98, 99]
                  └────── alla stängda ─────┘

calculate_all_features_vectorized(df)
→ Returnerar features för bars 0-99
→ Bar 99's features använder bars 0-99
```

---

## ⚠️ **CONSEQUENCE: OFF-BY-ONE OFFSET**

```
SAMMA CANDLES DATA (bars 0-99):

Live mode:   extract_features(candles, now_index=99)
             → Features från bars 0-98
             → Motsvarar bar 98's features

Backtest mode: vectorized(df.iloc[:100]).iloc[-1]
               → Features från bars 0-99
               → Motsvarar bar 99's features

RESULT: 1-BAR OFFSET! 🚨
```

---

## ✅ **SOLUTION: DIFFERENT USE CASES**

### **Use Case 1: Live Trading**

```python
# Server receives NEW candle (bar N is forming)
# Want features from LAST CLOSED bar (N-1)

candles = fetch_last_100_bars()  # Bars 0-99, bar 99 forming
feats, meta = extract_features(candles, now_index=99)
# → Uses bars 0-98 ✅ Correct!
```

### **Use Case 2: Backtesting**

```python
# We have HISTORICAL data (all bars closed)
# Want features for EACH bar

for i in range(len(df)):
    # For bar i, we have bars 0-i (all closed)
    # Want features AS OF bar i

    # WRONG:
    extract_features(candles, now_index=i)
    # → Uses bars 0-(i-1) ❌ Loses 1 bar!

    # CORRECT:
    extract_features(candles, now_index=i+1)
    # → Uses bars 0-i ✅ But confusing!

    # BEST:
    vectorized_features.iloc[i]
    # → Precomputed for all bars ✅
```

---

## 🎯 **RECOMMENDATION:**

### **For Development (NOW):**

**Keep BOTH methods but use them CORRECTLY:**

1. **Live Trading:** Use `extract_features()`

   - Call with `now_index = len(candles) - 1`
   - Gets features from last CLOSED bar

2. **Backtesting:** Use `calculate_all_features_vectorized()`

   - Precompute ALL features at once
   - 27,734× faster
   - All bars are closed historical data

3. **Validation:**
   - Compare: `extract_features(candles, now_index=i+1)`
   - vs: `vectorized(df).iloc[i]`
   - Should match!

### **For Production (FUTURE):**

**Option A:** Add `mode` parameter

```python
def extract_features(candles, now_index=None, mode="live"):
    if mode == "live":
        last_idx = idx - 1  # Skip forming bar
    else:  # mode == "backtest"
        last_idx = idx  # Use all bars
```

**Option B:** Separate functions

```python
extract_features_live(candles)  # Always skips last bar
extract_features_backtest(candles, bar_index)  # Uses all up to bar_index
```

---

## 📋 **CURRENT STATUS:**

```
✅ Vectorized: Optimized for BACKTEST (all bars closed)
✅ Per-sample: Optimized for LIVE (current bar forming)
⚠️ Validation: Need to account for 1-bar offset!
```

**TODO:** Fix validation script to compare correctly!

---

## ⚡ Fast Window & Precompute (Performance Mode 2025-11-10)

För att accelerera backtests och Optuna‑körningar finns två växlar:

### 1) Fast Window (NumPy views)

- Miljövariabel: `GENESIS_FAST_WINDOW=1`
- CLI‑flagga i backtest: `--fast-window`
- Effekt: OHLCV matas som NumPy‑views för att minska Python‑overhead.
- Caveat: Enstaka indikatorer som förväntar sig listor konverteras lokalt (t.ex. Bollinger). Detta hanteras i `features_asof.py`.

### 2) Precompute Features (on‑disk cache)

- Miljövariabel: `GENESIS_PRECOMPUTE_FEATURES=1`
- CLI‑flagga i backtest: `--precompute-features`
- Effekt: EMA50, swing points m.fl. förberäknas och cachas på disk (`cache/precomputed/*.npz`), vilket accelererar efterföljande körningar.
- Semantik: Backtestläget förblir deterministiskt och använder stängda bars (ingen lookahead).

### Canonical policy (quality decisions)

Från 2025‑12-18 är **1/1 (fast_window + precompute)** den **canonical** exekveringsmoden för:

- Optuna
- Explore→Validate
- champion‑jämförelser/promotion
- all rapportering som används för beslut

Det betyder att standardflöden aktivt undviker att “sticky” shell‑env råkar köra 0/0.

### Debug‑only mode (0/0)

0/0 (ingen fast_window + ingen precompute) är tillåtet för felsökning, men är **inte** jämförbart med canonical resultat.

- För att tillåta icke‑canonical mode måste du sätta `GENESIS_MODE_EXPLICIT=1`.
- Rekommenderat sätt är att använda CLI‑flaggor i `scripts/run_backtest.py` (t.ex.
  `--no-fast-window --no-precompute-features`), vilket markerar läget explicit.

Tips: Backtest‑artifacts sparar nu `backtest_info.execution_mode` så att du kan se exakt vilket läge som kördes.

### Determinism

- Runner sätter `GENESIS_RANDOM_SEED=42` för backtest‑subprocesser om inte redan satt.
- Sätt explicit i shell om du vill ändra:

  ```powershell
  $Env:GENESIS_RANDOM_SEED='123'
  ```

### Snabbstart (PowerShell)

```powershell
# Snabb backtest med fast window + precompute
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2024-10-22 --end 2025-10-01 --fast-window --precompute-features
```

---

## 🧪 Paritetstester 2025-11-14

För att garantera att alla pipelines producerar identiska features lades två pytest-case till:

1. `tests/test_feature_parity.py`
   - Kör `_extract_asof()` bar-för-bar och jämför mot v17-featurefiler.
   - Dataset: `tests/data/tBTCUSD_1h_sample.parquet` + `tests/data/tBTCUSD_1h_features_v17.parquet` (200 barer, december 2024).
2. `tests/test_precompute_vs_runtime.py`
   - Bygger `precomputed_features` exakt som `BacktestEngine` och validerar att `_extract_asof()` med/utan precompute ger samma resultat.

### Precompute-scriptet

`scripts/precompute_features_v17.py` genererar nu featurefiler genom att anropa `_extract_asof()` direkt. Nya flaggor:

- `--start-index / --end-index` – begränsa datafönster för snabba tester.
- `--candles-file` – kör mot valfri parquet (ex. `tests/data/tBTCUSD_1h_sample.parquet`).

Det betyder att v17-featurefilerna är bit-exakta mot runtime (ingen längre avvikelse mellan vectorized och live-kod).

### Rekommenderat flöde

| Scenario                 | Kommando                                                                                                                                |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Uppdatera hela v17-filen | `python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h`                                                             |
| Snabb sample (200 bar)   | `python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h --candles-file tests/data/tBTCUSD_1h_sample.parquet --quiet` |
| Paritetskontroll         | `python -m pytest tests/test_feature_parity.py tests/test_precompute_vs_runtime.py`                                                     |

Alla ändringar ovan säkerställer att:

- Backtest/Optuna (runtime) ↔ precompute ↔ ML-training använder samma definitioner.
- Regressionstester fångar om någon bryter pariteten framöver.
