# Research experiment RI objective slice 1 execution outcome

Date: 2026-03-27
Status: tracked / execution-complete / classified
Lane: `run_intent: research_experiment`
Slice: `ri objective slice 1`

## Execution basis

- symbol: `tBTCUSD`
- timeframe: `3h`
- fixed windows:
  - train: `2023-01-01..2023-12-31`
  - validation: `2024-01-01..2024-12-31`
- comparison basis:
  - RI anchor control
  - RI regime-calibration negative slice
  - RI balanced-conflict negative slice
- runtime behavior: unchanged
- objective probe: recompute ranking under existing `score_version = v2` versus current `v1`

## Recomputed scores

### Train window

- control: `v1=0.2921` / `v2=0.2918`
- regime-calibration candidate: `v1=0.1772` / `v2=0.1765`
- balanced-conflict candidate: `v1=0.2391` / `v2=0.2385`

### Validation window

- control: `v1=0.3124` / `v2=0.3118`
- regime-calibration candidate: `v1=0.2331` / `v2=0.2331`
- balanced-conflict candidate: `v1=0.2751` / `v2=0.2753`

## Observed effect

- `v2` preserved the same ordering as `v1` on both fixed windows.
- `v2` did not materially widen or sharpen the separation between the RI anchor and the two already degraded candidate slices.
- No new runtime-valid evidence was created; this remained a research-only ranking probe.

## Classification

- classification: `plateau`

## Decision

- Do not treat the existing built-in `v2` score as a meaningful new RI objective uplift by itself.
- The first RI objective probe is closed as non-confirming but non-harmful.
- If RI continues, the next admissible move is either:
  - open one additional bounded research-only score variant as a separate slice, or
  - pause RI and return to experiment-map selection outside RI.
