# Legacy + RI research Phase 2 RI preparation review

Date: 2026-03-27
Status: tracked / analysis-only / fail-closed
Lane: `run_intent: research_experiment`
Phase: `2 - RI internal research track`
Slice: `ri regime calibration slice 1`

## Purpose

This artifact reviews whether the selected RI regime-calibration slice can proceed to bounded preparation inside the current research lane.

## Result

- The slice cannot proceed further inside the current `research_experiment` lane.
- The correct action is to fail closed at this boundary.

## Why the slice is blocked

- The selected candidate surface is `src/core/strategy/prob_model.py`.
- The active research lane explicitly forbids modifying `src/core/**`.
- The existing regime-aware calibration seam is already wired through `ModelRegistry.get_meta(symbol, timeframe)` and the canonical model metadata files under `config/models/**`.
- For `tBTCUSD_3h`, the active calibration data lives in `config/models/tBTCUSD_3h.json`.
- Writing a new calibration mapping into that active file would be writeback to a production path, which is forbidden in this lane.
- A separate research-only model metadata path is not currently available through an existing config-only override seam.

## Boundary conclusion

- A config-only continuation is not currently admissible for this exact slice.
- An implementation continuation is also not admissible in this lane because it would require touching `src/core/**`.
- Therefore this exact RI regime-calibration slice is blocked under current lane constraints.

## Decision

- classify this slice as `blocked`
- do not implement
- do not create research config for this exact slice
- do not launch or validate execution for this slice

## Next admissible move

- return to governed selection and choose a different next-hypothesis slice that can proceed without touching `src/core/**` or production model paths
- or open a separately authorized lane before any code-surface continuation is considered
