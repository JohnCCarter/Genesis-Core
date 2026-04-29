# RI vs legacy — upstream candidate-authority diagnostic slice 2

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `research-diagnostic / observability only / no runtime change`

## Purpose

This document summarizes the executed slice-2 diagnostic defined in:

- `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_candidate_authority_diagnostic_slice2_precode_packet_2026-03-30.md`

The slice remained strictly bounded to the authority/calibration handoff after the already-known `authority_mode` selector step from slice 1.

Explicitly excluded from both artifact and interpretation:

- fib
- post-fib gates
- sizing
- exits
- readiness / promotion / comparison framing

## Diagnostic surface

Fixed observational surface:

- symbol/timeframe: `tBTCUSD 3h`
- fixed RI surface: governed slice8 full tuple
- research wrapper: `tmp/ri_upstream_candidate_authority_slice2_trace.py`
- structured artifact: `artifacts/diagnostics/ri_upstream_candidate_authority_slice2_trace_20260330.json`

Observational control definition:

> The legacy-authority branch in this slice is an in-memory observational control used only for same-window comparison. It is not a materialized runtime authority path, promoted config, or shared execution surface.

## Result

Processed bars: `1417`

Eligible rows for earliest-class adjudication: `0 / 1417`

Ineligible rows: `1417 / 1417` (`100.000000%`)

Observed ineligibility reason:

- `raw_regime_label_missing`: `1417 / 1417`

Observed branch pattern on class 1 fields:

- control branch raw regime label missing: `0 / 1417`
- RI branch raw regime label missing: `1417 / 1417`

So the bounded slice-2 trace did **not** produce any row where class 1 was fully comparable across branches.

Because slice 2 requires earlier classes to be present and equal on the same row before a later class can be adjudicated, no row was eligible to establish class 2, class 3, or class 4 as the earliest observed divergence class.

## Final classification

Final classification for slice 2:

> **falsified / no class-2 earliest divergence**

Bounded interpretation:

- this slice-2 diagnostic trace does **not** identify `normalized authority-state divergence` as the earliest eligible divergence class on the fixed slice8 surface
- the gating reason is not downstream behavior, but class-1 ineligibility: the RI branch has no comparable raw regime label in the trace on any processed row
- this is an **observed bounded result**, not a claim of root cause outside this surface

## Bottom line

On the fixed slice8 research surface, slice 2 does **not** reach an eligible earliest divergence class inside the ordered authority/calibration handoff, because class 1 is ineligible on every processed row due to missing RI raw regime label output.

That means the slice-2 hypothesis is **not supported** here, and the final bounded classification is:

- **falsified / no class-2 earliest divergence**
