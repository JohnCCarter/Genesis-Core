#!/bin/bash
# preflight_smoke_test.sh - 5-minute pre-flight smoke test for paper trading runner
#
# Usage: ./scripts/preflight_smoke_test.sh
#
# Verifies:
#   1. API server on port 8000 responds to /health
#   2. Today's runner log exists and has >50 lines
#   3. Runner log contains "Champion verified successfully"
#   4. State file exists and contains last_heartbeat
#   5. Runner log contains no FATAL errors
#
# Prerequisites:
#   - Runner must already be started (script does NOT start runner)
#   - Wait at least 2-3 minutes after runner startup before running this script
#
# Exit codes:
#   0 = All checks passed
#   1 = One or more checks failed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Use UTC date to match runner log filenames.
# NOTE: The runner log filename is chosen at runner start and does not necessarily rotate at UTC midnight.
# For robustness, prefer the most recently modified runner_*.log (runner is expected to be writing to it).
EXPECTED_LOG_FILE="logs/paper_trading/runner_$(date -u +%Y%m%d).log"
LATEST_LOG_FILE=$(ls -1t logs/paper_trading/runner_*.log 2>/dev/null | head -1)
if [ -n "$LATEST_LOG_FILE" ]; then
  LOG_FILE="$LATEST_LOG_FILE"
else
  LOG_FILE="$EXPECTED_LOG_FILE"
fi
STATE_FILE="logs/paper_trading/runner_state.json"

echo "========================================="
echo "=== Pre-flight Smoke Test (5 min) ======"
echo "========================================="
echo ""
echo "Expected log file (UTC date): $EXPECTED_LOG_FILE"
echo "Using log file: $LOG_FILE"
echo "State file: $STATE_FILE"
echo ""

# Track failures
FAILED=0

# Check 1: API server on port 8000 responds to /health
echo -n "[1/5] API server health check... "
if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
  HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep -o '"status":"ok"' || true)
  if [ -n "$HEALTH_STATUS" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
  else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Error: /health responded but status is not 'ok'"
    RESPONSE=$(curl -s http://localhost:8000/health)
    echo "  Response: $RESPONSE"
    FAILED=1
  fi
else
  echo -e "${RED}✗ FAIL${NC}"
  echo "  Error: API server not responding on http://localhost:8000/health"
  echo "  Possible causes:"
  echo "    - API server not started"
  echo "    - Port 8000 used by different process"
  echo "    - Network/firewall issue"
  echo "  Check: lsof -i :8000 -P -n"
  FAILED=1
fi

# Check 2: Today's runner log exists, is fresh, and has activity
echo -n "[2/5] Runner log file existence... "
if [ -f "$LOG_FILE" ]; then
  echo -e "${GREEN}✓ EXISTS${NC}"

  # Check 2a: Log file freshness (mtime within last 120 seconds)
  echo -n "      Log file freshness (mtime)... "

  # Get file modification time (Unix timestamp)
  # Try Linux stat first, fall back to macOS/BSD stat
  if stat -c %Y "$LOG_FILE" > /dev/null 2>&1; then
    # Linux
    FILE_MTIME=$(stat -c %Y "$LOG_FILE")
  elif stat -f %m "$LOG_FILE" > /dev/null 2>&1; then
    # macOS/BSD
    FILE_MTIME=$(stat -f %m "$LOG_FILE")
  else
    # Fallback: use ls + date parsing (less reliable)
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "  Warning: Cannot determine file mtime (stat not available)"
    echo "  Skipping freshness check"
    FILE_MTIME=0
  fi

  if [ "$FILE_MTIME" -ne 0 ]; then
    CURRENT_TIME=$(date +%s)
    FILE_AGE=$((CURRENT_TIME - FILE_MTIME))

    if [ "$FILE_AGE" -le 120 ]; then
      echo -e "${GREEN}✓ PASS${NC} (${FILE_AGE}s ago)"
    else
      echo -e "${RED}✗ FAIL${NC}"
      echo "  Error: Log file is stale (last modified ${FILE_AGE}s ago, expected <120s)"
      echo "  Possible causes:"
      echo "    - Runner not writing to this file (wrong filename/date)"
      echo "    - Runner crashed/stopped (not polling)"
      echo "    - Runner writing to different log file (timezone mismatch)"
      echo "  Current time: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
      echo "  File mtime: $(date -u -d @$FILE_MTIME +'%Y-%m-%d %H:%M:%S UTC' 2>/dev/null || date -r $FILE_MTIME -u +'%Y-%m-%d %H:%M:%S UTC' 2>/dev/null || echo 'unknown')"
      echo "  Check: ps aux | grep paper_trading_runner"
      echo "  Check: ls -lht logs/paper_trading/runner_*.log | head -3"
      FAILED=1
    fi
  fi

  # Check 2b: Line count (warning only, not fail)
  echo -n "      Log file activity (lines)... "
  LINE_COUNT=$(wc -l < "$LOG_FILE")
  if [ "$LINE_COUNT" -gt 50 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($LINE_COUNT lines)"
  else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "  Warning: Log file has only $LINE_COUNT lines (expected >50 after 2-3 min)"
    echo "  Possible causes:"
    echo "    - Runner just started (wait 2-3 more minutes)"
    echo "    - Runner crashed shortly after startup"
    echo "    - Runner not polling actively"
    echo "  Last 10 lines of log:"
    tail -10 "$LOG_FILE" | sed 's/^/        /'
    # Don't fail on this, just warn
  fi
else
  echo -e "${RED}✗ FAIL${NC}"
  echo "  Error: Log file not found: $LOG_FILE"
  echo "  Expected filename: runner_$(date -u +%Y%m%d).log (UTC date)"
  echo "  Note: If the runner started before UTC midnight, it may still be writing to yesterday's log file."
  echo "  Possible causes:"
  echo "    - Runner not started"
  echo "    - Runner started with different date (timezone mismatch - use TZ=UTC)"
  echo "    - Log directory missing (check logs/paper_trading/ exists)"
  echo "  Check: ls -lh logs/paper_trading/runner_*.log"
  FAILED=1
fi

# Check 3: Runner log contains "Champion verified successfully"
echo -n "[3/5] Champion verification... "
if [ -f "$LOG_FILE" ]; then
  if grep -q "Champion verified successfully" "$LOG_FILE"; then
    echo -e "${GREEN}✓ PASS${NC}"
  else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Error: 'Champion verified successfully' not found in log"
    echo "  Possible causes:"
    echo "    - Champion file missing (config/strategy/champions/tBTCUSD_1h.json)"
    echo "    - Champion structure invalid (missing merged_config key)"
    echo "    - Baseline fallback detected"
    echo "  Check for baseline fallback:"
    if grep -q "Baseline fallback detected" "$LOG_FILE"; then
      echo -e "    ${RED}FOUND: Baseline fallback detected in log${NC}"
      grep "Baseline fallback detected" "$LOG_FILE" | head -3 | sed 's/^/    /'
    else
      echo "    No 'Baseline fallback detected' found"
    fi
    echo "  Check for champion errors:"
    grep -E "Champion|champion|ERROR.*champion" "$LOG_FILE" | head -5 | sed 's/^/    /' || echo "    (no champion-related errors found)"
    FAILED=1
  fi
else
  echo -e "${RED}✗ SKIP${NC} (log file missing)"
fi

# Check 4: State file exists and contains last_heartbeat
echo -n "[4/5] State file heartbeat... "
if [ -f "$STATE_FILE" ]; then
  if grep -q "last_heartbeat" "$STATE_FILE"; then
    # Allow optional whitespace around ':' to avoid false warnings.
    HEARTBEAT=$(grep -oE '"last_heartbeat"[[:space:]]*:[[:space:]]*"[^"]*"' "$STATE_FILE" | head -1)
    if [ -n "$HEARTBEAT" ]; then
      echo -e "${GREEN}✓ PASS${NC}"
      echo "  $HEARTBEAT"
    else
      echo -e "${YELLOW}⚠ WARNING${NC}"
      echo "  Warning: last_heartbeat field present but empty/null"
      echo "  State file content:"
      cat "$STATE_FILE" | sed 's/^/    /'
      # Don't fail, heartbeat might be null if runner just started
    fi
  else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Error: 'last_heartbeat' field not found in state file"
    echo "  State file content:"
    cat "$STATE_FILE" | sed 's/^/    /'
    FAILED=1
  fi
else
  echo -e "${RED}✗ FAIL${NC}"
  echo "  Error: State file not found: $STATE_FILE"
  echo "  Possible causes:"
  echo "    - Runner not started"
  echo "    - Runner crashed before creating state file"
  echo "    - Permissions issue (cannot write to logs/paper_trading/)"
  echo "  Check: ls -lh logs/paper_trading/"
  FAILED=1
fi

# Check 5: Runner log contains no FATAL errors
echo -n "[5/5] No fatal errors... "
if [ -f "$LOG_FILE" ]; then
  FATAL_COUNT=$(grep -c "FATAL" "$LOG_FILE" || true)
  if [ "$FATAL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
  else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Error: Found $FATAL_COUNT FATAL error(s) in log"
    echo "  Fatal errors:"
    grep "FATAL" "$LOG_FILE" | sed 's/^/    /'
    FAILED=1
  fi
else
  echo -e "${RED}✗ SKIP${NC} (log file missing)"
fi

# Summary
echo ""
echo "========================================="
if [ "$FAILED" -eq 0 ]; then
  echo -e "=== ${GREEN}PRE-FLIGHT: PASS ✓${NC} ==============="
  echo "========================================="
  echo ""
  echo "Status: Runner is healthy and ready for 24h dry-run."
  echo ""
  echo "Next steps:"
  echo "  1. Monitor logs: tail -f $LOG_FILE"
  echo "  2. Wait for first candle close (top of next hour)"
  echo "  3. Run acceptance checks after 24h:"
  echo "     ./scripts/dry_run_acceptance.sh"
  echo ""
  exit 0
else
  echo -e "=== ${RED}PRE-FLIGHT: FAIL ✗${NC} ==============="
  echo "========================================="
  echo ""
  echo "Status: One or more pre-flight checks failed."
  echo ""
  echo "Action required:"
  echo "  1. Review errors above"
  echo "  2. Stop runner if running: pkill -f paper_trading_runner"
  echo "  3. Fix issues (see error messages for guidance)"
  echo "  4. Restart runner: TZ=UTC python scripts/paper_trading_runner.py --dry-run"
  echo "  5. Wait 2-3 minutes, then re-run this script"
  echo ""
  echo "DO NOT proceed to 24h dry-run until all pre-flight checks pass."
  echo ""
  exit 1
fi
