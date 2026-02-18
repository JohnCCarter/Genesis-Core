#!/usr/bin/env bash
set -uo pipefail

ROOT="${GENESIS_ROOT:-/opt/genesis/Genesis-Core}"
OUT_DIR="${RC_OUT_DIR:-$ROOT/logs/paper_trading}"
WINDOW_MINUTES=30

usage() {
  cat <<'EOF'
Usage: capture_paper_rc.sh [options]

Capture a root-cause diagnostics bundle for genesis-paper/genesis-runner.
No secrets are printed by design (basic redaction is applied).

Options:
  --window-minutes N   Journal window in minutes (default: 30)
  --out-dir PATH       Output directory (default: /opt/genesis/Genesis-Core/logs/paper_trading)
  -h, --help           Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --window-minutes)
      WINDOW_MINUTES="${2:-}"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[rc] unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "$WINDOW_MINUTES" =~ ^[0-9]+$ ]]; then
  echo "[rc] --window-minutes must be an integer" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"
TS="$(date -u +%Y%m%d_%H%M%SZ)"
OUT_FILE="$OUT_DIR/rc_capture_${TS}.txt"

redact() {
  sed -E \
    -e 's/(BITFINEX_[A-Z_]+=)[^[:space:]]+/\1***REDACTED***/g' \
    -e 's/(Authorization: Bearer )[A-Za-z0-9._-]+/\1***REDACTED***/g' \
    -e 's/(api[_-]?key[=:])[[:space:]]*[^[:space:]]+/\1 ***REDACTED***/Ig' \
    -e 's/(api[_-]?secret[=:])[[:space:]]*[^[:space:]]+/\1 ***REDACTED***/Ig'
}

run_block() {
  local title="$1"
  shift
  {
    echo
    echo "===== ${title} ====="
    "$@" 2>&1 | redact || true
  } >> "$OUT_FILE"
}

{
  echo "RC capture timestamp (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Root: $ROOT"
  echo "Journal window: last ${WINDOW_MINUTES}m"
} > "$OUT_FILE"

run_block "system basics" bash -lc "hostname && date -u"
run_block "systemctl show genesis-paper" systemctl show genesis-paper.service -p ActiveState -p SubState -p MainPID -p NRestarts -p ExecMainStatus -p ExecMainCode -p ExecMainStartTimestamp -p ExecMainExitTimestamp -p WorkingDirectory -p FragmentPath -p DropInPaths -p EnvironmentFiles --no-pager
run_block "systemctl show genesis-runner" systemctl show genesis-runner.service -p ActiveState -p SubState -p MainPID -p NRestarts -p ExecMainStatus -p ExecMainCode -p ExecMainStartTimestamp -p ExecMainExitTimestamp -p WorkingDirectory -p FragmentPath -p DropInPaths -p EnvironmentFiles --no-pager
run_block "systemctl cat genesis-paper" systemctl cat genesis-paper.service --no-pager
run_block "systemctl cat genesis-runner" systemctl cat genesis-runner.service --no-pager
run_block "listeners and processes" bash -lc "ss -ltnp | grep ':8000 ' || true; pgrep -af 'uvicorn|paper_trading_runner.py' || true"
run_block "journal genesis-paper (window)" journalctl -u genesis-paper.service --since "-${WINDOW_MINUTES} min" --no-pager -o short-iso
run_block "journal genesis-runner (window)" journalctl -u genesis-runner.service --since "-${WINDOW_MINUTES} min" --no-pager -o short-iso
run_block "error-focused grep paper" bash -lc "journalctl -u genesis-paper.service --since '-${WINDOW_MINUTES} min' --no-pager -o short-iso | grep -E 'status=1/FAILURE|Traceback|ERROR|Exception|Address already in use|invalid environment assignment|Failed with result' || true"
run_block "error-focused grep runner" bash -lc "journalctl -u genesis-runner.service --since '-${WINDOW_MINUTES} min' --no-pager -o short-iso | grep -E 'status=1/FAILURE|Traceback|ERROR|Exception|Failed with result' || true"
run_block "tail api_service.log" bash -lc "tail -n 200 '$ROOT/logs/paper_trading/api_service.log' || true"
run_block "tail runner_service.log" bash -lc "tail -n 200 '$ROOT/logs/paper_trading/runner_service.log' || true"
run_block "env file metadata" bash -lc "ls -lah '$ROOT/.env' '$ROOT/.env.systemd' 2>/dev/null || true; file -bi '$ROOT/.env' '$ROOT/.env.systemd' 2>/dev/null || true; echo -n '.env.systemd BOM(hex): '; head -c 3 '$ROOT/.env.systemd' 2>/dev/null | od -An -tx1 | tr -d ' \n'; echo; if grep -q $'\r' '$ROOT/.env.systemd' 2>/dev/null; then echo 'CRLF_FOUND'; else echo 'CRLF_OK'; fi"

echo "[rc] captured: $OUT_FILE"
