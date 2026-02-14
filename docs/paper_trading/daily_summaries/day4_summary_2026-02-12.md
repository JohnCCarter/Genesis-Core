# Phase 3 Day 4 Summary - 2026-02-12

**Day:** 4/42
**Date:** 2026-02-12
**Status:** ✅ ACTIVE - New West Europe VM is stable; services running; API bound to loopback

---

## Summary

Today’s focus was stabilizing and validating the new Azure VM setup in **West Europe**, ensuring:

- the API is **not publicly exposed** (binds only to `127.0.0.1:8000`),
- systemd supervision is stable (no ongoing restart loop), and
- the process model is clean (only one `uvicorn`).

---

## VM status (genesis-we)

- SSH target: **`genesis-we`** (SSH config alias)
- Repo location: `/opt/genesis/Genesis-Core`
- Branch: `feature/composable-strategy-phase2`
- Commit: `a1f0f1b`
- Python: `3.12.3`

### API server (systemd)

- Unit: `genesis-paper.service`
- Verified:
  - `uvicorn` is bound to `127.0.0.1:8000`
  - `/health` returns **200**
  - `pgrep -af uvicorn` shows **a single process**
  - `systemctl show ... -p NRestarts` is stable at **0**

**Note:** `api_service.log` / `journalctl` contains historical restart-loop entries caused by `Errno 98 (address already in use)`,
but the last start is successful and the service is stable.

### Runner (systemd)

- Unit: `genesis-runner.service`
- Status: `active (running)`
- `NRestarts=0` (stable)
- Latest runner log:
  - `logs/paper_trading/runner_20260212.log`

---

## Tooling / orchestration

- `scripts/phase3_remote_orchestrate.ps1` defaults to SSH target `genesis-we`.
- The orchestrator fails fast if systemd units are missing (more actionable than a late `systemctl start` failure).

---

## Documentation / operational hardening

- Paper trading docs were aligned to the current VM operating model:
  - Use `SYMBOL_MODE` (replacing historical `GENESIS_SYMBOL_MODE`).
  - systemd examples load settings via `EnvironmentFile=.../.env` and bind the API to loopback (`127.0.0.1`).
  - Added an incident note: `.env` must be **UTF-8 without BOM** when used with systemd `EnvironmentFile=`.
  - Added an operational note on **Bitfinex spot vs positions** (verify execution via runner logs + orders/wallet deltas).

- Bitfinex connectivity/auth was smoke-tested locally (project venv): REST/WS auth ok; public REST/WS ok.

---

## Next steps

1. If not already done for this VM instance, run the remote orchestrator **without** `-DryRun` once you want a clean restart + preflight.
2. Schedule the 24h acceptance check and confirm the output file appears under:
   - `logs/paper_trading/acceptance_check_<UTC_TS>.txt`
3. After 24h, review acceptance output and proceed per `docs/paper_trading/phase3_runbook.md`.
