# Genesis-Core - Data Directory

**Created:** 2025-10-07 (Phase 3 Prep)  
**Purpose:** Storage for historical market data and ML features

---

## 📁 Directory Structure

```
data/
├── candles/          # Historical OHLCV data (Parquet format)
├── features/         # Pre-computed features (Parquet format)
├── metadata/         # Data quality reports and fetch logs (JSON)
└── README.md         # This file
```

---

## 🔐 Not in Git

**Data files are NOT version controlled due to size.**

Ignored by `.gitignore`:
- `data/candles/*.parquet`
- `data/features/*.parquet`
- `data/metadata/*.json`

---

## 📦 Candles Format

**File naming:** `{SYMBOL}_{TIMEFRAME}.parquet`

**Examples:**
- `tBTCUSD_1m.parquet` - Bitcoin 1-minute candles
- `tETHUSD_1h.parquet` - Ethereum 1-hour candles

**Schema:**
```python
{
    "timestamp": int64,      # Unix timestamp (ms)
    "open": float64,         # Opening price
    "high": float64,         # Highest price
    "low": float64,          # Lowest price
    "close": float64,        # Closing price
    "volume": float64        # Trading volume
}
```

---

## 🧬 Features Format

**File naming:** `{SYMBOL}_{TIMEFRAME}_features.parquet`

**Examples:**
- `tBTCUSD_1m_features.parquet`
- `tETHUSD_1h_features.parquet`

**Schema:**
```python
{
    "timestamp": int64,          # Unix timestamp (ms)
    "ema_delta_pct": float64,    # EMA delta percentage
    "rsi": float64,              # RSI indicator
    # ... additional features as needed
}
```

---

## 📊 Metadata Format

**File naming:** `{SYMBOL}_{TIMEFRAME}_meta.json`

**Examples:**
- `tBTCUSD_1m_meta.json`
- `tETHUSD_1h_meta.json`

**Schema:**
```json
{
    "symbol": "tBTCUSD",
    "timeframe": "1m",
    "fetched_at": "2025-10-07T12:00:00Z",
    "start_date": "2025-04-07",
    "end_date": "2025-10-07",
    "total_candles": 262800,
    "missing_candles": 0,
    "quality_score": 1.0,
    "source": "bitfinex_public_api"
}
```

---

## 🚀 Usage

### **Fetch Historical Data:**
```bash
python scripts/fetch_historical.py --symbol tBTCUSD --timeframe 1m --months 6
```

### **Pre-compute Features:**
```bash
python scripts/precompute_features.py --symbol tBTCUSD --timeframe 1m
```

### **Check Data Quality:**
```bash
python scripts/validate_data.py --symbol tBTCUSD --timeframe 1m
```

---

## 💾 Storage Estimates

**Per Symbol/Timeframe (6 months):**

| Timeframe | Candles | Raw Size | Compressed (Parquet) |
|-----------|---------|----------|----------------------|
| 1m        | 262,800 | ~12 MB   | ~2-3 MB              |
| 5m        | 52,560  | ~2.5 MB  | ~500 KB              |
| 15m       | 17,520  | ~850 KB  | ~170 KB              |
| 1h        | 4,380   | ~210 KB  | ~50 KB               |
| 4h        | 1,095   | ~53 KB   | ~15 KB               |
| 1D        | 183     | ~9 KB    | ~3 KB                |

**Total for 16 symbols × 6 timeframes:** ~200-400 MB (compressed)

---

## 🔄 Data Lifecycle

1. **Fetch** - Download from Bitfinex API → `candles/*.parquet`
2. **Validate** - Check quality → `metadata/*_meta.json`
3. **Feature Engineering** - Compute indicators → `features/*.parquet`
4. **Training** - Use features to train ML models
5. **Refresh** - Periodic updates (weekly/monthly)

---

## ⚠️ Important Notes

- **Bitfinex Rate Limit:** 90 requests/min (managed by rate limiter)
- **Data Gaps:** Some timeframes may have missing candles (check metadata)
- **Disk Space:** Monitor usage, ~400 MB for full dataset
- **Backup:** Consider backing up to cloud storage for production

---

**For more details, see:** `TODO_PHASE3.md`
