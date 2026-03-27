# Research experiment RI objective slice 1 preparation

Date: 2026-03-27
Status: tracked / preparation-only / no execution yet
Lane: `run_intent: research_experiment`
Phase: `2 - RI internal research track`
Slice: `ri objective slice 1`

## Purpose

This artifact selects the smallest admissible first probe for the already defined RI objective slice.

This artifact does not authorize comparison, readiness, promotion, runtime mutation, or production writeback.

## Preparation decision

- The first objective probe should use the existing scoring surface before introducing any new score variant.
- The initial research comparison is therefore:
  - `score_version = v1` as the current reference
  - `score_version = v2` as the first bounded research-only alternative

## Why this is the smallest admissible probe

- `v2` already exists in `src/core/optimizer/scoring.py`
- it changes ranking logic without changing runtime decision behavior
- it avoids opening a new code seam before testing whether the current built-in alternative produces any meaningful change in RI selection evidence

## Exact bounded preparation surface

- `src/core/optimizer/scoring.py` existing `v1` / `v2` resolution only
- research-only execution notes or config preparation needed to replay the fixed `2023` and `2024` windows under each score version

## Fixed surface

- no RI runtime behavior change
- no strategy, gate, calibration, exit, or sizing changes
- no champion or runtime-default changes

## Decision rule for the first probe

- If `v2` materially improves RI ranking discipline or robustness evidence on the fixed windows, the objective lane may continue without introducing a new score variant yet.
- If `v2` is neutral or degrading, then either:
  - close this first objective probe, or
  - open one additional bounded research-only score variant as a separate next step

## Next admissible step

- The next admissible step after this preparation artifact is to run the fixed-window RI objective probe under `v1` and `v2` and classify the result.
- That run must remain research-only and must not be presented as comparison-eligible or runtime-valid evidence.
