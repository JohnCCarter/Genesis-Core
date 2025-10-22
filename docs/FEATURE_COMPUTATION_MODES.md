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
