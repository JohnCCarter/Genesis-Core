# Genesis-Core - Data Directory

**Created:** 2025-10-07 (Phase 3 Prep)
**Purpose:** Storage for historical market data and ML features

---

## 📁 Directory Structure

```
data/
├── curated/
│   └── v1/
│       └── candles/   # Versionerade datasets som används av pipeline
├── raw/
│   └── bitfinex/
│       └── candles/   # Senaste råhämtningar (parquet)
├── metadata/
│   └── curated/       # Metadata för v1-datasets
├── features/          # (Tom) reserverad för framtida feature dumps
├── archive/           # Legacy candles/features flyttas hit
└── DATA_FORMAT.md
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

**Examples (curated v1):**
- `tBTCUSD_6h.parquet` - Bitcoin 6-hour candles
- `tETHUSD_15m.parquet` - Ethereum 15-minute candles

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

**Status:** Mappen är tom just nu. Äldre features ligger i `data/archive/features/`.

---

## 📊 Metadata Format

**File naming:** `{SYMBOL}_{TIMEFRAME}_meta.json`

**Examples:**
**Examples:**
- `tBTCUSD_6h_v1.json`
- `tETHUSD_1h_v1.json`

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

1. **Fetch** - Download from Bitfinex API → `raw/bitfinex/candles/*.parquet`
2. **Curate** - Consolidate + validate → `curated/v1/candles/*.parquet`
3. **Metadata** - Versioned metadata → `metadata/curated/*_v1.json`
4. **Feature Engineering** - (Efter behov) exporteras till `features/`
5. **Archive** - Flytta gamla datasets till `archive/`

---

## ⚠️ Important Notes

- **Bitfinex Rate Limit:** 90 requests/min (managed by rate limiter)
- **Data Gaps:** Some timeframes may have missing candles (check metadata)
- **Disk Space:** Monitor usage, ~400 MB for full dataset
- **Backup:** Consider backing up to cloud storage for production

---

**For more details, see:** `TODO_PHASE3.md`

## Curated Layer

- `curated/v1/candles/`: Versionerade, validerade Parquet-filer (standardkälla för modellpipeline).
- `curated/v1/features/`: Validerade feature-filer (Feather/Parquet) per version
  - `.../<symbol>/<timeframe>/v17/` 14-feature set (base + Fibonacci + combos)
  - `.../<symbol>/<timeframe>/v18/` Kompakt 8-feature set (5 bas + 3 combos)

## Metadata

- `metadata/curated/`: JSON metadata, samt `.json` filer bredvid varje feature-feather (version, skapad tid, source).
