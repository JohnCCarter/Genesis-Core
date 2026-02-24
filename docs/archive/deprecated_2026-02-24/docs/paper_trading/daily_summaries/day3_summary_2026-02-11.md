# Phase 3 Day 3 Summary - 2026-02-11

**Day:** 3/42
**Date:** 2026-02-11
**Status:** ✅ ACTIVE - Remote runner started; preflight PASS; 24h acceptance scheduled

---

## Summary

This day was about two things:

1. Capturing the missing operational context around the Azure attempt (so it doesn’t only live in chat history).
2. Hardening the paper trading runner against a real-world failure mode we observed: fetching a candle window in the wrong order can quietly distort indicators and keep the strategy in a “stuck” confidence band.

---

## Work completed

### 1) Paper trading runner reliability (candles window ordering)

**Change:** When fetching a candles window for `/strategy/evaluate`, request the _newest_ $N$ candles ending at `end_ms` (`sort=-1`) and then reverse the payload back to chronological order before building arrays.

**Why:** Bitfinex candle history responses are order-sensitive; indicator calculations require chronological arrays (oldest → newest), but we also need the _most recent_ window.

**Regression coverage:** A focused unit test asserts:

- the request uses `sort=-1` (newest-first), and
- output arrays are chronological.

### 2) Defensive persisted-state guard

**Change:** On startup, if persisted `pipeline_state.last_close` differs wildly from the live startup candle close (relative mismatch threshold), reset `pipeline_state` to avoid propagating incompatible hysteresis/cooldown state.

---

## Azure notes (remote runner hosting)

### Update (later on 2026-02-11): remote runner is running

- Services are supervised by systemd (`genesis-paper.service`, `genesis-runner.service`).
- Preflight smoke test: **PASS**.
- 24h acceptance check was scheduled; output is written to:
  - `logs/paper_trading/acceptance_check_<UTC_TS>.txt` and `...txt.pid`
- API binds to `127.0.0.1:8000` on the VM (not exposed publicly).

### Identity / subscription visibility blocker

Symptom:

- Login succeeds (tenant is visible), but **0 subscriptions** are returned.

Impact:

- VM provisioning and recovery steps cannot proceed until a subscription is accessible.

### VS Code Azure “empty view” pitfall

We observed that VS Code Azure views can appear empty when a stale subscription filter exists:

- Setting: `azureResourceGroups.selectedSubscriptions`

Mitigation:

- Remove the stale filter and re-auth in VS Code so the extension can re-discover subscriptions.

### VM incident: accidental generalization

One VM became unusable after accidental generalization. Practical recovery path:

- **Recreate** a VM from an image/snapshot/disk backup (once subscription access is restored), then re-apply:
  - NSG hardening (SSH restricted to a single source IP /32)
  - key-based SSH only
  - systemd services for API server + runner

---

## Local repo hygiene

- Avoid committing local installer artifacts (e.g. `AzureCLI.msi`).

---

## Next steps

1. Restore Azure subscription visibility (Portal verification + ensure correct tenant/identity).
2. Once unblocked, rebuild the VM from a known-good image/snapshot/disk and re-apply security hardening.
3. Run the paper trading runner in dry-run mode for 24h on the remote host before enabling live paper orders.
