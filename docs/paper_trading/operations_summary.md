# Paper Trading Operations Summary

**Start Date:** 2026-02-04 09:29 UTC
**Champion:** v5a_sizing_exp1 (tBTCUSD_1h)
**Period:** 6 weeks (2026-02-04 to 2026-03-17)
**Status:** ✅ ACTIVE

---

## Current Drift Setup

**Server:**

- Process: uvicorn core.server:app (PID 24646)
- Port: 8000
- Method: nohup (manual, no auto-restart)
- Log: `logs/paper_trading/server_20260204_092946.log`
- Environment:
  - `GENESIS_SYMBOL_MODE=realistic`
  - `LOG_LEVEL=INFO`

**Persistence:** ⚠️ Manual (no auto-restart yet)

**Upgrade to persistent setup:** See `docs/paper_trading/server_setup.md`

- Recommended: Screen with auto-restart wrapper
- Alternative: pm2 or systemd

---

## Remote deployment (Azure VM) — status

**Goal:** Run the API server + runner on a small Ubuntu VM with persistent supervision (systemd) and a minimal attack surface.

**Current status (2026-02-12):** ✅ Remote runner is up.

- API service (`genesis-paper.service`): healthy on `http://127.0.0.1:8000/health` (VM-local only)
- Runner service (`genesis-runner.service`): running
- Preflight: **PASS**
- 24h acceptance: scheduled; output file is written under `logs/paper_trading/acceptance_check_<UTC_TS>.txt`
- Orchestration: `scripts/phase3_remote_orchestrate.ps1` (archives logs/state, stashes dirty repo, ff-pulls, restarts services)
  - Default SSH target: `genesis-we` (SSH config alias). Override via `-SshTarget` or `GENESIS_SSH_TARGET`.

**Stability checks (VM):**

```bash
# Verify only one uvicorn process is running
pgrep -af uvicorn

# Verify systemd restart counter is stable (not ticking up)
systemctl show genesis-paper.service -p MainPID -p NRestarts -p ActiveState -p SubState --no-pager

# Verify port 8000 is only bound on loopback
ss -ltnp | grep ':8000'
```

**What we learned (so far):**

- Earlier blocker: provisioning/workflows can be blocked until the signed-in identity can see at least one Azure subscription.
- VS Code Azure views can appear "empty" if a stale `azureResourceGroups.selectedSubscriptions` filter is present.
- One VM became unusable after accidental generalization; recovery path is to **recreate** from image/snapshot/disk once Azure access is restored.

**Security posture (intended):**

- SSH restricted to a single source IP (/32) in the NSG.
- Password authentication disabled; key-based auth only.

**Reference notes:**

- `docs/paper_trading/daily_summaries/day2_summary_2026-02-06.md` (initial tooling/subscription blocker)
- `docs/paper_trading/daily_summaries/day3_summary_2026-02-11.md` (identity/subscription + VS Code filter + VM incident)

---

## Artefakt-cykel

### 1. Daglig Health/Runtime Snapshot

**Script:** `scripts/daily_health_check.sh`
**Schedule:** Daily 00:00 UTC (manual until automated)
**Output:** `logs/paper_trading/daily_snapshots/health_YYYYMMDD.json`

**Content:**

- Server health (/health endpoint)
- Runtime config (/config/runtime)
- Git commit info (SHA, branch, clean status)
- Server uptime and PID
- Environment variables

**Action on failure:**

- Check server logs
- Restart server if needed
- Document incident

**Manual run:**

```bash
./scripts/daily_health_check.sh
```

---

### 2. Veckovis Metrics Report

**Script:** `scripts/calculate_paper_trading_metrics.py`
**Schedule:** Every Monday (end of week)
**Output:** `docs/paper_trading/weekly_reports/week_N_YYYYMMDD.md`

**Content:**

- Total trades
- Win rate, Profit factor, Max drawdown
- Commission %
- Primary criteria evaluation (PF ≥ 1.3, DD ≤ 3%, WR ≥ 50%, Trades ≥ 10)
- Secondary criteria (Sharpe, Return/DD, Commission)
- Pass/Fail status

**Manual run:**

```bash
python scripts/calculate_paper_trading_metrics.py \
  --start-date 2026-02-04 \
  --end-date 2026-02-10 \
  --week-num 1 \
  --output-dir docs/paper_trading/weekly_reports
```

**Documentation:** `docs/paper_trading/weekly_metrics.md`

---

### 3. Kontinuerlig Logging

**Server logs:**

- Location: `logs/paper_trading/server_YYYYMMDD.log`
- Rotation: Daily (automatic by filename)
- Retention: 30 days
- Monitor: `tail -f logs/paper_trading/server_$(date +%Y%m%d).log`

**Evaluate snapshots:**

- On-demand: `/strategy/evaluate` responses
- Location: `logs/paper_trading/evaluate_response_*.json`
- Purpose: Audit champion loading, decision quality

---

## Monitoring Checklist

### Daily (Automated)

- [ ] Health check passes
- [ ] Server uptime > 23 hours
- [ ] No errors in server log
- [ ] Champion loading verified (not baseline)

### Weekly (Manual)

- [ ] Metrics report generated
- [ ] Primary criteria pass/fail
- [ ] Red flags check (2 consecutive fails, DD > 5%)
- [ ] Trade count within expected range

### Ad-hoc (As needed)

- [ ] POST /strategy/evaluate test
- [ ] Champion file integrity check
- [ ] Git status clean (no uncommitted changes)
- [ ] Restart server if needed

---

## Red Flags (Stop Paper Trading)

1. **2 consecutive weeks fail primary criteria**
2. **Single week with DD > 5%**
3. **Champion loading fails** (baseline fallback detected)
4. **Unexpected errors** in strategy pipeline
5. **Server downtime** > 4 hours cumulative per week

**Action on red flag:**

1. Stop paper trading immediately
2. Document issue in daily summary
3. Investigate root cause
4. Escalate to decision: fix + continue OR abort period

---

## CI Re-verification Plan

**Context:**

- GitHub Actions degraded during pre-flight (incident f314nlctbfs5)
- Manual gate applied for commit 2ca031c (lint fixes + docs)
- Manual gate PASSED: pre-commit + pytest all green locally

**When to re-verify:**

- Monitor: https://www.githubstatus.com
- Wait for: "Actions: Operational" status
- Verify: No active incidents or degraded performance

**Re-verification steps:**

1. **Confirm GitHub Actions operational:**

   ```bash
   curl -s https://www.githubstatus.com/api/v2/status.json | grep -o '"indicator":"[^"]*"'
   # Expected: "indicator":"none" (no incidents)
   ```

2. **Check CI status for commit 2ca031c:**

   ```bash
   curl -s "https://api.github.com/repos/JohnCCarter/Genesis-Core/commits/2ca031c/check-runs" \
     | grep -E '"name"|"conclusion"'
   ```

3. **If CI not green, trigger re-run:**
   - Option A: Empty commit + push (triggers CI)
   - Option B: Manual re-run via GitHub UI

4. **Wait for CI green:**
   - lint-test: success
   - check-champion-freeze: success

5. **Update manual_gate doc:**

   ```bash
   # Append to docs/ops/manual_gate_2026-02-04.md
   echo "
   ## CI Re-verification (Post-Incident)

   **Date:** $(date -u +'%Y-%m-%d %H:%M:%S UTC')
   **GitHub Actions Status:** Operational
   **Commit:** 2ca031c

   **CI Results:**
   - lint-test: success
   - check-champion-freeze: success

   **Conclusion:** Manual gate validated by CI. Incident f314nlctbfs5 closed.
   " >> docs/ops/manual_gate_2026-02-04.md
   ```

6. **Commit update (docs-only):**

   ```bash
   git add docs/ops/manual_gate_2026-02-04.md
   git commit -m "docs: CI re-verified – incident f314nlctbfs5 closed

   GitHub Actions returned to operational status.
   Commit 2ca031c passed CI (lint-test + freeze-guard).
   Manual gate retrospectively validated.

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   git push
   ```

**Status:** ⏳ Monitoring GitHub Actions recovery

---

## Emergency Contacts / Escalation

**For issues during paper trading:**

1. Check `logs/paper_trading/` for recent errors
2. Review `docs/daily_summaries/` for context
3. Check `docs/bugs/known_issues.md` for documented problems
4. Escalate blocking issues immediately (freeze period is time-limited)

**Freeze period:** 2026-02-04 to 2026-03-17

- NO changes to champion config
- CI freeze-guard active
- Exception: Critical security/data-loss fixes only

---

## Success Criteria

**End of period (2026-03-17):**

**Primary:**

- ≥ 5/6 weeks pass primary criteria
- No red flags triggered
- Champion loading stable (no baseline fallbacks)
- Server uptime ≥ 99%

**Secondary:**

- Aggregate PF ≥ 1.3 (6-week average)
- Aggregate WR ≥ 55%
- Max single-week DD ≤ 3%
- Commission impact ≤ 2%

**Decision:**

- **PROMOTE:** All primary criteria met → Champion approved for live trading
- **ITERATE:** Primary criteria fail → Investigate, tune, re-validate
