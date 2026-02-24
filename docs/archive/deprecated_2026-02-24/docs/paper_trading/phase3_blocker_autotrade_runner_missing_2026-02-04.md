# Phase 3 Blocker: Autotrade Runner Missing

**Discovered:** 2026-02-04 10:40 UTC
**Severity:** CRITICAL - Blocks paper trading
**Status:** 🚨 **BLOCKED**

---

## Executive Summary

**Phase 3 paper trading är BLOCKED** pga saknad autotrade-runner.

**Vad vi har:**

- ✅ API-server operativ (http://localhost:8000)
- ✅ Champion v5a loaded och verified
- ✅ Manual evaluation via /strategy/evaluate fungerar
- ✅ Paper order submission endpoint (/paper/submit) finns

**Vad som SAKNAS:**

- ❌ **Autotrade-runner** - ingen process som driver trading-loopen
- ❌ Candle-close polling
- ❌ Automatisk evaluate → submit order flow
- ❌ Kontinuerlig paper trading execution

**Konsekvens:**

- Paper trading kan INTE köra automatiskt
- "LIVE sedan 2026-02-04 09:29 UTC" avser endast API-upptid
- **Ingen faktisk trading har skett eller kan ske utan manuell intervention**

---

## Bevis 1: Server Log Analysis

### Försök att starta paper trading server (2026-02-04 09:29 UTC)

**Log file:** `logs/paper_trading/server_20260204_092902.log`
**Size:** 435 bytes (efter 60+ minuter idle)

**Complete log content:**

```
INFO:     Started server process [48412]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000):
          normalt tillåts bara en användare för varje socketadress (protokoll/nätverkadress/port)
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
CONFIG_VERSION=105 CONFIG_HASH={"ev":{"R_de
```

**Analysis:**

- Server process 48412 försökte starta
- Port 8000 redan upptagen av annan process
- Server stängdes ned
- **Total log size 435 bytes = INGEN aktivitet efter startup**

**Expected for autotrade:**

- Skulle se: "Polling started", "Candle close detected", "Evaluating...", "Order submitted", etc.
- Skulle växa: Minst 1 log-rad per minut (candle polling), hundratals rader efter 60 min
- **Actual: 435 bytes static log = NO autotrade loop**

---

### Active server process (discovered 2026-02-04 10:40 UTC)

**Process info:**

```
PID: 18725
Started: 17:01:44 (2026-02-03, före pre-flight)
Command: /c/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/uvicorn
```

**Health check:**

```bash
$ curl -s http://localhost:8000/health
{"status":"ok","config_version":105, ...}
```

**Log location:** Unknown (inte logs/paper_trading/, ingen stdout/stderr visible)

**Analysis:**

- Server svarar på HTTP requests
- Ingen synlig logging aktivitet
- Startad FÖRE pre-flight (pre-existerande process)
- **NO scheduler/polling activity observed**

---

## Bevis 2: Server Source Code Analysis

### server.py lifespan analysis

**File:** `src/core/server.py` (1049 lines)

**Lifespan event handler:**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown."""
    # Startup
    try:
        _, h, v = _AUTH.get()
        print(f"CONFIG_VERSION={v} CONFIG_HASH={h[:12]}")
    except Exception as e:
        print(f"CONFIG_READ_FAILED: {e}")

    yield

    # Shutdown (cleanup if needed)
    try:
        await aclose_http_client()
    except Exception as e:
        _LOGGER.debug("shutdown_close_http_client_error: %s", e)
```

**Analysis:**

- ✅ Startup: Load config, print version
- ✅ Shutdown: Cleanup HTTP client
- ❌ **NO background tasks created**
- ❌ **NO scheduler started**
- ❌ **NO polling loop**
- ❌ **NO asyncio.create_task for autotrade**

**Search results:**

```bash
$ grep -n "app.add_event_handler\|BackgroundTasks\|scheduler\|autotrade\|polling" src/core/server.py
# NO RESULTS (only HTML template references to "background:" CSS)
```

**Conclusion:** Server är en ren request/response API-server utan autotrade-funktionalitet.

---

## Bevis 3: Scripts Directory Search

### Search for autotrade runner

**Commands executed:**

```bash
$ find scripts -name "*autotrade*" -o -name "*runner*" -o -name "*loop*" -o -name "*scheduler*"
scripts/verify_runner_fix.py  # (Optuna runner fix, inte autotrade)

$ ls scripts/ | grep -E "trade|run|loop|paper"
calculate_paper_trading_metrics.py  # Metrics (post-analysis)
run_backtest.py                     # Historical backtest
run_extended_validation_2024.py     # Validation runs
run_milestone3_exp1.py              # Backtest experiments
... (ingen autotrade runner)
```

**Analysis:**

- `calculate_paper_trading_metrics.py` - Metrics-rapport (EFTER trading, inte driver)
- Alla `run_*.py` scripts - Backtesting och validation (historisk data)
- **NO paper_trading_runner.py eller liknande**
- **NO script som pollar candles och skickar orders**

---

## Bevis 4: Endpoint Functionality Test

### Manual /strategy/evaluate verification (2026-02-04 09:29 UTC)

**Request:**

```bash
POST http://localhost:8000/strategy/evaluate
Body: {"policy":{"symbol":"tBTCUSD","timeframe":"1h"}}
```

**Response (excerpt):**

```json
{
  "result": {
    "action": "NONE",
    "confidence": { "overall": 0.353 },
    "regime": "balanced"
  },
  "meta": {
    "champion": {
      "source": "config\\strategy\\champions\\tBTCUSD_1h.json"
    }
  }
}
```

**Analysis:**

- ✅ Endpoint fungerar
- ✅ Champion laddas korrekt
- ✅ Evaluation körs
- ❌ **Men INGEN process anropar denna endpoint automatiskt**
- ❌ **Manual API-call endast - ingen loop**

---

## Impact Assessment

### Vad "LIVE sedan 2026-02-04 09:29 UTC" faktiskt betyder

**Vad som är LIVE:**

- API-server online och svarar på requests
- /health, /ui, /strategy/evaluate, /paper/submit endpoints operativa
- Champion v5a loaded och verified
- Manual testing möjlig via /ui eller curl

**Vad som INTE är LIVE:**

- ❌ Automatisk paper trading execution
- ❌ Candle-close detection
- ❌ Kontinuerlig evaluation loop
- ❌ Order submission baserat på signals
- ❌ **INGEN faktisk trading har skett**

**Paper Trading Status:**

- Declared: "LIVE från 2026-02-04 09:29 UTC"
- **Reality: BLOCKED - API-upptid endast, INGEN autotrade-process**
- Data collection: NONE (inga orders, inga trades)
- Metrics: N/A (ingen trading att rapportera)

---

## Root Cause Analysis

### Arkitektonisk brist

**System är designat som:**

- Stateless API-server (request/response only)
- Manual evaluation via HTTP endpoints
- UI för interactive testing

**System SAKNAR:**

- Background worker/scheduler
- Candle polling mechanism
- Autotrade decision loop
- Order submission automation

**Inte dokumenterat i:**

- `docs/paper_trading/README.md` - Nämner INTE att runner krävs
- `CLAUDE-LOCAL.md` - Beskriver endpoints, men INTE autotrade-runner
- Pre-flight checklist - INGEN verifiering av autotrade-process

**Discovery trigger:**

- User request: "kolla upp http://localhost:8000/ui"
- Follow-up question: Verify autotrade-runner exists
- Server log analysis: 435 bytes efter 60 min = NO activity
- Source code inspection: NO background tasks

---

## Freeze Rules Impact

### Current freeze status (2026-02-04 to 2026-03-17)

**Freeze-guard active:** `.github/workflows/champion-freeze-guard.yml`

**FORBIDDEN under freeze:**

- ❌ Champion config changes (`config/strategy/champions/`)
- ❌ Strategy logic changes (`src/core/strategy/`)
- ❌ Risk config changes
- ❌ Model changes (`config/models/`)

**ALLOWED under freeze:**

- ✅ Documentation updates (`docs/`)
- ✅ Process/ops improvements (server setup, monitoring)
- ✅ Scripts for data collection/analysis
- ✅ **NEW: Runner-process för autotrade (process/ops, INTE champion-change)**

**Rationale:**

- Autotrade-runner är en **process/operations komponent**
- Läser champion config (inte ändrar)
- Anropar befintliga endpoints (inte ändrar logic)
- Loggar decisions/orders (data collection)
- **INGEN påverkan på champion/strategy/risk**

---

## Proposed Resolution: Change Request

### CR-001: Introduce Autotrade Runner (Process/Ops)

**Type:** Process/Operations Enhancement (NOT strategy change)

**Scope:**

- Create: `scripts/paper_trading_runner.py`
- Purpose: Poll candles → evaluate → submit orders (execution only)
- Config: Read-only champion config
- No changes to: champion, strategy logic, risk map, models

**Implementation:**

1. **Polling loop:**
   - Fetch public candles from Bitfinex (tBTCUSD 1h)
   - Detect candle close
   - Rate limit: 1 request per 10 seconds

2. **Evaluation:**
   - POST to `/strategy/evaluate` with `{"policy":{"symbol":"tBTCUSD","timeframe":"1h"}}`
   - Use response to determine action

3. **Order submission:**
   - If action != NONE: POST to `/paper/submit`
   - Log order ID + response
   - Safety: Champion verification (abort if baseline fallback)

4. **Logging:**
   - All evaluations: `logs/paper_trading/runner_evaluations_YYYYMMDD.log`
   - All orders: `logs/paper_trading/runner_orders_YYYYMMDD.log`
   - Errors: `logs/paper_trading/runner_errors_YYYYMMDD.log`

5. **Safety mechanisms:**
   - Dry-run mode (log orders, don't submit)
   - Champion verification on startup
   - Max 1 order per candle-close
   - Abort if baseline fallback detected

**Deployment:**

```bash
# Start runner (separate from API server)
screen -S genesis-runner -dm python scripts/paper_trading_runner.py \
  --symbol tBTCUSD \
  --timeframe 1h \
  --dry-run false \
  --log-dir logs/paper_trading

# Monitor
tail -f logs/paper_trading/runner_*.log
```

**Testing:**

1. Dry-run mode först (24h) - verify logic, no orders sent
2. Single candle test - send 1 test order, verify reception
3. Enable live mode - monitor first 3 hours closely
4. Document in daily health snapshot

**Documentation:**

- Update: `docs/paper_trading/README.md` (add runner requirement)
- Create: `docs/paper_trading/runner_setup.md` (deployment guide)
- Update: `docs/paper_trading/operations_summary.md` (add runner to drift)

**Approval Required:**

- [ ] Verify: Runner läser champion (inte ändrar)
- [ ] Verify: Runner anropar endpoints (inte ändrar logic)
- [ ] Verify: Freeze-regler respekteras (process/ops, inte champion-change)
- [ ] Approve: Change Request CR-001

---

## Timeline

**2026-02-04 09:29 UTC:** Paper trading declared "LIVE" (API-upptid)
**2026-02-04 10:40 UTC:** Blocker discovered (autotrade-runner missing)
**2026-02-04 10:50 UTC:** Blocker documented (this file)
**2026-02-04 TBD:** Change Request approval pending
**2026-02-04 TBD:** Runner implementation (if approved)
**2026-02-04 TBD:** Dry-run testing (24h)
**2026-02-05 TBD:** Paper trading ACTUALLY live (if tests pass)

---

## Recommendations

### Immediate (Today)

1. **Acknowledge blocker:**
   - Paper trading är INTE live (endast API-upptid)
   - Inga trades har skett eller kan ske
   - Start-datum 2026-02-04 09:29 UTC är INVALID för trading

2. **Approve Change Request CR-001:**
   - Verify runner är process/ops (INTE champion-change)
   - Confirm freeze-regler respekteras
   - Greenlight implementation

3. **Update status:**
   - `docs/paper_trading/README.md` - Status: BLOCKED
   - Daily summary - Document blocker discovery
   - Kommunicera revised timeline

### Short-term (1-2 days)

1. **Implement runner** (if CR-001 approved)
2. **Dry-run testing** (24h) - verify logic without live orders
3. **Single-candle test** - send 1 test order, verify
4. **Enable live mode** - monitor closely

### Medium-term (Pre-flight v2)

1. **Update pre-flight checklist:**
   - Add: "Autotrade runner deployed and verified"
   - Add: "Runner logs show polling activity"
   - Add: "Test order submission successful"

2. **Documentation improvements:**
   - Clarify: Paper trading requires BOTH API-server AND runner
   - Document: Runner architecture and deployment
   - Add: Troubleshooting guide for runner issues

---

## Appendix: Server Log Evidence

**File:** `logs/paper_trading/server_20260204_092902.log`
**Created:** 2026-02-04 09:29:02 +0100
**Size:** 435 bytes
**Analyzed:** 2026-02-04 10:40 UTC (71 minutes after creation)

**Complete file content:**

```
INFO:     Started server process [48412]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): normalt tillåts bara en användare för varje socketadress (protokoll/nätverkadress/port)
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
CONFIG_VERSION=105 CONFIG_HASH={"ev":{"R_de
```

**Interpretation:**

- 6 log lines total
- No activity after startup failure
- Port conflict = server shutdown
- **Expected for autotrade:** 1000+ lines (polling, evaluations, decisions)
- **Actual:** 6 lines = static file = NO autotrade process

---

## Status

**Paper Trading:** 🚨 **BLOCKED** (autotrade-runner missing)
**API Server:** ✅ Online (request/response only)
**Champion:** ✅ Loaded and verified
**Trading Activity:** ❌ NONE (zero orders, zero trades)
**Change Request:** ⏳ Pending approval (CR-001: Autotrade Runner)

**Next Action:** Await explicit approval for CR-001 before implementation.
