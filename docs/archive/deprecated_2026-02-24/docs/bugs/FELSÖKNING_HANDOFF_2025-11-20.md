# Felsöknings-Handoff: Noll-Trade-Problemet

**Datum:** 2025-11-20
**Repository:** JohnCCarter/Genesis-Core
**Branch:** Phase-7d
**Senaste commit:** `99f1cea` (perf: ATR/Fibonacci cache optimization)

---

## Problemsammanfattning

**Symptom:** Backtest-körningar genererar **0 trades** trots aggressivt sänkta trösklar för Fibonacci-gates och signal adaptation.

**Förväntad:** Champion-konfigurationen (`config/strategy/champions/tBTCUSD_1h.json`) har historiskt givit 75+ trades på samma tidsperiod.

**Aktuellt:** Även med toleranser sänkta till 0.3/0.4 (HTF/LTF) och ATR-zoner till 0.22/0.26/0.30 → fortfarande 0 trades.

---

## Senaste Diagnostic-Körning

**Fil:** `diagnose_output.txt`
**Datum:** 2025-11-17 11:08
**Kommando:** `python scripts/diagnose_fib_flow.py`

### Konfiguration använd

- **Symbol:** tBTCUSD
- **Timeframe:** 1h
- **Period:** 2024-10-22 till 2024-11-22 (732 candles)
- **Warmup:** 120 bars
- **Champion:** `config/strategy/champions/tBTCUSD_1h.json`

### Fibonacci-toleranser

```json
{
  "htf_fib": {
    "entry": {
      "enabled": true,
      "tolerance_atr": 0.5,
      "long_max_level": 0.618,
      "short_min_level": 0.382
    }
  },
  "ltf_fib": {
    "entry": {
      "enabled": true,
      "tolerance_atr": 0.5,
      "long_max_level": 0.618,
      "short_min_level": 0.382
    }
  }
}
```

### Resultat

```
[RESULT] Trades: 0
[RESULT] Return: 0.00%
[RESULT] PF: inf
[RESULT] DD: 0.00%
```

### Logganalys

**Positivt:** Fibonacci-kontexten skapas korrekt:

```
[FIB-FLOW] HTF fibonacci context created: symbol=tBTCUSD timeframe=1h available=True
[FIB-FLOW] LTF fibonacci context created: symbol=tBTCUSD timeframe=1h available=True
[FIB-FLOW] evaluate_pipeline state assembly: htf_available=True ltf_available=True
```

**Problem:** Inga `[DECISION]`-loggar hittades i `diagnose_output.txt`, vilket tyder på att beslutsfunktionen antingen:

1. Inte anropas alls
2. Blockeras innan Fibonacci-gates nås
3. Loggar inte skrivs trots att koden körts (osannolikt eftersom FIB-FLOW loggar syns)

---

## Dataflöde (Aktuell Implementation)

### 1. Feature Extraction (`src/core/strategy/features_asof.py`)

**Funktion:** `extract_features()`

**Ansvar:**

- Läser HTF/LTF Fibonacci-konfiguration
- Anropar `get_htf_fibonacci_context()` och `get_ltf_fibonacci_context()`
- Bygger `feats_meta` dictionary med nycklar:
  - `feats_meta['htf_fibonacci']` - HTF kontext
  - `feats_meta['ltf_fibonacci']` - LTF kontext
  - `feats_meta['htf_selector']` - MTF selector metadata

**Bekräftat fungerande:**

```python
# Från diagnose_output.txt rad 50+
INFO - core.strategy.features_asof - [FIB-FLOW] HTF fibonacci context created: symbol=tBTCUSD timeframe=1h available=True
INFO - core.strategy.features_asof - [FIB-FLOW] LTF fibonacci context created: symbol=tBTCUSD timeframe=1h available=True
```

### 2. Pipeline Orchestration (`src/core/strategy/evaluate.py`)

**Funktion:** `evaluate_pipeline()`

**Rad 139-156 (kritisk sektion):**

```python
htf_fib_data = feats_meta.get("htf_fibonacci")
ltf_fib_data = feats_meta.get("ltf_fibonacci")

log_fib_flow(
    "[FIB-FLOW] evaluate_pipeline state assembly: symbol=%s timeframe=%s htf_available=%s ltf_available=%s",
    symbol,
    timeframe,
    htf_fib_data.get("available") if isinstance(htf_fib_data, dict) else False,
    ltf_fib_data.get("available") if isinstance(ltf_fib_data, dict) else False,
)

state = {
    **state,
    "current_atr": feats.get("atr_14"),
    "atr_percentiles": feats_meta.get("atr_percentiles"),
    "htf_fib": htf_fib_data,
    "ltf_fib": ltf_fib_data,
    "last_close": last_close,
}

action, action_meta = decide(
    policy,
    probas=probas,
    confidence=conf,
    regime=regime,
    state=state,  # <--- HTF/LTF data finns här
    risk_ctx=configs.get("risk"),
    cfg=configs,
)
```

**Bekräftat fungerande:**

```python
# Från diagnose_output.txt
INFO - core.strategy.evaluate - [FIB-FLOW] evaluate_pipeline state assembly: symbol=tBTCUSD timeframe=1h htf_available=True ltf_available=True
```

### 3. Decision Logic (`src/core/strategy/decision.py`)

**Funktion:** `decide()`

**HTF Fibonacci Gate (rad 493-550):**

```python
htf_entry_cfg = (cfg.get("htf_fib") or {}).get("entry") or {}

if use_htf_block and htf_entry_cfg.get("enabled"):
    htf_ctx = state_in.get("htf_fib") or {}  # <--- Läser från state

    log_fib_flow(
        "[FIB-FLOW] HTF gate active: symbol=%s timeframe=%s enabled=%s htf_ctx_keys=%s available=%s",
        policy_symbol,
        policy_timeframe,
        htf_entry_cfg.get("enabled"),
        list(htf_ctx.keys()) if isinstance(htf_ctx, dict) else [],
        htf_ctx.get("available") if isinstance(htf_ctx, dict) else None,
        logger=_LOG,
    )

    # Gate-logik som kan returnera "NONE"
    if not htf_ctx.get("available"):
        # ... blockering eller pass
```

**Förväntade loggar (saknas i diagnose_output.txt):**

- `[FIB-FLOW] HTF gate active: ...`
- `[DECISION] HTF_FIB_BLOCK ...`
- `[DECISION] CANDIDATE_SELECTED ...`

---

## Hypoteser

### Hypotes 1: Beslutsfunktionen nås aldrig ✅ TROLIGAST

**Bevis:**

- Inga `[DECISION]`-loggar trots att `_log_decision_event()` anropas tidigt i `decide()` (rad 305)
- FIB-FLOW loggar från `features_asof.py` och `evaluate.py` syns väl

**Möjliga orsaker:**

- Exception kastas innan `decide()` anropas i `evaluate_pipeline()`
- `predict_proba_for()` eller `compute_confidence()` misslyckas tyst
- `decide()` anropas men exception kastas före första loggningen

**Åtgärd:**

```python
# I evaluate.py, före decide()-anrop, lägg till:
_LOG.info("[DEBUG] About to call decide() with state keys: %s", list(state.keys()))

try:
    action, action_meta = decide(...)
except Exception as e:
    _LOG.error("[ERROR] decide() failed: %s", e, exc_info=True)
    raise
```

### Hypotes 2: Fibonacci-context är tom/felaktig

**Status:** ❌ OSANNOLIKT (loggar visar `available=True`)

**Men:** Vi ser aldrig innehållet av `htf_ctx` dictionary. Kan vara:

```python
{"available": True}  # Men saknar "levels", "swing_high", etc.
```

**Åtgärd:**

```python
# I decision.py rad ~501
htf_ctx = state_in.get("htf_fib") or {}
_LOG.info("[DEBUG] HTF context raw: %s", htf_ctx)
```

### Hypotes 3: Tidigare gate blockerar

**Status:** ⚠️ MÖJLIG

Beslutsfunktionen har gates före HTF/LTF-checks:

1. EV-filter (rad ~150)
2. Proba-tröskel (rad ~250)
3. Confidence-gate (rad ~800+)

**Åtgärd:**
Kör backtest med extremt låga trösklar:

```json
{
  "thresholds": {
    "entry_conf_overall": 0.05,
    "exit_conf_threshold": 0.05
  },
  "ev": {
    "enabled": false
  }
}
```

### Hypotes 4: Logging-systemet felkonfigurerat

**Status:** ❌ OSANNOLIKT (andra loggar fungerar)

Men kontrollera:

```bash
# .env eller miljövariabler
FIB_FLOW_LOGS_ENABLED=1  # <--- Måste vara aktiverad!
CORE_LOG_LEVEL=INFO
```

---

## Diagnos-Verktyg

### Script 1: `scripts/diagnose_fib_flow.py`

**Syfte:** Kör backtest med förstärkt FIB-FLOW-loggning

**Användning:**

```powershell
python scripts/diagnose_fib_flow.py > diagnose_output.txt 2>&1
```

**Output:** `diagnose_output.txt` (6227 rader, sista körning 2025-11-17)

### Script 2: `scripts/diagnose_zero_trades.py`

**Syfte:** Analyserar varför ingen trade skapades

**Användning:**

```powershell
python scripts/diagnose_zero_trades.py
```

**Output:** Klassificerar blockerings-orsaker (PROBA_THRESHOLD, LTF_FIB_BLOCK, etc.)

---

## Nuvarande Configuration State

### Runtime Config (`config/runtime.json`)

**Version:** 94
**Senast synkad:** 2025-11-19 (commit `99f1cea`)

**Signal Adaptation (ATR zones):**

```json
{
  "signal_adaptation": {
    "zones": {
      "low": { "entry": 0.25, "regime": 0.45 },
      "mid": { "entry": 0.28, "regime": 0.5 },
      "high": { "entry": 0.32, "regime": 0.55 }
    }
  }
}
```

**Fibonacci Gates:**

```json
{
  "htf_fib": {
    "entry": {
      "enabled": true,
      "tolerance_atr": 0.5,
      "long_max_level": 0.618,
      "short_min_level": 0.382
    }
  },
  "ltf_fib": {
    "entry": {
      "enabled": true,
      "tolerance_atr": 0.5,
      "long_max_level": 0.618,
      "short_min_level": 0.382
    }
  }
}
```

**Multi-Timeframe:**

```json
{
  "multi_timeframe": {
    "use_htf_block": true,
    "allow_ltf_override": false,
    "ltf_override_threshold": 0.75
  }
}
```

### Seed Config (`config/runtime.seed.json`)

**Status:** Synkad med runtime.json 2025-11-19
**Syfte:** Bootstrap-mall när runtime.json saknas

---

## Nästa Steg (Prioriterad Åtgärdslista)

### Steg 1: Bekräfta att `decide()` anropas ⭐ HÖGSTA PRIORITET

```python
# Lägg till i src/core/strategy/evaluate.py rad ~157
_LOG.info("[DEBUG] Pre-decide state keys: %s", list(state.keys()))
_LOG.info("[DEBUG] Pre-decide htf_fib available: %s",
          state.get('htf_fib', {}).get('available') if isinstance(state.get('htf_fib'), dict) else None)

try:
    action, action_meta = decide(
        policy,
        probas=probas,
        confidence=conf,
        regime=regime,
        state=state,
        risk_ctx=configs.get("risk"),
        cfg=configs,
    )
    _LOG.info("[DEBUG] Post-decide action: %s reasons: %s", action, action_meta.get('reasons'))
except Exception as e:
    _LOG.error("[ERROR] decide() exception: %s", e, exc_info=True)
    raise
```

### Steg 2: Inspektera HTF-context innehåll

```python
# I src/core/strategy/decision.py rad ~501
htf_ctx = state_in.get("htf_fib") or {}
_LOG.info("[DEBUG-HTF] Raw HTF context: %s", htf_ctx)
_LOG.info("[DEBUG-HTF] Available: %s, Keys: %s",
          htf_ctx.get('available'),
          list(htf_ctx.keys()) if isinstance(htf_ctx, dict) else 'NOT_DICT')
```

### Steg 3: Testa extrema trösklar

**Mål:** Avgöra om problemet är threshold-relaterat eller strukturellt

**Test-config** (`config/tmp/emergency_permissive.json`):

```json
{
  "cfg": {
    "parameters": {
      "thresholds": {
        "entry_conf_overall": 0.01,
        "exit_conf_threshold": 0.01
      },
      "signal_adaptation": {
        "zones": {
          "low": { "entry": 0.05, "regime": 0.1 },
          "mid": { "entry": 0.1, "regime": 0.2 },
          "high": { "entry": 0.15, "regime": 0.3 }
        }
      },
      "ev": {
        "enabled": false
      },
      "gates": {
        "proba": {
          "enabled": false
        }
      },
      "htf_fib": {
        "entry": {
          "enabled": false
        }
      },
      "ltf_fib": {
        "entry": {
          "enabled": false
        }
      }
    }
  }
}
```

**Kör:**

```powershell
python scripts/run_backtest.py --config config/tmp/emergency_permissive.json --symbol tBTCUSD --timeframe 1h
```

**Förväntat resultat:**

- **Om 0 trades:** Strukturellt problem (exception/dataflöde)
- **Om >0 trades:** Threshold-problem (justera gates stegvis)

### Steg 4: Lägg till `[DECISION]`-loggar i toppen av `decide()`

```python
# I src/core/strategy/decision.py rad ~90 (direkt efter function definition)
def decide(
    policy: dict[str, Any],
    *,
    probas: dict[str, float] | None,
    confidence: dict[str, float] | None,
    regime: str | None,
    state: dict[str, Any] | None,
    risk_ctx: dict[str, Any] | None,
    cfg: dict[str, Any] | None,
) -> tuple[Action, dict[str, Any]]:
    # LÄGG TILL DENNA RAD FÖRST:
    _LOG.info("[DECISION] Function called - probas: %s, confidence: %s, regime: %s",
              probas, confidence, regime)

    # Resten av funktionen...
```

### Steg 5: Kör ny diagnostic med förstärkt loggning

```powershell
# Sätt miljövariabler
$env:FIB_FLOW_LOGS_ENABLED='1'
$env:CORE_LOG_LEVEL='DEBUG'
$env:LOG_LEVEL='DEBUG'

# Kör diagnostic
python scripts/diagnose_fib_flow.py > diagnose_output_2025-11-20.txt 2>&1

# Analysera
Select-String -Path diagnose_output_2025-11-20.txt -Pattern '\[DECISION\]|\[DEBUG\]|\[ERROR\]'
```

---

## Referensfiler

### Kodbas

- **Pipeline:** `src/core/strategy/evaluate.py` (rad 100-192)
- **Beslut:** `src/core/strategy/decision.py` (rad 1-1043)
- **Features:** `src/core/strategy/features_asof.py`
- **HTF Fibonacci:** `src/core/indicators/htf_fibonacci.py`
- **LTF Fibonacci:** `src/core/indicators/fibonacci.py`

### Konfiguration

- **Champion:** `config/strategy/champions/tBTCUSD_1h.json`
- **Runtime:** `config/runtime.json` (version 94)
- **Seed:** `config/runtime.seed.json`

### Diagnostik

- **Output:** `diagnose_output.txt` (2025-11-17)
- **Scripts:** `scripts/diagnose_fib_flow.py`, `scripts/diagnose_zero_trades.py`

### Dokumentation

- **Agent-handoff:** `AGENTS.md` (uppdaterad 2025-11-19)
- **Daily summary:** `docs/daily_summaries/daily_summary_2025-11-19.md`
- **Performance:** `docs/performance/PERFORMANCE_OPTIMIZATION_SUMMARY_.md`

---

## Senaste Kod-Ändringar (Commit 99f1cea)

**Optimeringar som KAN påverka:**

1. ✅ **ATR/Fibonacci cache** - Kan ha förändrat timing/tillgänglighet
2. ✅ **RuntimeConfig schema** - Kan ha påverkat config-parsing
3. ✅ **fib_logging.py** - Ny logging-modul (default-off!)
4. ✅ **Decision.py logging** - Lade till `[DECISION]`-loggar

**Kritisk insikt:**
`fib_logging.py` är **default-off** (`FIB_FLOW_LOGS_ENABLED=0`), MEN loggar från `features_asof.py` och `evaluate.py` syns i diagnose_output.txt. Detta tyder på att:

- FIB_FLOW_LOGS_ENABLED var aktiverad under körningen (korrekt)
- `[DECISION]`-loggarna använder `_LOG.info()` direkt, inte `log_fib_flow()`
- Om `[DECISION]`-loggar saknas är det INTE p.g.a. logging-config

---

## Kontaktinformation & Historik

**Senaste arbetssession:**

- **Datum:** 2025-11-19
- **Aktiviteter:**
  - Cache-optimering (37% snabbare backtester)
  - RuntimeConfig-utökning
  - Decision-logging-förbättring
  - Performance-profiling

**Tidigare sessioner:**

- **2025-11-17:** Diagnostic-körning som producerade `diagnose_output.txt`
- **2025-11-14:** Championparametrar återställda från run_20251023_141747

**Git-status:**

- **Branch:** Phase-7d
- **Commit:** 99f1cea
- **Status:** Working tree clean

---

## Sammanfattning för AI-Agent

**Du står inför ett klassiskt "ghost bug":** Loggar visar att Fibonacci-context skapas korrekt (`available=True`), men ingen trade genereras och inga besluts-loggar syns.

**Primär misstanke:** Exception eller tyst failure mellan `evaluate_pipeline()` och `decide()`, alternativt i toppen av `decide()` innan loggar skrivs.

**Omedelbar åtgärd:**

1. Lägg till try-catch runt `decide()`-anropet i `evaluate.py`
2. Lägg till `[DECISION] Function called` som första rad i `decide()`
3. Kör ny diagnostic och leta efter `[ERROR]` eller `[DEBUG]` i output

**Om inga loggar syns:** Problemet är före `decide()` - granska `predict_proba_for()` och `compute_confidence()`.

**Om loggar syns men 0 trades:** Följ `[DECISION]`-loggarnas reasons för att se vilken gate som blockerar.

Lycka till! 🚀
