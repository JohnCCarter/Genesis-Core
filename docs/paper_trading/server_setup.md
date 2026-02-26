# Paper Trading Server Setup

## Server Persistence Options

### Option 1: Screen (Recommended for Windows/MINGW)

**Start server in detached screen:**

```bash
cd /c/Users/fa06662/Projects/Genesis-Core
. .venv/Scripts/activate

# Create new screen session
screen -S genesis-paper -dm bash -c "
  SYMBOL_MODE=realistic LOG_LEVEL=INFO \
  uvicorn core.server:app --app-dir src --port 8000 \
  >> logs/paper_trading/server_\$(date +%Y%m%d).log 2>&1
"

# Verify running
screen -ls
```

**Attach to running session:**

```bash
screen -r genesis-paper
# Ctrl+A, D to detach
```

**Auto-restart wrapper:**

```bash
# Create restart script: scripts/start_paper_trading_server.sh
#!/bin/bash
cd /c/Users/fa06662/Projects/Genesis-Core
. .venv/Scripts/activate

while true; do
  echo "$(date): Starting server..." >> logs/paper_trading/restart.log
  SYMBOL_MODE=realistic LOG_LEVEL=INFO \
    uvicorn core.server:app --app-dir src --port 8000 \
    >> logs/paper_trading/server_$(date +%Y%m%d).log 2>&1

  echo "$(date): Server stopped. Restarting in 5s..." >> logs/paper_trading/restart.log
  sleep 5
done
```

**Start with auto-restart:**

```bash
chmod +x scripts/start_paper_trading_server.sh
screen -S genesis-paper -dm scripts/start_paper_trading_server.sh
```

---

### Option 2: pm2 (Node.js process manager)

**Install:**

```bash
npm install -g pm2
```

**Start:**

```bash
cd /c/Users/fa06662/Projects/Genesis-Core
pm2 start --name genesis-paper \
  --interpreter .venv/Scripts/python \
  --interpreter-args "$(which uvicorn) core.server:app --app-dir src --port 8000" \
  --log logs/paper_trading/server_$(date +%Y%m%d).log \
  --env SYMBOL_MODE=realistic \
  --env LOG_LEVEL=INFO \
  --restart-delay 3000
```

**Monitor:**

```bash
pm2 status
pm2 logs genesis-paper
pm2 restart genesis-paper
pm2 stop genesis-paper
```

---

### Option 3: systemd (Linux, incl. Azure VM)

**Important:** Use native Linux paths and a Linux-created virtualenv (`.venv/bin/python`).
Do not point systemd at Windows paths or a Windows-created venv.

**Create service file:** `/etc/systemd/system/genesis-paper.service`

```ini
[Unit]
Description=Genesis Paper Trading Server
After=network.target

[Service]
Type=simple
User=genesis
WorkingDirectory=/opt/genesis/Genesis-Core
# Generate /opt/genesis/Genesis-Core/.env.systemd from .env before daemon-reload.
# Load secrets and runtime settings from the systemd-safe env file.
EnvironmentFile=/opt/genesis/Genesis-Core/.env.systemd
ExecStart=/opt/genesis/Genesis-Core/.venv/bin/python \
  -m uvicorn core.server:app --app-dir src --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
# Prefer journald via `journalctl -u genesis-paper`.
# If you need file logs, use a fixed path + logrotate (avoid strftime-like tokens in unit files).
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Control:**

```bash
sudo systemctl start genesis-paper
sudo systemctl status genesis-paper
sudo systemctl enable genesis-paper  # Auto-start on boot
```

### Dev vs Runtime paths on `genesis-we` (important)

On the VM there are often two repo trees:

- **Dev workspace:** `/home/azureuser/Genesis-Core`
- **Runtime/systemd workspace:** `/opt/genesis/Genesis-Core`

`genesis-paper.service` runs from `WorkingDirectory=/opt/genesis/Genesis-Core`.
Changes in `/home/azureuser/Genesis-Core` do **not** go live until you explicitly deploy/sync to `/opt/genesis/Genesis-Core` and restart.

### Minimal deploy checklist (`/home` -> `/opt`)

1. **Verify both trees (before deploy):**

```bash
git -C /home/azureuser/Genesis-Core rev-parse --short HEAD
git -C /opt/genesis/Genesis-Core rev-parse --short HEAD
git -C /home/azureuser/Genesis-Core status --short
git -C /opt/genesis/Genesis-Core status --short
```

2. **Sync code from dev to runtime tree** (adjust excludes as needed):

```bash
rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'logs' \
  --exclude 'results' \
  /home/azureuser/Genesis-Core/ /opt/genesis/Genesis-Core/
```

**One-command alternative (recommended):**

```bash
/home/azureuser/Genesis-Core/scripts/deploy_home_to_opt.sh --dry-run
/home/azureuser/Genesis-Core/scripts/deploy_home_to_opt.sh
```

By default, deploy script also writes an RC diagnostics bundle to:

- `/opt/genesis/Genesis-Core/logs/paper_trading/rc_capture_<UTC>.txt`

Disable this for a specific deploy with:

```bash
/home/azureuser/Genesis-Core/scripts/deploy_home_to_opt.sh --no-rc
```

3. **Regenerate systemd-safe env file** (if `.env` changed):

```bash
/opt/genesis/Genesis-Core/scripts/generate_env_systemd.sh \
  /opt/genesis/Genesis-Core/.env \
  /opt/genesis/Genesis-Core/.env.systemd
```

4. **Reload and restart services:**

```bash
sudo systemctl daemon-reload
sudo systemctl restart genesis-paper genesis-runner
```

5. **Post-deploy verification:**

```bash
systemctl show genesis-paper -p WorkingDirectory -p MainPID -p NRestarts -p ActiveState -p SubState --no-pager
systemctl show genesis-paper -p EnvironmentFiles -p DropInPaths --no-pager
ss -ltnp | grep ':8000 '
curl -s http://127.0.0.1:8000/health
```

6. **Confirm trees are aligned** (optional but recommended):

```bash
git -C /home/azureuser/Genesis-Core rev-parse --short HEAD
git -C /opt/genesis/Genesis-Core rev-parse --short HEAD
```

If HEAD differs, you are running code that is not identical to your dev workspace.

---

## Historical Note (Local manual start)

This section is a historical snapshot from early Phase 3 bring-up. For Azure VM production, prefer the systemd setup
above and treat PIDs as ephemeral (record them via snapshots rather than hardcoding).

**Started:** 2026-02-04 09:29 UTC
**PID:** 24646
**Method:** nohup (no auto-restart)
**Log:** `logs/paper_trading/server_20260204_092946.log`

**To upgrade to persistent setup:**

1. Stop current server: `kill 24646`
2. Choose option (Screen recommended)
3. Start with auto-restart
4. Verify with `curl http://localhost:8000/health`

---

## Health Monitoring

**Manual check:**

```bash
curl -s http://localhost:8000/health | python -c "
import json, sys
d = json.load(sys.stdin)
print(f\"Status: {d.get('status')}\")
print(f\"Config version: {d.get('config_version')}\")
"
```

**Automated daily check:** See `scripts/daily_health_check.sh`

---

## UTF-8 without BOM for `.env` (systemd EnvironmentFile)

When using `EnvironmentFile=.../.env`, systemd reads the file as plain text. If the file starts with a UTF-8 BOM
(`EF BB BF`), the first variable name can become invisible/invalid and variables may not load as expected.

### How to detect BOM

- **On Linux (VM):**

  ```bash
  # Prints "UTF-8 Unicode (with BOM)" if BOM is present
  file -b --mime-encoding /opt/genesis/Genesis-Core/.env

  # Hex-dump first bytes (BOM = ef bb bf)
  head -c 3 /opt/genesis/Genesis-Core/.env | hexdump -C
  ```

- **On Windows (VS Code):**
  - Look at the status bar (bottom-right). It should say **UTF-8** (not **UTF-8 with BOM**).
  - Command Palette → “Change File Encoding” → “Save with Encoding” → **UTF-8**.

### How to remove BOM

- **On Linux:**

  ```bash
  # Create a BOM-free copy atomically
  sed '1s/^\xEF\xBB\xBF//' /opt/genesis/Genesis-Core/.env > /opt/genesis/Genesis-Core/.env.tmp \
    && mv /opt/genesis/Genesis-Core/.env.tmp /opt/genesis/Genesis-Core/.env
  ```

- **On Windows:** re-save the file as **UTF-8** (no BOM) in your editor, then re-deploy `.env` to the VM.

### Why this matters

If the API starts but behaves like credentials/settings are missing (while the `.env` “looks fine”), BOM is a common
culprit for the first line.

### Recommended operation: generate `.env.systemd` from `.env`

Instead of pointing systemd directly at `.env`, generate a dedicated systemd-safe file and use that in all services.

```bash
# From repo root on the VM:
./scripts/generate_env_systemd.sh /opt/genesis/Genesis-Core/.env /opt/genesis/Genesis-Core/.env.systemd

# Then reload + restart services that use EnvironmentFile
sudo systemctl daemon-reload
sudo systemctl restart genesis-paper genesis-runner genesis-mcp
```

Operational routine after editing `.env`:

1. Regenerate `.env.systemd`
2. `daemon-reload`
3. Restart affected services
4. Verify health endpoints + `systemctl show ... -p NRestarts`

---

## Service Reliability (systemd)

Recommended hardening for long-running services:

- Use `Restart=always` for the API and runner.
- Use a small backoff (`RestartSec=5`–`10`) to avoid restart storms.
- Set `TimeoutStopSec` so deploy/restart doesn't hang indefinitely.

### Verify service health

```bash
sudo systemctl status genesis-paper --no-pager
sudo systemctl show genesis-paper -p MainPID -p NRestarts -p ActiveState -p SubState --no-pager

# API is loopback-only on the VM
curl -s http://127.0.0.1:8000/health

# Logs (preferred)
journalctl -u genesis-paper -n 200 --no-pager
```

### Capture RC diagnostics bundle on demand

```bash
/opt/genesis/Genesis-Core/scripts/capture_paper_rc.sh --window-minutes 30
```

This captures systemd status/cat, targeted journald windows, listener/process snapshots,
and recent service log tails into a timestamped file for root-cause analysis.

### Simulate a crash test (safe)

This is useful after deploy/hardening changes.

```bash
# Force-stop the process and confirm systemd restarts it
sudo systemctl kill -s SIGKILL genesis-paper
sleep 2
sudo systemctl show genesis-paper -p NRestarts -p MainPID --no-pager
```

---

## Weekend Go-Live Gate (Recommended)

Before enabling `genesis-runner` for a weekend run, execute the automated gate:

```bash
cd /opt/genesis/Genesis-Core
./scripts/weekend_bot_gate.sh
```

Expected signature:

- `RESULT: PASS`
- Report artifact written to:
  - `logs/paper_trading/weekend_gate_<UTC>.txt`

Stop policy:

- If any check fails, the script exits non-zero and prints `RESULT: FAIL`.
- Do not proceed with manual runner activation until the failing check is fixed.

Runtime note for `1h` timeframe:

- Between candle closes, logs can show polling/skip behavior without new actions.
- This is normal and not itself a failure.

## Log Rotation

**Daily logs:** Server creates new log per day (filename includes YYYYMMDD)

**Cleanup old logs (manual):**

```bash
# Keep last 30 days
find logs/paper_trading/ -name "server_*.log" -mtime +30 -delete
```

**Automated cleanup:** Add to daily cron or Task Scheduler

---

## Emergency Procedures

**Server not responding:**

```bash
# 1. Check if process running
ps aux | grep uvicorn

# 2. Check logs
tail -50 logs/paper_trading/server_$(date +%Y%m%d).log

# 3. Restart (if using screen)
screen -X -S genesis-paper quit
screen -S genesis-paper -dm scripts/start_paper_trading_server.sh

# 4. Verify
curl http://localhost:8000/health
```

**Port already in use:**

```bash
# Find process using port 8000
netstat -ano | grep :8000
# Kill process (Windows)
taskkill /PID <PID> /F
```

---

## Paper Trading Validation Period

**Duration:** 2026-02-04 to 2026-03-17 (6 weeks)
**Uptime target:** 99%+ (allow brief restarts for updates)
**Monitor:** Daily health checks + weekly metrics reports
