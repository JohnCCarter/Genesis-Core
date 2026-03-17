# RI P1 OFF parity governed baseline reset — execution outcome sign-off summary

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `execution-complete / sign-off achieved for ri_p1_off_parity_v1`

## Purpose

This document closes the governed execution for:

- `governed baseline reset via parity rerun`
- under frozen spec `ri_p1_off_parity_v1`

It records the canonical outcome, the execution provenance, and the sign-off basis for this completed run.

## Canonical artifact

Canonical artifact produced by the rerun:

- `results/evaluation/ri_p1_off_parity_v1_ri-20260317-001.json`

Recorded canonical result:

- `parity_verdict=PASS`
- `action_mismatch_count=0`
- `reason_mismatch_count=0`
- `size_mismatch_count=0`
- `added_row_count=0`
- `missing_row_count=0`
- `size_tolerance=1e-12`

## Execution provenance

This run was executed against the pinned reviewed provenance:

- branch: `feature/regime-intelligence-cutover-analysis-v1`
- full SHA: `1c2f38ad88723034b819b7844c69d138a7702086`
- `run_id=ri-20260317-001`
- `window_spec_id=ri_p1_off_parity_v1`
- `mode=OFF`
- spec symbol recorded in artifact metadata: `tTESTBTC:TESTUSD`
- datasource-materialized backtest symbol: `tBTCUSD`
- timeframe: `1h`
- `start_utc=2025-01-01T00:00:00Z`
- `end_utc=2025-01-31T23:59:59Z`
- `runtime_config_source=default runtime authority (no --config-file)`

The datasource materialization through `tBTCUSD` was an explicitly approved execution detail only.
It did **not** change the frozen spec symbol and did **not** change canonical artifact metadata.

## Supplemental evidence retained

The completed run retained the following supplemental governance evidence:

- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_ri-20260317-001.json`
- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_ri-20260317-001.json`
- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_ri-20260317-001.json`

Manifest-linked SHA256 values:

- baseline rows: `b135558eb81941728f2bff5e852c9765d360247e48d64d26a29ec47960a57e6a`
- candidate rows: `b135558eb81941728f2bff5e852c9765d360247e48d64d26a29ec47960a57e6a`
- canonical artifact: `1e4e4267c499ae5ffc7b899cab58adb868d14798b25a3f43739c0376a6e4e9ff`

## Gate bundle outcome

The full gate bundle required by the execution runbook was executed on the pinned execution worktree and completed green.

This includes:

- repo hygiene / smoke
- determinism replay
- feature cache invariance
- pipeline invariant
- evaluate/source contract checks
- comparator / decision-row contract checks
- named skill checks

Outcome:

- full gate bundle: `PASS`

## Sign-off conclusion

The governed rerun satisfied the RI P1 OFF parity sign-off contract for the frozen spec `ri_p1_off_parity_v1`.

Sign-off basis for this completed run:

- canonical artifact produced at the locked path shape
- `parity_verdict=PASS`
- all mismatch counters equal `0`
- full gate bundle green
- provenance and supplemental evidence retained with manifest-linked hashes

This execution therefore completes the governed baseline reset parity rerun for:

- `ri_p1_off_parity_v1`
- canonical artifact: `ri_p1_off_parity_v1_ri-20260317-001.json`
