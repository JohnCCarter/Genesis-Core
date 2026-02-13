# Paper Trading Runner - Deployment Guide

**Script:** `scripts/paper_trading_runner.py`
**Purpose:** Autotrade loop for Phase 3 paper trading (candle polling → evaluation → order submission)

---

## Pre-flight (5 min)

**IMPORTANT:** Use UTC timezone (`date -u`) for consistency with runner logs.

**Fallback note:** If `grep -oP` fails (macOS/BSD), use `grep -E` with `sed` instead:

```bash
# Instead of: grep -oP 'ts=\K[0-9]+'
# Use: grep -oE 'ts=[0-9]+' | sed 's/ts=//'
```

### 1. Verify API Server Running (Port 8000)

**Check which process owns port 8000:**

```bash
# Linux/macOS (lsof)
lsof -i :8000 -P -n

# Linux alternative (ss)
ss -tlnp | grep :8000

# Windows Git Bash (netstat)
netstat -ano | grep :8000
```

**Expected output example:**

```
COMMAND   PID   USER   TYPE DEVICE   NAME
python   1234   user   TCP  *:8000 (LISTEN)
```

**Verify it's the Genesis API server:**

```bash
# Get PID from above output
PID=<pid_from_above>

# Check process command line
ps -fp $PID

# Expected: Should show uvicorn or python with core.server:app
# Example: python /path/to/.venv/bin/uvicorn core.server:app --app-dir src
```

**Health check:**

```bash
curl -s http://localhost:8000/health | grep '"status":"ok"'

# Expected: {"status":"ok","config_version":105,...}
# If fails: API server not running or not responding
```

**If port 8000 not in use (start API server first):**

```bash
cd /c/Users/fa06662/Projects/Genesis-Core
source .venv/Scripts/activate

# Start API server (in separate terminal or screen)
uvicorn core.server:app --app-dir src --port 8000
```

---

### 2. Start Runner in Dry-Run Mode (UTC Timezone)

**CRITICAL:** Use `TZ=UTC` to ensure log filenames and timestamps align.

```bash
# Activate venv (if not already)
source .venv/Scripts/activate

# Start runner with UTC timezone
TZ=UTC python scripts/paper_trading_runner.py --dry-run --symbol tBTCUSD --timeframe 1h --poll-interval 10
```

**Expected startup output:**

```
================================================================================
Paper Trading Runner Started
Symbol: tBTCUSD, Timeframe: 1h
Poll interval: 10s
Mode: DRY-RUN (no orders)
State file: logs/paper_trading/runner_state.json
================================================================================
Verifying champion loading...
Champion verified successfully.
```

**Stop conditions (startup failures):**

- "Failed to evaluate strategy on startup" → API server down or unreachable
- "Champion verification failed" → Champion file missing/corrupt
- "Baseline fallback detected" → Champion not loading correctly
- Any FATAL error → Stop and investigate before proceeding

---

### 3. Verify Log File Writing (Within 2 Minutes)

**Check log file created with correct UTC date:**

```bash
# Use date -u for UTC (matches runner)
LOG_FILE="logs/paper_trading/runner_$(date -u +%Y%m%d).log"

# Verify file exists
ls -lh "$LOG_FILE"

# Expected: File created, size >0 (should be 1-2 KB after startup)
```

**Tail logs in real-time:**

```bash
tail -f logs/paper_trading/runner_$(date -u +%Y%m%d).log
```

**Verify polling activity (every 10 seconds):**

```bash
# Count log lines (should grow steadily)
wc -l logs/paper_trading/runner_$(date -u +%Y%m%d).log

# After 2 minutes: Should have 50+ lines (startup + ~12 polls)
```

**Check for champion verification:**

```bash
grep "Champion verified successfully" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Expected: At least 1 line
```

**Check for errors in first 2 minutes:**

```bash
grep -E "ERROR|FATAL" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Expected: Empty (or only transient "Failed to fetch candle" is OK if rare)
```

---

### 4. Verify State File Created and Updates (Within 2 Minutes)

**Check state file exists:**

```bash
ls -lh logs/paper_trading/runner_state.json

# Expected: File created within 60 seconds of startup
```

**Check initial state:**

```bash
cat logs/paper_trading/runner_state.json

# Expected (before first candle):
# {
#   "last_processed_candle_ts": null,
#   "total_evaluations": 0,
#   "total_orders_submitted": 0,
#   "last_heartbeat": null
# }
```

**Wait for first heartbeat (~100 seconds after startup):**

```bash
# Heartbeat occurs every 10 polls * 10s = 100 seconds
# Wait 2 minutes, then check state
sleep 120
cat logs/paper_trading/runner_state.json | grep last_heartbeat

# Expected: "last_heartbeat": "2026-02-04T10:01:40+00:00" (recent UTC timestamp)
```

**Verify state file updates:**

```bash
# Get initial last_heartbeat
HEARTBEAT1=$(cat logs/paper_trading/runner_state.json | grep -o '"last_heartbeat":"[^"]*"')

# Wait 2 minutes
sleep 120

# Get new last_heartbeat
HEARTBEAT2=$(cat logs/paper_trading/runner_state.json | grep -o '"last_heartbeat":"[^"]*"')

# Should be different (state file is updating)
echo "Initial: $HEARTBEAT1"
echo "After 2min: $HEARTBEAT2"
```

**Stop condition:** If state file not created or not updating → STOP and investigate.

---

### 5. Pre-flight Smoke Test Summary

**Run after 5 minutes:**

```bash
echo "=== Pre-flight Smoke Test ==="

# 1. API server responding
echo "[1/5] API server..."
curl -s http://localhost:8000/health > /dev/null && echo "  ✓ OK" || echo "  ✗ FAIL"

# 2. Log file exists and growing
echo "[2/5] Log file..."
LOG_FILE="logs/paper_trading/runner_$(date -u +%Y%m%d).log"
if [ -f "$LOG_FILE" ] && [ $(wc -l < "$LOG_FILE") -gt 50 ]; then
  echo "  ✓ OK ($(wc -l < "$LOG_FILE") lines)"
else
  echo "  ✗ FAIL (file missing or too small)"
fi

# 3. Champion verified
echo "[3/5] Champion loading..."
grep -q "Champion verified successfully" "$LOG_FILE" && echo "  ✓ OK" || echo "  ✗ FAIL"

# 4. State file exists
echo "[4/5] State file..."
[ -f "logs/paper_trading/runner_state.json" ] && echo "  ✓ OK" || echo "  ✗ FAIL"

# 5. No fatal errors
echo "[5/5] No fatal errors..."
! grep -q "FATAL" "$LOG_FILE" && echo "  ✓ OK" || echo "  ✗ FAIL"

echo ""
echo "If all ✓ OK: Pre-flight passed. Continue 24h dry-run."
echo "If any ✗ FAIL: Stop runner and investigate before proceeding."
```

**Expected output:**

```
=== Pre-flight Smoke Test ===
[1/5] API server...
  ✓ OK
[2/5] Log file...
  ✓ OK (127 lines)
[3/5] Champion loading...
  ✓ OK
[4/5] State file...
  ✓ OK
[5/5] No fatal errors...
  ✓ OK

If all ✓ OK: Pre-flight passed. Continue 24h dry-run.
```

---

## Quick Start

### Dry-Run Mode (Safe - No Orders Submitted)

```powershell
# Activate venv
. .\.venv\Scripts\Activate.ps1

# Run in dry-run mode (logs orders but doesn't submit)
python scripts/paper_trading_runner.py --dry-run
```

**Default behavior:**

- Symbol: tBTCUSD
- Timeframe: 1h
- Poll interval: 10 seconds
- API server: http://localhost:8000
- State file: `logs/paper_trading/runner_state.json`
- Logs: `logs/paper_trading/runner_YYYYMMDD.log`

### Live Paper Trading

```powershell
# Run in live-paper mode (submits real paper orders)
python scripts/paper_trading_runner.py --live-paper
```

**IMPORTANT:** Only use `--live-paper` after:

1. 24h dry-run test passes
2. Champion verification confirmed
3. Single test order successful

---

## CLI Options

```
--host HOST               API server host (default: localhost)
--port PORT               API server port (default: 8000)
--symbol SYMBOL           Trading symbol (default: tBTCUSD)
--timeframe TIMEFRAME     Candle timeframe (default: 1h)
--poll-interval SECONDS   Polling interval (default: 10)
--dry-run                 Dry-run mode: log orders but don't submit
--live-paper              Live paper trading: submit real orders
--log-dir PATH            Log directory (default: logs/paper_trading)
--state-file PATH         State file for idempotency (default: logs/paper_trading/runner_state.json)
```

**Mutual exclusivity:** Cannot set both `--dry-run` and `--live-paper`.
**Default mode:** If neither flag is set, defaults to `--dry-run`.

---

## Deployment Options

### Option 1: Screen (Recommended for Development)

**Start runner in screen:**

```powershell
# Windows Git Bash or WSL
screen -S genesis-runner -dm bash -c ". .venv/Scripts/activate && python scripts/paper_trading_runner.py --live-paper 2>&1 | tee -a logs/paper_trading/runner_screen.log"

# Attach to session
screen -r genesis-runner

# Detach: Ctrl+A, then D

# Stop runner
screen -S genesis-runner -X quit
```

**Check if running:**

```bash
screen -ls | grep genesis-runner
```

**View logs:**

```bash
tail -f logs/paper_trading/runner_$(date +%Y%m%d).log
```

### Option 2: PM2 (Cross-Platform)

**Install PM2:**

```bash
npm install -g pm2
```

**Start runner:**

```bash
pm2 start scripts/paper_trading_runner.py --name genesis-runner --interpreter python -- --live-paper
```

**Management:**

```bash
pm2 status                   # Check status
pm2 logs genesis-runner      # View logs
pm2 restart genesis-runner   # Restart
pm2 stop genesis-runner      # Stop
pm2 delete genesis-runner    # Remove
```

**Auto-restart on boot:**

```bash
pm2 startup
pm2 save
```

### Option 3: Systemd (Linux Production)

**Azure/remote note (minimal):**

- If you run this on an Azure VM, keep the VM surface area small:
  - Restrict SSH in the NSG to a single source IP (/32)
  - Disable password auth; key-based only
- Ensure you can actually provision/recover the VM first (subscription visibility). See:
  - `docs/paper_trading/operations_summary.md` (Remote deployment status)
  - `docs/paper_trading/daily_summaries/day2_summary_2026-02-06.md`
  - `docs/paper_trading/daily_summaries/day3_summary_2026-02-11.md`

**Create service file:** `/etc/systemd/system/genesis-runner.service`

```ini
[Unit]
Description=Genesis-Core Paper Trading Runner
After=network.target

[Service]
Type=simple
User=genesis
WorkingDirectory=/opt/genesis/Genesis-Core

# Load secrets and runtime settings from systemd-safe env file.
# Generate it from .env before daemon-reload:
#   ./scripts/generate_env_systemd.sh /opt/genesis/Genesis-Core/.env /opt/genesis/Genesis-Core/.env.systemd
EnvironmentFile=/opt/genesis/Genesis-Core/.env.systemd

ExecStart=/opt/genesis/Genesis-Core/.venv/bin/python scripts/paper_trading_runner.py --live-paper
Restart=always
RestartSec=10
TimeoutStopSec=30

# Prefer journald via `journalctl -u genesis-runner`.

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable genesis-runner
sudo systemctl start genesis-runner

# Check status
sudo systemctl status genesis-runner

# View logs
journalctl -u genesis-runner -f
```

If you changed `.env`, regenerate `.env.systemd` first:

```bash
./scripts/generate_env_systemd.sh /opt/genesis/Genesis-Core/.env /opt/genesis/Genesis-Core/.env.systemd
sudo systemctl daemon-reload
sudo systemctl restart genesis-runner
```

### Option 4: Nohup (Simple Background)

```bash
nohup python scripts/paper_trading_runner.py --live-paper > logs/paper_trading/runner_nohup.log 2>&1 &

# Get PID
echo $!

# Stop (replace PID)
kill <PID>
```

---

## Monitoring

### Check Runner Status

```bash
# Check if process is running
ps aux | grep paper_trading_runner

# View logs (today)
tail -f logs/paper_trading/runner_$(date +%Y%m%d).log

# Check state file
cat logs/paper_trading/runner_state.json
```

**Expected state file content:**

---

## Weekend Gate (Pre-start)

Use the automated gate before weekend activation:

```bash
cd /opt/genesis/Genesis-Core
./scripts/weekend_bot_gate.sh
```

The gate verifies:

1. `.env.systemd` regeneration + BOM/CRLF safety
2. systemd chain (`paper` health, `runner` start sequencing, restart stability)
3. Trading safety checks (`/paper/submit`, symbol fallback contract, `/account/orders`)
4. Strategy/data livetecken (`Champion verified successfully`, candle/evaluation logs)

Result handling:

1. `RESULT: PASS` => proceed
2. `RESULT: FAIL` => stop and fix before any live-paper continuation

```json
{
  "last_processed_candle_ts": 1704067200000,
  "total_evaluations": 42,
  "total_orders_submitted": 10,
  "last_heartbeat": "2026-02-04T12:00:00Z"
}
```

### Log Patterns

**Healthy operation:**

```
INFO - ============================================================
INFO - Paper Trading Runner Started
INFO - Symbol: tBTCUSD, Timeframe: 1h
INFO - Poll interval: 10s
INFO - Mode: LIVE PAPER TRADING
INFO - ============================================================
INFO - Verifying champion loading...
INFO - Champion verified successfully.
INFO - NEW CANDLE CLOSE: ts=1704067200000, close=50100.00
INFO - EVALUATION: action=BUY, signal=1, confidence=0.750
INFO - Submitting BUY order...
INFO - ORDER SUBMITTED: {...}
INFO - Heartbeat: evaluations=42, orders=10, last_candle_ts=1704067200000
```

**Error patterns to watch:**

```
ERROR - Champion NOT loaded! Source: baseline:fallback_1h
ERROR - Baseline fallback detected. ABORTING.
ERROR - HTTP error fetching candles: ...
ERROR - Evaluation failed. Skipping this candle.
ERROR - Order submission failed.
```

### Restart After Failure

Runner is idempotent - safe to restart at any time:

```bash
# Stop old process
pkill -f paper_trading_runner

# Start new process (automatically resumes from last_processed_candle_ts)
python scripts/paper_trading_runner.py --live-paper
```

**State persistence ensures:**

- No duplicate candle processing
- No missed candles (resumes from last processed)
- Counters preserved (total_evaluations, total_orders_submitted)

---

## Safety Features

### 1. Idempotency

**State file:** `logs/paper_trading/runner_state.json`

**Behavior:**

- Tracks `last_processed_candle_ts`
- Skips candles with `ts <= last_processed_candle_ts`
- Fail-closed: Exits on corrupt state file (manual intervention required)

**Restart scenario:**

```
1. Runner processes candle ts=1000 → state saved
2. Runner crashes
3. Runner restarts → loads state (last_processed_candle_ts=1000)
4. Fetches latest candle ts=1000 → SKIPPED (already processed)
5. Fetches latest candle ts=2000 → PROCESSED (new candle)
```

### 2. Champion Verification

**Startup check:**

- POST /strategy/evaluate on startup
- Verify `champion.source` contains "champions"
- Exit if baseline fallback detected

**Per-evaluation check:**

- Verify champion loaded after each /strategy/evaluate
- Exit immediately if baseline fallback detected mid-run

### 3. Dry-Run Default

**Safety by default:**

- If neither `--dry-run` nor `--live-paper` is set, defaults to `--dry-run`
- Dry-run mode logs all orders but never submits to /paper/submit
- Must explicitly enable `--live-paper` for order submission

### 4. Rate Limiting

**Polling discipline:**

- Max 1 request per `poll-interval` seconds (default: 10s)
- Sleep after each poll (success or failure)
- No burst requests

### 5. Graceful Shutdown

**Signal handling:**

- Catches SIGINT (Ctrl+C) and SIGTERM
- Saves state before exit
- Closes HTTP client cleanly

---

## Testing

### Run Tests

```powershell
# Run all runner tests
pytest tests/test_paper_trading_runner.py -v

# Run specific test
pytest tests/test_paper_trading_runner.py::test_idempotency_skips_processed_candles -v
```

**Test coverage:**

- Timeframe conversion (1m, 5m, 15m, 1h, 4h, 1D)
- State persistence (save/load roundtrip)
- Corrupt state fail-closed (verifies sys.exit(1))
- Candle-close detection (closed vs forming)
- HTTP error handling
- Idempotency (skip duplicate candles)
- Champion verification (detect baseline fallback)

### Dry-Run Test (24 Hours)

**Purpose:** Verify logic without live orders

**Steps:**

1. Start in dry-run mode:

```bash
python scripts/paper_trading_runner.py --dry-run
```

2. Monitor logs for 24 hours:

```bash
tail -f logs/paper_trading/runner_$(date +%Y%m%d).log
```

3. Verify expectations:
   - New candles detected every hour (for 1h timeframe)
   - Evaluations run for each candle
   - Orders logged when action != NONE
   - No actual orders submitted (dry-run mode)
   - State file updates correctly

4. Check state file:

```bash
cat logs/paper_trading/runner_state.json
```

**Expected after 24h:**

- `last_processed_candle_ts`: Recent timestamp
- `total_evaluations`: ~24 (one per hour)
- `total_orders_submitted`: 0 (dry-run mode)

### Single-Candle Live Test

**Purpose:** Verify order submission works

**Steps:**

1. Wait for candle close (top of hour for 1h timeframe)

2. Run in live-paper mode:

```bash
python scripts/paper_trading_runner.py --live-paper --poll-interval 5
```

3. Monitor logs for first evaluation + order:

```bash
tail -f logs/paper_trading/runner_$(date +%Y%m%d).log
```

4. Verify order submission:
   - Look for "ORDER SUBMITTED: {...}" in logs
   - Check `total_orders_submitted` in state file
   - Verify order appears in Bitfinex paper trading UI

5. Stop runner:

```bash
# Ctrl+C (graceful shutdown)
```

6. Verify state persisted:

```bash
cat logs/paper_trading/runner_state.json
```

**If test passes:** Enable persistent deployment (screen/pm2/systemd)

---

## Troubleshooting

### Runner exits immediately

**Symptom:** Runner starts then exits with error

**Possible causes:**

1. **Champion not loaded:**

```
ERROR - Champion NOT loaded! Source: baseline:fallback_1h
ERROR - Champion verification failed. Exiting.
```

**Fix:** Verify `config/strategy/champions/tBTCUSD_1h.json` exists and has `merged_config` key.

2. **API server not running:**

```
ERROR - Failed to evaluate strategy on startup. Exiting.
```

**Fix:** Start API server first: `uvicorn core.server:app --app-dir src --port 8000`

3. **Corrupt state file:**

```
FATAL: State file corrupt: logs/paper_trading/runner_state.json
Fail-closed: Cannot proceed with corrupt state.
```

**Fix:** Delete state file (will start fresh): `rm logs/paper_trading/runner_state.json`

### No candles fetched

**Symptom:** Logs show "Failed to fetch candle. Retrying..."

**Possible causes:**

1. **Network issue:** Check internet connection
2. **Bitfinex API error:** Check https://api-pub.bitfinex.com/v2/platform/status
3. **Invalid symbol:** Verify symbol format (tBTCUSD not BTCUSD)

### No orders submitted

**Symptom:** Evaluations run but no orders logged

**Possible causes:**

1. **action=NONE:** Strategy decision is NONE (no signal)
   - Check logs for "EVALUATION: action=NONE"
   - Review decision reasons in evaluation response

2. **Dry-run mode:** Runner in dry-run mode (default)
   - Check logs for "Mode: DRY-RUN (no orders)"
   - Switch to `--live-paper` if intended

### Duplicate orders

**Symptom:** Same candle processed multiple times

**Diagnosis:** Idempotency failure (should not happen)

**Immediate action:**

1. Stop runner immediately
2. Check state file for corruption
3. Review logs for duplicate candle timestamps
4. Do NOT restart until root cause identified

**Prevention:** State file is saved atomically after each candle processing.

---

## Upgrade Path

### From Dry-Run to Live-Paper

1. Stop dry-run process:

```bash
pkill -f paper_trading_runner
```

2. Verify state file exists and is recent:

```bash
cat logs/paper_trading/runner_state.json
```

3. Start in live-paper mode:

```bash
python scripts/paper_trading_runner.py --live-paper
```

**State is preserved:** Runner resumes from `last_processed_candle_ts`.

### From Manual to Persistent

1. Test runner manually first (dry-run 24h + single-candle live test)

2. Choose deployment option (screen/pm2/systemd)

3. Deploy with chosen option (see Deployment Options above)

4. Verify logs show continuous operation

5. Monitor for first 3 hours closely

---

## Integration with Operations

### Daily Health Check

**Include runner status in daily health snapshot:**

```bash
# Check runner process
ps aux | grep paper_trading_runner

# Check state file age (should be recent)
stat logs/paper_trading/runner_state.json

# Count today's evaluations (in logs)
grep "EVALUATION:" logs/paper_trading/runner_$(date +%Y%m%d).log | wc -l
```

**Expected for 1h timeframe:**

- Process running: YES
- State file age: < 10 minutes
- Evaluations today: ~hour_of_day (e.g., 12 evaluations by noon)

### Weekly Metrics

**Runner provides data for weekly metrics report:**

- `total_evaluations`: Should match expected cadence (168 for 1h/week)
- `total_orders_submitted`: Feed into trade count metrics
- Logs: Source for order decisions, confidence, regime

**Script integration:**

`scripts/calculate_paper_trading_metrics.py` reads order logs to generate weekly report.

---

## Emergency Procedures

### Stop Paper Trading

**Immediate stop:**

```bash
# Kill runner process
pkill -f paper_trading_runner

# Verify stopped
ps aux | grep paper_trading_runner
```

**State preserved:** Safe to restart later (idempotent).

### Restart After Emergency

1. Verify API server is healthy:

```bash
curl -s http://localhost:8000/health
```

2. Check state file integrity:

```bash
python -c "import json; print(json.load(open('logs/paper_trading/runner_state.json')))"
```

3. If state corrupt: Delete and accept data loss

```bash
mv logs/paper_trading/runner_state.json logs/paper_trading/runner_state.json.bak
```

4. Restart runner:

```bash
python scripts/paper_trading_runner.py --live-paper
```

### Rollback to Dry-Run

**If issues detected during live-paper:**

1. Stop live-paper runner
2. Start in dry-run mode to continue logging without orders
3. Investigate issue
4. Resume live-paper after fix confirmed

---

## Success Criteria

**Runner operational if:**

- Process running continuously (uptime > 23h/day)
- State file updates every hour (for 1h timeframe)
- Evaluations logged for each new candle
- Orders submitted when action != NONE (live-paper mode)
- No champion verification failures
- No state corruption errors

**Monitor weekly:**

- Runner uptime: Should be 99%+
- Evaluation cadence: Should match timeframe (168 for 1h/week)
- Order submission success rate: Should be 100% (no API errors)

---

## References

- **Runner source:** `scripts/paper_trading_runner.py`
- **Runner tests:** `tests/test_paper_trading_runner.py`
- **Operations summary:** `docs/paper_trading/operations_summary.md`
- **Weekly metrics:** `docs/paper_trading/weekly_metrics.md`
- **Server setup:** `docs/paper_trading/server_setup.md`
- **Paper trading README:** `docs/paper_trading/README.md`
