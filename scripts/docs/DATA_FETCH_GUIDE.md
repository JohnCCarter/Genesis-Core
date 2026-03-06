# Data Fetch Guide - Genesis-Core

## 🎯 Quick Reference

| Script                  | Duration   | Use Case                                        |
| ----------------------- | ---------- | ----------------------------------------------- |
| `fetch_quick_start.ps1` | ~5-10 sek  | **START HERE** - Minimal setup (tBTCUSD 1h)     |
| `fetch_overnight.ps1`   | ~10-15 min | Comprehensive dataset (BTC+ETH, all timeframes) |
| `fetch_all_data.ps1`    | Variabel   | Custom batch fetch (configurable)               |

---

## 🚀 Quick Start (REKOMMENDERAD)

**För att komma igång direkt med Genesis-Core workflow:**

```powershell
# Hämta minimal data för att börja (5-10 sekunder)
.\scripts\fetch\fetch_quick_start.ps1
```

**Vad hämtas:**

- Symbol: `tBTCUSD`
- Timeframe: `1h`
- Period: 18 månader
- Candles: ~12,960 st
- Tid: ~5-10 sekunder ⚡

**Nästa steg:**

```powershell
# 1. Precompute features (vektoriserat - snabbt!)
python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h

# 2. Train model
python scripts/train/train_model.py --symbol tBTCUSD --timeframe 1h --use-holdout
```

---

## 🌙 Overnight Fetch

**För att hämta komplett dataset över natten:**

```powershell
# Starta innan du går och lägga dig (~10-15 min)
.\scripts\fetch\fetch_overnight.ps1
```

**Vad hämtas:**

- Symbols: `tBTCUSD`, `tETHUSD`
- Timeframes: `1m`, `5m`, `15m`, `1h`, `6h`, `1D`
- Period: 18 månader
- Total tid: ~10-15 minuter

**Detta ger dig:**

- Multi-timeframe analysis capabilities
- Higher timeframe (6h, 1D) för trend-following strategies
- Lower timeframe (1m, 5m) för quick backtesting
- Två assets för diversification testing

---

## ⚙️ Custom Batch Fetch

**För att anpassa exakt vad du vill hämta:**

```powershell
# Exempel 1: Bara 6h och 1D för BTC (för trend-following)
.\scripts\fetch\fetch_all_data.ps1 `
    -Symbols "tBTCUSD" `
    -Timeframes "6h,1D" `
    -Months 18

# Exempel 2: Top 5 crypto på 1h timeframe
.\scripts\fetch\fetch_all_data.ps1 `
    -Symbols "tBTCUSD,tETHUSD,tSOLUSD,tADAUSD,tDOGEUSD" `
    -Timeframes "1h" `
    -Months 18

# Exempel 3: Full dataset (16 symboler, alla major timeframes)
# ⚠️ VARNING: Tar 30-60 minuter!
.\scripts\fetch\fetch_all_data.ps1 `
    -Symbols "tBTCUSD,tETHUSD,tSOLUSD,tADAUSD,tDOGEUSD,tALGOUSD,tAVAXUSD,tDOTUSD,tLTCUSD,tAPTUSD,tEOSUSD,tFILUSD,tNEARUSD,tXAUTUSD,tXTZUSD,tXRPUSD" `
    -Timeframes "1m,5m,15m,1h,6h,1D" `
    -Months 18
```

---

## ⏱️ Time Estimates

### Per Symbol/Timeframe (18 månader):

| Timeframe | Candles | API Requests | Duration |
| --------- | ------- | ------------ | -------- |
| 1m        | 777,600 | ~78          | ~3 min   |
| 5m        | 155,520 | ~16          | ~35 sek  |
| 15m       | 51,840  | ~6           | ~13 sek  |
| 30m       | 25,920  | ~3           | ~7 sek   |
| 1h        | 12,960  | ~2           | ~5 sek   |
| 3h        | 4,320   | ~1           | ~2 sek   |
| 6h        | 2,160   | ~1           | ~2 sek   |
| 12h       | 1,080   | ~1           | ~2 sek   |
| 1D        | 540     | ~1           | ~2 sek   |
| 1W        | 77      | ~1           | ~2 sek   |

**⚠️ Note:** `4h` is NOT supported by Bitfinex API. Use `3h` or `6h` instead.

### Batch Estimates:

| Scenario                    | Duration   |
| --------------------------- | ---------- |
| 1 symbol, 1 timeframe (1h)  | ~5 sek     |
| 1 symbol, all timeframes    | ~4-5 min   |
| 2 symbols, all timeframes   | ~8-10 min  |
| 5 symbols, 1 timeframe (1h) | ~25 sek    |
| 16 symbols, all timeframes  | ~30-60 min |

---

## 💾 Storage Requirements

**Per symbol (18 månader, compressed Parquet):**

| Timeframe | Storage |
| --------- | ------- |
| 1m        | ~3.5 MB |
| 5m        | ~700 KB |
| 15m       | ~250 KB |
| 1h        | ~75 KB  |
| 3h        | ~35 KB  |
| 6h        | ~20 KB  |
| 1D        | ~5 KB   |

**Total for 2 symbols × 6 timeframes:** ~10 MB
**Total for 16 symbols × 6 timeframes:** ~80 MB

---

## 🔄 Rate Limits

**Bitfinex Public API:**

- Rate limit: 90 requests/min
- Safety margin: 27 requests/min (~2.22s delay)
- Max candles per request: 10,000

**Scripts automatically handle:**

- ✅ Rate limiting (built-in delays)
- ✅ Retry on rate limit errors (60s backoff)
- ✅ Error handling
- ✅ Progress tracking

---

## 📝 After Fetching Data

**1. Validate data integrity:**

```powershell
python scripts/validate_data.py --symbol tBTCUSD --timeframe 1h
```

**2. Precompute features (VECTORIZED - FAST!):**

```powershell
python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h
```

**3. Train model:**

```powershell
python scripts/train/train_model.py --symbol tBTCUSD --timeframe 1h --use-holdout --save-provenance
```

**4. Run comprehensive analysis:**

```powershell
python scripts/comprehensive_feature_analysis.py --symbol tBTCUSD --timeframe 1h
```

---

## ⚠️ Important Notes

1. **Curated datasets** - Efter hämtning, konsolidera till `data/curated/v1/candles/`
2. **Raw-cache** - Individuella hämtningar sparas i `data/raw/bitfinex/`
3. **Metadata** - Validerad metadata gick till `data/metadata/curated/*_v1.json`
4. **Idempotent fetch** - Skriptet kan köras om; äldre filer skrivs över
5. **Internet required** - Hämtar via Bitfinex public API (inga API-nycklar)

---

## 🆘 Troubleshooting

**Problem: "Rate limit hit"**

```
Solution: Script automatically retries after 60s. Just wait.
```

**Problem: "No module named httpx"**

```powershell
Solution: pip install httpx pandas pyarrow tqdm
```

**Problem: "Connection timeout"**

```
Solution: Check internet connection, retry script
```

**Problem: "File already exists"**

```
Solution: This is OK! Script overwrites existing files.
```

---

## 📚 See Also

- `README.agents.md` - Full ML pipeline workflow
- `data/DATA_FORMAT.md` - Data format specifications
- `scripts/fetch/fetch_historical.py` - Individual fetch script (advanced use)
- `AGENTS.md` - Current project status, deliverables and next steps

---

**Rekommendation:** Börja med `fetch_quick_start.ps1` → träna din första modell → utöka sedan till fler timeframes/symboler baserat på resultat!
