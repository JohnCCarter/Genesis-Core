#!/bin/bash
#
# Daily Health Check - Genesis Paper Trading
#
# Usage: ./scripts/daily_health_check.sh
# Schedule: Daily (cron or Task Scheduler)
#

set -euo pipefail

REPO_ROOT="/c/Users/fa06662/Projects/Genesis-Core"
SNAPSHOT_DIR="$REPO_ROOT/logs/paper_trading/daily_snapshots"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

cd "$REPO_ROOT"
mkdir -p "$SNAPSHOT_DIR"

SNAPSHOT_FILE="$SNAPSHOT_DIR/health_${DATE}.json"

echo "=== Daily Health Check: $TIMESTAMP ===" | tee -a logs/paper_trading/health_check.log

# Function to check server health
check_health() {
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    curl -s http://localhost:8000/health
    return 0
  else
    echo '{"status":"error","message":"Server not responding"}'
    return 1
  fi
}

# Function to get runtime config
get_runtime() {
  if curl -sf http://localhost:8000/config/runtime > /dev/null 2>&1; then
    curl -s http://localhost:8000/config/runtime
    return 0
  else
    echo '{"error":"Runtime config not available"}'
    return 1
  fi
}

# Function to get git info
get_git_info() {
  echo "{"
  echo "  \"commit\": \"$(git log -1 --format='%H')\","
  echo "  \"commit_short\": \"$(git log -1 --format='%h')\","
  echo "  \"commit_date\": \"$(git log -1 --format='%ci')\","
  echo "  \"commit_message\": \"$(git log -1 --format='%s' | sed 's/"/\\"/g')\","
  echo "  \"branch\": \"$(git branch --show-current)\","
  echo "  \"status_clean\": $([ -z "$(git status --porcelain)" ] && echo "true" || echo "false")"
  echo "}"
}

# Function to get server uptime
get_uptime() {
  if pgrep -f "uvicorn core.server:app" > /dev/null; then
    PID=$(pgrep -f "uvicorn core.server:app" | head -1)
    ps -p "$PID" -o etime= | xargs
  else
    echo "not_running"
  fi
}

# Collect snapshot
{
  echo "{"
  echo "  \"snapshot_date\": \"$DATE\","
  echo "  \"timestamp\": \"$TIMESTAMP\","

  echo "  \"health\": $(check_health || echo '{"status":"error"}'),"

  echo "  \"runtime_config\": $(get_runtime || echo '{}'),"

  echo "  \"git\": $(get_git_info),"

  echo "  \"server\": {"
  echo "    \"uptime\": \"$(get_uptime)\","
  echo "    \"pid\": $(pgrep -f "uvicorn core.server:app" | head -1 || echo "null")"
  echo "  },"

  echo "  \"environment\": {"
  echo "    \"GENESIS_SYMBOL_MODE\": \"${GENESIS_SYMBOL_MODE:-not_set}\","
  echo "    \"LOG_LEVEL\": \"${LOG_LEVEL:-not_set}\","
  echo "    \"python_version\": \"$(python --version 2>&1)\""
  echo "  }"

  echo "}"
} > "$SNAPSHOT_FILE"

# Pretty print
python3 -m json.tool "$SNAPSHOT_FILE" > "${SNAPSHOT_FILE}.tmp" && mv "${SNAPSHOT_FILE}.tmp" "$SNAPSHOT_FILE"

echo "Snapshot saved: $SNAPSHOT_FILE" | tee -a logs/paper_trading/health_check.log

# Check for issues
HEALTH_STATUS=$(cat "$SNAPSHOT_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['health']['status'])" 2>/dev/null || echo "unknown")

if [ "$HEALTH_STATUS" != "ok" ]; then
  echo "WARNING: Health check failed! Status: $HEALTH_STATUS" | tee -a logs/paper_trading/health_check.log
  exit 1
fi

echo "Health check PASSED" | tee -a logs/paper_trading/health_check.log
exit 0
