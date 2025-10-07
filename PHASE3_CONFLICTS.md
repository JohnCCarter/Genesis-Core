# Phase 3 - Potentiella Konflikter & Lösningar

**Skapad:** 2025-10-07  
**Status:** Granskning innan Phase 3 påbörjas  
**Syfte:** Identifiera och planera för alla potentiella konflikter mellan befintlig infrastruktur och Phase 3-implementation

---

## 🔴 KRITISKA KONFLIKTER

### 1. Modell-fil Struktur Inkonsistens

**Problem:**
```
BTC & ETH: Multi-timeframe struktur
{
  "1m": {...},
  "5m": {...},
  "1h": {...}
}

ANDRA 14 SYMBOLER: Flat struktur (endast 1m implicit)
{
  "schema": [...],
  "buy": {...},
  "sell": {...}
}
```

**Påverkan:**
- ML training scripts kommer behöva hantera BÅDA strukturer
- ModelRegistry har redan fallback-logik (line 72-82) MEN:
  - Flat struktur har ingen timeframe-info
  - Training måste veta vilken struktur som ska användas
  - Risk för att skriva fel format

**Lösning:**
```markdown
Priority: KRITISKT - Innan ML training

1. Migrera alla 14 flat-strukturer till multi-timeframe:
   ```bash
   python scripts/migrate_model_structure.py --all
   ```

2. Skapa migration script:
   - Läs flat JSON
   - Wrap i {"1m": <flat_content>}
   - Kopiera till andra timeframes (5m, 15m, 1h, 4h, 1D)
   - Behåll Git history (rename → edit)

3. Validera:
   - Kör alla tester
   - Verifiera ModelRegistry laddar korrekt
   - Test med alla symbols × alla timeframes
```

**Risk om ej åtgärdat:**
- Training script kraschar eller skriver fel format
- Inkonsistent data mellan symbols
- Svårt att debugga

---

### 2. ModelRegistry Cache Invalidation

**Problem:**
```python
# model_registry.py line 48-56
cached = self._cache.get(key)
if cached and abs(cached[1] - mtime) < 1e-6:
    return cached[0]  # ← PROBLEM!
```

**Scenario:**
```
1. Bot läser tBTCUSD.json → cached
2. ML training uppdaterar tBTCUSD.json → ny mtime
3. Bot kör pipeline → cache hit (mtime diff < 1μs?)
4. Bot använder GAMLA vikter! ❌
```

**Påverkan:**
- Training-resultat syns inte i live bot
- A/B testing blir felaktigt
- Champion deployment tar inte effekt

**Lösning:**
```python
Priority: HÖGT - Innan ML deployment

1. Förbättra cache invalidation:
   ```python
   # Öka precision eller använd hash
   if cached and stat.st_mtime == cached[1]:
       return cached[0]
   ```

2. Eller: Force reload efter training:
   ```python
   # I train_model.py efter save
   ModelRegistry()._cache.clear()
   ```

3. Lägg till explicit reload-endpoint:
   ```python
   # server.py
   @app.post("/models/reload")
   def reload_models():
       ModelRegistry()._cache.clear()
       return {"ok": True}
   ```
```

**Test:**
```bash
1. Starta bot
2. Kör pipeline → Result A
3. Uppdatera model fil manuellt
4. Kör pipeline igen → Result B (ska vara olika!)
```

---

### 3. Data Directory Missing

**Problem:**
```
data/ directory existerar inte
└── Behövs för:
    ├── candles/
    ├── features/
    └── metadata/
```

**Påverkan:**
- Historical fetcher kraschar
- Ingen plats att spara data
- Git ignorerar inte data-filer

**Lösning:**
```markdown
Priority: HÖGT - Innan data fetch

1. Skapa directory structure:
   ```bash
   mkdir -p data/{candles,features,metadata}
   ```

2. Uppdatera .gitignore:
   ```gitignore
   # Data files
   data/candles/*.parquet
   data/features/*.parquet
   data/metadata/*.json
   
   # Behåll README
   !data/README.md
   !data/**/README.md
   ```

3. Skapa data/README.md:
   ```markdown
   # Genesis-Core - Data Directory
   
   ## Structure
   - candles/: Historical OHLCV data (Parquet)
   - features/: Pre-computed features (Parquet)
   - metadata/: Data quality reports (JSON)
   
   ## NOT IN GIT
   Data files are not version controlled due to size.
   Use scripts/fetch_historical.py to download.
   ```
```

---

## 🟡 MEDEL KONFLIKTER

### 4. Bitfinex Rate Limiting

**Problem:**
```python
# Bitfinex Candles API limits (VERIFIED):
# Source: https://docs.bitfinex.com/reference/rest-public-candles
- 30 requests / minute (candles endpoint specific)
- Historical data: max 10,000 candles/request
- 6 months @ 1m = ~262,800 candles → 27 requests
```

**Påverkan:**
```
Fetch 6 months × 5 timeframes × 2 symbols = 270 requests
→ 9 minuter minimum (med 30 req/min)
→ Managed med rate limiter
```

**Lösning:**
```python
Priority: MEDIUM - Innan mass fetch

1. Implementera rate limiter i fetch_historical.py:
   ```python
   from ratelimit import limits, sleep_and_retry
   
   @sleep_and_retry
   @limits(calls=27, period=60)  # 27/min (säkerhetsmarginal från 30)
   def fetch_candles_page(...):
       ...
   ```

2. Progress tracking:
   ```python
   from tqdm import tqdm
   
   for symbol in tqdm(symbols):
       for tf in tqdm(timeframes):
           fetch_with_retry(symbol, tf)
   ```

3. Retry logic med exponential backoff:
   ```python
   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=60)
   )
   def fetch_with_retry(...):
       ...
   ```
```

**Fallback:**
```python
# Om rate limit ändå träffas:
# Spara progress → pause 60s → fortsätt
metadata = {
    "last_fetched": "tBTCUSD_5m",
    "progress": "40%",
    "timestamp": "2025-10-07T12:00:00Z"
}
```

---

### 5. Training Overwriting Production Models

**Problem:**
```python
# train_model.py uppdaterar direkt:
with open("config/models/tBTCUSD.json", "w") as f:
    json.dump(new_model, f)  # ← Överskriver LIVE model!
```

**Påverkan:**
- Otestade modeller går live direkt
- Ingen A/B testing möjlig
- Svårt att rulla tillbaka

**Lösning:**
```python
Priority: MEDIUM - Innan första träning

1. Använd versioning:
   ```python
   # Spara som ny version först
   output = f"config/models/tBTCUSD_v{version}.json"
   with open(output, "w") as f:
       json.dump(new_model, f)
   ```

2. Champion selection process:
   ```python
   # Manuell review innan deployment
   python scripts/select_champion.py \
     --baseline config/models/tBTCUSD.json \
     --candidate config/models/tBTCUSD_v2.json \
     --backtest-period 2024-09-01:2024-10-01
   
   # Om bättre → deploy
   # Om sämre → behåll baseline
   ```

3. Git workflow:
   ```bash
   # Branch för training
   git checkout -b train/btc-v2
   # Train & commit
   git add config/models/tBTCUSD_v2.json
   git commit -m "feat: trained BTC model v2"
   # Review → merge om godkänd
   ```
```

---

### 6. Feature Schema Changes

**Problem:**
```python
# Nuvarande models: ["ema_delta_pct", "rsi"]
# Om vi lägger till fler features i training:
# → Old models inte kompatibla
```

**Påverkan:**
- Gamla modeller kraschar med nya features
- Eller nya modeller saknar features
- Version conflict

**Lösning:**
```python
Priority: MEDIUM - Innan feature expansion

1. Strict schema validation:
   ```python
   def validate_features(features, model_schema):
       required = set(model_schema)
       available = set(features.keys())
       missing = required - available
       if missing:
           raise ValueError(f"Missing features: {missing}")
   ```

2. Feature version in model:
   ```json
   {
     "1m": {
       "schema": ["ema_delta_pct", "rsi"],
       "schema_version": "v1",  ← NY!
       "buy": {...}
     }
   }
   ```

3. Backward compatibility:
   ```python
   # Om model kräver v2 men vi har v1:
   # → Beräkna extra features on-the-fly
   # → Eller refuse to load
   ```
```

---

## 🟢 MINDRE KONFLIKTER

### 7. Disk Space för Parquet Files

**Problem:**
```
6 months @ 1m = 262,800 rows
× 6 columns (OHLCV + timestamp)
× 8 bytes (float64)
= ~12 MB per symbol/timeframe (uncompressed)

16 symbols × 6 timeframes = 96 files
× 12 MB = 1.15 GB
```

**Lösning:**
- Parquet compression → ~200-400 MB
- Acceptabelt för development
- Production: använd cloud storage

---

### 8. Pandas Import Performance

**Problem:**
```python
import pandas as pd  # ← 200-500ms första gången
```

**Påverkan:**
- Server startup latency
- Testing blir långsammare

**Lösning:**
```python
# Lazy import i backtest/training:
def run_backtest(...):
    import pandas as pd  # ← Only när backtest körs
    ...

# INTE i pipeline-kod (behåller 0.6ms latency)
```

---

### 9. Test Symbols vs Real Symbols

**Problem:**
```python
# Paper trading: tTESTBTC:TESTUSD
# Historical data: tBTCUSD
# Models: tBTCUSD
```

**Påverkan:**
- Confusion mellan test/real symbols
- Fel symbol i training

**Lösning:**
```python
# Tydlig namngivning:
# DATA:   tBTCUSD (real market data)
# MODEL:  tBTCUSD (trained on real data)
# PAPER:  tTESTBTC:TESTUSD (test execution)

# Symbol mapping finns redan i SymbolMapper
```

---

### 10. Concurrent Model Updates

**Problem:**
```
Bot läser model → Training skriver model → Race condition
```

**Lösning:**
```python
# Atomic writes:
import tempfile
import os

def save_model_atomic(path, data):
    with tempfile.NamedTemporaryFile(
        mode='w', 
        dir=path.parent, 
        delete=False
    ) as f:
        json.dump(data, f)
        temp_path = f.name
    os.replace(temp_path, path)  # Atomic på POSIX
```

---

## 📋 PRE-PHASE3 CHECKLIST

**Innan du börjar Phase 3, gör:**

- [ ] **Migrera alla modeller till multi-timeframe struktur**
  - Script: `scripts/migrate_model_structure.py`
  - Validera: Kör alla tester
  - Commit: `feat: migrate all models to multi-timeframe structure`

- [ ] **Förbättra ModelRegistry cache invalidation**
  - Fixa mtime-check eller använd hash
  - Test: Manuell model update → verify reload
  - Commit: `fix: improve model cache invalidation`

- [ ] **Skapa data directory structure**
  - `mkdir -p data/{candles,features,metadata}`
  - Uppdatera `.gitignore`
  - Skapa `data/README.md`
  - Commit: `chore: setup data directory structure`

- [ ] **Implementera rate limiter**
  - Install: `pip install ratelimit tenacity`
  - Base utility: `src/core/utils/rate_limit.py`
  - Commit: `feat: add rate limiting utility`

- [ ] **Review och dokumentera**
  - Läs igenom TODO_PHASE3.md
  - Läs igenom denna fil (PHASE3_CONFLICTS.md)
  - Diskutera om något är oklart

---

## 🔄 KONFLIKT-LÖSNINGS PRIORITET

```
1. KRITISKT (Innan Phase 3):
   ✅ Migrera model struktur
   ✅ Fixa cache invalidation
   ✅ Skapa data directories

2. HÖGT (Innan första träning):
   ✅ Rate limiting
   ✅ Versioning workflow
   ✅ Schema validation

3. MEDIUM (Kan fixas under Phase 3):
   ⚠️ Feature schema changes
   ⚠️ Disk space planning
   ⚠️ Lazy imports

4. LÅGT (Nice-to-have):
   ○ Concurrent update handling
   ○ Cloud storage integration
```

---

## 🎯 SAMMANFATTNING

**Totalt identifierade konflikter:** 10  
**Kritiska:** 3  
**Medel:** 3  
**Mindre:** 4  

**Estimated resolution time:**
- Kritiska: 4-6 timmar
- Medel: 4-6 timmar
- Mindre: 2-3 timmar
**Total: 1-2 arbetsdagar**

**Rekommendation:**
Lös alla kritiska konflikter INNAN Phase 3 påbörjas.
Detta sparar tid och förhindrar problem senare.

**Status:** ✅ Redo att börja resolution

---

**Nästa steg:**
1. Skapa `scripts/migrate_model_structure.py`
2. Kör migration
3. Kör alla tester
4. Fortsätt med nästa kritiska konflikt
