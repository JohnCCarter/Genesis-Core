param(
    [Parameter(Mandatory = $true)]
    [string]$SshTarget,

    [string]$RepoDir = "/opt/genesis/Genesis-Core",
    [string]$Branch = "feature/composable-strategy-phase2",

    [string]$ApiService = "genesis-paper.service",
    [string]$RunnerService = "genesis-runner.service",

    [int]$PreflightWaitSeconds = 180,

    [bool]$ScheduleAcceptance = $true,
    [int]$AcceptanceDelayHours = 24,

    [bool]$UseSudo = $true,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Quote-BashSingle {
    param([string]$Value)
    return "'" + ($Value -replace "'", "'\\''") + "'"
}

$repoDirQ = Quote-BashSingle $RepoDir
$branchQ = Quote-BashSingle $Branch
$apiSvcQ = Quote-BashSingle $ApiService
$runnerSvcQ = Quote-BashSingle $RunnerService
$preflightWait = [Math]::Max(0, $PreflightWaitSeconds)
$acceptanceDelay = [Math]::Max(0, $AcceptanceDelayHours)
$useSudoFlag = if ($UseSudo) { "1" } else { "0" }
$scheduleFlag = if ($ScheduleAcceptance) { "1" } else { "0" }

# IMPORTANT: Build the remote bash script without PowerShell string interpolation.
# We prepend a small variable-assignment header (inserted values are already bash-single-quoted),
# then append a literal bash body that may contain $VARS and $(...) without PowerShell touching it.
$remoteHeader = "set -euo pipefail`n" +
"REPO_DIR=$repoDirQ`n" +
"BRANCH=$branchQ`n" +
"API_SERVICE=$apiSvcQ`n" +
"RUNNER_SERVICE=$runnerSvcQ`n" +
"USE_SUDO=$useSudoFlag`n" +
"SCHEDULE_ACCEPTANCE=$scheduleFlag`n" +
"PREFLIGHT_WAIT_SECONDS=$preflightWait`n" +
"ACCEPTANCE_DELAY_HOURS=$acceptanceDelay`n"

$remoteBody = @'

cd "$REPO_DIR"

TS="$(date -u +%Y%m%d_%H%M%S)"
ARCHIVE_DIR="logs/paper_trading/_archive/restart_${TS}"
mkdir -p "$ARCHIVE_DIR"

echo "[remote] repo=$REPO_DIR"
echo "[remote] branch=$BRANCH"
echo "[remote] archive=$ARCHIVE_DIR"

if [ -f logs/paper_trading/runner_state.json ]; then
  mv logs/paper_trading/runner_state.json "$ARCHIVE_DIR/" || true
fi

# Move runner logs to ensure a clean 24h acceptance window.
shopt -s nullglob
for f in logs/paper_trading/runner_*.log; do
  mv "$f" "$ARCHIVE_DIR/" || true
done

if [ "$USE_SUDO" = "1" ]; then
  sudo -n true >/dev/null 2>&1 || { echo "ERROR: sudo requires a password. Re-run with -UseSudo:\$false or configure NOPASSWD."; exit 2; }
  sudo -n systemctl stop "$RUNNER_SERVICE" || true
  sudo -n systemctl stop "$API_SERVICE" || true
else
  systemctl stop "$RUNNER_SERVICE" || true
  systemctl stop "$API_SERVICE" || true
fi

echo "[remote] git fetch/pull..."
git fetch origin

git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"
echo "[remote] HEAD=$(git rev-parse --short HEAD)"

if [ "$USE_SUDO" = "1" ]; then
  sudo -n systemctl start "$API_SERVICE"
else
  systemctl start "$API_SERVICE"
fi

echo "[remote] waiting for /health..."
OK=0
for i in $(seq 1 30); do
  if command -v curl >/dev/null 2>&1; then
    if curl -fsS --max-time 2 http://127.0.0.1:8000/health >/dev/null; then OK=1; break; fi
  else
    if python3 - <<'PY'
import sys, urllib.request
try:
  urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()
  sys.exit(0)
except Exception:
  sys.exit(1)
PY
    then OK=1; break; fi
  fi
  sleep 1
done

if [ "$OK" -ne 1 ]; then
  echo "ERROR: API server did not become healthy on 127.0.0.1:8000"
  exit 3
fi

echo "[remote] API healthy. Starting runner..."
if [ "$USE_SUDO" = "1" ]; then
  sudo -n systemctl start "$RUNNER_SERVICE"
else
  systemctl start "$RUNNER_SERVICE"
fi

echo "[remote] waiting ${PREFLIGHT_WAIT_SECONDS}s before preflight..."
sleep "$PREFLIGHT_WAIT_SECONDS"

echo "[remote] running preflight..."
bash ./scripts/preflight_smoke_test.sh

LATEST_LOG=$(ls -1t logs/paper_trading/runner_*.log 2>/dev/null | head -1 || true)
echo "[remote] latest runner log: ${LATEST_LOG:-<none>}"

if [ "$SCHEDULE_ACCEPTANCE" = "1" ]; then
  DELAY_SECS=$((ACCEPTANCE_DELAY_HOURS * 3600))
  OUT="logs/paper_trading/acceptance_check_${TS}.txt"
  echo "[remote] scheduling acceptance in ${ACCEPTANCE_DELAY_HOURS}h -> $OUT"
  nohup bash -lc "sleep ${DELAY_SECS}; cd \"$REPO_DIR\"; bash ./scripts/dry_run_acceptance.sh" >"$OUT" 2>&1 </dev/null &
  echo $! >"${OUT}.pid"
fi

echo "[remote] done."
'@

$remoteScript = $remoteHeader + $remoteBody

Write-Host "SSH target: $SshTarget"
Write-Host "RepoDir: $RepoDir"
Write-Host "Branch: $Branch"
Write-Host "API service: $ApiService"
Write-Host "Runner service: $RunnerService"
Write-Host "Use sudo: $UseSudo"
Write-Host "Schedule acceptance: $ScheduleAcceptance"
Write-Host ""

if ($DryRun) {
    Write-Host "--- Remote script (dry-run) ---"
    Write-Host $remoteScript
    exit 0
}

# Run in a single SSH session. Requires key-based auth.
& ssh $SshTarget "bash -lc $(Quote-BashSingle $remoteScript)"
