# RI vs legacy — upstream candidate-authority diagnostic slice 1

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `research-diagnostic / observability only / no runtime change`

## Purpose

This document summarizes the first executed upstream diagnostic slice defined in:

- `docs/governance/regime_intelligence_upstream_candidate_authority_diagnostic_slice1_precode_packet_2026-03-30.md`

The slice was intentionally bounded to the upstream pre-fib chain only:

- `authority_mode_resolver`
- `evaluate`
- `prob_model`
- `decision_gates.select_candidate(...)`

Explicitly excluded from both artifact and interpretation:

- fib
- post-fib gates
- sizing
- exits
- trade-performance interpretation

## Diagnostic surface

Fixed observational surface:

- symbol/timeframe: `tBTCUSD 3h`
- fixed RI surface: slice8 full tuple on the sample window `2023-12-21 .. 2024-06-30`
- research wrapper: `tmp/ri_upstream_candidate_authority_trace.py`
- structured artifact: `artifacts/diagnostics/ri_upstream_candidate_authority_slice1_trace_20260330.json`

Observational control definition:

> The legacy-authority branch is an in-memory observational diagnostic control executed on the same fixed slice8 surface only. It is not a runtime-valid or launchable config, does not mutate on-disk configuration, and must not be interpreted as a promotion, readiness, or approved behavior-change proposal.

## Trace result

Processed bars: `1417`

Bars with any divergence in the bounded upstream trace: `1417 / 1417` (`100.000000%`)

First divergence stage counts:

- `authority_mode_resolver`: `1417`
- `evaluate`: `0` as first stage
- `prob_model`: `0` as first stage
- `decision_gates`: `0` as first stage
- `none`: `0`

This means the first observable divergence occurs immediately at:

> **`authority_mode_resolver`**

## How far the divergence propagates

Although first divergence appears immediately at authority resolution, it does not always stop there.

Stage-level divergence counts anywhere in the bounded chain:

- `authority_mode_resolver`: `1417 / 1417` (`100.000000%`)
- `evaluate`: `1417 / 1417` (`100.000000%`)
- `prob_model`: `1417 / 1417` (`100.000000%`)
- `decision_gates`: `328 / 1417` (`23.147495%`)

Candidate-formation divergence:

- bars with different candidate state: `327 / 1417` (`23.076923%`)
- bars with different direction outcome: `327 / 1417` (`23.076923%`)
- threshold-pass divergence:
  - buy-side: `148 / 1417`
  - sell-side: `27 / 1417`

So the diagnostic result is not merely metadata drift.

The local legacy-authority control diverges from the fixed RI branch at authority resolution on every processed bar, and that upstream divergence reaches the pre-fib candidate boundary on a meaningful minority of bars.

## Classification

Final classification for slice 1:

> **early upstream divergence**

Reason:

- first divergence appears at `authority_mode_resolver`, not late at `decision_gates`
- the divergence propagates through `evaluate` and `prob_model` on all processed bars
- pre-fib candidate formation is also affected on `327` bars, which means the divergence is upstream and action-relevant before fib/post-fib/sizing are involved

## Bottom line

On the fixed slice8 research surface, the first observable control-vs-RI separation occurs immediately at **authority resolution**, propagates through the upstream regime/probability handoff on **all** processed bars, and reaches pre-fib candidate formation on about **23.08%** of bars.

That makes the slice-1 result a clear case of **early upstream divergence**, not a late downstream-only effect.
