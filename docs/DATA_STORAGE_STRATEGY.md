# Data Storage Strategy - Genesis-Core

## 📦 Format Philosophy

**Hybrid approach: Right format for right use case**

### Feather vs Parquet - When to use what?

| Format | Use Case | Why | Speed | Compression |
|--------|----------|-----|-------|-------------|
| **Feather** | Features (frequent reads) | 2× faster reads | ⚡⚡⚡ ~20ms | Medium |
| **Parquet** | Raw candles (long-term storage) | Better compression, inter-op | ⚡⚡ ~40ms | High |

---

## 🏗️ Current Architecture

```
data/
├── candles/                    # ❌ OLD: Flat structure
│   └── {symbol}_{timeframe}.parquet
│
└── features/                   # ✅ GOOD: Hybrid format
    ├── {symbol}_{timeframe}_features_v17.feather  # Primary (fast)
    └── {symbol}_{timeframe}_features_v17.parquet  # Backup
```

### Smart loader (src/core/utils/data_loader.py):
```python
# Try Feather first (2× faster)
if feather_path.exists():
    return pd.read_feather(feather_path)
# Fallback to Parquet
elif parquet_path.exists():
    return pd.read_parquet(parquet_path)
```

---

## 🎯 Proposed: Two-Layer Architecture

```
data/
├── raw/                        # Raw Lake (immutable, timestamped)
│   └── bitfinex/
│       └── candles/
│           └── {symbol}_{timeframe}_{YYYY-MM-DD}.parquet
│
├── curated/                    # Gold Layer (validated, versioned)
│   └── v1/
│       ├── candles/
│       │   └── {symbol}_{timeframe}.parquet
│       └── features/
│           ├── {symbol}_{timeframe}_features.feather  # Primary
│           └── {symbol}_{timeframe}_features.parquet  # Backup
│
└── metadata/
    └── curated/
        └── {symbol}_{timeframe}_v1.json
```

---

## 📊 Format Performance Comparison

### Read Performance (tBTCUSD_1h, 12,960 bars):

| Format | Read Time | Use Case |
|--------|-----------|----------|
| Feather | ~20ms | ✅ Features (read frequently during training) |
| Parquet | ~40ms | ✅ Candles (read once, compress well) |
| CSV | ~150ms | ❌ Legacy only |

### Storage (18 months data):

| Data Type | Feather | Parquet | CSV |
|-----------|---------|---------|-----|
| Candles (OHLCV) | ~100 KB | ~75 KB ⭐ | ~500 KB |
| Features (17 cols) | ~250 KB ⭐ | ~200 KB | ~1.2 MB |

**Conclusion:**
- Candles: Parquet saves ~25% space, read speed less critical
- Features: Feather 2× faster, minimal size penalty

---

## 🔄 Migration Strategy

### Step 1: Restructure (dry-run first)
```bash
# See what would change
python scripts/restructure_data_layers.py --dry-run

# Execute migration
python scripts/restructure_data_layers.py --execute
```

### Step 2: Update fetch scripts
```python
# OLD: Overwrites existing
fetch_historical.py → data/candles/{symbol}_{timeframe}.parquet

# NEW: Timestamped + versioned
fetch_historical.py → data/raw/bitfinex/candles/{symbol}_{timeframe}_{date}.parquet
                   → data/curated/v1/candles/{symbol}_{timeframe}.parquet
```

### Step 3: Incremental sync (future)
```python
# Only fetch new data since last sync
sync_incremental.py → Append to Raw Lake
                   → Update Curated with validation
```

---

## 📝 Best Practices

### For Candles (OHLCV):
```python
# ✅ GOOD: Parquet with snappy compression
df.to_parquet(path, index=False, compression="snappy")

# ❌ BAD: Feather for long-term storage (less compression)
df.to_feather(path)  # Use only for features!
```

### For Features:
```python
# ✅ BEST: Both formats for flexibility
df.to_feather(f"{symbol}_{tf}_features_v17.feather")  # Fast reads
df.to_parquet(f"{symbol}_{tf}_features_v17.parquet")  # Backup

# Loader tries Feather first, falls back to Parquet
```

### For Large Datasets (future):
```python
# Partition by year/month for massive datasets
df.to_parquet(
    "data/raw/bitfinex/candles",
    partition_cols=["year", "month"],
    compression="snappy"
)
```

---

## 🎓 Why This Matters

### Problem 1: Concept Drift
**Without versioning:**
```
2024-10-01: Fetch data → Train model → IC = 0.05
2024-10-15: Re-fetch data (different endpoint/filter) → IC = 0.03
```
**What changed?** No way to know!

**With versioning:**
```
data/raw/bitfinex/candles/tBTCUSD_1h_2024-10-01.parquet  (immutable)
data/curated/v1/candles/tBTCUSD_1h.parquet  (validated)
data/metadata/curated/tBTCUSD_1h_v1.json  (quality_score: 0.98)
```
**Reproducible!** Can always trace back.

### Problem 2: Incremental Updates
**Without Raw Lake:**
```
Daily sync overwrites existing data
→ Can't verify if new data matches old data
→ Risk of introducing gaps/inconsistencies
```

**With Raw Lake:**
```
Daily sync → Append to Raw Lake (timestamped)
           → Validate + merge into Curated
           → Track adjustments in metadata
```

### Problem 3: Multi-Exchange (future)
**Genesis-Core might expand to:**
```
data/raw/
├── bitfinex/
├── binance/
└── kraken/

data/curated/v1/  (merged, normalized, validated)
```

---

## 🚀 Implementation Priority

### Phase 1: Immediate (this week)
- [x] Document current format strategy
- [x] Create restructure script with dry-run
- [ ] Test migration on existing data
- [ ] Update fetch scripts to use two-layer

### Phase 2: Short-term (next sprint)
- [ ] Implement incremental sync
- [ ] Add quality monitoring
- [ ] Version bump process (v1 → v2)

### Phase 3: Long-term (future)
- [ ] Multi-exchange support
- [ ] Automated data quality checks
- [ ] Cloud backup strategy

---

## 📚 References

- **Feather format:** https://arrow.apache.org/docs/python/feather.html
- **Parquet format:** https://parquet.apache.org/
- **Genesis-Core data loader:** `src/core/utils/data_loader.py`
- **Migration script:** `scripts/restructure_data_layers.py`

---

**Updated:** 2025-10-10  
**Author:** Genesis-Core Team  
**Status:** Proposed → Pending Review

