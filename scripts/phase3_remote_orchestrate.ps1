param(
    # Optional: allow automation to pass SSH target via env var.
    # Recommended: use an SSH config alias (e.g. 'genesis-we') instead of hardcoding IPs.
    [string]$SshTarget = $(if ($Env:GENESIS_SSH_TARGET) { $Env:GENESIS_SSH_TARGET } else { "genesis-we" }),

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

if ([string]::IsNullOrWhiteSpace($SshTarget)) {
    Write-Error (
        "Missing -SshTarget and GENESIS_SSH_TARGET is not set. " +
        "Pass -SshTarget (e.g. 'genesis-we' or 'user@host') or set '$Env:GENESIS_SSH_TARGET' to 'genesis-we'."
    )
    exit 1
}

# Fail-fast: prevent accidental placeholder targets (e.g. genesis@<DIN_VM>) from reaching ssh.
if ($SshTarget -match '[<>]' -or $SshTarget -match 'DIN_VM') {
    Write-Error (
        "Invalid -SshTarget: appears to be a placeholder ('$SshTarget'). " +
        "Use a real SSH target, e.g. genesis@203.0.113.10 or genesis@myvm.example.com (no angle brackets)."
    )
    exit 1
}

if ($SshTarget -notmatch '@') {
    # If the target looks like a host/IP (contains '.' or ':'), missing '@' is often accidental (wrong user).
    # If the target looks like an SSH config alias (e.g. 'genesis-we'), this is expected.
    if ($SshTarget -match '[\.:]' -or $SshTarget -match '^\d{1,3}(?:\.\d{1,3}){3}$') {
        Write-Warning (
            "-SshTarget '$SshTarget' does not contain '@'. If this is a host/IP, " +
            "consider using 'user@host' to avoid connecting as the wrong user. " +
            "If it's an SSH config alias, you're fine."
        )
    }
    else {
        Write-Host "Info: using SSH config alias '$SshTarget' (no '@' expected)."
    }
}

function ConvertTo-BashSingleQuoted {
    param([string]$Value)
    # Bash-safe single-quote wrapper.
    # To embed a single quote in a single-quoted bash string: close, insert escaped quote, reopen => '\''
    # Note: use -replace with a literal replacement string that contains a single backslash.
    return "'" + ($Value -replace "'", "'\''") + "'"
}

$repoDirQ = ConvertTo-BashSingleQuoted $RepoDir
$branchQ = ConvertTo-BashSingleQuoted $Branch
$apiSvcQ = ConvertTo-BashSingleQuoted $ApiService
$runnerSvcQ = ConvertTo-BashSingleQuoted $RunnerService
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

    svc_exists() {
    local svc="$1"
    if [ "$USE_SUDO" = "1" ]; then
    sudo -n systemctl cat "$svc" >/dev/null 2>&1
    else
    systemctl cat "$svc" >/dev/null 2>&1
    fi
    }

    if ! svc_exists "$API_SERVICE"; then
    echo "[remote] ERROR: systemd unit not found: $API_SERVICE"
    echo "[remote] Hint: deploy the service unit, then run: sudo systemctl daemon-reload"
    exit 20
    fi

    if ! svc_exists "$RUNNER_SERVICE"; then
    echo "[remote] ERROR: systemd unit not found: $RUNNER_SERVICE"
    echo "[remote] Hint: deploy the service unit, then run: sudo systemctl daemon-reload"
    exit 21
    fi

        # Normalize REPO_DIR (strip any stray CR / trailing backslashes) and auto-detect if needed.
        REPO_DIR="${REPO_DIR%\\}"

        if [ ! -d "$REPO_DIR" ]; then
        echo "[remote] WARN: repo dir not found: $REPO_DIR"
        for c in /opt/genesis/Genesis-Core "$HOME/Genesis-Core" /opt/Genesis-Core; do
        if [ -d "$c" ] && [ -d "$c/.git" ]; then
        echo "[remote] INFO: using detected repo dir: $c"
        REPO_DIR="$c"
        break
        fi
        done
        fi

        if [ ! -d "$REPO_DIR" ]; then
        echo "[remote] ERROR: repo directory not found (after auto-detect)."
        echo "[remote] REPO_DIR=$REPO_DIR"
        echo "[remote] Debug listing: /opt/genesis and HOME"
        ls -la /opt/genesis 2>/dev/null || true
        ls -la "$HOME" 2>/dev/null || true
        exit 10
        fi

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
        DIRTY="$(git status --porcelain 2>/dev/null || true)"
        if [ -n "$DIRTY" ]; then
        echo "[remote] WARN: repo has local modifications; stashing before pull"
        git status --porcelain=v1 >"$ARCHIVE_DIR/git_status_porcelain.txt" 2>/dev/null || true
        git status >"$ARCHIVE_DIR/git_status.txt" 2>/dev/null || true
        git diff >"$ARCHIVE_DIR/git_diff.patch" 2>/dev/null || true
        git diff --cached >"$ARCHIVE_DIR/git_diff_cached.patch" 2>/dev/null || true
        git stash push -u -m "orchestrate_${TS}" >/dev/null 2>&1 || { echo "ERROR: git stash failed"; exit 11; }
        echo "[remote] stashed: $(git stash list | head -1 || true)"
        fi
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
        if python3 -c "import sys,urllib.request;\
    u=urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=2);\
    u.read();\
    sys.exit(0)" >/dev/null 2>&1; then OK=1; break; fi
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

# IMPORTANT: Normalize Windows CRLF to LF before sending to bash.
# Otherwise remote bash can error with: $'\r': command not found
$remoteScript = $remoteScript.Replace("`r`n", "`n").Replace("`r", "")

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
# Send payload as base64 to avoid nested-quoting issues in very long multiline bash scripts.
$remoteScriptB64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($remoteScript))
$remoteExec = "printf %s " + (ConvertTo-BashSingleQuoted $remoteScriptB64) + " | base64 -d | bash -seuo pipefail"
& ssh $SshTarget "bash -lc $(ConvertTo-BashSingleQuoted $remoteExec)"
