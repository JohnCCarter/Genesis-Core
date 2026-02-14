#!/usr/bin/env bash
set -euo pipefail

ROOT="${GENESIS_ROOT:-/opt/genesis/Genesis-Core}"
REPORT_DIR="$ROOT/logs/paper_trading"
TS="$(date -u +%Y%m%d_%H%M%SZ)"
REPORT="$REPORT_DIR/weekend_gate_${TS}.txt"
RESTART_STABILITY_SECONDS="${RESTART_STABILITY_SECONDS:-30}"

mkdir -p "$REPORT_DIR"
exec > >(tee -a "$REPORT") 2>&1

fail() {
  echo "[FAIL] $*"
  echo "RESULT: FAIL"
  exit 1
}

warn() {
  echo "[WARN] $*"
}

pass() {
  echo "[PASS] $*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"
}

check_json_status_ok() {
  local payload="$1"
  python3 - "$payload" <<'PY'
import json, sys
obj = json.loads(sys.argv[1])
if obj.get("status") != "ok":
    raise SystemExit(1)
PY
}

for c in bash awk grep sed curl systemctl ss python3 file head hexdump; do
  require_cmd "$c"
done

echo "=== Weekend Bot Gate ==="
echo "Root: $ROOT"
echo "Report: $REPORT"

[[ -d "$ROOT" ]] || fail "missing root: $ROOT"
[[ -x "$ROOT/scripts/generate_env_systemd.sh" ]] || fail "missing generator: $ROOT/scripts/generate_env_systemd.sh"
[[ -x "$ROOT/scripts/wait_for_paper.sh" ]] || fail "missing wait script: $ROOT/scripts/wait_for_paper.sh"

echo "--- 1) Environment & config ---"
"$ROOT/scripts/generate_env_systemd.sh" "$ROOT/.env" "$ROOT/.env.systemd" || fail "generate .env.systemd failed"
pass ".env.systemd regenerated"

hex="$(head -c 3 "$ROOT/.env.systemd" | od -An -tx1 | tr -d ' \n')"
[[ "$hex" != "efbbbf" ]] || fail ".env.systemd starts with UTF-8 BOM"
pass ".env.systemd has no BOM"

enc="$(file -b --mime-encoding "$ROOT/.env.systemd")"
[[ "$enc" == "utf-8" ]] || fail ".env.systemd encoding is not utf-8 (got: $enc)"
pass ".env.systemd encoding utf-8"

for k in BITFINEX_API_KEY BITFINEX_API_SECRET BITFINEX_WS_API_KEY BITFINEX_WS_API_SECRET; do
  grep -Eq "^${k}=" "$ROOT/.env.systemd" || fail "missing key in .env.systemd: $k"
done
pass "required REST/WS keys present in .env.systemd"

[[ -x "$ROOT/.venv/bin/python" ]] || fail "missing venv python: $ROOT/.venv/bin/python"
pass "venv python exists"

"$ROOT/.venv/bin/python" - <<'PY' || fail "python import check failed"
import core.server  # noqa: F401
import core.pipeline  # noqa: F401
import mcp  # noqa: F401
print("imports_ok")
PY
pass "critical python imports OK"

echo "--- 2) systemd chain ---"
systemctl cat genesis-paper.service --no-pager | grep -q 'EnvironmentFile=/opt/genesis/Genesis-Core/.env.systemd' \
  || fail "genesis-paper does not use .env.systemd"
systemctl cat genesis-runner.service --no-pager | grep -q 'EnvironmentFile=/opt/genesis/Genesis-Core/.env.systemd' \
  || fail "genesis-runner does not use .env.systemd"
systemctl cat genesis-runner.service --no-pager | grep -q 'ExecStartPre=/opt/genesis/Genesis-Core/scripts/wait_for_paper.sh' \
  || fail "genesis-runner missing ExecStartPre wait_for_paper"
systemctl cat genesis-runner.service --no-pager | grep -q '^StartLimitIntervalSec=300' \
  || fail "genesis-runner missing StartLimitIntervalSec=300"
systemctl cat genesis-runner.service --no-pager | grep -q '^StartLimitBurst=5' \
  || fail "genesis-runner missing StartLimitBurst=5"
systemctl cat genesis-runner.service --no-pager | grep -q '^RestartSec=5' \
  || fail "genesis-runner RestartSec is not 5"
pass "runner unit policy looks correct"

sudo systemctl daemon-reload || fail "daemon-reload failed"
pass "daemon-reload OK"

sudo systemctl start genesis-paper.service || fail "failed to start genesis-paper"
health_json=""
for _ in $(seq 1 20); do
  if health_json="$(curl -fsS --max-time 2 http://127.0.0.1:8000/health 2>/dev/null)"; then
    break
  fi
  sleep 1
done
[[ -n "$health_json" ]] || fail "paper health endpoint failed"
check_json_status_ok "$health_json" || fail "paper health status != ok"
ss -ltnp | grep -q '127.0.0.1:8000' || fail "paper port 8000 not listening"
pass "paper service healthy on 127.0.0.1:8000"

before_restarts="$(systemctl show genesis-runner.service -p NRestarts --value)"
sudo systemctl start genesis-runner.service || fail "failed to start genesis-runner"
sleep 2
systemctl is-active --quiet genesis-runner.service || fail "runner not active after start"
pass "runner active"

journalctl -u genesis-runner.service -n 80 --no-pager | grep -q 'Started genesis-runner.service' \
  || fail "runner start event not found in journal"
tail -n 120 "$ROOT/logs/paper_trading/runner_service.log" | grep -q '\[wait_for_paper\] API ready' \
  || fail "ExecStartPre wait_for_paper success not observed in runner_service.log"
pass "ExecStartPre wait_for_paper succeeded"

sleep "$RESTART_STABILITY_SECONDS"
after_restarts="$(systemctl show genesis-runner.service -p NRestarts --value)"
[[ "$after_restarts" == "$before_restarts" ]] || fail "runner NRestarts changed during stability window ($before_restarts -> $after_restarts)"
pass "runner NRestarts stable for ${RESTART_STABILITY_SECONDS}s"

echo "--- 3) Trading safety ---"
submit_resp="$(curl -fsS -X POST http://127.0.0.1:8000/paper/submit \
  -H 'content-type: application/json' \
  -d '{"symbol":"tBTCUSD","side":"NONE","size":0.001,"type":"MARKET"}')" || fail "/paper/submit probe failed"
echo "$submit_resp" | grep -q '"ok":false' || fail "/paper/submit invalid-action probe expected ok=false"
pass "/paper/submit endpoint reachable (invalid-action probe)"

"$ROOT/.venv/bin/python" "$ROOT/scripts/smoke_submit_call.py" >/tmp/weekend_symbol_gate.json 2>/tmp/weekend_symbol_gate.err \
  || fail "symbol fallback contract test failed (smoke_submit_call.py)"
"$ROOT/.venv/bin/python" - /tmp/weekend_symbol_gate.json <<'PY' || fail "symbol fallback output invalid"
import json, sys
path = sys.argv[1]
obj = json.loads(open(path, encoding="utf-8").read())
sym = (
    obj.get("mapped_symbol")
    or (obj.get("request") or {}).get("symbol")
    or ""
)
if not (isinstance(sym, str) and sym.startswith("tTEST") and ":TEST" in sym):
    raise SystemExit(1)
print("symbol_gate_ok")
PY
pass "symbol fallback/clamp contract OK"

orders_resp="$(curl -fsS http://127.0.0.1:8000/account/orders)" || fail "/account/orders failed"
python3 - "$orders_resp" <<'PY' || fail "/account/orders payload invalid"
import json, sys
obj = json.loads(sys.argv[1])
if "items" not in obj:
    raise SystemExit(1)
print("orders_ok")
PY
pass "/account/orders returns payload"

tail -n 200 "$ROOT/logs/paper_trading/runner_service.log" | grep -q 'Mode: LIVE PAPER TRADING' \
  || fail "runner log does not show LIVE PAPER mode"
if tail -n 200 "$ROOT/logs/paper_trading/runner_service.log" | grep -q 'Would submit'; then
  fail "dry-run style 'Would submit' detected in runner logs"
fi
pass "runner logs indicate live-paper mode (no dry-run markers)"

"$ROOT/.venv/bin/python" - "$ROOT/config/strategy/champions/tBTCUSD_1h.json" <<'PY' || fail "champion guardrails check failed"
import json, sys
path = sys.argv[1]
obj = json.loads(open(path, encoding="utf-8").read())
cfg = obj.get("merged_config") or obj.get("cfg") or {}
components = cfg.get("components", []) if isinstance(cfg, dict) else []
if not components:
    raise SystemExit(1)
has_cooldown_like = any(
    isinstance(c, dict)
    and isinstance(c.get("params"), dict)
    and "min_bars_between_trades" in c.get("params", {})
    for c in components
)
if not has_cooldown_like:
    raise SystemExit(1)
print("guardrails_ok")
PY
pass "champion guardrails look present (cooldown component found)"

echo "--- 4) Data & strategy ---"
tail -n 200 "$ROOT/logs/paper_trading/runner_service.log" | grep -q 'Champion verified successfully.' \
  || fail "champion verification log missing"
pass "champion verified log found"

if tail -n 400 "$ROOT/logs/paper_trading/runner_$(date -u +%Y%m%d).log" | grep -q 'NEW CANDLE CLOSE:'; then
  pass "candle close progression observed"
else
  warn "no NEW CANDLE CLOSE in current log window (can be normal between 1h closes)"
fi

eval_lines="$(tail -n 400 "$ROOT/logs/paper_trading/runner_$(date -u +%Y%m%d).log" | grep 'EVALUATION:' || true)"
if [[ -n "$eval_lines" ]]; then
  if echo "$eval_lines" | grep -q 'action=NONE' && ! echo "$eval_lines" | grep -Eq 'action=(LONG|SHORT)'; then
    warn "recent evaluations are all NONE; check thresholds/features/regime if this persists"
  else
    pass "evaluation stream contains actionable diversity or mixed outcomes"
  fi
else
  warn "no EVALUATION lines in current tail window yet"
fi

echo "RESULT: PASS"
echo "Report saved: $REPORT"
