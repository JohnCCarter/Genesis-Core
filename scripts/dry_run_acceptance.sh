#!/bin/bash
# dry_run_acceptance.sh - Automated acceptance check for Phase 3 dry-run
#
# Usage: ./scripts/dry_run_acceptance.sh
#
# Verifies:
#   - Candle uniqueness (no duplicates)
#   - Candle frequency (~24 per 24h)
#   - Source metadata present
#   - No order submission in dry-run
#   - Evaluation count matches candle count
#   - State file consistency
#   - Champion loading
#   - No fatal errors
#   - Heartbeat logging
#
# IMPORTANT: Uses UTC date (date -u) to match runner log filenames

set -e

# Use UTC date to match runner log filenames
LOG_FILE="logs/paper_trading/runner_$(date -u +%Y%m%d).log"
STATE_FILE="logs/paper_trading/runner_state.json"

echo "=== Phase 3 Dry-Run Acceptance Check ==="
echo "Log file: $LOG_FILE"
echo "State file: $STATE_FILE"
echo ""

# Verify files exist
if [ ! -f "$LOG_FILE" ]; then
  echo "ERROR: Log file not found: $LOG_FILE"
  exit 1
fi

if [ ! -f "$STATE_FILE" ]; then
  echo "ERROR: State file not found: $STATE_FILE"
  exit 1
fi

# 1. Candle uniqueness
echo "[1/10] Checking candle uniqueness..."
DUPLICATES=$(grep "NEW CANDLE CLOSE" "$LOG_FILE" | grep -oP 'ts=\K[0-9]+' | sort | uniq -c | grep -v '^\s*1 ' | wc -l)
if [ "$DUPLICATES" -eq 0 ]; then
  echo "  ✓ PASS: No duplicate candles"
else
  echo "  ✗ FAIL: $DUPLICATES duplicate timestamps found"
  echo ""
  echo "Duplicate timestamps:"
  grep "NEW CANDLE CLOSE" "$LOG_FILE" | grep -oP 'ts=\K[0-9]+' | sort | uniq -c | grep -v '^\s*1 '
  exit 1
fi

# 2. Candle count
echo "[2/10] Checking candle count..."
CANDLE_COUNT=$(grep -c "NEW CANDLE CLOSE" "$LOG_FILE")
echo "  Candles detected: $CANDLE_COUNT (expected ~24 per 24h)"
if [ "$CANDLE_COUNT" -lt 20 ]; then
  echo "  ⚠ WARNING: Low candle count (expected ~24 for 24h run)"
fi

# 3. Source logging
echo "[3/10] Checking source logging..."
CANDLE_COUNT=$(grep -c "NEW CANDLE CLOSE" "$LOG_FILE")
SOURCE_COUNT=$(grep "NEW CANDLE CLOSE" "$LOG_FILE" | grep -c "source=")
if [ "$CANDLE_COUNT" -eq "$SOURCE_COUNT" ]; then
  echo "  ✓ PASS: All candles have source metadata"
else
  echo "  ✗ FAIL: Missing source in $((CANDLE_COUNT - SOURCE_COUNT)) candles"
  exit 1
fi

# 4. Audit logging
echo "[4/10] Checking audit logging..."
AUDIT_COUNT=$(grep -c "Candle selection:" "$LOG_FILE" || true)
if [ "$AUDIT_COUNT" -ge "$CANDLE_COUNT" ]; then
  echo "  ✓ PASS: Audit debug logs present ($AUDIT_COUNT entries)"
else
  echo "  ⚠ WARNING: Audit logs incomplete (expected >=$CANDLE_COUNT, got $AUDIT_COUNT)"
fi

# 5. No order submission
echo "[5/10] Checking no orders submitted..."
ORDER_COUNT=$(grep -c "ORDER SUBMITTED" "$LOG_FILE" || true)
SUBMIT_COUNT=$(grep -cE "Submitting (BUY|SELL) order" "$LOG_FILE" || true)
if [ "$ORDER_COUNT" -eq 0 ] && [ "$SUBMIT_COUNT" -eq 0 ]; then
  echo "  ✓ PASS: No orders submitted (dry-run mode)"
else
  echo "  ✗ FAIL: Orders submitted in dry-run mode!"
  echo "    ORDER SUBMITTED count: $ORDER_COUNT"
  echo "    Submitting order count: $SUBMIT_COUNT"
  exit 1
fi

# 6. Evaluation count
echo "[6/10] Checking evaluation count..."
EVAL_COUNT=$(grep -c "EVALUATION: action=" "$LOG_FILE")
if [ "$CANDLE_COUNT" -eq "$EVAL_COUNT" ]; then
  echo "  ✓ PASS: 1 evaluation per candle ($EVAL_COUNT evals)"
else
  echo "  ✗ FAIL: Candles=$CANDLE_COUNT, Evaluations=$EVAL_COUNT"
  exit 1
fi

# 7. State file consistency
echo "[7/10] Checking state file consistency..."
LATEST_CANDLE=$(grep "NEW CANDLE CLOSE" "$LOG_FILE" | grep -oP 'ts=\K[0-9]+' | tail -1)
STATE_TS=$(python -c "import json; print(json.load(open('$STATE_FILE'))['last_processed_candle_ts'])")
if [ "$LATEST_CANDLE" == "$STATE_TS" ]; then
  echo "  ✓ PASS: State matches logs (ts=$STATE_TS)"
else
  echo "  ✗ FAIL: State mismatch"
  echo "    Latest candle in logs: $LATEST_CANDLE"
  echo "    State file ts: $STATE_TS"
  exit 1
fi

# 8. State orders counter
echo "[8/10] Checking state orders counter..."
STATE_ORDERS=$(python -c "import json; print(json.load(open('$STATE_FILE'))['total_orders_submitted'])")
if [ "$STATE_ORDERS" -eq 0 ]; then
  echo "  ✓ PASS: State shows 0 orders (dry-run mode)"
else
  echo "  ✗ FAIL: State shows $STATE_ORDERS orders submitted in dry-run mode!"
  exit 1
fi

# 9. Champion verification
echo "[9/10] Checking champion loading..."
CHAMPION_OK=$(grep -c "Champion verified successfully" "$LOG_FILE")
BASELINE_FAIL=$(grep -c "Baseline fallback detected" "$LOG_FILE" || true)
if [ "$CHAMPION_OK" -ge 1 ] && [ "$BASELINE_FAIL" -eq 0 ]; then
  echo "  ✓ PASS: Champion loaded correctly"
else
  echo "  ✗ FAIL: Champion not loading"
  echo "    Champion verified: $CHAMPION_OK"
  echo "    Baseline fallback: $BASELINE_FAIL"
  exit 1
fi

# 10. No fatal errors
echo "[10/10] Checking for fatal errors..."
FATAL_COUNT=$(grep -c "FATAL" "$LOG_FILE" || true)
if [ "$FATAL_COUNT" -eq 0 ]; then
  echo "  ✓ PASS: No fatal errors"
else
  echo "  ✗ FAIL: $FATAL_COUNT fatal errors found"
  echo ""
  echo "Fatal errors:"
  grep "FATAL" "$LOG_FILE"
  exit 1
fi

# Bonus: Heartbeat check
echo ""
echo "[BONUS] Checking heartbeat logging..."
HEARTBEAT_COUNT=$(grep -c "Heartbeat: evaluations=" "$LOG_FILE")
if [ "$HEARTBEAT_COUNT" -ge 1 ]; then
  echo "  ✓ PASS: Heartbeats present ($HEARTBEAT_COUNT heartbeats)"
else
  echo "  ⚠ WARNING: No heartbeats found"
fi

# Summary
echo ""
echo "========================================="
echo "=== DRY-RUN ACCEPTANCE: PASS ✓ ========="
echo "========================================="
echo ""
echo "Summary:"
echo "  Candles processed: $CANDLE_COUNT"
echo "  Evaluations: $EVAL_COUNT"
echo "  Orders submitted: 0 (dry-run mode)"
echo "  Champion: Verified"
echo "  Fatal errors: 0"
echo "  Heartbeats: $HEARTBEAT_COUNT"
echo ""
echo "State file:"
python -c "import json; print(json.dumps(json.load(open('$STATE_FILE')), indent=2))"
echo ""
echo "Status: ✓ READY FOR SINGLE-CANDLE LIVE TEST"
echo ""
echo "Next steps:"
echo "  1. Document dry-run results in daily summary"
echo "  2. Run single-candle live test (see runner_deployment.md)"
echo "  3. Deploy persistent setup if single-candle test passes"
