# Daily Runtime Snapshot - Phase 3 Paper Trading

**Date:** YYYY-MM-DD (UTC)
**Day:** N/42 (2026-02-04 to 2026-03-17)
**Snapshot Time:** HH:MM UTC

---

## 1. API Server Status

**Port 8000 Verification:**
```bash
# Command: lsof -i :8000 -P -n (or ss -tlnp | grep :8000)
PID: <pid>
Command: <command_name>
Process: <full_command_line>
Status: [ ] Running ✓ / [ ] Not Running ✗
```

**Health Check:**
```bash
# Command: curl -s http://localhost:8000/health
Status: <ok/error>
Config Version: <version>
Response Time: <ms>
```

---

## 2. Runner Status

**Process Verification:**
```bash
# Command: ps aux | grep paper_trading_runner
PID: <pid>
Started: <timestamp>
Command: <full_command_line>
Status: [ ] Running ✓ / [ ] Not Running ✗
```

**Mode:**
- [ ] Dry-run
- [ ] Live-paper

**Timezone:** TZ=<timezone> (expected: UTC)

---

## 3. Pre-flight Smoke Test Results

**Command:** `./scripts/preflight_smoke_test.sh`

**Exit Code:** <0 or 1>

**Check Results:**

| Check | Status | Details |
|-------|--------|---------|
| [1/5] API server health | [ ] ✓ PASS / [ ] ✗ FAIL | <details> |
| [2/5] Log file freshness | [ ] ✓ PASS / [ ] ✗ FAIL | mtime: <seconds>s ago |
| [2/5] Log file activity | [ ] ✓ PASS / [ ] ⚠ WARN | <line_count> lines |
| [3/5] Champion verification | [ ] ✓ PASS / [ ] ✗ FAIL | <details> |
| [4/5] State file heartbeat | [ ] ✓ PASS / [ ] ✗ FAIL | <heartbeat_timestamp> |
| [5/5] No fatal errors | [ ] ✓ PASS / [ ] ✗ FAIL | FATAL count: <count> |

**Overall:** [ ] PASS ✓ / [ ] FAIL ✗

---

## 4. Recent Candle Activity

**Latest 3 Candle Closes:**

```bash
# Command: grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date -u +%Y%m%d).log | tail -3
```

```
1. ts=<timestamp>, close=<price>, source=<latest/previous>
2. ts=<timestamp>, close=<price>, source=<latest/previous>
3. ts=<timestamp>, close=<price>, source=<latest/previous>
```

**Candle Frequency Check:**
- Time between candles: <minutes> min (expected: 60 min for 1h timeframe)
- Gap detected: [ ] No / [ ] Yes (details: <gap_duration>)

**Source Distribution (last 10 candles):**
```bash
# Command: grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date -u +%Y%m%d).log | tail -10 | grep -c "source=previous"
```
- source=previous: <count>/10 (expected: >8 for 10s poll interval)
- source=latest: <count>/10

---

## 5. State File Status

**File:** `logs/paper_trading/runner_state.json`

```bash
# Command: cat logs/paper_trading/runner_state.json
```

**Key Values:**

| Field | Value | Expected/Notes |
|-------|-------|----------------|
| last_processed_candle_ts | <timestamp_ms> | Should be recent (within last hour) |
| total_evaluations | <count> | Should match total candles processed |
| total_orders_submitted | <count> | Should be 0 for dry-run, >0 for live-paper |
| last_heartbeat | <iso_timestamp> | Should be recent (within last 2 min) |

**State Consistency Check:**
```bash
# Latest candle from logs matches state file?
Latest log candle ts: <timestamp>
State last_processed: <timestamp>
Match: [ ] Yes ✓ / [ ] No ✗
```

---

## 6. Errors and Deviations

**FATAL Errors:**
```bash
# Command: grep "FATAL" logs/paper_trading/runner_$(date -u +%Y%m%d).log
```

**Count:** <count> (expected: 0)

**Details:**
```
<paste FATAL error lines if any>
```

**Baseline Fallback Check:**
```bash
# Command: grep "Baseline fallback detected" logs/paper_trading/runner_$(date -u +%Y%m%d).log
```

**Count:** <count> (expected: 0)

**Other Deviations:**

- [ ] No deviations ✓
- [ ] Deviation detected:
  - **Type:** <error_type>
  - **Description:** <details>
  - **Impact:** <impact_assessment>
  - **Action Taken:** <action_description>
  - **Status:** [ ] Resolved / [ ] Ongoing / [ ] Escalated

---

## 7. Action Items / Follow-up

**Today's Actions:**

- [ ] <action_item_1>
- [ ] <action_item_2>

**Pending from Previous Days:**

- [ ] <pending_item_1>
- [ ] <pending_item_2>

**Next Snapshot:**

- **Scheduled:** <YYYY-MM-DD HH:MM UTC>
- **Special checks:** <any_additional_checks>

---

## Stop Conditions Reference

**Immediate abort if ANY detected:**

1. **Duplicate candle timestamp**
   - Check: `grep "NEW CANDLE CLOSE" logs/paper_trading/runner_*.log | grep -oP 'ts=\K[0-9]+' | sort | uniq -c | grep -v '^\s*1 '`
   - Action: Stop runner, document, report as CRITICAL BUG

2. **Order submitted in dry-run mode**
   - Check: `grep "ORDER SUBMITTED" logs/paper_trading/runner_*.log`
   - Action: Emergency stop, DO NOT proceed to live-paper

3. **Champion baseline fallback**
   - Check: `grep "Baseline fallback detected" logs/paper_trading/runner_*.log`
   - Action: Stop runner, verify champion file, restart API server

4. **Missing hours (>2h gap in candles)**
   - Check: Verify candle timestamps are ~1h apart
   - Action: Check for errors in gap period, investigate crash

5. **State file corruption**
   - Check: `python -c "import json; json.load(open('logs/paper_trading/runner_state.json'))"`
   - Action: Backup corrupt file, DO NOT delete, report CRITICAL BUG

**Full details:** `docs/paper_trading/dry_run_acceptance_checklist.md` - Stop Conditions section

---

## Notes

**Observations:**

<Add any observations about runner behavior, performance, decision patterns, etc.>

**Context:**

<Add any relevant context: champion version, config changes (if any), external events, etc.>

---

## Snapshot Signature

**Completed by:** <name/system>
**Verified:** [ ] Yes / [ ] No
**Next review:** <YYYY-MM-DD HH:MM UTC>

---

## Appendix: Quick Commands Reference

```bash
# API server PID
lsof -i :8000 -P -n

# Runner PID
ps aux | grep paper_trading_runner

# Pre-flight test
./scripts/preflight_smoke_test.sh

# Latest candles
grep "NEW CANDLE CLOSE" logs/paper_trading/runner_$(date -u +%Y%m%d).log | tail -3

# State file
cat logs/paper_trading/runner_state.json

# FATAL check
grep "FATAL" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Baseline fallback check
grep "Baseline fallback detected" logs/paper_trading/runner_$(date -u +%Y%m%d).log

# Log file freshness
stat -c %Y logs/paper_trading/runner_$(date -u +%Y%m%d).log  # Linux
stat -f %m logs/paper_trading/runner_$(date -u +%Y%m%d).log  # macOS

# Current time (UTC)
date -u +'%Y-%m-%d %H:%M:%S UTC'
```
