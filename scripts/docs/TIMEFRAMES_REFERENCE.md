# Bitfinex Timeframes - Komplett referens

## ✅ Tillgängliga timeframes (verifierat från Bitfinex API v2)

```python
SUPPORTED_TIMEFRAMES = [
    "1m",   # 1 minut
    "5m",   # 5 minuter
    "15m",  # 15 minuter
    "30m",  # 30 minuter
    "1h",   # 1 timme
    "3h",   # 3 timmar
    "6h",   # 6 timmar
    "12h",  # 12 timmar
    "1D",   # 1 dag
    "1W",   # 1 vecka
    "14D",  # 14 dagar
    "1M"    # 1 månad
]
```

---

## ❌ VIKTIGT: 4h finns INTE!

**`4h` timeframe stöds INTE av Bitfinex API!**

### Alternativ till 4h:

- **`3h`** - Närmare intraday trading (8 candles/dag)
- **`6h`** - Mer stabil, position trading (4 candles/dag) ⭐ **REKOMMENDERAT**
- **`12h`** - Mycket stabil (2 candles/dag)

---

## 📊 Detaljerad tabell

| Timeframe | Intervall  | Candles/dag | Candles/18mån | API Requests | Fetch tid | Användning              |
| --------- | ---------- | ----------- | ------------- | ------------ | --------- | ----------------------- |
| **1m**    | 1 minut    | 1,440       | 777,600       | ~78          | ~3 min    | Scalping                |
| **5m**    | 5 minuter  | 288         | 155,520       | ~16          | ~35 sek   | Day trading             |
| **15m**   | 15 minuter | 96          | 51,840        | ~6           | ~13 sek   | Active trading          |
| **30m**   | 30 minuter | 48          | 25,920        | ~3           | ~7 sek    | Intraday                |
| **1h**    | 1 timme    | 24          | 12,960        | ~2           | ~5 sek    | **Swing trading** ⭐    |
| **3h**    | 3 timmar   | 8           | 4,320         | ~1           | ~2 sek    | Position trading        |
| **6h**    | 6 timmar   | 4           | 2,160         | ~1           | ~2 sek    | **Position trading** ⭐ |
| **12h**   | 12 timmar  | 2           | 1,080         | ~1           | ~2 sek    | Long positions          |
| **1D**    | 1 dag      | 1           | 540           | ~1           | ~2 sek    | Trend following         |
| **1W**    | 1 vecka    | 0.14        | 77            | ~1           | ~2 sek    | Very long-term          |
| **14D**   | 14 dagar   | 0.07        | 39            | ~1           | ~2 sek    | Macro trends            |
| **1M**    | 1 månad    | 0.03        | 18            | ~1           | ~2 sek    | Macro trends            |

---

## 🎯 Rekommendationer för ML

### **För mean-reversion strategier:**

```
1h  - Nuvarande Genesis-Core strategi (IC +0.0528)
30m - Snabbare entries
3h  - Mer stabila signaler
```

### **För trend-following strategier:**

```
6h  - Rekommenderat (stabil, bra signal/noise)
1D  - Långsiktig trend
12h - Mellan 6h och 1D
```

### **För multi-timeframe:**

```
HTF: 1D  - Trend direction
MTF: 1h  - Entry timing
LTF: 15m - Precision entry
```

---

## 💾 Storage requirements (18 månader, compressed Parquet)

| Timeframe | Storage/symbol |
| --------- | -------------- |
| 1m        | ~3.5 MB        |
| 5m        | ~700 KB        |
| 15m       | ~250 KB        |
| 30m       | ~130 KB        |
| 1h        | ~75 KB         |
| 3h        | ~35 KB         |
| 6h        | ~20 KB         |
| 12h       | ~12 KB         |
| 1D        | ~5 KB          |
| 1W        | ~1 KB          |

**Total för 2 symbols × 6 timeframes:** ~10 MB
**Total för 16 symbols × 6 timeframes:** ~80 MB

---

## 🚀 Quick commands

### **Hämta single timeframe:**

```powershell
python scripts/fetch/fetch_historical.py --symbol tBTCUSD --timeframe 6h --months 18
```

### **Hämta multiple timeframes:**

```powershell
.\scripts\fetch\fetch_all_data.ps1 `
    -Symbols "tBTCUSD" `
    -Timeframes "1h,6h,1D" `
    -Months 18
```

### **Trend-following test setup:**

```powershell
# Testa om högre timeframes har bättre trend-features
.\scripts\fetch\fetch_trend_test.ps1

# Eller custom:
.\scripts\fetch\fetch_all_data.ps1 `
    -Symbols "tBTCUSD" `
    -Timeframes "3h,6h,12h,1D" `
    -Months 12
```

---

## ⚠️ Vanliga misstag

### ❌ **FELAKTIGT:**

```powershell
# 4h finns inte!
.\scripts\fetch\fetch_all_data.ps1 -Timeframes "1h,4h,1D"
```

### ✅ **KORREKT:**

```powershell
# Använd 3h eller 6h istället
.\scripts\fetch\fetch_all_data.ps1 -Timeframes "1h,6h,1D"
```

---

## 📝 API Endpoint format

Bitfinex använder följande format för candles:

```
GET /v2/candles/trade:{TIMEFRAME}:{SYMBOL}/hist

Exempel:
/v2/candles/trade:1h:tBTCUSD/hist
/v2/candles/trade:6h:tBTCUSD/hist
/v2/candles/trade:1D:tBTCUSD/hist
```

---

## 🔗 Se även

- `DATA_FETCH_GUIDE.md` - Komplett guide för datahämtning
- `fetch_historical.py` - Base script för single fetch
- `fetch_all_data.ps1` - Batch fetch script
- Bitfinex docs: https://docs.bitfinex.com/reference/rest-public-candles

---

**Uppdaterad:** 2025-10-10
**Källa:** Bitfinex API v2 + Genesis-Core testing
