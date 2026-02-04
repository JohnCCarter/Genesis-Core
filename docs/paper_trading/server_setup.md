# Paper Trading Server Setup

## Server Persistence Options

### Option 1: Screen (Recommended for Windows/MINGW)

**Start server in detached screen:**
```bash
cd /c/Users/fa06662/Projects/Genesis-Core
. .venv/Scripts/activate

# Create new screen session
screen -S genesis-paper -dm bash -c "
  GENESIS_SYMBOL_MODE=realistic LOG_LEVEL=INFO \
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
  GENESIS_SYMBOL_MODE=realistic LOG_LEVEL=INFO \
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
  --env GENESIS_SYMBOL_MODE=realistic \
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

### Option 3: systemd (Linux/WSL)

**Create service file:** `/etc/systemd/system/genesis-paper.service`
```ini
[Unit]
Description=Genesis Paper Trading Server
After=network.target

[Service]
Type=simple
User=fa06662
WorkingDirectory=/c/Users/fa06662/Projects/Genesis-Core
Environment="GENESIS_SYMBOL_MODE=realistic"
Environment="LOG_LEVEL=INFO"
ExecStart=/c/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python \
  -m uvicorn core.server:app --app-dir src --port 8000
Restart=always
RestartSec=5
StandardOutput=append:/c/Users/fa06662/Projects/Genesis-Core/logs/paper_trading/server_%Y%m%d.log
StandardError=append:/c/Users/fa06662/Projects/Genesis-Core/logs/paper_trading/server_%Y%m%d.log

[Install]
WantedBy=multi-user.target
```

**Control:**
```bash
sudo systemctl start genesis-paper
sudo systemctl status genesis-paper
sudo systemctl enable genesis-paper  # Auto-start on boot
```

---

## Current Setup (Manual)

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
