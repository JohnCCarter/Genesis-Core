#!/bin/bash
# capture_phase3_snapshot.sh - Capture Phase 3 runtime snapshot without stopping processes
#
# Usage: ./scripts/capture_phase3_snapshot.sh
#
# Creates timestamped snapshot in logs/paper_trading/snapshots/ with:
#   - System info (date, hostname)
#   - Port 8000 process details
#   - API health check
#   - Latest 80 lines from runner log
#   - State file contents
#   - Pre-flight test results (if available)
#
# Output: logs/paper_trading/snapshots/snapshot_YYYYMMDD_HHMMSSZ.txt
# No secrets are written to snapshot.

set -euo pipefail

# UTC timestamp for filename
TIMESTAMP=$(date -u +'%Y%m%d_%H%M%SZ')
SNAPSHOT_DIR="logs/paper_trading/snapshots"
SNAPSHOT_FILE="${SNAPSHOT_DIR}/snapshot_${TIMESTAMP}.txt"

# Ensure snapshot directory exists
mkdir -p "$SNAPSHOT_DIR"

# Runner log file (UTC date)
RUNNER_LOG="logs/paper_trading/runner_$(date -u +%Y%m%d).log"
STATE_FILE="logs/paper_trading/runner_state.json"

# Start snapshot
{
    echo "========================================"
    echo "=== Phase 3 Runtime Snapshot =========="
    echo "========================================"
    echo ""
    echo "Captured: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
    echo "Hostname: $(hostname)"
    echo ""

    # Section 1: Port 8000 process
    echo "========================================"
    echo "=== Port 8000 Process =================="
    echo "========================================"
    echo ""

    # Try ss first (Linux), fallback to lsof (macOS/BSD), then netstat (Windows/cross-platform)
    if command -v ss >/dev/null 2>&1; then
        echo "$ ss -tlnp | grep :8000"
        ss -tlnp 2>/dev/null | grep :8000 || echo "(no process listening on port 8000)"
    elif command -v lsof >/dev/null 2>&1; then
        echo "$ lsof -i :8000 -P -n"
        lsof -i :8000 -P -n 2>/dev/null || echo "(no process listening on port 8000)"
    elif command -v netstat >/dev/null 2>&1; then
        echo "$ netstat -an | grep :8000"
        netstat -an 2>/dev/null | grep :8000 || echo "(no process listening on port 8000)"
    else
        echo "WARNING: No port inspection tool available (ss, lsof, netstat)"
        echo "API health check below will indicate if port 8000 is responding."
    fi
    echo ""

    # Section 2: API health check
    echo "========================================"
    echo "=== API Health Check ==================="
    echo "========================================"
    echo ""
    echo "$ curl -s http://localhost:8000/health"

    if HEALTH_RESP=$(curl -s --max-time 5 http://localhost:8000/health 2>&1); then
        echo "$HEALTH_RESP"
        echo ""
        echo "Status: SUCCESS"
    else
        echo "(API not responding)"
        echo ""
        echo "Status: FAILED"
    fi
    echo ""

    # Section 3: Latest 80 lines from runner log
    echo "========================================"
    echo "=== Runner Log (latest 80 lines) ======"
    echo "========================================"
    echo ""
    echo "Log file: $RUNNER_LOG"
    echo ""

    if [ -f "$RUNNER_LOG" ]; then
        tail -80 "$RUNNER_LOG"
    else
        echo "(log file not found: $RUNNER_LOG)"
    fi
    echo ""

    # Section 4: State file contents
    echo "========================================"
    echo "=== Runner State File =================="
    echo "========================================"
    echo ""
    echo "State file: $STATE_FILE"
    echo ""

    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo "(state file not found: $STATE_FILE)"
    fi
    echo ""

    # Section 5: Pre-flight smoke test (if script exists)
    echo "========================================"
    echo "=== Pre-flight Smoke Test =============="
    echo "========================================"
    echo ""

    if [ -f "./scripts/preflight_smoke_test.sh" ]; then
        echo "$ ./scripts/preflight_smoke_test.sh"
        echo ""

        # Capture output and exit code
        set +e
        PREFLIGHT_OUTPUT=$(./scripts/preflight_smoke_test.sh 2>&1)
        PREFLIGHT_EXIT=$?
        set -e

        echo "$PREFLIGHT_OUTPUT"
        echo ""
        echo "Exit code: $PREFLIGHT_EXIT"

        if [ "$PREFLIGHT_EXIT" -eq 0 ]; then
            echo "Status: PASS ✓"
        else
            echo "Status: FAIL ✗"
        fi
    else
        echo "(preflight script not found: ./scripts/preflight_smoke_test.sh)"
    fi
    echo ""

    # End of snapshot
    echo "========================================"
    echo "=== Snapshot Complete =================="
    echo "========================================"
    echo ""
    echo "Snapshot saved to: $SNAPSHOT_FILE"
    echo "Size: $(du -h "$SNAPSHOT_FILE" | cut -f1)"
    echo ""

} > "$SNAPSHOT_FILE" 2>&1

# Report to user
echo "Phase 3 snapshot captured successfully."
echo ""
echo "File: $SNAPSHOT_FILE"
echo "Size: $(du -h "$SNAPSHOT_FILE" | cut -f1)"
echo "Time: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
echo ""
echo "To view:"
echo "  cat $SNAPSHOT_FILE"
echo "  less $SNAPSHOT_FILE"
