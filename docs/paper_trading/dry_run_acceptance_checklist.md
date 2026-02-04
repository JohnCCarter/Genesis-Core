# Phase 3 Dry-Run Acceptance Checklist

**Purpose:** Verify paper_trading_runner correctness before live-paper trading.

**Duration:** 24 hours minimum (recommended: 48 hours for full validation)

**Mode:** `--dry-run` (no orders submitted)

---

## Pre-Flight

**Start dry-run:**

```bash
# Ensure API server is running
curl -s http://localhost:8000/health | grep '"status":"ok"'

# Start runner in dry-run mode
python scripts/paper_trading_runner.py --dry-run --symbol tBTCUSD --timeframe 1h --poll-interval 10
```

**Expected startup output:**

```
Paper Trading Runner Started
Symbol: tBTCUSD, Timeframe: 1h
Mode: DRY-RUN (no orders)
Verifying champion loading...
Champion verified successfully.
```

**Verify log file created:**

```bash
ls -lh logs/paper_trading/runner_$(date +%Y%m%d).log
```

---

## Acceptance Criteria (After 24 Hours)

### 1. Candle-Close Uniqueness (No Duplicates)

**Verify: Each candle timestamp appears EXACTLY ONCE in "NEW CANDLE CLOSE" logs.**

**Command:**

```bash
# Extract all candle close timestamps
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -oP 'ts=\K[0-9]+' \
  | sort \
  | uniq -c

# Expected: All counts = 1 (no duplicates)
# Example output:
#   1 1704067200000
#   1 1704070800000
#   1 1704074400000
#   ...
```

**Pass Criteria:** All lines show count = 1

**Failure Example:**

```
  2 1704067200000  ← DUPLICATE! Stop test immediately.
  1 1704070800000
```

**Stop Condition:** If ANY timestamp has count > 1 → **ABORT DRY-RUN** and investigate idempotency failure.

---

### 2. Candle-Close Frequency (Exactly 1 Per Hour)

**Verify: Candles detected at 1-hour intervals (for 1h timeframe).**

**Command:**

```bash
# Count unique candle timestamps
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -oP 'ts=\K[0-9]+' \
  | sort -u \
  | wc -l

# Expected: ~24 candles per 24 hours (±1 for startup/shutdown timing)
```

**Pass Criteria:** Count within 23-25 for 24-hour run

**Verify hourly spacing:**

```bash
# Show candle timestamps (should be 3600000ms = 1h apart)
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -oP 'ts=\K[0-9]+' \
  | sort -u

# Manually verify: each ts = previous_ts + 3600000
```

**Stop Condition:** If gap > 2 hours (7200000ms) → **CHECK LOGS** for errors or runner downtime.

---

### 3. Candle Source Logging (Audit Trail)

**Verify: Every "NEW CANDLE CLOSE" includes source metadata.**

**Command:**

```bash
# Count "NEW CANDLE CLOSE" lines with source field
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -c "source="

# Count total "NEW CANDLE CLOSE" lines
grep -c "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log

# Both counts should be equal
```

**Pass Criteria:** Counts match (every candle close has source)

**Verify audit debug logging:**

```bash
# Check for "Candle selection" debug logs
grep "Candle selection:" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | head -3

# Expected format:
# Candle selection: source=previous, ts=1704067200000, now_ms=..., latest_ts=..., latest_close_ms=...
```

**Pass Criteria:** Debug logs present with all fields (source, ts, now_ms, latest_ts, latest_close_ms)

**Stop Condition:** If source field missing → **BUG** in candle selection logging.

---

### 4. Source Distribution (Latest vs Previous)

**Verify: Reasonable mix of "source=latest" and "source=previous".**

**Command:**

```bash
# Count latest vs previous
echo "Latest candles:"
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -c "source=latest"

echo "Previous candles:"
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -c "source=previous"
```

**Expected:** Majority should be "source=previous" (since runner polls at 10s intervals, usually catching candles before they close).

**Pass Criteria:** At least 80% "source=previous" (for 10s poll interval on 1h candles)

**Stop Condition:** If 100% "source=latest" → **CHECK** poll-interval too long or timing issue.

---

### 5. No Order Submission in Dry-Run

**Verify: ZERO "Submitting" or "ORDER SUBMITTED" logs (dry-run mode).**

**Command:**

```bash
# Check for order submission attempts
grep -E "Submitting (BUY|SELL) order" logs/paper_trading/runner_$(date +%Y%m%d).log

# Should return: (no output - grep exits with code 1)

# Check for actual submissions
grep "ORDER SUBMITTED" logs/paper_trading/runner_$(date +%Y%m%d).log

# Should return: (no output)
```

**Pass Criteria:** Both greps return EMPTY (no matches)

**Check for DRY-RUN logs instead:**

```bash
# Should see DRY-RUN messages for non-NONE actions
grep "DRY-RUN: Would submit" logs/paper_trading/runner_$(date +%Y%m%d).log

# Example output:
# DRY-RUN: Would submit BUY order (skipped)
# DRY-RUN: Would submit SELL order (skipped)
```

**Stop Condition:** If ANY "ORDER SUBMITTED" found → **CRITICAL FAILURE** - dry-run leaked orders! ABORT IMMEDIATELY.

---

### 6. Evaluation Count Matches Candle Count

**Verify: Exactly 1 evaluation per candle.**

**Command:**

```bash
# Count candles
CANDLE_COUNT=$(grep -c "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log)
echo "Candles detected: $CANDLE_COUNT"

# Count evaluations
EVAL_COUNT=$(grep -c "EVALUATION: action=" logs/paper_trading/runner_$(date +%Y%m%d).log)
echo "Evaluations run: $EVAL_COUNT"

# Should be equal
if [ "$CANDLE_COUNT" -eq "$EVAL_COUNT" ]; then
  echo "PASS: 1 evaluation per candle"
else
  echo "FAIL: Mismatch - candles=$CANDLE_COUNT, evals=$EVAL_COUNT"
fi
```

**Pass Criteria:** Counts equal

**Stop Condition:** If mismatch → **CHECK LOGS** for evaluation errors or skipped candles.

---

### 7. State File Consistency

**Verify: runner_state.json matches latest processed candle.**

**Command:**

```bash
# Get latest candle timestamp from logs
LATEST_CANDLE=$(grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -oP 'ts=\K[0-9]+' \
  | tail -1)
echo "Latest candle from logs: $LATEST_CANDLE"

# Get last_processed_candle_ts from state file
STATE_TS=$(python -c "import json; print(json.load(open('logs/paper_trading/runner_state.json'))['last_processed_candle_ts'])")
echo "State file last_processed_candle_ts: $STATE_TS"

# Should match
if [ "$LATEST_CANDLE" == "$STATE_TS" ]; then
  echo "PASS: State file consistent with logs"
else
  echo "FAIL: State mismatch - logs=$LATEST_CANDLE, state=$STATE_TS"
fi
```

**Pass Criteria:** Timestamps match

**Verify state file structure:**

```bash
# Pretty-print state file
python -c "import json; print(json.dumps(json.load(open('logs/paper_trading/runner_state.json')), indent=2))"

# Expected fields:
# {
#   "last_processed_candle_ts": 1704067200000,
#   "total_evaluations": 24,
#   "total_orders_submitted": 0,  ← Should be 0 in dry-run
#   "last_heartbeat": "2026-02-04T12:00:00+00:00"
# }
```

**Pass Criteria:**
- `last_processed_candle_ts` is recent (within last hour)
- `total_evaluations` matches candle count
- `total_orders_submitted` == 0 (dry-run mode)

**Stop Condition:** If `total_orders_submitted` > 0 → **CRITICAL FAILURE** - orders leaked in dry-run mode!

---

### 8. No Champion Fallback Errors

**Verify: Champion loaded correctly (no baseline fallback).**

**Command:**

```bash
# Check for champion verification success
grep "Champion verified successfully" logs/paper_trading/runner_$(date +%Y%m%d).log | wc -l

# Should be >= 1 (startup verification)

# Check for baseline fallback errors
grep "Baseline fallback detected" logs/paper_trading/runner_$(date +%Y%m%d).log

# Should return: (no output)
```

**Pass Criteria:** Champion verified, no fallback errors

**Stop Condition:** If "Baseline fallback detected" found → **ABORT** - champion not loading correctly.

---

### 9. No Unexpected Errors

**Verify: No FATAL, ERROR, or exception logs.**

**Command:**

```bash
# Check for FATAL errors
grep "FATAL" logs/paper_trading/runner_$(date +%Y%m%d).log

# Should return: (no output in dry-run)

# Check for ERROR logs
grep "ERROR" logs/paper_trading/runner_$(date +%Y%m%d).log | head -10

# Expected: Only transient errors like "Failed to fetch candle" are OK if rare

# Check for exceptions
grep -i "exception\|traceback" logs/paper_trading/runner_$(date +%Y%m%d).log

# Should return: (no output)
```

**Pass Criteria:** No FATAL, no exceptions, minimal transient errors (<5% of polls)

**Stop Condition:** If FATAL or exception found → **INVESTIGATE** before continuing.

---

### 10. Heartbeat Frequency

**Verify: Heartbeat logged every 10 polls.**

**Command:**

```bash
# Count heartbeats
HEARTBEAT_COUNT=$(grep "Heartbeat: evaluations=" logs/paper_trading/runner_$(date +%Y%m%d).log | wc -l)
echo "Heartbeats logged: $HEARTBEAT_COUNT"

# For 24h with 10s poll interval: ~8640 polls = ~864 heartbeats (every 10 polls)
# Actual will be lower due to candle processing time
```

**Pass Criteria:** Heartbeats present (at least a few dozen for 24h run)

**Check heartbeat content:**

```bash
# Show last 3 heartbeats
grep "Heartbeat: evaluations=" logs/paper_trading/runner_$(date +%Y%m%d).log | tail -3

# Expected format:
# Heartbeat: evaluations=24, orders=0, last_candle_ts=1704067200000
```

**Pass Criteria:** Heartbeat shows `orders=0` (dry-run mode)

---

## Stop Conditions (Immediate Abort)

**ABORT DRY-RUN IMMEDIATELY if ANY of these detected:**

### 1. Duplicate Candle Timestamp

**Symptom:**

```bash
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -oP 'ts=\K[0-9]+' \
  | sort \
  | uniq -c \
  | grep -v '^\s*1 '
```

**If output is non-empty:** Duplicate detected → **STOP RUNNER**

**Action:**
1. Stop runner (Ctrl+C or `pkill -f paper_trading_runner`)
2. Document timestamp of duplicate
3. Check state file: `cat logs/paper_trading/runner_state.json`
4. Report as **CRITICAL BUG** - idempotency failure

---

### 2. Order Submitted in Dry-Run Mode

**Symptom:**

```bash
grep "ORDER SUBMITTED" logs/paper_trading/runner_$(date +%Y%m%d).log
```

**If ANY output:** Order leaked → **STOP RUNNER IMMEDIATELY**

**Action:**
1. Emergency stop: `pkill -f paper_trading_runner`
2. Check state file: `total_orders_submitted` value
3. Report as **CRITICAL BUG** - dry-run safety failure
4. DO NOT PROCEED to live-paper mode

---

### 3. Champion Baseline Fallback

**Symptom:**

```bash
grep "Baseline fallback detected" logs/paper_trading/runner_$(date +%Y%m%d).log
```

**If ANY output:** Champion not loading → **STOP RUNNER**

**Action:**
1. Stop runner
2. Verify champion file exists: `ls -lh config/strategy/champions/tBTCUSD_1h.json`
3. Check champion structure: `python -c "import json; c=json.load(open('config/strategy/champions/tBTCUSD_1h.json')); print('merged_config' in c)"`
4. Restart API server and retry
5. If persists: Report as **BLOCKER**

---

### 4. Missing Hours (Gap in Candle Detection)

**Symptom:**

```bash
# Extract candle timestamps and check for gaps > 2 hours
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log \
  | grep -oP 'ts=\K[0-9]+' \
  | sort -u \
  | awk 'NR>1 {gap=($1-prev)/3600000; if(gap>2) print "GAP:",gap,"hours between",prev,"and",$1} {prev=$1}'
```

**If gaps > 2 hours detected:** Runner downtime or errors

**Action:**
1. Check for errors in gap period: `grep ERROR logs/paper_trading/runner_$(date +%Y%m%d).log`
2. Check for runner crashes: `grep "Runner stopped" logs/paper_trading/runner_$(date +%Y%m%d).log`
3. If unexplained: Document and investigate before proceeding

---

### 5. State File Corruption

**Symptom:**

```bash
python -c "import json; json.load(open('logs/paper_trading/runner_state.json'))"
# If this fails with JSONDecodeError → corruption
```

**Action:**
1. Stop runner immediately
2. Backup corrupt file: `cp logs/paper_trading/runner_state.json logs/paper_trading/runner_state.json.corrupt`
3. Report as **CRITICAL BUG** - atomic write failure
4. DO NOT delete state file (forensic evidence)

---

## Full Acceptance Script

**Run after 24 hours:**

```bash
#!/bin/bash
# dry_run_acceptance.sh - Automated acceptance check

set -e

LOG_FILE="logs/paper_trading/runner_$(date +%Y%m%d).log"
STATE_FILE="logs/paper_trading/runner_state.json"

echo "=== Phase 3 Dry-Run Acceptance Check ==="
echo "Log file: $LOG_FILE"
echo ""

# 1. Candle uniqueness
echo "[1/10] Checking candle uniqueness..."
DUPLICATES=$(grep "NEW CANDLE CLOSE" "$LOG_FILE" | grep -oP 'ts=\K[0-9]+' | sort | uniq -c | grep -v '^\s*1 ' | wc -l)
if [ "$DUPLICATES" -eq 0 ]; then
  echo "  PASS: No duplicate candles"
else
  echo "  FAIL: $DUPLICATES duplicate timestamps found"
  exit 1
fi

# 2. Candle count
echo "[2/10] Checking candle count..."
CANDLE_COUNT=$(grep -c "NEW CANDLE CLOSE" "$LOG_FILE")
echo "  Candles detected: $CANDLE_COUNT (expected ~24 per 24h)"
if [ "$CANDLE_COUNT" -lt 20 ]; then
  echo "  WARNING: Low candle count"
fi

# 3. Source logging
echo "[3/10] Checking source logging..."
CANDLE_COUNT=$(grep -c "NEW CANDLE CLOSE" "$LOG_FILE")
SOURCE_COUNT=$(grep "NEW CANDLE CLOSE" "$LOG_FILE" | grep -c "source=")
if [ "$CANDLE_COUNT" -eq "$SOURCE_COUNT" ]; then
  echo "  PASS: All candles have source metadata"
else
  echo "  FAIL: Missing source in $((CANDLE_COUNT - SOURCE_COUNT)) candles"
  exit 1
fi

# 4. No order submission
echo "[4/10] Checking no orders submitted..."
ORDER_COUNT=$(grep -c "ORDER SUBMITTED" "$LOG_FILE" || true)
if [ "$ORDER_COUNT" -eq 0 ]; then
  echo "  PASS: No orders submitted (dry-run mode)"
else
  echo "  FAIL: $ORDER_COUNT orders submitted in dry-run mode!"
  exit 1
fi

# 5. Evaluation count
echo "[5/10] Checking evaluation count..."
EVAL_COUNT=$(grep -c "EVALUATION: action=" "$LOG_FILE")
if [ "$CANDLE_COUNT" -eq "$EVAL_COUNT" ]; then
  echo "  PASS: 1 evaluation per candle ($EVAL_COUNT evals)"
else
  echo "  FAIL: Candles=$CANDLE_COUNT, Evaluations=$EVAL_COUNT"
  exit 1
fi

# 6. State file consistency
echo "[6/10] Checking state file consistency..."
LATEST_CANDLE=$(grep "NEW CANDLE CLOSE" "$LOG_FILE" | grep -oP 'ts=\K[0-9]+' | tail -1)
STATE_TS=$(python -c "import json; print(json.load(open('$STATE_FILE'))['last_processed_candle_ts'])")
if [ "$LATEST_CANDLE" == "$STATE_TS" ]; then
  echo "  PASS: State matches logs (ts=$STATE_TS)"
else
  echo "  FAIL: State mismatch - logs=$LATEST_CANDLE, state=$STATE_TS"
  exit 1
fi

# 7. State orders counter
echo "[7/10] Checking state orders counter..."
STATE_ORDERS=$(python -c "import json; print(json.load(open('$STATE_FILE'))['total_orders_submitted'])")
if [ "$STATE_ORDERS" -eq 0 ]; then
  echo "  PASS: State shows 0 orders (dry-run mode)"
else
  echo "  FAIL: State shows $STATE_ORDERS orders submitted!"
  exit 1
fi

# 8. Champion verification
echo "[8/10] Checking champion loading..."
CHAMPION_OK=$(grep -c "Champion verified successfully" "$LOG_FILE")
BASELINE_FAIL=$(grep -c "Baseline fallback detected" "$LOG_FILE" || true)
if [ "$CHAMPION_OK" -ge 1 ] && [ "$BASELINE_FAIL" -eq 0 ]; then
  echo "  PASS: Champion loaded correctly"
else
  echo "  FAIL: Champion not loading (baseline fallback detected)"
  exit 1
fi

# 9. No fatal errors
echo "[9/10] Checking for fatal errors..."
FATAL_COUNT=$(grep -c "FATAL" "$LOG_FILE" || true)
if [ "$FATAL_COUNT" -eq 0 ]; then
  echo "  PASS: No fatal errors"
else
  echo "  FAIL: $FATAL_COUNT fatal errors found"
  exit 1
fi

# 10. Heartbeat check
echo "[10/10] Checking heartbeat logging..."
HEARTBEAT_COUNT=$(grep -c "Heartbeat: evaluations=" "$LOG_FILE")
if [ "$HEARTBEAT_COUNT" -ge 1 ]; then
  echo "  PASS: Heartbeats present ($HEARTBEAT_COUNT heartbeats)"
else
  echo "  WARNING: No heartbeats found"
fi

echo ""
echo "=== DRY-RUN ACCEPTANCE: PASS ==="
echo ""
echo "Summary:"
echo "  Candles processed: $CANDLE_COUNT"
echo "  Evaluations: $EVAL_COUNT"
echo "  Orders submitted: 0 (dry-run mode)"
echo "  Champion: Verified"
echo "  Fatal errors: 0"
echo ""
echo "Status: READY FOR SINGLE-CANDLE LIVE TEST"
```

**Run:**

```bash
chmod +x scripts/dry_run_acceptance.sh
./scripts/dry_run_acceptance.sh
```

**Expected output:**

```
=== Phase 3 Dry-Run Acceptance Check ===
[1/10] Checking candle uniqueness...
  PASS: No duplicate candles
[2/10] Checking candle count...
  Candles detected: 24 (expected ~24 per 24h)
[3/10] Checking source logging...
  PASS: All candles have source metadata
[4/10] Checking no orders submitted...
  PASS: No orders submitted (dry-run mode)
[5/10] Checking evaluation count...
  PASS: 1 evaluation per candle (24 evals)
[6/10] Checking state file consistency...
  PASS: State matches logs (ts=1704067200000)
[7/10] Checking state orders counter...
  PASS: State shows 0 orders (dry-run mode)
[8/10] Checking champion loading...
  PASS: Champion loaded correctly
[9/10] Checking for fatal errors...
  PASS: No fatal errors
[10/10] Checking heartbeat logging...
  PASS: Heartbeats present (144 heartbeats)

=== DRY-RUN ACCEPTANCE: PASS ===

Summary:
  Candles processed: 24
  Evaluations: 24
  Orders submitted: 0 (dry-run mode)
  Champion: Verified
  Fatal errors: 0

Status: READY FOR SINGLE-CANDLE LIVE TEST
```

---

## Post-Acceptance Actions

**If ALL checks pass:**

1. Document dry-run results in daily summary
2. Proceed to single-candle live test (see `runner_deployment.md`)
3. After single-candle test OK → deploy persistent setup

**If ANY check fails:**

1. Stop runner immediately
2. Document failure in `docs/daily_summaries/daily_summary_$(date +%Y-%m-%d).md`
3. Create GitHub issue with:
   - Failed check description
   - Log excerpts
   - State file contents
   - Reproduction steps
4. DO NOT proceed to live-paper mode until fixed and re-tested

---

## Appendix: Manual Spot Checks

**Visual inspection of logs (random sampling):**

```bash
# Show first 50 lines
head -50 logs/paper_trading/runner_$(date +%Y%m%d).log

# Show random candle closes
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date +%Y%m%d).log | shuf -n 5

# Show random evaluations
grep "EVALUATION: action=" logs/paper_trading/runner_$(date +%Y%m%d).log | shuf -n 5

# Show DRY-RUN messages
grep "DRY-RUN:" logs/paper_trading/runner_$(date +%Y%m%d).log | head -10
```

**Verify candle data consistency (manual):**

```bash
# Pick a candle timestamp
TS=1704067200000

# Show all logs for that candle
grep "$TS" logs/paper_trading/runner_$(date +%Y%m%d).log

# Expected sequence:
# 1. "Candle selection: source=..., ts=1704067200000, ..."
# 2. "NEW CANDLE CLOSE: ts=1704067200000, close=50100.00, source=previous"
# 3. "EVALUATION: action=BUY, signal=1, confidence=0.750"
# 4. "DRY-RUN: Would submit BUY order (skipped)" (if action != NONE)
```

---

## Reference

- **Runner source:** `scripts/paper_trading_runner.py`
- **Deployment guide:** `docs/paper_trading/runner_deployment.md`
- **Operations summary:** `docs/paper_trading/operations_summary.md`
- **Bug fixes:** Commit bc89767 (Bug #1 + Bug #2)
