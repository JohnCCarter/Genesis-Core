# Phase 3 Paper Trading Runbook

**Period:** 2026-02-04 to 2026-03-17 (6 weeks)
**Objective:** 24h dry-run validation → 41 days live-paper with champion freeze
**Champion:** `config/strategy/champions/tBTCUSD_1h.json` (frozen)

---

## Prerequisites

Before starting Day 0, verify:

- [ ] API server running on port 8000 (`curl http://localhost:8000/health`)
- [ ] Champion file exists: `config/strategy/champions/tBTCUSD_1h.json`
- [ ] Champion structure validated (has `merged_config` key)
- [ ] Log directory exists: `logs/paper_trading/`
- [ ] Scripts are executable:
  - `scripts/paper_trading_runner.py`
  - `scripts/preflight_smoke_test.sh`
  - `scripts/dry_run_acceptance.sh`
  - `scripts/capture_phase3_snapshot.sh`

### Remote hosting (Azure VM) — note

If you intend to run Phase 3 remotely (e.g. on an Azure VM), keep the operational narrative and blockers documented here:

- `docs/paper_trading/operations_summary.md` (Remote deployment status)
- `docs/paper_trading/daily_summaries/day2_summary_2026-02-06.md` (tooling/subscription blocker)
- `docs/paper_trading/daily_summaries/day3_summary_2026-02-11.md` (identity/subscription + VS Code filter + VM incident)

For Windows → Azure VM operations (sync → restart → preflight → schedule 24h acceptance), use:

- `scripts/phase3_remote_orchestrate.ps1`

Notes (remote orchestrator):

- Default SSH target is the SSH-config alias `genesis-we`.
  - Override with `-SshTarget <alias|user@host>` or `GENESIS_SSH_TARGET`.
- The orchestrator fails fast if systemd units are missing (`genesis-paper.service`, `genesis-runner.service`).
  Deploy services first, then `sudo systemctl daemon-reload`.
- Quick stability checks (VM):

  ```bash
  # Verify only one uvicorn is running
  pgrep -af uvicorn

  # Verify service is stable (restart counter not increasing)
  systemctl show genesis-paper.service -p MainPID -p NRestarts -p ActiveState -p SubState --no-pager
  ```

### VM SSH quick-start (interactive session)

Use this when you want to log in and do quick sanity checks manually on the VM.

```bash
# 0) Log in (if you are not already in)
ssh genesis-we

# 1) Become the correct user (if you SSH in as another user)
whoami
sudo -iu genesis

# 2) Go to the repo directory
cd /opt/genesis/Genesis-Core
pwd
ls -la

# 3) Confirm .env is readable and BOM-free
# (Shows invisible characters; the first line should NOT begin with odd symbols.)
head -n 2 .env | cat -A

# 4) Activate venv (if you use .venv)
test -f .venv/bin/activate && source .venv/bin/activate
python -V
which python
pip -V

# 5) Load env vars into the current shell (only if you need to run scripts manually)
# NOTE: Avoid this if your .env contains spaces/quotes you do not want to export naively.
set -a
source .env
set +a

# 6) Sanity: are services up?
sudo systemctl status genesis-paper --no-pager
sudo systemctl status genesis-runner --no-pager

# 7) API health (VM-local loopback)
curl -fsS http://127.0.0.1:8000/health && echo
```

### VM log locations (where logs end up)

On the Azure VM (systemd-managed), logs are primarily available via **journald**:

```bash
# API service logs
journalctl -u genesis-paper -n 200 --no-pager
journalctl -u genesis-paper -f

# Runner service logs
journalctl -u genesis-runner -n 200 --no-pager
journalctl -u genesis-runner -f
```

The runner also writes **its own files** under the repo working directory:

- `/opt/genesis/Genesis-Core/logs/paper_trading/runner_YYYYMMDD.log`
- `/opt/genesis/Genesis-Core/logs/paper_trading/runner_state.json`

Other Phase 3 artefacts typically land in the same directory tree:

- Acceptance output: `/opt/genesis/Genesis-Core/logs/paper_trading/acceptance_check_<UTC_TS>.txt`
- Snapshots: `/opt/genesis/Genesis-Core/logs/paper_trading/snapshots/`

If you use `scripts/phase3_remote_orchestrate.ps1`, it intentionally archives the runner state + runner log files before
restarts to create a clean acceptance window:

- `/opt/genesis/Genesis-Core/logs/paper_trading/_archive/restart_<UTC_TS>/runner_*.log`
- `/opt/genesis/Genesis-Core/logs/paper_trading/_archive/restart_<UTC_TS>/runner_state.json`

Note: The API server does **not** necessarily write `logs/paper_trading/server_*.log` on the VM when running under
systemd; stdout/stderr are captured by journald unless you explicitly redirect to a file.

---

## Execution Verification Checklist

Use this checklist **after each larger operational change** (deploy, config change, service restart, runner update) to
formalize how we verify the system is actually working end-to-end.

### 1) Health endpoint

```bash
curl -s http://127.0.0.1:8000/health
```

### 2) Wallets endpoint (spot-style verification anchor)

```bash
curl -s http://127.0.0.1:8000/account/wallets
```

Record a baseline snapshot (timestamp + relevant wallet balances). This is the reference for the wallet delta check.

### 3) Manual test order (TEST symbols only)

Submit a **small** manual test order through the normal paper path.

- Verify in logs: `ORDER SUBMITTED` (+ follow-up status)
- Verify in API: `/account/orders` (open orders)

### 4) Verify wallet delta

Re-run wallets and confirm a **wallet delta** versus your baseline snapshot.

```bash
curl -s http://127.0.0.1:8000/account/wallets
```

### 5) systemd stability (restart counters)

```bash
systemctl show genesis-paper.service -p MainPID -p NRestarts -p ActiveState -p SubState --no-pager
systemctl show genesis-runner.service -p MainPID -p NRestarts -p ActiveState -p SubState --no-pager

journalctl -u genesis-paper -n 200 --no-pager
journalctl -u genesis-runner -n 200 --no-pager
```

### 6) Runner log tail

```bash
tail -n 200 -f logs/paper_trading/runner_$(date -u +%Y%m%d).log
```

---

## Day 0: Initial Start (Dry-Run)

**Goal:** Start runner in DRY-RUN mode and verify healthy operation within 5 minutes.

### Step 1: Start Runner (DRY-RUN mode)

```bash
# CRITICAL: Use TZ=UTC to ensure log filename consistency
TZ=UTC python scripts/paper_trading_runner.py --dry-run
```

**Expected output:**

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

**Runner process should:**

- Poll every 10 seconds
- Log to `logs/paper_trading/runner_YYYYMMDD.log` (UTC date)
- Create `logs/paper_trading/runner_state.json`
- NOT submit any orders (dry-run mode)

Leave runner running in the background (do NOT stop).

---

### Step 2: Pre-flight Smoke Test (2-3 minutes after start)

**Wait 2-3 minutes** to allow runner to:

- Create log file
- Write initial state
- Poll for first candle

Then run:

```bash
./scripts/preflight_smoke_test.sh
```

**Required result:** Exit code **0** (all checks PASS).

**If exit code 1 (FAIL):**

1. Review error output (script provides detailed guidance)
2. Stop runner: `pkill -f paper_trading_runner` or Ctrl+C
3. Fix issues (see "STOP if FAIL" section below)
4. Restart from Step 1
5. **DO NOT proceed until pre-flight PASSES**

**Expected output (success):**

```
=========================================
=== PRE-FLIGHT: PASS ✓ ===============
=========================================

Status: Runner is healthy and ready for 24h dry-run.

Next steps:
  1. Monitor logs: tail -f logs/paper_trading/runner_$(date -u +%Y%m%d).log
  2. Wait for first candle close (top of next hour)
  3. Run acceptance checks after 24h:
     ./scripts/dry_run_acceptance.sh
```

---

### Step 3: Capture Startup Snapshot

**Immediately after pre-flight PASS**, capture startup snapshot as proof:

```bash
./scripts/capture_phase3_snapshot.sh
```

**Expected output:**

```
Phase 3 snapshot captured successfully.

File: logs/paper_trading/snapshots/snapshot_20260204_HHMMSSZ.txt
Size: 8.0K
Time: 2026-02-04 HH:MM:SS UTC
```

**Record snapshot filename** in your Phase 3 log:

- Example: `snapshot_20260204_120000Z.txt` = Day 0 startup proof
- This snapshot documents healthy startup state

---

### Step 4: Verify Stability (Next Hour)

**Monitor for first candle close** (top of next hour, e.g., 13:00 UTC):

```bash
tail -f logs/paper_trading/runner_$(date -u +%Y%m%d).log
```

**Expected log entry (at top of hour):**

```
NEW CANDLE CLOSE: ts=1707134400000, close=50123.45, source=previous
EVALUATION: action=NONE, signal=0, confidence=0.450
Action=NONE. No order.
```

**Verify:**

- [ ] Candle detected at top of hour (00:00, 01:00, etc.)
- [ ] `source=previous` or `source=latest` present
- [ ] Evaluation runs (action logged)
- [ ] No "ORDER SUBMITTED" (dry-run mode)
- [ ] No FATAL errors

**If stable:** Runner is ready for 24h dry-run. Proceed to Daily Operations.

---

## Daily Operations (Day 1-42)

**Frequency:** Once per day (recommend same time each day, e.g., 12:00 UTC)

### Daily Snapshot

```bash
./scripts/capture_phase3_snapshot.sh
```

**Purpose:** Capture runtime state for audit trail.

### Daily Summary

Fill in `docs/paper_trading/daily_runtime_snapshot_template.md` copy:

```bash
# Create daily summary file
cp docs/paper_trading/daily_runtime_snapshot_template.md \
   docs/paper_trading/daily_summaries/daily_summary_$(date -u +%Y-%m-%d).md

# Edit with actual values from snapshot
```

**Key fields to update:**

1. Date and snapshot time
2. API server PID (from snapshot)
3. Runner PID (from snapshot)
4. Pre-flight test results (if re-run)
5. Latest 3 candle closes (from runner log)
6. State file values (from snapshot)
7. Any errors or deviations

### Log Monitoring

**Quick checks:**

```bash
# Check for FATAL errors
grep "FATAL" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Check candle count (should be ~24 per day for 1h timeframe)
grep -c "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Check for baseline fallback (should be 0)
grep -c "Baseline fallback detected" logs/paper_trading/runner_$(date -u +%Y%m%d).log
```

**If any issues:** See "STOP if FAIL" section.

---

## Day 1: 24h Dry-Run Acceptance

**After 24 hours of stable dry-run** (Day 0 12:00 UTC → Day 1 12:00 UTC):

### Step 1: Run Acceptance Script

```bash
./scripts/dry_run_acceptance.sh
```

**Required result:** Exit code **0** (all 10 checks PASS).

**Expected output (success):**

```
=========================================
=== DRY-RUN ACCEPTANCE: PASS ✓ =========
=========================================

Summary:
  Candles processed: 24
  Evaluations: 24
  Orders submitted: 0 (dry-run mode)
  Champion: Verified
  Fatal errors: 0
  Heartbeats: 144

Status: ✓ READY FOR SINGLE-CANDLE LIVE TEST
```

**If exit code 1 (FAIL):**

- Review error output
- Fix issues (see "STOP if FAIL" section)
- May need to restart 24h dry-run
- **DO NOT proceed to live-paper until acceptance PASSES**

---

### Step 2: Capture Acceptance Snapshot

```bash
./scripts/capture_phase3_snapshot.sh
```

**Record snapshot filename** as Day 1 acceptance proof:

- Example: `snapshot_20260205_120000Z.txt` = 24h acceptance proof

---

### Step 3: Decision Point

**If acceptance PASSED:**

1. **Stop dry-run runner:**

   ```bash
   pkill -f paper_trading_runner
   # OR use Ctrl+C if running in foreground
   ```

2. **Start live-paper runner:**

   ```bash
   TZ=UTC python scripts/paper_trading_runner.py --live-paper
   ```

   **Operational risk note (Bitfinex spot vs positions):**

- Paper trading here is spot-style for TEST symbols. Spot execution primarily shows up as **wallet balance changes**.
- The `/account/positions` endpoint can legitimately be empty even when spot orders are being submitted/filled.
- To verify execution in live-paper:
  - Check runner logs for `ORDER SUBMITTED` and any follow-up status.
  - Check `/account/orders` for open orders.
  - Check `/account/wallets` and verify a **wallet delta** vs. the previous snapshot (exchange wallet).
    This is often the most reliable “did something actually happen?” signal for spot-style flow.

3. **Run pre-flight again** (after 2-3 min):

   ```bash
   ./scripts/preflight_smoke_test.sh
   ```

4. **Capture live-paper startup snapshot:**

   ```bash
   ./scripts/capture_phase3_snapshot.sh
   ```

5. **Continue daily operations** for remaining 41 days

**If acceptance FAILED:**

- Document failure in daily summary
- Fix issues (may require code changes outside freeze scope)
- Restart from Day 0 after fixes
- **DO NOT proceed to live-paper**

---

## STOP if FAIL: Immediate Abort Conditions

**Stop runner IMMEDIATELY if ANY of these detected:**

### 1. Duplicate Candle Timestamp

**Check:**

```bash
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_*.log \
  | grep -oP 'ts=\K[0-9]+' \
  | sort \
  | uniq -c \
  | grep -v '^\s*1 '
```

**If output (duplicate found):**

- STOP runner immediately
- Document as CRITICAL BUG
- DO NOT restart until investigated

**Root cause:** Determinism failure in candle selection logic.

---

### 2. Order Submitted in Dry-Run Mode

**Check:**

```bash
grep "ORDER SUBMITTED" logs/paper_trading/runner_*.log
```

**If output (any matches):**

- EMERGENCY STOP runner immediately
- DO NOT proceed to live-paper
- Document as CRITICAL SAFETY VIOLATION

**Root cause:** Dry-run gate failure (Bug #2).

---

### 3. Champion Baseline Fallback

**Check:**

```bash
grep "Baseline fallback detected" logs/paper_trading/runner_*.log
```

**If output (any matches):**

- STOP runner immediately
- Verify champion file: `cat config/strategy/champions/tBTCUSD_1h.json`
- Check for `merged_config` key
- Restart API server: `uvicorn core.server:app --reload --app-dir src`
- Restart runner from Step 1

**Root cause:** Champion file missing, corrupt, or wrong structure.

---

### 4. Missing Hours (>2h Gap in Candles)

**Check:**

```bash
# Review candle timestamps (should be ~1h apart for 1h timeframe)
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_*.log \
  | grep -oP 'ts=\K[0-9]+' \
  | tail -10
```

**If gap >2 hours detected:**

- Review logs for errors during gap period
- Check if runner crashed (no heartbeat logs)
- Check system time/timezone consistency
- Investigate root cause before restarting

**Root cause:** Runner crash, network outage, or system issue.

---

### 5. State File Corruption

**Check:**

```bash
python -c "import json; json.load(open('logs/paper_trading/runner_state.json'))"
```

**If error (JSON parse failure):**

- **DO NOT delete state file**
- Backup corrupt file: `cp logs/paper_trading/runner_state.json logs/paper_trading/runner_state_corrupt_$(date -u +%Y%m%d_%H%M%S).json`
- Document as CRITICAL BUG
- Investigate root cause (atomic write failure)

**Root cause:** Disk full, write interrupted, or file system issue.

---

### 6. FATAL Errors in Log

**Check:**

```bash
grep "FATAL" logs/paper_trading/runner_$(date -u +%Y%m%d).log
```

**If any FATAL errors:**

- STOP runner immediately
- Review error context (surrounding log lines)
- Document error details
- Fix root cause before restarting

**Common causes:**

- Corrupt state file
- Order submission failure (live-paper mode)
- Champion verification failure

---

## Troubleshooting

### Runner Not Writing to Log File

**Symptoms:**

- Pre-flight fails: "Log file not found"
- OR log file exists but stale (mtime >120s)

**Diagnosis:**

```bash
# Check if runner is actually running
ps aux | grep paper_trading_runner

# Check which log file runner would create
date -u +%Y%m%d
# Should match: logs/paper_trading/runner_YYYYMMDD.log

# List all runner logs
ls -lht logs/paper_trading/runner_*.log | head -5
```

**Fix:**

1. Verify runner started with `TZ=UTC`
2. Check runner is not writing to different date (timezone mismatch)
3. Restart runner: `TZ=UTC python scripts/paper_trading_runner.py --dry-run`

---

### API Server Not Responding

**Symptoms:**

- Pre-flight fails: "API server not responding on http://localhost:8000/health"
- Snapshot shows: "API not responding"

**Diagnosis:**

```bash
# Check port 8000
lsof -i :8000 -P -n  # macOS/Linux
netstat -an | grep :8000  # Windows/cross-platform

# Test health endpoint
curl -v http://localhost:8000/health
```

**Fix:**

1. Start API server: `uvicorn core.server:app --reload --app-dir src`
2. Verify champion file exists
3. Check logs for startup errors

---

### Champion Not Loading

**Symptoms:**

- Pre-flight fails: "Champion verified successfully" not found
- Logs show: "Baseline fallback detected"

**Diagnosis:**

```bash
# Verify champion file exists
ls -lh config/strategy/champions/tBTCUSD_1h.json

# Verify structure (must have merged_config)
python -c "import json; c=json.load(open('config/strategy/champions/tBTCUSD_1h.json')); print('merged_config' in c)"
# Expected: True
```

**Fix:**

1. Verify champion file is not corrupted
2. Restart API server to reload champion
3. Restart runner

---

### No Candles Detected After 1 Hour

**Symptoms:**

- No "NEW CANDLE CLOSE" logs after 1 hour
- Heartbeat logs present (runner is polling)

**Diagnosis:**

```bash
# Check latest log entries
tail -50 logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Check for fetch errors
grep -E "HTTP error|Error fetching" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Test Bitfinex API directly
curl "https://api-pub.bitfinex.com/v2/candles/trade:1h:tBTCUSD/hist?limit=2&sort=-1"
```

**Fix:**

1. Verify network connectivity to Bitfinex API
2. Check for rate limiting or API errors
3. Restart runner if transient network issue

---

## Quick Reference Commands

```bash
# Start runner (dry-run)
TZ=UTC python scripts/paper_trading_runner.py --dry-run

# Start runner (live-paper, after 24h acceptance)
TZ=UTC python scripts/paper_trading_runner.py --live-paper

# Pre-flight test (5 min)
./scripts/preflight_smoke_test.sh

# Dry-run acceptance (24h)
./scripts/dry_run_acceptance.sh

# Daily snapshot
./scripts/capture_phase3_snapshot.sh

# Monitor runner log (live)
tail -f logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Check for errors
grep "FATAL\|ERROR" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Check candle count (today)
grep -c "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Verify state file
cat logs/paper_trading/runner_state.json

# Stop runner
pkill -f paper_trading_runner
# OR Ctrl+C if foreground

# API health check
curl http://localhost:8000/health

# Port 8000 process
lsof -i :8000 -P -n  # macOS/Linux
netstat -an | grep :8000  # Windows
```

---

## Phase 3 Timeline

**Day 0 (2026-02-04):**

- Start dry-run
- Pre-flight test PASS
- Capture startup snapshot
- Monitor first candle

**Day 1 (2026-02-05):**

- Run 24h acceptance test
- Capture acceptance snapshot
- Transition to live-paper (if PASS)
- Daily snapshot + summary

**Day 2-42 (2026-02-06 to 2026-03-17):**

- Daily snapshot
- Daily summary
- Monitor for stop conditions
- No champion changes (freeze)

**Day 42 (2026-03-17):**

- Final snapshot
- Phase 3 completion report
- Champion promotion decision (if metrics acceptable)

---

## Support and Escalation

**For issues during Phase 3:**

1. **Check this runbook** (troubleshooting section)
2. **Review acceptance checklist** (`docs/paper_trading/dry_run_acceptance_checklist.md`)
3. **Check deployment guide** (`docs/paper_trading/runner_deployment.md`)
4. **Document issue** in daily summary
5. **Capture snapshot** for evidence
6. **Escalate** if CRITICAL BUG (duplicate candles, orders in dry-run, etc.)

**CRITICAL BUG escalation requires:**

- Snapshot file showing issue
- Relevant log excerpts
- State file backup (if corrupted)
- Steps to reproduce

---

## Notes

- All times in UTC (use `date -u` consistently)
- Snapshots stored in `logs/paper_trading/snapshots/` (gitignored)
- Daily summaries in `docs/paper_trading/daily_summaries/` (can be committed)
- Champion file is FROZEN during Phase 3 (no edits)
- Runner uses 10s poll interval (adjustable if needed)
- 1h timeframe = expect ~24 candles per 24h

---

**Document Version:** 1.0
**Last Updated:** 2026-02-04
**Reviewed By:** Phase 3 Ops Team
